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
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class IdeaToPrdRunSkillTests(unittest.TestCase):
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
        self.assertIn("idea_to_prd_idea_brief", payload["capabilities"])

    def test_run_skill_writes_runtime_metadata_and_invokes_pipeline(self):
        run_dir = self.make_run_dir()
        proc = self.run_skill(
            run_dir,
            "--mode",
            "dev-mock",
            "--allow-mock",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((run_dir / ".dispatch" / "runtime-config.json").exists())
        self.assertTrue((run_dir / ".dispatch" / "capability-report.json").exists())
        self.assertTrue((run_dir / "idea-brief.json").exists())
        self.assertTrue((run_dir / "market-research.json").exists())
        self.assertTrue((run_dir / "competitor-analysis.json").exists())
        self.assertTrue((run_dir / "prd.json").exists())
        self.assertTrue((run_dir / ".framework" / "provenance" / "prd-generation.json").exists())


if __name__ == "__main__":
    unittest.main()
