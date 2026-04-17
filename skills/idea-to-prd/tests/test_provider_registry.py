import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = SKILL_ROOT / "scripts"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from runtime.provider_registry import (  # noqa: E402
    ProviderSelectionError,
    required_capability_for_stage,
    select_provider,
)
from runtime.runtime_config import build_runtime_config  # noqa: E402


class IdeaToPrdProviderRegistryTests(unittest.TestCase):
    def test_maps_prd_generation_stage_to_capability(self):
        self.assertEqual(required_capability_for_stage("prd-generation"), "idea_to_prd_prd_generation")

    def test_selects_ready_provider(self):
        report = {
            "runtime": "codex-session",
            "capabilities": {
                "idea_to_prd_market_research": {"status": "ready", "provider": "cli"},
            },
        }
        provider = select_provider(
            "market-research",
            capability_report=report,
            config=build_runtime_config("codex-session", allow_mock=False, allow_seed=False, check_only=False),
        )
        self.assertEqual(provider["provider"], "cli")
        self.assertEqual(provider["capability"], "idea_to_prd_market_research")

    def test_raises_missing_capability_in_normal_mode(self):
        report = {
            "runtime": "codex-session",
            "capabilities": {
                "idea_to_prd_competitor_analysis": {"status": "missing", "provider": "none"},
            },
        }
        with self.assertRaises(ProviderSelectionError) as ctx:
            select_provider(
                "competitor-analysis",
                capability_report=report,
                config=build_runtime_config("codex-session", allow_mock=False, allow_seed=False, check_only=False),
            )
        self.assertEqual(ctx.exception.failure_type, "missing-capability")

    def test_allows_mock_provider_only_in_dev_mock_mode(self):
        report = {
            "runtime": "dev-mock",
            "capabilities": {
                "idea_to_prd_market_research": {"status": "missing", "provider": "none"},
            },
        }
        provider = select_provider(
            "market-research",
            capability_report=report,
            config=build_runtime_config("dev-mock", allow_mock=True, allow_seed=False, check_only=False),
        )
        self.assertEqual(provider["provider"], "mock")
        self.assertEqual(provider["status"], "ready")


if __name__ == "__main__":
    unittest.main()
