from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping

from runtime.runtime_config import RuntimeConfig


FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[3] / "pipeline-framework" / "scripts"
if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))

from framework.runtime.capability_core import (  # noqa: E402
    PROVIDER_BUILTIN,
    PROVIDER_NONE,
    STATUS_MISSING,
    STATUS_READY,
    build_capability_report,
)


def probe_capabilities(
    config: RuntimeConfig,
    env: Mapping[str, str] | None = None,
    paths: Mapping[str, bool] | None = None,
) -> dict:
    del paths
    env = env or {}
    defaults = {
        "example_stage_a": (STATUS_READY, PROVIDER_BUILTIN),
        "example_stage_b": (STATUS_MISSING, PROVIDER_NONE),
    }
    prefixes = {
        "example_stage_a": "EXAMPLE_STAGE_A",
        "example_stage_b": "EXAMPLE_STAGE_B",
    }
    return build_capability_report(config.mode, env, defaults, prefixes)
