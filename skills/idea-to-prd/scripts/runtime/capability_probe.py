from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping

from runtime.runtime_config import RuntimeConfig


FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[2].parent / "pipeline-framework" / "scripts"
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
        "idea_to_prd_idea_brief": (STATUS_READY, PROVIDER_BUILTIN),
        "idea_to_prd_market_research": (STATUS_MISSING, PROVIDER_NONE),
        "idea_to_prd_competitor_analysis": (STATUS_MISSING, PROVIDER_NONE),
        "idea_to_prd_prd_generation": (STATUS_READY, PROVIDER_BUILTIN),
    }
    prefixes = {
        "idea_to_prd_idea_brief": "IDEA_TO_PRD_IDEA_BRIEF",
        "idea_to_prd_market_research": "IDEA_TO_PRD_MARKET_RESEARCH",
        "idea_to_prd_competitor_analysis": "IDEA_TO_PRD_COMPETITOR_ANALYSIS",
        "idea_to_prd_prd_generation": "IDEA_TO_PRD_PRD_GENERATION",
    }
    return build_capability_report(config.mode, env, defaults, prefixes)
