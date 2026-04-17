#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent, indent


def slugify(value: str, separator: str = "-") -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", separator, value.strip().lower()).strip(separator)
    return normalized or "pipeline-skill"


def python_name(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized or "stage"


def title_case_slug(value: str) -> str:
    return " ".join(part.capitalize() for part in slugify(value).split("-"))


@dataclass(frozen=True)
class StageSpec:
    stage_id: str
    title: str
    purpose: str
    artifact_basename: str
    json_fields: tuple[str, ...]
    template_title: str
    template_sections: tuple[str, ...]
    input_files: tuple[str, ...]

    @property
    def module_name(self) -> str:
        return python_name(self.stage_id)

    @property
    def adapter_filename(self) -> str:
        return f"{self.module_name}_adapter.py"

    @property
    def validator_filename(self) -> str:
        return f"{self.module_name}_validator.py"

    @property
    def json_filename(self) -> str:
        return f"{self.artifact_basename}.json"

    @property
    def markdown_filename(self) -> str:
        return f"{self.artifact_basename}.md"


@dataclass(frozen=True)
class SkillSpec:
    skill_slug: str
    display_name: str
    description: str
    goal: str
    stage_prefix: str
    stages: tuple[StageSpec, ...]

    @property
    def capability_prefix(self) -> str:
        return python_name(self.stage_prefix)


def parse_stage(stage_data: dict, previous_json: str | None) -> StageSpec:
    stage_id = stage_data["id"]
    artifact_basename = slugify(stage_data.get("artifact_basename", stage_id))
    json_fields = tuple(stage_data.get("json_fields") or ("summary",))
    template_sections = tuple(stage_data.get("template_sections") or ("目标", "内容", "待确认项"))
    input_files = tuple(stage_data.get("input_files") or (() if previous_json is None else (previous_json,)))
    return StageSpec(
        stage_id=stage_id,
        title=stage_data.get("title", title_case_slug(stage_id)),
        purpose=stage_data.get("purpose", f"完成 {stage_id} 阶段产出。"),
        artifact_basename=artifact_basename,
        json_fields=json_fields,
        template_title=stage_data.get("template_title", title_case_slug(artifact_basename)),
        template_sections=template_sections,
        input_files=input_files,
    )


def load_spec(path: Path) -> SkillSpec:
    payload = json.loads(path.read_text(encoding="utf-8"))
    previous_json: str | None = None
    stages = []
    for raw_stage in payload["stages"]:
        stage = parse_stage(raw_stage, previous_json)
        stages.append(stage)
        previous_json = stage.json_filename
    skill_slug = slugify(payload["skill_slug"])
    stage_prefix = payload.get("stage_prefix") or python_name(skill_slug)
    return SkillSpec(
        skill_slug=skill_slug,
        display_name=payload.get("display_name", title_case_slug(skill_slug)),
        description=payload.get(
            "description",
            f"Use when 需要执行 {skill_slug} 对应的多阶段业务流水线。",
        ),
        goal=payload.get("goal", f"完成 {skill_slug} 的核心业务产物输出。"),
        stage_prefix=stage_prefix,
        stages=tuple(stages),
    )


def capability_key(spec: SkillSpec, stage: StageSpec) -> str:
    return f"{spec.capability_prefix}_{python_name(stage.stage_id)}"


def capability_env_prefix(spec: SkillSpec, stage: StageSpec) -> str:
    return capability_key(spec, stage).upper()


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def indent_block(text: str, spaces: int) -> str:
    return indent(text.rstrip(), " " * spaces)


def render_skill_md(spec: SkillSpec) -> str:
    stage_lines = "\n".join(f"- `{stage.stage_id}`" for stage in spec.stages)
    artifact_lines = "\n".join(
        f"- `{stage.json_filename}` / `{stage.markdown_filename}`" for stage in spec.stages
    )
    return dedent(
        f"""\
        ---
        name: {spec.skill_slug}
        description: {spec.description}
        ---

        # {spec.display_name}

        `{spec.skill_slug}` 是一个基于 `pipeline-framework` 的业务流水线 skill，用于完成这项目标：

        {spec.goal}

        ## Quick Reference

        核心阶段：

        {stage_lines}

        核心产物：

        {artifact_lines}

        主要入口：

        - `scripts/run_skill.py`
        - `scripts/run_pipeline.py`
        - `references/pipeline.md`

        ## Quick Start

        只做 capability probe：

        ```bash
        python3 skills/{spec.skill_slug}/scripts/run_skill.py <run_dir> --check-only
        ```

        执行整条流水线：

        ```bash
        python3 skills/{spec.skill_slug}/scripts/run_skill.py <run_dir> --mode dev-mock --allow-mock
        ```

        ## Generated Notes

        这个 skill 由 `pipeline-create` 生成，默认所有阶段先提供 `builtin` provider 以保证闭环可运行。

        继续业务化时，优先补这些内容：

        - `references/pipeline.md` 的阶段说明
        - `assets/templates/` 的真实模板
        - `scripts/adapters/` 的真实 provider 逻辑
        - `scripts/validators/` 的更严格契约校验
        """
    )


def render_openai_yaml(spec: SkillSpec) -> str:
    return dedent(
        f"""\
        interface:
          display_name: "{spec.display_name}"
          short_description: "生成后的业务流水线 skill"
          default_prompt: "Use ${spec.skill_slug} to run the generated business pipeline and produce its stage artifacts."
        """
    )


def render_reference_pipeline_md(spec: SkillSpec) -> str:
    sections = []
    for index, stage in enumerate(spec.stages, start=1):
        inputs = ", ".join(stage.input_files) if stage.input_files else "(none)"
        outputs = f"{stage.json_filename}, {stage.markdown_filename}"
        sections.append(
            dedent(
                f"""\
                {index}. `{stage.stage_id}`
                   - purpose: {stage.purpose}
                   - inputs: {inputs}
                   - outputs: {outputs}
                """
            ).rstrip()
        )
    body = "\n".join(sections)
    return dedent(
        f"""\
        # {spec.display_name} Pipeline

        目标：

        {spec.goal}

        阶段定义：

        {body}

        说明：

        - 所有阶段默认先走 builtin，以便先验证 framework 接入闭环
        - 第二阶段起默认依赖上一阶段的 `.json` 产物
        - 如需接入真实 provider，按 stage 逐步替换 adapter 即可
        """
    )


def render_template(stage: StageSpec) -> str:
    sections = "\n\n".join(f"## {section}\n- 待确认" for section in stage.template_sections)
    return dedent(
        f"""\
        # {stage.template_title}

        {sections}
        """
    )


def render_pipeline_spec_py(spec: SkillSpec) -> str:
    stage_order = ",\n".join(f'    "{stage.stage_id}"' for stage in spec.stages)
    stage_inputs = ",\n".join(
        f'    "{stage.stage_id}": {list(stage.input_files)!r}' for stage in spec.stages
    )
    stage_outputs = ",\n".join(
        f'    "{stage.stage_id}": {[stage.json_filename, stage.markdown_filename]!r}' for stage in spec.stages
    )
    adapters = ",\n".join(
        f'    "{stage.stage_id}": "{stage.adapter_filename}"' for stage in spec.stages
    )
    validators = ",\n".join(
        f'    "{stage.stage_id}": "{stage.validator_filename}"' for stage in spec.stages
    )
    return (
        "from __future__ import annotations\n\n"
        "from pathlib import Path\n\n\n"
        "STAGE_ORDER = [\n"
        f"{stage_order}\n"
        "]\n\n"
        "STAGE_INPUTS = {\n"
        f"{stage_inputs}\n"
        "}\n\n"
        "STAGE_OUTPUTS = {\n"
        f"{stage_outputs}\n"
        "}\n\n"
        "ADAPTERS = {\n"
        f"{adapters}\n"
        "}\n\n"
        "VALIDATORS = {\n"
        f"{validators}\n"
        "}\n\n\n"
        "def adapter_paths(script_root: Path) -> dict[str, Path]:\n"
        '    adapter_dir = script_root / "adapters"\n'
        "    return {stage: adapter_dir / ADAPTERS[stage] for stage in STAGE_ORDER}\n\n\n"
        "def validator_paths(script_root: Path) -> dict[str, Path]:\n"
        '    validator_dir = script_root / "validators"\n'
        "    return {stage: validator_dir / VALIDATORS[stage] for stage in STAGE_ORDER}\n"
    )


def render_run_skill_py(spec: SkillSpec) -> str:
    return dedent(
        f"""\
        #!/usr/bin/env python3
        from __future__ import annotations

        import argparse
        import os
        import sys
        from pathlib import Path


        SCRIPT_ROOT = Path(__file__).resolve().parent
        if str(SCRIPT_ROOT) not in sys.path:
            sys.path.insert(0, str(SCRIPT_ROOT))

        FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[1].parent / "pipeline-framework" / "scripts"
        if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:
            sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))

        from framework.runner.core import execute_skill_launcher  # noqa: E402
        from runtime.capability_probe import probe_capabilities  # noqa: E402


        def build_parser() -> argparse.ArgumentParser:
            parser = argparse.ArgumentParser(description="Runtime-aware launcher for the {spec.skill_slug} pipeline skill")
            parser.add_argument("run_dir")
            parser.add_argument("--mode", default="codex-session")
            parser.add_argument("--allow-mock", action="store_true")
            parser.add_argument("--allow-seed", action="store_true")
            parser.add_argument("--check-only", action="store_true")
            return parser


        def main(argv: list[str] | None = None) -> int:
            parser = build_parser()
            args = parser.parse_args(argv)
            return execute_skill_launcher(
                Path(args.run_dir),
                mode=args.mode,
                allow_mock=args.allow_mock,
                allow_seed=args.allow_seed,
                check_only=args.check_only,
                probe_capabilities=probe_capabilities,
                pipeline_script=SCRIPT_ROOT / "run_pipeline.py",
                blocked_report_name="{spec.skill_slug}-report.md",
                env=os.environ,
            )


        if __name__ == "__main__":
            raise SystemExit(main())
        """
    )


def render_run_pipeline_py() -> str:
    return dedent(
        """\
        #!/usr/bin/env python3
        from __future__ import annotations

        import argparse
        import json
        import sys
        from pathlib import Path


        FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[1].parent / "pipeline-framework" / "scripts"
        if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:
            sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))

        from framework.runner.core import run_pipeline_stages  # noqa: E402
        from pipeline_spec import STAGE_INPUTS, STAGE_ORDER, STAGE_OUTPUTS, adapter_paths, validator_paths  # noqa: E402


        def main(argv: list[str] | None = None) -> int:
            parser = argparse.ArgumentParser()
            parser.add_argument("run_dir")
            args = parser.parse_args(argv)

            run_dir = Path(args.run_dir).resolve()
            run_dir.mkdir(parents=True, exist_ok=True)
            response = run_pipeline_stages(
                run_dir,
                STAGE_ORDER,
                STAGE_INPUTS,
                STAGE_OUTPUTS,
                adapter_paths(Path(__file__).resolve().parent),
                validator_paths(Path(__file__).resolve().parent),
            )
            if not response.get("ok"):
                print(json.dumps(response, ensure_ascii=False))
                return 1
            print(json.dumps({"ok": True, "stages": STAGE_ORDER}, ensure_ascii=False))
            return 0


        if __name__ == "__main__":
            raise SystemExit(main())
        """
    )


def render_runtime_config_py() -> str:
    return dedent(
        """\
        from __future__ import annotations

        import sys
        from pathlib import Path


        FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[2].parent / "pipeline-framework" / "scripts"
        if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:
            sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))

        from framework.runtime.runtime_config import RuntimeConfig, RuntimeMode, VALID_RUNTIME_MODES, build_runtime_config, parse_runtime_mode  # noqa: E402,F401
        """
    )


def render_provider_registry_py(spec: SkillSpec) -> str:
    mapping = "\n".join(
        f'    "{stage.stage_id}": "{capability_key(spec, stage)}",' for stage in spec.stages
    )
    return (
        "from __future__ import annotations\n\n"
        "import sys\n"
        "from pathlib import Path\n\n"
        "from runtime.runtime_config import RuntimeConfig\n\n\n"
        'FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[2].parent / "pipeline-framework" / "scripts"\n'
        "if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:\n"
        "    sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))\n\n"
        "from framework.runtime.provider_core import ProviderSelectionError, select_provider_for_capability  # noqa: E402\n\n\n"
        "STAGE_TO_CAPABILITY = {\n"
        f"{mapping}\n"
        "}\n\n\n"
        "def required_capability_for_stage(stage: str) -> str:\n"
        "    if stage not in STAGE_TO_CAPABILITY:\n"
        '        raise ValueError(f"Unsupported stage \'{stage}\'")\n'
        "    return STAGE_TO_CAPABILITY[stage]\n\n\n"
        "def select_provider(stage: str, capability_report: dict, config: RuntimeConfig) -> dict:\n"
        "    capability = required_capability_for_stage(stage)\n"
        "    return select_provider_for_capability(stage, capability, capability_report, config)\n"
    )


def render_capability_probe_py(spec: SkillSpec) -> str:
    defaults = "\n".join(
        f'        "{capability_key(spec, stage)}": (STATUS_READY, PROVIDER_BUILTIN),'
        for stage in spec.stages
    )
    prefixes = "\n".join(
        f'        "{capability_key(spec, stage)}": "{capability_env_prefix(spec, stage)}",'
        for stage in spec.stages
    )
    return (
        "from __future__ import annotations\n\n"
        "import sys\n"
        "from pathlib import Path\n"
        "from typing import Mapping\n\n"
        "from runtime.runtime_config import RuntimeConfig\n\n\n"
        'FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[2].parent / "pipeline-framework" / "scripts"\n'
        "if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:\n"
        "    sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))\n\n"
        "from framework.runtime.capability_core import (  # noqa: E402\n"
        "    PROVIDER_BUILTIN,\n"
        "    STATUS_READY,\n"
        "    build_capability_report,\n"
        ")\n\n\n"
        "def probe_capabilities(\n"
        "    config: RuntimeConfig,\n"
        "    env: Mapping[str, str] | None = None,\n"
        "    paths: Mapping[str, bool] | None = None,\n"
        ") -> dict:\n"
        "    del paths\n"
        "    env = env or {}\n"
        "    defaults = {\n"
        f"{defaults}\n"
        "    }\n"
        "    prefixes = {\n"
        f"{prefixes}\n"
        "    }\n"
        "    return build_capability_report(config.mode, env, defaults, prefixes)\n"
    )


def render_bridges_base_py() -> str:
    return dedent(
        """\
        from __future__ import annotations

        import sys
        from pathlib import Path


        FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[2].parent / "pipeline-framework" / "scripts"
        if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:
            sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))

        from framework.bridges.base import execute_provider  # noqa: E402,F401
        """
    )


def render_adapters_common_py() -> str:
    return dedent(
        """\
        from __future__ import annotations

        import sys
        from pathlib import Path
        from typing import Iterable


        FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[2].parent / "pipeline-framework" / "scripts"
        if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:
            sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))

        from framework.adapters.common import (  # noqa: E402
            blocked_result,
            capability_report_path,
            dispatch_dir,
            extract_failure_type,
            load_capability_report,
            load_request,
            load_response_if_exists,
            load_runtime_config,
            output_path,
            request_path,
            response_path,
            result,
            run_cli_command,
            runtime_config_path,
            stage_staging_dir,
            write_json,
            write_text,
        )
        from runtime.provider_registry import select_provider  # noqa: E402


        def skill_root() -> Path:
            return Path(__file__).resolve().parents[2]


        def template_path(name: str) -> Path:
            return skill_root() / "assets" / "templates" / name


        def ensure_inputs(run_dir: Path, inputs: Iterable[str]):
            missing = [name for name in inputs if not (run_dir / name).exists()]
            if missing:
                raise FileNotFoundError(f"Missing required inputs: {', '.join(missing)}")


        def copy_template(path: Path, template_name: str):
            write_text(path, template_path(template_name).read_text(encoding="utf-8"))


        def resolve_provider(run_dir: Path, stage: str):
            config = load_runtime_config(run_dir)
            capability_report = load_capability_report(run_dir, config)
            provider = select_provider(stage, capability_report, config)
            return config, capability_report, provider
        """
    )


def render_stage_adapter(spec: SkillSpec, stage: StageSpec) -> str:
    payload_lines = [f'"{field}": "{stage.title}: {field} 待确认",' for field in stage.json_fields]
    if stage.input_files:
        payload_lines.append(f'"source_artifacts": {list(stage.input_files)!r},')
    payload_lines.append('"stage": STAGE,')
    payload_block = indent_block("\n".join(payload_lines), 12)
    guard_block = ""
    if stage.input_files:
        guard_block = indent_block(f"ensure_inputs(run_dir, {list(stage.input_files)!r})", 8) + "\n"
    return (
        "#!/usr/bin/env python3\n"
        "from __future__ import annotations\n\n"
        "import json\n"
        "import sys\n"
        "from pathlib import Path\n\n\n"
        "SCRIPT_ROOT = Path(__file__).resolve().parents[1]\n"
        "if str(SCRIPT_ROOT) not in sys.path:\n"
        "    sys.path.insert(0, str(SCRIPT_ROOT))\n\n"
        "from adapters.common import (  # noqa: E402\n"
        "    blocked_result,\n"
        "    copy_template,\n"
        "    ensure_inputs,\n"
        "    extract_failure_type,\n"
        "    load_request,\n"
        "    resolve_provider,\n"
        "    result,\n"
        "    stage_staging_dir,\n"
        "    write_json,\n"
        ")\n"
        "from bridges.base import execute_provider  # noqa: E402\n\n\n"
        f'STAGE = "{stage.stage_id}"\n'
        f'TOOL = "{stage.stage_id}"\n'
        f'CLI_ENV_VAR = "{capability_env_prefix(spec, stage)}_CLI_CMD"\n\n\n'
        "def builtin_handler(run_dir: Path) -> dict:\n"
        "    staging_dir = stage_staging_dir(run_dir, STAGE)\n"
        f'    md_path = staging_dir / "{stage.markdown_filename}"\n'
        f'    json_path = staging_dir / "{stage.json_filename}"\n'
        "    if not md_path.exists():\n"
        f'        copy_template(md_path, "{stage.markdown_filename}")\n'
        "    write_json(\n"
        "        json_path,\n"
        "        {\n"
        f"{payload_block}\n"
        "        },\n"
        "    )\n"
        "    return result(\n"
        "        True,\n"
        "        STAGE,\n"
        "        TOOL,\n"
        '        provider="builtin",\n'
        f'        created=["{stage.markdown_filename}", "{stage.json_filename}"],\n'
        '        notes="builtin stage output generated to staging",\n'
        "    )\n\n\n"
        "def main(argv: list[str] | None = None) -> int:\n"
        "    run_dir = Path((argv or sys.argv[1:])[0]).resolve()\n"
        "    try:\n"
        "        request = load_request(run_dir, STAGE)\n"
        "        del request\n"
        f"{guard_block}"
        "        _, _, provider = resolve_provider(run_dir, STAGE)\n"
        "        payload = execute_provider(\n"
        "            run_dir,\n"
        "            STAGE,\n"
        "            provider,\n"
        "            CLI_ENV_VAR,\n"
        "            builtin_handler=lambda: builtin_handler(run_dir),\n"
        "            mock_handler=lambda: builtin_handler(run_dir),\n"
        "        )\n"
        "    except Exception as exc:\n"
        "        payload = blocked_result(STAGE, TOOL, extract_failure_type(exc), str(exc))\n"
        "    print(json.dumps(payload, ensure_ascii=False))\n"
        "    return 0\n\n\n"
        'if __name__ == "__main__":\n'
        "    raise SystemExit(main())\n"
    )


def render_stage_validator(stage: StageSpec) -> str:
    checks = []
    for field in stage.json_fields:
        checks.append(f'if not payload.get("{field}"):\n    raise RuntimeError("contract-violation: {stage.json_filename} is missing {field}")')
    checks_block = indent_block("\n".join(checks), 4)
    return (
        "from __future__ import annotations\n\n"
        "import json\n"
        "from pathlib import Path\n\n\n"
        "def validate(staging_dir: Path) -> None:\n"
        f'    payload = json.loads((staging_dir / "{stage.json_filename}").read_text(encoding="utf-8"))\n'
        f"{checks_block}\n"
    )


def render_test_run_skill(spec: SkillSpec) -> str:
    expected_capabilities = [capability_key(spec, stage) for stage in spec.stages]
    expected_outputs = [stage.json_filename for stage in spec.stages] + [stage.markdown_filename for stage in spec.stages]
    return dedent(
        f"""\
        import json
        import subprocess
        import tempfile
        import unittest
        from pathlib import Path


        SKILL_ROOT = Path(__file__).resolve().parents[1]
        SCRIPT_ROOT = SKILL_ROOT / "scripts"
        REPO_ROOT = Path(__file__).resolve().parents[3]


        class GeneratedRunSkillTests(unittest.TestCase):
            def make_run_dir(self) -> Path:
                tmp = tempfile.TemporaryDirectory()
                self.addCleanup(tmp.cleanup)
                return Path(tmp.name)

            def run_skill(self, run_dir: Path, *extra_args: str):
                return subprocess.run(
                    ["python3", str(SCRIPT_ROOT / "run_skill.py"), str(run_dir), *extra_args],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )

            def test_check_only_prints_capability_report(self):
                run_dir = self.make_run_dir()
                proc = self.run_skill(run_dir, "--check-only")
                self.assertEqual(proc.returncode, 0, proc.stderr)
                payload = json.loads(proc.stdout)
                self.assertEqual(payload["runtime"], "codex-session")
                for capability in {expected_capabilities!r}:
                    self.assertIn(capability, payload["capabilities"])

            def test_run_skill_executes_full_pipeline(self):
                run_dir = self.make_run_dir()
                proc = self.run_skill(run_dir, "--mode", "dev-mock", "--allow-mock")
                self.assertEqual(proc.returncode, 0, proc.stderr)
                for filename in {expected_outputs!r}:
                    self.assertTrue((run_dir / filename).exists())


        if __name__ == "__main__":
            unittest.main()
        """
    )


def render_test_run_pipeline(spec: SkillSpec) -> str:
    cap_entries = ",\n".join(
        f'                            "{capability_key(spec, stage)}": {{"status": "ready", "provider": "builtin"}}'
        for stage in spec.stages
    )
    expected_outputs = [stage.json_filename for stage in spec.stages] + [stage.markdown_filename for stage in spec.stages]
    return dedent(
        f"""\
        import json
        import subprocess
        import tempfile
        import unittest
        from pathlib import Path


        SKILL_ROOT = Path(__file__).resolve().parents[1]
        SCRIPT_ROOT = SKILL_ROOT / "scripts"
        REPO_ROOT = Path(__file__).resolve().parents[3]


        def write_json(path: Path, payload: dict) -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")


        class GeneratedRunPipelineTests(unittest.TestCase):
            def make_run_dir(self) -> Path:
                tmp = tempfile.TemporaryDirectory()
                self.addCleanup(tmp.cleanup)
                return Path(tmp.name)

            def run_pipeline(self, run_dir: Path):
                return subprocess.run(
                    ["python3", str(SCRIPT_ROOT / "run_pipeline.py"), str(run_dir)],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )

            def test_pipeline_runs_with_builtin_capabilities(self):
                run_dir = self.make_run_dir()
                write_json(run_dir / ".dispatch" / "runtime-config.json", {{"mode": "codex-session", "allow_mock": False, "check_only": False}})
                write_json(
                    run_dir / ".dispatch" / "capability-report.json",
                    {{
                        "runtime": "codex-session",
                        "capabilities": {{
        {cap_entries}
                        }},
                    }},
                )

                proc = self.run_pipeline(run_dir)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                for filename in {expected_outputs!r}:
                    self.assertTrue((run_dir / filename).exists())


        if __name__ == "__main__":
            unittest.main()
        """
    )


def render_test_capability_probe(spec: SkillSpec) -> str:
    expected_capabilities = [capability_key(spec, stage) for stage in spec.stages]
    return dedent(
        f"""\
        import sys
        import unittest
        from pathlib import Path


        SKILL_ROOT = Path(__file__).resolve().parents[1]
        SCRIPT_ROOT = SKILL_ROOT / "scripts"
        if str(SCRIPT_ROOT) not in sys.path:
            sys.path.insert(0, str(SCRIPT_ROOT))

        from runtime.capability_probe import probe_capabilities  # noqa: E402
        from runtime.runtime_config import RuntimeConfig  # noqa: E402


        class CapabilityProbeTests(unittest.TestCase):
            def test_probe_reports_builtin_defaults(self):
                report = probe_capabilities(RuntimeConfig())
                self.assertEqual(report["runtime"], "codex-session")
                for capability in {expected_capabilities!r}:
                    self.assertEqual(report["capabilities"][capability]["provider"], "builtin")


        if __name__ == "__main__":
            unittest.main()
        """
    )


def render_test_provider_registry(spec: SkillSpec) -> str:
    first_stage = spec.stages[0]
    first_capability = capability_key(spec, first_stage)
    return dedent(
        f"""\
        import sys
        import unittest
        from pathlib import Path


        SKILL_ROOT = Path(__file__).resolve().parents[1]
        SCRIPT_ROOT = SKILL_ROOT / "scripts"
        if str(SCRIPT_ROOT) not in sys.path:
            sys.path.insert(0, str(SCRIPT_ROOT))

        from runtime.provider_registry import required_capability_for_stage, select_provider  # noqa: E402
        from runtime.runtime_config import RuntimeConfig  # noqa: E402


        class ProviderRegistryTests(unittest.TestCase):
            def test_required_capability_matches_stage_mapping(self):
                self.assertEqual(required_capability_for_stage("{first_stage.stage_id}"), "{first_capability}")

            def test_select_provider_returns_builtin_when_capability_ready(self):
                provider = select_provider(
                    "{first_stage.stage_id}",
                    {{
                        "capabilities": {{
                            "{first_capability}": {{"status": "ready", "provider": "builtin"}}
                        }}
                    }},
                    RuntimeConfig(),
                )
                self.assertEqual(provider["provider"], "builtin")


        if __name__ == "__main__":
            unittest.main()
        """
    )


def generate_skill(spec: SkillSpec, output_root: Path) -> Path:
    skill_root = output_root / spec.skill_slug
    write_file(skill_root / "SKILL.md", render_skill_md(spec))
    write_file(skill_root / "agents" / "openai.yaml", render_openai_yaml(spec))
    write_file(skill_root / "references" / "pipeline.md", render_reference_pipeline_md(spec))
    write_file(skill_root / "scripts" / "__init__.py", "")
    write_file(skill_root / "scripts" / "run_skill.py", render_run_skill_py(spec))
    write_file(skill_root / "scripts" / "run_pipeline.py", render_run_pipeline_py())
    write_file(skill_root / "scripts" / "pipeline_spec.py", render_pipeline_spec_py(spec))
    write_file(skill_root / "scripts" / "runtime" / "__init__.py", "")
    write_file(skill_root / "scripts" / "runtime" / "runtime_config.py", render_runtime_config_py())
    write_file(skill_root / "scripts" / "runtime" / "provider_registry.py", render_provider_registry_py(spec))
    write_file(skill_root / "scripts" / "runtime" / "capability_probe.py", render_capability_probe_py(spec))
    write_file(skill_root / "scripts" / "bridges" / "__init__.py", "")
    write_file(skill_root / "scripts" / "bridges" / "base.py", render_bridges_base_py())
    write_file(skill_root / "scripts" / "adapters" / "__init__.py", "")
    write_file(skill_root / "scripts" / "adapters" / "common.py", render_adapters_common_py())
    write_file(skill_root / "scripts" / "validators" / "__init__.py", "")
    for stage in spec.stages:
        write_file(skill_root / "assets" / "templates" / stage.markdown_filename, render_template(stage))
        write_file(skill_root / "scripts" / "adapters" / stage.adapter_filename, render_stage_adapter(spec, stage))
        write_file(skill_root / "scripts" / "validators" / stage.validator_filename, render_stage_validator(stage))
    write_file(skill_root / "tests" / "test_run_skill.py", render_test_run_skill(spec))
    write_file(skill_root / "tests" / "test_run_pipeline.py", render_test_run_pipeline(spec))
    write_file(skill_root / "tests" / "test_capability_probe.py", render_test_capability_probe(spec))
    write_file(skill_root / "tests" / "test_provider_registry.py", render_test_provider_registry(spec))
    return skill_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a pipeline-framework consumer skill from a JSON spec.")
    parser.add_argument("--spec", required=True, help="Path to the JSON specification file.")
    parser.add_argument("--output-root", default="skills", help="Directory under which the generated skill folder will be created.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    spec = load_spec(Path(args.spec).resolve())
    skill_root = generate_skill(spec, Path(args.output_root).resolve())
    print(json.dumps({"ok": True, "skill_root": str(skill_root)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
