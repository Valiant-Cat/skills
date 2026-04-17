import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = SKILL_ROOT / "scripts"
REPO_ROOT = Path(__file__).resolve().parents[5]


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

    def test_runs_full_builtin_pipeline(self):
        run_dir = self.make_run_dir()
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "check_only": False})
        write_json(
            run_dir / ".dispatch" / "capability-report.json",
            {
                "runtime": "codex-session",
                "capabilities": {
                    "example_seed_note": {"status": "ready", "provider": "builtin"},
                    "example_publish_note": {"status": "ready", "provider": "builtin"},
                },
            },
        )

        proc = self.run_pipeline(run_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((run_dir / "seed-note.json").exists())
        self.assertTrue((run_dir / "publish-note.json").exists())
        self.assertTrue((run_dir / ".framework" / "provenance" / "seed-note.json").exists())
        self.assertTrue((run_dir / ".framework" / "state" / "stages" / "publish-note.json").exists())


if __name__ == "__main__":
    unittest.main()
