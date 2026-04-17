import json
import os
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

    def run_skill(self, run_dir: Path, *extra_args: str, env: dict[str, str] | None = None):
        proc_env = os.environ.copy()
        if env:
            proc_env.update(env)
        return subprocess.run(
            ["python3", str(SCRIPT_ROOT / "run_skill.py"), str(run_dir), *extra_args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            env=proc_env,
        )

    def test_check_only_prints_capability_report(self):
        run_dir = self.make_run_dir()
        proc = self.run_skill(run_dir, "--check-only")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["runtime"], "codex-session")
        self.assertIn("idea_to_prd_idea_brief", payload["capabilities"])

    def test_strict_check_fails_when_required_capabilities_are_missing(self):
        run_dir = self.make_run_dir()
        proc = self.run_skill(run_dir, "--check-only", "--strict-check")
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        report_path = run_dir / "idea-to-prd-report.md"
        self.assertTrue(report_path.exists())
        self.assertIn("market-research", report_path.read_text(encoding="utf-8"))

    def test_strict_check_passes_with_ready_overrides(self):
        run_dir = self.make_run_dir()
        proc = self.run_skill(
            run_dir,
            "--check-only",
            "--strict-check",
            env={
                "IDEA_TO_PRD_MARKET_RESEARCH_PROVIDER": "cli",
                "IDEA_TO_PRD_MARKET_RESEARCH_STATUS": "ready",
                "IDEA_TO_PRD_MARKET_RESEARCH_CLI_CMD": "printf '{}\\n'",
                "IDEA_TO_PRD_COMPETITOR_ANALYSIS_PROVIDER": "cli",
                "IDEA_TO_PRD_COMPETITOR_ANALYSIS_STATUS": "ready",
                "IDEA_TO_PRD_COMPETITOR_ANALYSIS_CLI_CMD": "printf '{}\\n'",
            },
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["capabilities"]["idea_to_prd_market_research"]["status"], "ready")
        self.assertEqual(payload["capabilities"]["idea_to_prd_competitor_analysis"]["status"], "ready")

    def test_strict_check_fails_when_cli_provider_lacks_command(self):
        run_dir = self.make_run_dir()
        proc = self.run_skill(
            run_dir,
            "--check-only",
            "--strict-check",
            env={
                "IDEA_TO_PRD_MARKET_RESEARCH_PROVIDER": "cli",
                "IDEA_TO_PRD_MARKET_RESEARCH_STATUS": "ready",
                "IDEA_TO_PRD_COMPETITOR_ANALYSIS_PROVIDER": "cli",
                "IDEA_TO_PRD_COMPETITOR_ANALYSIS_STATUS": "ready",
            },
        )
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        report_path = run_dir / "idea-to-prd-report.md"
        self.assertIn("CLI_CMD", report_path.read_text(encoding="utf-8"))

    def test_strict_check_passes_with_seed_bundles_when_allowed(self):
        run_dir = self.make_run_dir()
        dispatch_dir = run_dir / ".dispatch"
        dispatch_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            dispatch_dir / "market-research-response.json",
            {"ok": True, "stage": "market-research", "tool": "market-research", "provider": "seed", "created": ["market-research.json", "market-research.md"], "updated": [], "notes": "seed", "retryable": False},
        )
        write_json(
            dispatch_dir / "competitor-analysis-response.json",
            {"ok": True, "stage": "competitor-analysis", "tool": "competitor-analysis", "provider": "seed", "created": ["competitor-analysis.json", "competitor-analysis.md"], "updated": [], "notes": "seed", "retryable": False},
        )
        write_json(run_dir / "market-research.json", {"ok": True})
        (run_dir / "market-research.md").write_text("# market\n", encoding="utf-8")
        write_json(run_dir / "competitor-analysis.json", {"ok": True})
        (run_dir / "competitor-analysis.md").write_text("# competitor\n", encoding="utf-8")

        proc = self.run_skill(run_dir, "--check-only", "--strict-check", "--allow-seed")
        self.assertEqual(proc.returncode, 0, proc.stderr)

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
