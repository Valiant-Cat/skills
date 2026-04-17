import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = SKILL_ROOT / "scripts"
REPO_ROOT = Path(__file__).resolve().parents[5]


class ExamplePipelineRunSkillTests(unittest.TestCase):
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
        self.assertIn("example_seed_note", payload["capabilities"])

    def test_run_skill_executes_full_pipeline(self):
        run_dir = self.make_run_dir()
        proc = self.run_skill(run_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((run_dir / "seed-note.json").exists())
        self.assertTrue((run_dir / "publish-note.json").exists())


if __name__ == "__main__":
    unittest.main()
