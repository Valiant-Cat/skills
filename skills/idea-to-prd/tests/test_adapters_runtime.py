import os
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


class IdeaToPrdAdapterRuntimeTests(unittest.TestCase):
    def make_run_dir(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        run_dir = Path(tmp.name)
        write_json(run_dir / ".dispatch" / "idea-brief-request.json", {"stage": "idea-brief"})
        return run_dir

    def run_adapter(self, adapter: str, run_dir: Path, *extra_args: str, env: dict | None = None):
        proc_env = os.environ.copy()
        if env:
            proc_env.update(env)
        return subprocess.run(
            ["python3", str(SCRIPT_ROOT / "adapters" / adapter), str(run_dir), *extra_args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            env=proc_env,
        )

    def test_idea_brief_builtin_provider_writes_outputs(self):
        run_dir = self.make_run_dir()
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "check_only": False})
        write_json(
            run_dir / ".dispatch" / "capability-report.json",
            {"runtime": "codex-session", "capabilities": {"idea_to_prd_idea_brief": {"status": "ready", "provider": "builtin"}}},
        )

        proc = self.run_adapter("idea_brief_adapter.py", run_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue((run_dir / ".framework" / "staging" / "idea-brief" / "idea-brief.md").exists())
        self.assertTrue((run_dir / ".framework" / "staging" / "idea-brief" / "idea-brief.json").exists())

    def test_prd_generation_builtin_provider_writes_outputs(self):
        run_dir = self.make_run_dir()
        (run_dir / "idea-brief.md").write_text("# Idea Brief\n", encoding="utf-8")
        write_json(run_dir / "idea-brief.json", {"product_name": "Example"})
        (run_dir / "market-research.md").write_text("# Market Research\n", encoding="utf-8")
        write_json(run_dir / "market-research.json", {"market_exists": True})
        (run_dir / "competitor-analysis.md").write_text("# Competitor Analysis\n", encoding="utf-8")
        write_json(run_dir / "competitor-analysis.json", {"competitors": []})
        write_json(run_dir / ".dispatch" / "prd-generation-request.json", {"stage": "prd-generation"})
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "check_only": False})
        write_json(
            run_dir / ".dispatch" / "capability-report.json",
            {"runtime": "codex-session", "capabilities": {"idea_to_prd_prd_generation": {"status": "ready", "provider": "builtin"}}},
        )

        proc = self.run_adapter("prd_generation_adapter.py", run_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue((run_dir / ".framework" / "staging" / "prd-generation" / "prd.md").exists())
        self.assertTrue((run_dir / ".framework" / "staging" / "prd-generation" / "prd.json").exists())

    def test_market_research_blocks_with_missing_capability(self):
        run_dir = self.make_run_dir()
        write_json(run_dir / ".dispatch" / "market-research-request.json", {"stage": "market-research"})
        write_json(run_dir / "idea-brief.json", {"product_name": "Example"})
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "check_only": False})
        write_json(
            run_dir / ".dispatch" / "capability-report.json",
            {"runtime": "codex-session", "capabilities": {"idea_to_prd_market_research": {"status": "missing", "provider": "none"}}},
        )

        proc = self.run_adapter("market_research_adapter.py", run_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("missing-capability", payload["notes"])

    def test_market_research_allows_mock_in_dev_mock_mode(self):
        run_dir = self.make_run_dir()
        write_json(run_dir / ".dispatch" / "market-research-request.json", {"stage": "market-research"})
        write_json(run_dir / "idea-brief.json", {"product_name": "Example"})
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "dev-mock", "allow_mock": True, "check_only": False})
        write_json(
            run_dir / ".dispatch" / "capability-report.json",
            {"runtime": "dev-mock", "capabilities": {"idea_to_prd_market_research": {"status": "missing", "provider": "none"}}},
        )

        proc = self.run_adapter("market_research_adapter.py", run_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue((run_dir / ".framework" / "staging" / "market-research" / "market-research.md").exists())
        self.assertTrue((run_dir / ".framework" / "staging" / "market-research" / "market-research.json").exists())

    def test_market_research_executes_cli_command(self):
        run_dir = self.make_run_dir()
        write_json(run_dir / ".dispatch" / "market-research-request.json", {"stage": "market-research"})
        write_json(run_dir / "idea-brief.json", {"product_name": "Example"})
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "check_only": False})
        write_json(
            run_dir / ".dispatch" / "capability-report.json",
            {"runtime": "codex-session", "capabilities": {"idea_to_prd_market_research": {"status": "ready", "provider": "cli"}}},
        )
        cli_cmd = (
            "python3 -c \"import json, os; "
            "staging_dir=os.environ['STAGING_DIR']; "
            "open(os.path.join(staging_dir, 'market-research.md'),'w',encoding='utf-8').write('# Market Research\\n'); "
            "open(os.path.join(staging_dir, 'market-research.json'),'w',encoding='utf-8').write(json.dumps({'market_exists': True}, ensure_ascii=False)); "
            "open(os.environ['RESPONSE_PATH'],'w',encoding='utf-8').write(json.dumps({'ok': True, 'stage': 'market-research', 'tool': 'market-research', 'provider': 'cli', 'created': ['market-research.md', 'market-research.json'], 'updated': [], 'notes': 'cli ok', 'retryable': False}, ensure_ascii=False))\""
        )

        proc = self.run_adapter(
            "market_research_adapter.py",
            run_dir,
            env={"IDEA_TO_PRD_MARKET_RESEARCH_CLI_CMD": cli_cmd},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["provider"], "cli")
        self.assertTrue((run_dir / ".framework" / "staging" / "market-research" / "market-research.md").exists())
        self.assertTrue((run_dir / ".framework" / "staging" / "market-research" / "market-research.json").exists())

    def test_competitor_analysis_allows_mock_in_dev_mock_mode(self):
        run_dir = self.make_run_dir()
        write_json(run_dir / ".dispatch" / "competitor-analysis-request.json", {"stage": "competitor-analysis"})
        write_json(run_dir / "idea-brief.json", {"product_name": "Example"})
        write_json(run_dir / "market-research.json", {"market_exists": True})
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "dev-mock", "allow_mock": True, "check_only": False})
        write_json(
            run_dir / ".dispatch" / "capability-report.json",
            {"runtime": "dev-mock", "capabilities": {"idea_to_prd_competitor_analysis": {"status": "missing", "provider": "none"}}},
        )

        proc = self.run_adapter("competitor_analysis_adapter.py", run_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue((run_dir / ".framework" / "staging" / "competitor-analysis" / "competitor-analysis.md").exists())
        self.assertTrue((run_dir / ".framework" / "staging" / "competitor-analysis" / "competitor-analysis.json").exists())

    def test_competitor_analysis_executes_cli_command(self):
        run_dir = self.make_run_dir()
        write_json(run_dir / ".dispatch" / "competitor-analysis-request.json", {"stage": "competitor-analysis"})
        write_json(run_dir / "idea-brief.json", {"product_name": "Example"})
        write_json(run_dir / "market-research.json", {"market_exists": True})
        write_json(run_dir / ".dispatch" / "runtime-config.json", {"mode": "codex-session", "allow_mock": False, "check_only": False})
        write_json(
            run_dir / ".dispatch" / "capability-report.json",
            {"runtime": "codex-session", "capabilities": {"idea_to_prd_competitor_analysis": {"status": "ready", "provider": "cli"}}},
        )
        cli_cmd = (
            "python3 -c \"import json, os; "
            "staging_dir=os.environ['STAGING_DIR']; "
            "open(os.path.join(staging_dir, 'competitor-analysis.md'),'w',encoding='utf-8').write('# Competitor Analysis\\n'); "
            "open(os.path.join(staging_dir, 'competitor-analysis.json'),'w',encoding='utf-8').write(json.dumps({'competitors': []}, ensure_ascii=False)); "
            "open(os.environ['RESPONSE_PATH'],'w',encoding='utf-8').write(json.dumps({'ok': True, 'stage': 'competitor-analysis', 'tool': 'competitor-analysis', 'provider': 'cli', 'created': ['competitor-analysis.md', 'competitor-analysis.json'], 'updated': [], 'notes': 'cli ok', 'retryable': False}, ensure_ascii=False))\""
        )

        proc = self.run_adapter(
            "competitor_analysis_adapter.py",
            run_dir,
            env={"IDEA_TO_PRD_COMPETITOR_ANALYSIS_CLI_CMD": cli_cmd},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["provider"], "cli")
        self.assertTrue((run_dir / ".framework" / "staging" / "competitor-analysis" / "competitor-analysis.md").exists())
        self.assertTrue((run_dir / ".framework" / "staging" / "competitor-analysis" / "competitor-analysis.json").exists())


if __name__ == "__main__":
    unittest.main()
