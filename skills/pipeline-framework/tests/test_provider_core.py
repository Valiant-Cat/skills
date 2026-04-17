import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = SKILL_ROOT / "scripts"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from framework.runtime.provider_core import ProviderSelectionError, select_provider_for_capability  # noqa: E402
from framework.runtime.runtime_config import build_runtime_config  # noqa: E402


class ProviderCoreTests(unittest.TestCase):
    def test_selects_ready_provider(self):
        provider = select_provider_for_capability(
            stage="market-research",
            capability="cap_market",
            capability_report={
                "capabilities": {
                    "cap_market": {"status": "ready", "provider": "cli"},
                }
            },
            config=build_runtime_config("codex-session", allow_mock=False, allow_seed=False, check_only=False),
        )
        self.assertEqual(provider["provider"], "cli")
        self.assertEqual(provider["status"], "ready")

    def test_raises_missing_capability(self):
        with self.assertRaises(ProviderSelectionError) as ctx:
            select_provider_for_capability(
                stage="competitor-analysis",
                capability="cap_competitor",
                capability_report={
                    "capabilities": {
                        "cap_competitor": {"status": "missing", "provider": "none"},
                    }
                },
                config=build_runtime_config("codex-session", allow_mock=False, allow_seed=False, check_only=False),
            )
        self.assertEqual(ctx.exception.failure_type, "missing-capability")

    def test_dev_mock_mode_forces_mock_provider(self):
        provider = select_provider_for_capability(
            stage="market-research",
            capability="cap_market",
            capability_report={
                "capabilities": {
                    "cap_market": {"status": "missing", "provider": "none"},
                }
            },
            config=build_runtime_config("dev-mock", allow_mock=True, allow_seed=False, check_only=False),
        )
        self.assertEqual(provider["provider"], "mock")
        self.assertEqual(provider["status"], "ready")


if __name__ == "__main__":
    unittest.main()
