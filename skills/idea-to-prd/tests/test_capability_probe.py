import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = SKILL_ROOT / "scripts"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from runtime.capability_probe import probe_capabilities  # noqa: E402
from runtime.runtime_config import build_runtime_config  # noqa: E402


class IdeaToPrdCapabilityProbeTests(unittest.TestCase):
    def test_marks_builtin_stages_ready_by_default(self):
        report = probe_capabilities(
            build_runtime_config("codex-session", allow_mock=False, allow_seed=False, check_only=True),
            env={},
            paths={},
        )
        self.assertEqual(report["capabilities"]["idea_to_prd_idea_brief"]["status"], "ready")
        self.assertEqual(report["capabilities"]["idea_to_prd_idea_brief"]["provider"], "builtin")
        self.assertEqual(report["capabilities"]["idea_to_prd_prd_generation"]["status"], "ready")
        self.assertEqual(report["capabilities"]["idea_to_prd_prd_generation"]["provider"], "builtin")

    def test_marks_market_research_missing_without_override(self):
        report = probe_capabilities(
            build_runtime_config("codex-session", allow_mock=False, allow_seed=False, check_only=True),
            env={},
            paths={},
        )
        self.assertEqual(report["capabilities"]["idea_to_prd_market_research"]["status"], "missing")
        self.assertEqual(report["capabilities"]["idea_to_prd_market_research"]["provider"], "none")

    def test_market_research_remains_missing_with_cli_cmd_only(self):
        report = probe_capabilities(
            build_runtime_config("codex-session", allow_mock=False, allow_seed=False, check_only=True),
            env={"IDEA_TO_PRD_MARKET_RESEARCH_CLI_CMD": "echo ok"},
            paths={},
        )
        self.assertEqual(report["capabilities"]["idea_to_prd_market_research"]["status"], "missing")
        self.assertEqual(report["capabilities"]["idea_to_prd_market_research"]["provider"], "none")

    def test_accepts_override_for_competitor_analysis(self):
        report = probe_capabilities(
            build_runtime_config("codex-session", allow_mock=False, allow_seed=False, check_only=True),
            env={
                "IDEA_TO_PRD_COMPETITOR_ANALYSIS_PROVIDER": "mcp",
                "IDEA_TO_PRD_COMPETITOR_ANALYSIS_STATUS": "ready",
            },
            paths={},
        )
        self.assertEqual(report["capabilities"]["idea_to_prd_competitor_analysis"]["status"], "ready")
        self.assertEqual(report["capabilities"]["idea_to_prd_competitor_analysis"]["provider"], "mcp")

    def test_competitor_analysis_remains_missing_with_cli_cmd_only(self):
        report = probe_capabilities(
            build_runtime_config("codex-session", allow_mock=False, allow_seed=False, check_only=True),
            env={"IDEA_TO_PRD_COMPETITOR_ANALYSIS_CLI_CMD": "echo ok"},
            paths={},
        )
        self.assertEqual(report["capabilities"]["idea_to_prd_competitor_analysis"]["status"], "missing")
        self.assertEqual(report["capabilities"]["idea_to_prd_competitor_analysis"]["provider"], "none")


if __name__ == "__main__":
    unittest.main()
