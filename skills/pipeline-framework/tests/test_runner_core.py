import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = SKILL_ROOT / "scripts"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from framework.runner.core import execute_skill_launcher, run_pipeline_stages, write_runtime_metadata  # noqa: E402
from framework.runtime.runtime_config import build_runtime_config  # noqa: E402


def write_adapter(path: Path, stage: str, output_name: str):
    path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import json",
                "import sys",
                "from pathlib import Path",
                "",
                f"stage = {stage!r}",
                f"output_name = {output_name!r}",
                "run_dir = Path(sys.argv[1])",
                "staging_dir = run_dir / '.framework' / 'staging' / stage",
                "staging_dir.mkdir(parents=True, exist_ok=True)",
                "(staging_dir / output_name).write_text('ok\\n', encoding='utf-8')",
                "print(json.dumps({",
                "    'ok': True,",
                "    'stage': stage,",
                "    'tool': stage,",
                "    'provider': 'builtin',",
                "    'created': [output_name],",
                "    'updated': [],",
                "    'notes': 'ok',",
                "    'retryable': False,",
                "}, ensure_ascii=False))",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_minimal_response_adapter(path: Path, stage: str, output_name: str):
    path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import json",
                "import sys",
                "from pathlib import Path",
                "",
                "run_dir = Path(sys.argv[1])",
                "stage = sys.argv[2] if len(sys.argv) > 2 else 'unknown'",
                "staging_dir = run_dir / '.framework' / 'staging' / stage",
                "staging_dir.mkdir(parents=True, exist_ok=True)",
                f"(staging_dir / {output_name!r}).write_text('ok\\n', encoding='utf-8')",
                "print(json.dumps({'ok': True}, ensure_ascii=False))",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_flaky_adapter(path: Path, stage: str, output_name: str, flag_name: str):
    path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import json",
                "import os",
                "import sys",
                "from pathlib import Path",
                "",
                f"stage = {stage!r}",
                f"output_name = {output_name!r}",
                f"flag_name = {flag_name!r}",
                "run_dir = Path(sys.argv[1])",
                "if os.environ.get(flag_name) != '1':",
                "    print('forced failure', file=sys.stderr)",
                "    raise SystemExit(2)",
                "staging_dir = run_dir / '.framework' / 'staging' / stage",
                "staging_dir.mkdir(parents=True, exist_ok=True)",
                "(staging_dir / output_name).write_text('ok\\n', encoding='utf-8')",
                "print(json.dumps({",
                "    'ok': True,",
                "    'stage': stage,",
                "    'tool': stage,",
                "    'provider': 'builtin',",
                "    'created': [output_name],",
                "    'updated': [],",
                "    'notes': 'ok',",
                "    'retryable': False,",
                "}, ensure_ascii=False))",
                "",
            ]
        ),
        encoding="utf-8",
    )


class RunnerCoreTests(unittest.TestCase):
    def make_run_dir(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Path(tmp.name)

    def test_write_runtime_metadata_writes_both_dispatch_files(self):
        run_dir = self.make_run_dir()
        config = build_runtime_config("codex-session", allow_mock=False, allow_seed=False, check_only=False)
        report = {"runtime": "codex-session", "capabilities": {"cap_a": {"status": "ready", "provider": "builtin"}}}

        write_runtime_metadata(run_dir, config, report)

        runtime_payload = json.loads((run_dir / ".dispatch" / "runtime-config.json").read_text(encoding="utf-8"))
        capability_payload = json.loads((run_dir / ".dispatch" / "capability-report.json").read_text(encoding="utf-8"))
        self.assertEqual(runtime_payload["mode"], "codex-session")
        self.assertEqual(capability_payload["capabilities"]["cap_a"]["provider"], "builtin")

    def test_run_pipeline_stages_commits_outputs_and_writes_provenance(self):
        run_dir = self.make_run_dir()
        write_json = lambda path, payload: path.parent.mkdir(parents=True, exist_ok=True) or path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "allow_seed": False, "check_only": False})
        adapter_dir = run_dir / "adapters"
        adapter_dir.mkdir(parents=True, exist_ok=True)
        adapter_a = adapter_dir / "stage_a.py"
        adapter_b = adapter_dir / "stage_b.py"
        write_adapter(adapter_a, "stage-a", "a.json")
        write_adapter(adapter_b, "stage-b", "b.json")

        response = run_pipeline_stages(
            run_dir=run_dir,
            stage_order=["stage-a", "stage-b"],
            stage_inputs={"stage-a": [], "stage-b": ["a.json"]},
            stage_outputs={"stage-a": ["a.json"], "stage-b": ["b.json"]},
            adapter_paths={"stage-a": adapter_a, "stage-b": adapter_b},
        )

        self.assertTrue(response["ok"])
        self.assertTrue((run_dir / "a.json").exists())
        self.assertTrue((run_dir / "b.json").exists())
        self.assertTrue((run_dir / ".framework" / "provenance" / "stage-a.json").exists())
        self.assertTrue((run_dir / ".framework" / "provenance" / "stage-b.json").exists())
        stage_b_state = json.loads((run_dir / ".framework" / "state" / "stages" / "stage-b.json").read_text(encoding="utf-8"))
        self.assertEqual(stage_b_state["status"], "COMMITTED")

    def test_run_pipeline_stages_allows_seed_import_when_enabled(self):
        run_dir = self.make_run_dir()
        write_json = lambda path, payload: path.parent.mkdir(parents=True, exist_ok=True) or path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "allow_seed": True, "check_only": False})
        (run_dir / "a.json").write_text('ok\n', encoding="utf-8")
        write_json(
            run_dir / ".dispatch" / "stage-a-response.json",
            {"ok": True, "stage": "stage-a", "tool": "stage-a", "provider": "seed", "created": ["a.json"], "updated": [], "notes": "seed", "retryable": False},
        )
        adapter_dir = run_dir / "adapters"
        adapter_dir.mkdir(parents=True, exist_ok=True)
        adapter_b = adapter_dir / "stage_b.py"
        write_adapter(adapter_b, "stage-b", "b.json")

        response = run_pipeline_stages(
            run_dir=run_dir,
            stage_order=["stage-a", "stage-b"],
            stage_inputs={"stage-a": [], "stage-b": ["a.json"]},
            stage_outputs={"stage-a": ["a.json"], "stage-b": ["b.json"]},
            adapter_paths={"stage-a": adapter_b, "stage-b": adapter_b},
        )

        self.assertTrue(response["ok"])
        provenance = json.loads((run_dir / ".framework" / "provenance" / "stage-a.json").read_text(encoding="utf-8"))
        self.assertEqual(provenance["provider"], "seed")

    def test_run_pipeline_stages_blocks_when_committed_output_is_tampered(self):
        run_dir = self.make_run_dir()
        write_json = lambda path, payload: path.parent.mkdir(parents=True, exist_ok=True) or path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "allow_seed": False, "check_only": False})
        adapter_dir = run_dir / "adapters"
        adapter_dir.mkdir(parents=True, exist_ok=True)
        adapter_a = adapter_dir / "stage_a.py"
        adapter_b = adapter_dir / "stage_b.py"
        write_adapter(adapter_a, "stage-a", "a.json")
        write_adapter(adapter_b, "stage-b", "b.json")

        first = run_pipeline_stages(
            run_dir=run_dir,
            stage_order=["stage-a"],
            stage_inputs={"stage-a": []},
            stage_outputs={"stage-a": ["a.json"]},
            adapter_paths={"stage-a": adapter_a},
        )
        self.assertTrue(first["ok"])
        (run_dir / "a.json").write_text("tampered\n", encoding="utf-8")

        with self.assertRaisesRegex(RuntimeError, "no longer matches provenance"):
            run_pipeline_stages(
                run_dir=run_dir,
                stage_order=["stage-a", "stage-b"],
                stage_inputs={"stage-a": [], "stage-b": ["a.json"]},
                stage_outputs={"stage-a": ["a.json"], "stage-b": ["b.json"]},
                adapter_paths={"stage-a": adapter_a, "stage-b": adapter_b},
            )

    def test_run_pipeline_stages_blocks_when_commit_manifest_is_missing(self):
        run_dir = self.make_run_dir()
        write_json = lambda path, payload: path.parent.mkdir(parents=True, exist_ok=True) or path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "allow_seed": False, "check_only": False})
        adapter_dir = run_dir / "adapters"
        adapter_dir.mkdir(parents=True, exist_ok=True)
        adapter_a = adapter_dir / "stage_a.py"
        adapter_b = adapter_dir / "stage_b.py"
        write_adapter(adapter_a, "stage-a", "a.json")
        write_adapter(adapter_b, "stage-b", "b.json")

        first = run_pipeline_stages(
            run_dir=run_dir,
            stage_order=["stage-a"],
            stage_inputs={"stage-a": []},
            stage_outputs={"stage-a": ["a.json"]},
            adapter_paths={"stage-a": adapter_a},
        )
        self.assertTrue(first["ok"])
        (run_dir / ".framework" / "commit" / "manifests" / "stage-a.json").unlink()

        with self.assertRaisesRegex(RuntimeError, "has no commit manifest"):
            run_pipeline_stages(
                run_dir=run_dir,
                stage_order=["stage-a", "stage-b"],
                stage_inputs={"stage-a": [], "stage-b": ["a.json"]},
                stage_outputs={"stage-a": ["a.json"], "stage-b": ["b.json"]},
                adapter_paths={"stage-a": adapter_a, "stage-b": adapter_b},
            )

    def test_run_pipeline_stages_blocks_when_provenance_is_missing(self):
        run_dir = self.make_run_dir()
        write_json = lambda path, payload: path.parent.mkdir(parents=True, exist_ok=True) or path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "allow_seed": False, "check_only": False})
        adapter_dir = run_dir / "adapters"
        adapter_dir.mkdir(parents=True, exist_ok=True)
        adapter_a = adapter_dir / "stage_a.py"
        adapter_b = adapter_dir / "stage_b.py"
        write_adapter(adapter_a, "stage-a", "a.json")
        write_adapter(adapter_b, "stage-b", "b.json")

        first = run_pipeline_stages(
            run_dir=run_dir,
            stage_order=["stage-a"],
            stage_inputs={"stage-a": []},
            stage_outputs={"stage-a": ["a.json"]},
            adapter_paths={"stage-a": adapter_a},
        )
        self.assertTrue(first["ok"])
        (run_dir / ".framework" / "provenance" / "stage-a.json").unlink()

        with self.assertRaisesRegex(RuntimeError, "has no committed provenance"):
            run_pipeline_stages(
                run_dir=run_dir,
                stage_order=["stage-a", "stage-b"],
                stage_inputs={"stage-a": [], "stage-b": ["a.json"]},
                stage_outputs={"stage-a": ["a.json"], "stage-b": ["b.json"]},
                adapter_paths={"stage-a": adapter_a, "stage-b": adapter_b},
            )

    def test_run_pipeline_stages_blocks_when_uncommitted_output_exists_in_outputs(self):
        run_dir = self.make_run_dir()
        write_json = lambda path, payload: path.parent.mkdir(parents=True, exist_ok=True) or path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "allow_seed": False, "check_only": False})
        adapter_dir = run_dir / "adapters"
        adapter_dir.mkdir(parents=True, exist_ok=True)
        adapter_a = adapter_dir / "stage_a.py"
        adapter_b = adapter_dir / "stage_b.py"
        write_adapter(adapter_a, "stage-a", "a.json")
        write_adapter(adapter_b, "stage-b", "b.json")
        (run_dir / "b.json").write_text("manual\n", encoding="utf-8")

        with self.assertRaisesRegex(RuntimeError, "producer stage 'stage-b' is not committed"):
            run_pipeline_stages(
                run_dir=run_dir,
                stage_order=["stage-a", "stage-b"],
                stage_inputs={"stage-a": [], "stage-b": ["a.json"]},
                stage_outputs={"stage-a": ["a.json"], "stage-b": ["b.json"]},
                adapter_paths={"stage-a": adapter_a, "stage-b": adapter_b},
            )

    def test_rerun_after_failed_stage_preserves_committed_stage(self):
        run_dir = self.make_run_dir()
        write_json = lambda path, payload: path.parent.mkdir(parents=True, exist_ok=True) or path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "allow_seed": False, "check_only": False})
        adapter_dir = run_dir / "adapters"
        adapter_dir.mkdir(parents=True, exist_ok=True)
        adapter_a = adapter_dir / "stage_a.py"
        adapter_b = adapter_dir / "stage_b.py"
        write_adapter(adapter_a, "stage-a", "a.json")
        write_flaky_adapter(adapter_b, "stage-b", "b.json", "PIPELINE_STAGE_B_READY")

        first = run_pipeline_stages(
            run_dir=run_dir,
            stage_order=["stage-a"],
            stage_inputs={"stage-a": []},
            stage_outputs={"stage-a": ["a.json"]},
            adapter_paths={"stage-a": adapter_a},
        )
        self.assertTrue(first["ok"])
        stage_a_before = json.loads((run_dir / ".framework" / "provenance" / "stage-a.json").read_text(encoding="utf-8"))

        with self.assertRaisesRegex(RuntimeError, "forced failure"):
            run_pipeline_stages(
                run_dir=run_dir,
                stage_order=["stage-a", "stage-b"],
                stage_inputs={"stage-a": [], "stage-b": ["a.json"]},
                stage_outputs={"stage-a": ["a.json"], "stage-b": ["b.json"]},
                adapter_paths={"stage-a": adapter_a, "stage-b": adapter_b},
            )

        self.assertEqual(
            json.loads((run_dir / ".framework" / "state" / "stages" / "stage-a.json").read_text(encoding="utf-8"))["status"],
            "COMMITTED",
        )
        self.assertFalse((run_dir / "b.json").exists())

        old_value = os.environ.get("PIPELINE_STAGE_B_READY")
        os.environ["PIPELINE_STAGE_B_READY"] = "1"
        try:
            second = run_pipeline_stages(
                run_dir=run_dir,
                stage_order=["stage-a", "stage-b"],
                stage_inputs={"stage-a": [], "stage-b": ["a.json"]},
                stage_outputs={"stage-a": ["a.json"], "stage-b": ["b.json"]},
                adapter_paths={"stage-a": adapter_a, "stage-b": adapter_b},
            )
        finally:
            if old_value is None:
                os.environ.pop("PIPELINE_STAGE_B_READY", None)
            else:
                os.environ["PIPELINE_STAGE_B_READY"] = old_value

        self.assertTrue(second["ok"])
        self.assertTrue((run_dir / "b.json").exists())
        stage_a_after = json.loads((run_dir / ".framework" / "provenance" / "stage-a.json").read_text(encoding="utf-8"))
        self.assertEqual(stage_a_before["committed_outputs"], stage_a_after["committed_outputs"])

    def test_execute_skill_launcher_check_only_prints_probe_and_skips_pipeline(self):
        run_dir = self.make_run_dir()

        def probe(config, env):
            self.assertEqual(config.mode, "codex-session")
            self.assertEqual(env["FRAMEWORK_TEST_ENV"], "1")
            return {"runtime": config.mode, "capabilities": {"cap_a": {"status": "ready", "provider": "builtin"}}}

        pipeline_script = run_dir / "should_not_run.py"
        pipeline_script.write_text("raise SystemExit(99)\n", encoding="utf-8")

        from io import StringIO
        from contextlib import redirect_stdout

        buffer = StringIO()
        with redirect_stdout(buffer):
            code = execute_skill_launcher(
                run_dir,
                mode="codex-session",
                allow_mock=False,
                allow_seed=False,
                check_only=True,
                probe_capabilities=probe,
                pipeline_script=pipeline_script,
                blocked_report_name="blocked.md",
                env={**os.environ, "FRAMEWORK_TEST_ENV": "1"},
            )
        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["runtime"], "codex-session")

    def test_execute_skill_launcher_writes_blocked_report_on_pipeline_failure(self):
        run_dir = self.make_run_dir()

        def probe(config, env):
            return {"runtime": config.mode, "capabilities": {}}

        pipeline_script = run_dir / "fail_pipeline.py"
        pipeline_script.write_text(
            "from __future__ import annotations\n"
            "raise RuntimeError('boom')\n",
            encoding="utf-8",
        )

        from io import StringIO
        from contextlib import redirect_stdout

        buffer = StringIO()
        with redirect_stdout(buffer):
            code = execute_skill_launcher(
                run_dir,
                mode="codex-session",
                allow_mock=False,
                allow_seed=False,
                check_only=False,
                probe_capabilities=probe,
                pipeline_script=pipeline_script,
                blocked_report_name="blocked.md",
                env=os.environ,
            )
        self.assertEqual(code, 2)
        self.assertTrue((run_dir / "blocked.md").exists())
        self.assertTrue((run_dir / ".dispatch" / "runtime-config.json").exists())


if __name__ == "__main__":
    unittest.main()
