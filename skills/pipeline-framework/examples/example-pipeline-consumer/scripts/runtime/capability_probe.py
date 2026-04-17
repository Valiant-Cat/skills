from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping

from runtime.runtime_config import RuntimeConfig


FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[4] / "scripts"
if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))

from framework.runtime.capability_core import (  # noqa: E402
    PROVIDER_BUILTIN,
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
        "example_seed_note": (STATUS_READY, PROVIDER_BUILTIN),
        "example_publish_note": (STATUS_READY, PROVIDER_BUILTIN),
    }
    prefixes = {
        "example_seed_note": "EXAMPLE_SEED_NOTE",
        "example_publish_note": "EXAMPLE_PUBLISH_NOTE",
    }
    return build_capability_report(config.mode, env, defaults, prefixes)
