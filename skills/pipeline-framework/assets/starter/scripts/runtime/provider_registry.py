from __future__ import annotations

import sys
from pathlib import Path


FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[3] / "pipeline-framework" / "scripts"
if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))

from framework.runtime.provider_core import ProviderSelectionError, select_provider_for_capability  # noqa: E402
from runtime.runtime_config import RuntimeConfig  # noqa: E402


STAGE_TO_CAPABILITY = {
    "stage-a": "example_stage_a",
    "stage-b": "example_stage_b",
}


def required_capability_for_stage(stage: str) -> str:
    if stage not in STAGE_TO_CAPABILITY:
        raise ValueError(f"Unsupported stage '{stage}'")
    return STAGE_TO_CAPABILITY[stage]


def select_provider(stage: str, capability_report: dict, config: RuntimeConfig) -> dict:
    capability = required_capability_for_stage(stage)
    return select_provider_for_capability(stage, capability, capability_report, config)
