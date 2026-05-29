#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent


SCRIPT_ROOT = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_ROOT.parent
STARTER_ROOT = SKILL_ROOT / "assets" / "starter"


def slugify(value: str, separator: str = "-") -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", separator, value.strip().lower()).strip(separator)
    return normalized or "workflow-skill"


def title_case_slug(value: str) -> str:
    return " ".join(part.capitalize() for part in slugify(value).split("-"))


def python_name(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized or "stage"


@dataclass(frozen=True)
class StageSpec:
    stage_id: str
    title: str
    purpose: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    acceptance_checks: tuple[str, ...]
    template_sections: tuple[str, ...]

    @property
    def template_filename(self) -> str:
        return f"{slugify(self.stage_id)}.md"

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
    def input_files(self) -> tuple[str, ...]:
        return tuple(item for item in self.inputs if Path(item).suffix)


@dataclass(frozen=True)
class WorkflowSpec:
    skill_slug: str
    display_name: str
    description: str
    goal: str
    workflow_type: str
    version: str
    stages: tuple[StageSpec, ...]

    @property
    def capability_prefix(self) -> str:
        return python_name(self.skill_slug)


def normalize_items(value: object, fallback: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return fallback
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


def normalize_description(value: str) -> str:
    description = value.strip()
    if len(description) >= 40:
        return description
    suffix = "，需要按阶段产出可复核交付物并核对验收条件。"
    return description.rstrip("。.") + suffix


def validate_relative_artifact_path(value: str, *, field: str) -> None:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{field} must be a relative artifact path inside the run directory: {value}")


def parse_stage(stage_data: dict) -> StageSpec:
    stage_id = slugify(stage_data["id"])
    return StageSpec(
        stage_id=stage_id,
        title=stage_data.get("title", title_case_slug(stage_id)),
        purpose=stage_data.get("purpose", f"完成 {stage_id} 阶段收敛。"),
        inputs=normalize_items(stage_data.get("inputs"), ("用户输入",)),
        outputs=normalize_items(stage_data.get("outputs"), (f"{stage_id}.md",)),
        acceptance_checks=normalize_items(
            stage_data.get("acceptance_checks"),
            ("产物覆盖本阶段目标", "未确认信息明确标记为待确认"),
        ),
        template_sections=normalize_items(
            stage_data.get("template_sections"),
            ("目标", "输入", "输出", "待确认项"),
        ),
    )


def load_spec(path: Path) -> WorkflowSpec:
    payload = json.loads(path.read_text(encoding="utf-8"))
    skill_slug = slugify(payload["skill_slug"])
    stages = tuple(parse_stage(raw_stage) for raw_stage in payload["stages"])
    if not stages:
        raise ValueError("workflow spec must include at least one stage")
    spec = WorkflowSpec(
        skill_slug=skill_slug,
        display_name=payload.get("display_name", title_case_slug(skill_slug)),
        description=normalize_description(
            payload.get(
                "description",
                f"Use when 需要执行 {skill_slug} 对应的标准化工作流并产出可复核交付物。",
            )
        ),
        goal=payload.get("goal", f"完成 {skill_slug} 的工作流目标。"),
        workflow_type=payload.get("workflow_type", "general-workflow"),
        version=payload.get("version", "1.0.0"),
        stages=stages,
    )
    validate_workflow_spec(spec)
    return spec


def validate_workflow_spec(spec: WorkflowSpec) -> None:
    if not spec.description.startswith("Use when "):
        raise ValueError("description must start with 'Use when ' so the generated Skill has a clear trigger")

    seen_stage_ids: set[str] = set()
    seen_outputs: dict[str, str] = {}
    for stage in spec.stages:
        if stage.stage_id in seen_stage_ids:
            raise ValueError(f"duplicate stage id after normalization: {stage.stage_id}")
        seen_stage_ids.add(stage.stage_id)
        if not stage.inputs:
            raise ValueError(f"stage '{stage.stage_id}' must include at least one input")
        if not stage.outputs:
            raise ValueError(f"stage '{stage.stage_id}' must include at least one output")
        if not stage.acceptance_checks:
            raise ValueError(f"stage '{stage.stage_id}' must include at least one acceptance check")
        if len(set(stage.inputs)) != len(stage.inputs):
            raise ValueError(f"stage '{stage.stage_id}' has duplicate inputs")
        if len(set(stage.outputs)) != len(stage.outputs):
            raise ValueError(f"stage '{stage.stage_id}' has duplicate outputs")
        if len(set(stage.acceptance_checks)) != len(stage.acceptance_checks):
            raise ValueError(f"stage '{stage.stage_id}' has duplicate acceptance checks")
        for item in stage.input_files:
            validate_relative_artifact_path(item, field=f"stage '{stage.stage_id}' input")
        for output in stage.outputs:
            validate_relative_artifact_path(output, field=f"stage '{stage.stage_id}' output")
            if output in seen_outputs:
                raise ValueError(
                    f"duplicate output '{output}' declared by stages '{seen_outputs[output]}' and '{stage.stage_id}'"
                )
            seen_outputs[output] = stage.stage_id


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def read_starter_script(relative_path: str) -> str:
    return (STARTER_ROOT / "scripts" / relative_path).read_text(encoding="utf-8")


def copy_starter_scripts(target_scripts: Path) -> None:
    for path in (STARTER_ROOT / "scripts").rglob("*"):
        if path.is_dir():
            continue
        relative = path.relative_to(STARTER_ROOT / "scripts")
        if relative.name in {"workflow_contract.py", "validate_workflow.py"}:
            continue
        dest = target_scripts / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)


def bullet_lines(items: tuple[str, ...]) -> str:
    return "\n".join(f"- {item}" for item in items)


def indented_bullet_lines(items: tuple[str, ...], spaces: int = 2) -> str:
    prefix = " " * spaces
    return "\n".join(f"{prefix}- {item}" for item in items)


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_skill_md(spec: WorkflowSpec) -> str:
    stage_lines = "\n".join(f"- `{stage.stage_id}`: {stage.purpose}" for stage in spec.stages)
    artifact_lines = "\n".join(
        f"- `{stage.stage_id}` -> {', '.join(f'`{output}`' for output in stage.outputs)}"
        for stage in spec.stages
    )
    return f"""\
---
name: {spec.skill_slug}
description: {yaml_string(spec.description)}
metadata:
  version: {yaml_string(spec.version)}
---

# {spec.display_name}

`{spec.skill_slug}` 是一个标准化工作流 Skill，用于稳定执行这项目标：

{spec.goal}

## When to Use

- 用户需要按固定阶段推进 `{spec.workflow_type}` 类型工作流
- 用户需要可复核的阶段产物、阻塞原因和验收记录
- 用户需要把一次性流程沉淀成可重复使用的 Skill

## Workflow Contract

- 先确认目标、输入、阶段顺序和最终产物，再开始执行。
- 每个阶段只负责一个清晰收敛动作，不把多个决策混在同一阶段。
- 阶段产物必须可被下一阶段引用；缺失输入时必须阻塞并列出缺口。
- 不得把猜测写成事实；不确定信息必须写入“待确认项”。
- 完成后必须按 `references/workflow.md` 中的验收项逐项核对。

## Intake Checklist

开始执行前先确认：

- 用户目标是否与本 Skill 的 goal 一致
- 已知输入、缺失输入和不可验证假设是否分开记录
- 阶段顺序是否仍适合当前任务
- 最终交付物、格式和接收方是否明确
- 是否存在需要用户先确认的业务事实、权限或外部依赖

## Workflow Stages

{stage_lines}

## Expected Artifacts

{artifact_lines}

## Execution

1. 阅读 `references/workflow.md`，确认阶段输入、输出和验收项。
2. 阅读 `references/architecture.md`，确认 Runner、Adapter、Input 和 Output 契约。
3. 使用 `scripts/run_skill.py <run_dir> --check-only` 检查 capability。
4. 使用 `scripts/run_skill.py <run_dir> --mode dev-mock --allow-mock` 跑通 starter。
5. 按阶段替换 `scripts/adapters/` 和 `assets/templates/` 中的业务逻辑。
6. 全部阶段完成后，汇总产物路径、验证结果和剩余风险。

## Quality Gates

- 每个阶段的 required inputs 都有来源或明确标记为缺失
- 每个阶段的 outputs 都能追溯到输入和工作记录
- 每个 acceptance check 都有对应证据或阻塞说明
- 没有把待确认信息写成事实
- 最终报告列出完成项、未完成项、风险和下一步

## Completion Report

完成时按这个结构回复：

- `产物`：列出每个阶段生成或更新的文件
- `验证`：列出已核对的验收项
- `阻塞`：如有，说明缺失输入和影响范围
- `风险`：列出剩余不确定性
- `下一步`：说明建议继续动作

## Version

Current version: {spec.version}

## Version History

- {spec.version} - Initial standard workflow Skill generated by pipeline-creator.
"""


def render_openai_yaml(spec: WorkflowSpec) -> str:
    return dedent(
        f"""\
        interface:
          display_name: {yaml_string(spec.display_name)}
          short_description: "标准化工作流 Skill"
          default_prompt: "Use ${spec.skill_slug} to run the workflow, produce stage artifacts, and verify the workflow contract."
        """
    )


def render_workflow_md(spec: WorkflowSpec) -> str:
    sections = []
    for index, stage in enumerate(spec.stages, start=1):
        sections.append(
            f"""\
## {index}. {stage.title}

- stage_id: `{stage.stage_id}`
- purpose: {stage.purpose}
- inputs:
{indented_bullet_lines(stage.inputs)}
- outputs:
{indented_bullet_lines(stage.outputs)}
- acceptance_checks:
{indented_bullet_lines(stage.acceptance_checks)}
- template: `assets/templates/{stage.template_filename}`
""".rstrip()
        )
    return f"""\
# {spec.display_name} Workflow

## Goal

{spec.goal}

## Workflow Type

`{spec.workflow_type}`

## Stages

{chr(10).join(sections)}

## Handoff Rules

- 后一阶段只能依赖前一阶段已经完成并验收过的输出。
- 如果阶段输出发生变化，必须重新检查所有下游阶段的输入假设。
- 交接时必须说明产物路径、已知限制和待确认项。
- 不允许用口头结论替代阶段产物。

## Blocking Policy

遇到以下情况必须暂停并说明阻塞：

- required input 缺失且无法从上下文可靠补齐
- 用户目标、阶段顺序或验收标准互相冲突
- 关键事实无法验证，继续执行会把猜测写成事实
- 产物格式或接收方要求不明确，影响后续阶段使用

## Global Acceptance Checklist

- 所有阶段输出都已生成或说明阻塞原因
- 所有阶段验收项都已逐项核对
- 所有待确认项都单独列出
- 最终回复包含产物、验证、阻塞、风险和下一步

## Completion Rule

工作流只有在每个阶段的输出都存在、验收项均已核对、剩余风险已明确列出时，才可声明完成。
"""


def render_architecture_md(spec: WorkflowSpec) -> str:
    registry_rows = "\n".join(
        f"| `{stage.stage_id}` | {stage.title} | {', '.join(stage.inputs)} | {', '.join(stage.outputs)} |"
        for stage in spec.stages
    )
    adapter_rows = "\n".join(
        f"| `{stage.stage_id}` | 接收 `{stage.stage_id}` 输入 | 产出 {', '.join(f'`{output}`' for output in stage.outputs)} | 核对 {len(stage.acceptance_checks)} 项验收 |"
        for stage in spec.stages
    )
    return f"""\
# {spec.display_name} Architecture

这份文档把工作流拆成 Runner、Adapter、Input 和 Output 四类契约。

## Runner Contract

Runner 是执行编排者，职责是：

- 按 `references/workflow.md` 中的阶段顺序推进
- 在每个阶段开始前确认 required inputs
- 调用对应阶段的 Adapter 说明完成阶段转换
- 阶段失败或输入缺失时停止下游推进
- 在完成后汇总产物、验收证据、阻塞项和剩余风险

Runner 由 `scripts/run_skill.py` 和 `scripts/run_pipeline.py` 提供入口，负责执行阶段顺序和失败阻断。

## Adapter Contract

Adapter 是阶段转换单元，职责是把输入转成该阶段承诺的输出：

| Stage | Adapter Input | Adapter Output | Validation |
| --- | --- | --- | --- |
{adapter_rows}

Adapter 可以是人工整理、CLI、MCP、API、脚本或模型调用，但必须把来源、判断和产物写清楚。

## Input Contract

- 每个 input 都必须有来源：用户提供、前序产物、文件路径、系统上下文或外部工具结果。
- 输入缺失时不得继续假装完成；必须进入 Blocking Policy。
- 输入发生变化时，受影响阶段及其下游阶段必须重新核对。
- 输入中的猜测、假设和事实必须分开写。

## Output Contract

- 每个 output 都必须对应一个阶段目标和至少一个 acceptance check。
- 输出必须能被下游阶段引用，不能只写不可复用的聊天摘要。
- 输出中未确认信息必须进入 Open Questions 或 Risks，不得写成事实。
- 输出变更必须记录原因、影响阶段和重新验收结果。

## Stage Registry

| Stage | Title | Inputs | Outputs |
| --- | --- | --- | --- |
{registry_rows}

## Failure Semantics

- `missing-input`：关键输入缺失，Runner 停止当前阶段。
- `contract-conflict`：目标、阶段、输入或验收规则冲突。
- `validation-failed`：输出存在但未通过 acceptance checks。
- `external-blocked`：外部系统、权限或工具不可用。

失败时必须说明失败类型、影响范围、可恢复方式和需要用户补充的信息。
"""


def render_template(stage: StageSpec) -> str:
    custom_sections = "\n\n".join(f"## {section}\n- 待确认" for section in stage.template_sections)
    return f"""\
# {stage.title}

## Stage Context

- stage_id: `{stage.stage_id}`
- purpose: {stage.purpose}

## Required Inputs

{bullet_lines(stage.inputs)}

## Adapter Notes

- 输入到输出的转换方式：
- 使用的工具或资料：
- 关键判断依据：
- 不采用的方案及原因：

## Work Log

- 已执行：
- 关键判断：
- 数据或事实来源：

## Draft Output

{custom_sections}

## Expected Outputs

{bullet_lines(stage.outputs)}

## Acceptance Evidence

{bullet_lines(stage.acceptance_checks)}

## Open Questions

- 待确认：

## Risks And Follow-Ups

- 风险：
- 后续动作：
"""


def capability_key(spec: WorkflowSpec, stage: StageSpec) -> str:
    return f"{spec.capability_prefix}_{python_name(stage.stage_id)}"


def capability_env_prefix(spec: WorkflowSpec, stage: StageSpec) -> str:
    return capability_key(spec, stage).upper()


def render_pipeline_spec_py(spec: WorkflowSpec) -> str:
    stage_order = ",\n".join(f'    "{stage.stage_id}"' for stage in spec.stages)
    stage_inputs = ",\n".join(f'    "{stage.stage_id}": {list(stage.input_files)!r}' for stage in spec.stages)
    stage_outputs = ",\n".join(f'    "{stage.stage_id}": {list(stage.outputs)!r}' for stage in spec.stages)
    adapters = ",\n".join(f'    "{stage.stage_id}": "{stage.adapter_filename}"' for stage in spec.stages)
    validators = ",\n".join(f'    "{stage.stage_id}": "{stage.validator_filename}"' for stage in spec.stages)
    return f"""\
#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


STAGE_ORDER = [
{stage_order}
]

STAGE_INPUTS = {{
{stage_inputs}
}}

STAGE_OUTPUTS = {{
{stage_outputs}
}}

ADAPTERS = {{
{adapters}
}}

VALIDATORS = {{
{validators}
}}


def adapter_paths(script_root: Path) -> dict[str, Path]:
    adapter_dir = script_root / "adapters"
    return {{stage: adapter_dir / ADAPTERS[stage] for stage in STAGE_ORDER}}


def validator_paths(script_root: Path) -> dict[str, Path]:
    validator_dir = script_root / "validators"
    return {{stage: validator_dir / VALIDATORS[stage] for stage in STAGE_ORDER}}
"""


def render_provider_registry_py(spec: WorkflowSpec) -> str:
    mapping = "\n".join(f'    "{stage.stage_id}": "{capability_key(spec, stage)}",' for stage in spec.stages)
    return f"""\
from __future__ import annotations

from runtime.runtime_config import RuntimeConfig
from workflow_runtime.runtime.provider_core import select_provider_for_capability


STAGE_TO_CAPABILITY = {{
{mapping}
}}


def required_capability_for_stage(stage: str) -> str:
    if stage not in STAGE_TO_CAPABILITY:
        raise ValueError(f"Unsupported stage '{{stage}}'")
    return STAGE_TO_CAPABILITY[stage]


def select_provider(stage: str, capability_report: dict, config: RuntimeConfig) -> dict:
    capability = required_capability_for_stage(stage)
    return select_provider_for_capability(stage, capability, capability_report, config)
"""


def render_capability_probe_py(spec: WorkflowSpec) -> str:
    defaults = "\n".join(
        f'        "{capability_key(spec, stage)}": (STATUS_READY, PROVIDER_BUILTIN),'
        for stage in spec.stages
    )
    prefixes = "\n".join(
        f'        "{capability_key(spec, stage)}": "{capability_env_prefix(spec, stage)}",'
        for stage in spec.stages
    )
    return f"""\
from __future__ import annotations

from typing import Mapping

from runtime.runtime_config import RuntimeConfig
from workflow_runtime.runtime.capability_core import (
    PROVIDER_BUILTIN,
    STATUS_READY,
    build_capability_report,
)


def probe_capabilities(
    config: RuntimeConfig,
    env: Mapping[str, str] | None = None,
    paths: Mapping[str, bool] | None = None,
) -> dict:
    del paths
    env = env or {{}}
    defaults = {{
{defaults}
    }}
    prefixes = {{
{prefixes}
    }}
    return build_capability_report(config.mode, env, defaults, prefixes)
"""


def render_stage_adapter(spec: WorkflowSpec, stage: StageSpec) -> str:
    payload_lines = [
        f"{python_name(output)!r}: {f'{stage.title}: {output} 待业务化'!r},"
        for output in stage.outputs
    ]
    payload_lines.append('"stage": STAGE,')
    payload_lines.append('"inputs": INPUTS,')
    payload_block = "\n".join(f"            {line}" for line in payload_lines)
    return f"""\
#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from adapters.common import (  # noqa: E402
    blocked_result,
    copy_template,
    ensure_inputs,
    extract_failure_type,
    load_request,
    resolve_provider,
    result,
    stage_staging_dir,
    write_json,
)
from bridges.base import execute_provider  # noqa: E402


STAGE = {stage.stage_id!r}
TOOL = {stage.stage_id!r}
INPUTS = {list(stage.input_files)!r}
OUTPUTS = {list(stage.outputs)!r}
CLI_ENV_VAR = {f"{capability_env_prefix(spec, stage)}_CLI_CMD"!r}


def builtin_handler(run_dir: Path) -> dict:
    staging_dir = stage_staging_dir(run_dir, STAGE)
    for output in OUTPUTS:
        output_path = staging_dir / output
        if output_path.suffix == ".md":
            copy_template(output_path, {stage.template_filename!r})
        elif output_path.suffix == ".json":
            write_json(
                output_path,
                {{
{payload_block}
                }},
            )
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(f"{{STAGE}} output placeholder\\n", encoding="utf-8")
    return result(True, STAGE, TOOL, provider="builtin", created=OUTPUTS, notes="starter output generated to staging")


def main(argv: list[str] | None = None) -> int:
    run_dir = Path((argv or sys.argv[1:])[0]).resolve()
    try:
        request = load_request(run_dir, STAGE)
        del request
        ensure_inputs(run_dir, INPUTS)
        _, _, provider = resolve_provider(run_dir, STAGE)
        payload = execute_provider(
            run_dir,
            STAGE,
            provider,
            CLI_ENV_VAR,
            builtin_handler=lambda: builtin_handler(run_dir),
            mock_handler=lambda: builtin_handler(run_dir),
        )
    except Exception as exc:
        payload = blocked_result(STAGE, TOOL, extract_failure_type(exc), str(exc))
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def render_stage_validator(stage: StageSpec) -> str:
    checks = "\n".join(
        f"    if not (staging_dir / {output!r}).exists():\n"
        f"        raise RuntimeError({'contract-violation: missing ' + output!r})"
        for output in stage.outputs
    )
    return f"""\
from __future__ import annotations

from pathlib import Path


def validate(staging_dir: Path) -> None:
{checks}
"""


def render_workflow_contract_py(spec: WorkflowSpec) -> str:
    stages_payload = [
        {
            "id": stage.stage_id,
            "title": stage.title,
            "purpose": stage.purpose,
            "inputs": list(stage.inputs),
            "outputs": list(stage.outputs),
            "acceptance_checks": list(stage.acceptance_checks),
            "template": f"assets/templates/{stage.template_filename}",
        }
        for stage in spec.stages
    ]
    return (
        read_starter_script("workflow_contract.py")
        .replace('"__WORKFLOW_NAME__"', repr(spec.display_name))
        .replace('"__WORKFLOW_TYPE__"', repr(spec.workflow_type))
        .replace('"__WORKFLOW_GOAL__"', repr(spec.goal))
        .replace("__STAGES_JSON__", json.dumps(stages_payload, ensure_ascii=False, indent=4))
    )


def render_validate_workflow_py() -> str:
    return read_starter_script("validate_workflow.py")


def render_contract_test(spec: WorkflowSpec) -> str:
    expected_stage_ids = [stage.stage_id for stage in spec.stages]
    expected_outputs = sorted({output for stage in spec.stages for output in stage.outputs})
    return dedent(
        f"""\
        import unittest
        from pathlib import Path


        SKILL_ROOT = Path(__file__).resolve().parents[1]
        SCRIPT_ROOT = SKILL_ROOT / "scripts"
        import sys
        if str(SCRIPT_ROOT) not in sys.path:
            sys.path.insert(0, str(SCRIPT_ROOT))

        from validate_workflow import validate_skill_root  # noqa: E402


        class WorkflowContractTests(unittest.TestCase):
            def test_skill_declares_workflow_contract(self):
                skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
                workflow_md = (SKILL_ROOT / "references" / "workflow.md").read_text(encoding="utf-8")
                combined = skill_md + workflow_md

                self.assertIn("## Workflow Contract", skill_md)
                self.assertIn("references/architecture.md", skill_md)
                self.assertTrue((SKILL_ROOT / "references" / "architecture.md").exists())
                self.assertNotIn(".framework", combined)

            def test_workflow_reference_lists_all_stages_and_outputs(self):
                workflow_md = (SKILL_ROOT / "references" / "workflow.md").read_text(encoding="utf-8")
                for stage_id in {expected_stage_ids!r}:
                    self.assertIn(stage_id, workflow_md)
                for output in {expected_outputs!r}:
                    self.assertIn(output, workflow_md)

            def test_stage_templates_exist(self):
                template_dir = SKILL_ROOT / "assets" / "templates"
                for stage_id in {expected_stage_ids!r}:
                    self.assertTrue((template_dir / f"{{stage_id}}.md").exists())

            def test_generated_validator_passes(self):
                result = validate_skill_root(SKILL_ROOT)
                self.assertTrue(result["ok"], result["errors"])


        if __name__ == "__main__":
            unittest.main()
        """
    )


def generate_skill(spec: WorkflowSpec, output_root: Path, *, force: bool = False) -> Path:
    skill_root = output_root / spec.skill_slug
    if skill_root.exists():
        if not force:
            raise FileExistsError(
                f"target skill already exists: {skill_root}. Use --force to replace this generated skill."
            )
        shutil.rmtree(skill_root)
    scripts_root = skill_root / "scripts"
    write_file(skill_root / "SKILL.md", render_skill_md(spec))
    write_file(skill_root / "agents" / "openai.yaml", render_openai_yaml(spec))
    write_file(skill_root / "references" / "workflow.md", render_workflow_md(spec))
    write_file(skill_root / "references" / "architecture.md", render_architecture_md(spec))
    copy_starter_scripts(scripts_root)
    run_skill = (scripts_root / "run_skill.py").read_text(encoding="utf-8").replace("__SKILL_SLUG__", spec.skill_slug)
    write_file(scripts_root / "run_skill.py", run_skill)
    write_file(scripts_root / "pipeline_spec.py", render_pipeline_spec_py(spec))
    write_file(scripts_root / "workflow_contract.py", render_workflow_contract_py(spec))
    write_file(scripts_root / "validate_workflow.py", render_validate_workflow_py())
    write_file(scripts_root / "runtime" / "provider_registry.py", render_provider_registry_py(spec))
    write_file(scripts_root / "runtime" / "capability_probe.py", render_capability_probe_py(spec))
    for stage in spec.stages:
        write_file(skill_root / "assets" / "templates" / stage.template_filename, render_template(stage))
        write_file(scripts_root / "adapters" / stage.adapter_filename, render_stage_adapter(spec, stage))
        write_file(scripts_root / "validators" / stage.validator_filename, render_stage_validator(stage))
    write_file(skill_root / "tests" / "test_workflow_contract.py", render_contract_test(spec))
    return skill_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a standard workflow Skill from a JSON spec.")
    parser.add_argument("--spec", required=True, help="Path to the JSON workflow specification file.")
    parser.add_argument("--output-root", default="skills", help="Directory under which the generated skill folder will be created.")
    parser.add_argument("--force", action="store_true", help="Replace the target generated skill directory if it already exists.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    spec = load_spec(Path(args.spec).resolve())
    skill_root = generate_skill(spec, Path(args.output_root).resolve(), force=args.force)
    print(json.dumps({"ok": True, "skill_root": str(skill_root)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
