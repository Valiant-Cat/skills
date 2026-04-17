import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = SKILL_ROOT / "scripts"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from framework.runtime.capability_core import (  # noqa: E402
    PROVIDER_BUILTIN,
    PROVIDER_NONE,
    STATUS_MISSING,
    STATUS_READY,
    build_capability_report,
    capability,
    override_capability,
)


class CapabilityCoreTests(unittest.TestCase):
    def test_capability_builds_uniform_payload(self):
        self.assertEqual(
            capability(STATUS_READY, PROVIDER_BUILTIN),
            {"status": STATUS_READY, "provider": PROVIDER_BUILTIN},
        )

    def test_override_capability_uses_ready_as_default_status(self):
        payload = override_capability(
            {"PIPE_PROVIDER": "cli"},
            "PIPE",
        )
        self.assertEqual(payload, {"status": STATUS_READY, "provider": "cli"})

    def test_build_capability_report_merges_overrides_and_defaults(self):
        report = build_capability_report(
            "codex-session",
            env={"PIPE_A_PROVIDER": "mcp", "PIPE_A_STATUS": "ready"},
            defaults={
                "cap_a": (STATUS_MISSING, PROVIDER_NONE),
                "cap_b": (STATUS_READY, PROVIDER_BUILTIN),
            },
            prefixes={
                "cap_a": "PIPE_A",
                "cap_b": "PIPE_B",
            },
        )
        self.assertEqual(report["runtime"], "codex-session")
        self.assertEqual(report["capabilities"]["cap_a"], {"status": "ready", "provider": "mcp"})
        self.assertEqual(report["capabilities"]["cap_b"], {"status": STATUS_READY, "provider": PROVIDER_BUILTIN})


if __name__ == "__main__":
    unittest.main()
