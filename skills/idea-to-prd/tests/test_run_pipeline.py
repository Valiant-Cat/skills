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


class IdeaToPrdRunPipelineTests(unittest.TestCase):
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

    def test_runs_full_pipeline_with_builtin_and_mock_providers(self):
        run_dir = self.make_run_dir()
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "dev-mock", "allow_mock": True, "check_only": False})
        write_json(
            run_dir / ".dispatch" / "capability-report.json",
            {
                "runtime": "dev-mock",
                "capabilities": {
                    "idea_to_prd_idea_brief": {"status": "ready", "provider": "builtin"},
                    "idea_to_prd_market_research": {"status": "missing", "provider": "none"},
                    "idea_to_prd_competitor_analysis": {"status": "missing", "provider": "none"},
                    "idea_to_prd_prd_generation": {"status": "ready", "provider": "builtin"},
                },
            },
        )

        proc = self.run_pipeline(run_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((run_dir / "idea-brief.json").exists())
        self.assertTrue((run_dir / "market-research.json").exists())
        self.assertTrue((run_dir / "competitor-analysis.json").exists())
        self.assertTrue((run_dir / "prd.json").exists())
        self.assertTrue((run_dir / ".framework" / "provenance" / "market-research.json").exists())
        self.assertTrue((run_dir / ".framework" / "state" / "stages" / "prd-generation.json").exists())

    def test_blocks_when_market_research_has_no_provider_and_no_bundle(self):
        run_dir = self.make_run_dir()
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "check_only": False})
        write_json(
            run_dir / ".dispatch" / "capability-report.json",
            {
                "runtime": "codex-session",
                "capabilities": {
                    "idea_to_prd_idea_brief": {"status": "ready", "provider": "builtin"},
                    "idea_to_prd_market_research": {"status": "missing", "provider": "none"},
                    "idea_to_prd_competitor_analysis": {"status": "missing", "provider": "none"},
                    "idea_to_prd_prd_generation": {"status": "ready", "provider": "builtin"},
                },
            },
        )

        proc = self.run_pipeline(run_dir)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("market-research", proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
