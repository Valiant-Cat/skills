from __future__ import annotations

import sys
from pathlib import Path


FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[2].parent / "pipeline-framework" / "scripts"
if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))

from framework.runtime.provider_core import ProviderSelectionError, select_provider_for_capability  # noqa: E402


STAGE_TO_CAPABILITY = {
    "idea-brief": "idea_to_prd_idea_brief",
    "market-research": "idea_to_prd_market_research",
    "competitor-analysis": "idea_to_prd_competitor_analysis",
    "prd-generation": "idea_to_prd_prd_generation",
}


def required_capability_for_stage(stage: str) -> str:
    if stage not in STAGE_TO_CAPABILITY:
        raise ValueError(f"Unsupported stage '{stage}'")
    return STAGE_TO_CAPABILITY[stage]


def select_provider(stage: str, capability_report: dict, config: RuntimeConfig) -> dict:
    capability = required_capability_for_stage(stage)
    return select_provider_for_capability(stage, capability, capability_report, config)
