import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = SKILL_ROOT / "scripts"
REPO_ROOT = Path(__file__).resolve().parents[4]


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
        self.assertIn("example_stage_a", payload["capabilities"])


if __name__ == "__main__":
    unittest.main()
