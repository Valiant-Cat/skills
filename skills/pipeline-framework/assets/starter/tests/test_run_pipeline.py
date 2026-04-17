import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = SKILL_ROOT / "scripts"
REPO_ROOT = Path(__file__).resolve().parents[4]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class ExamplePipelineRunPipelineTests(unittest.TestCase):
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

    def test_runs_with_response_bundle_for_second_stage(self):
        run_dir = self.make_run_dir()
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "check_only": False})
        write_json(
            run_dir / ".dispatch" / "capability-report.json",
            {
                "runtime": "codex-session",
                "capabilities": {
                    "example_stage_a": {"status": "ready", "provider": "builtin"},
                    "example_stage_b": {"status": "missing", "provider": "none"},
                },
            },
        )
        write_json(
            run_dir / ".dispatch" / "stage-b-response.json",
            {
                "ok": True,
                "stage": "stage-b",
                "tool": "stage-b",
                "created": ["stage-b.json", "stage-b.md"],
                "updated": [],
                "notes": "prebuilt",
                "retryable": False,
            },
        )
        write_json(run_dir / "stage-b.json", {"ok": True})
        (run_dir / "stage-b.md").write_text("# Stage B\n", encoding="utf-8")

        proc = self.run_pipeline(run_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((run_dir / "stage-a.json").exists())


if __name__ == "__main__":
    unittest.main()
