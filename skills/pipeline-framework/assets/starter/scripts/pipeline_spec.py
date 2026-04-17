from __future__ import annotations

from pathlib import Path


STAGE_ORDER = [
    "stage-a",
    "stage-b",
]

STAGE_INPUTS = {
    "stage-a": [],
    "stage-b": ["stage-a.json"],
}

STAGE_OUTPUTS = {
    "stage-a": ["stage-a.json", "stage-a.md"],
    "stage-b": ["stage-b.json", "stage-b.md"],
}

ADAPTERS = {
    "stage-a": "stage_a_adapter.py",
    "stage-b": "stage_b_adapter.py",
}

VALIDATORS = {
    "stage-a": "stage_a_validator.py",
    "stage-b": "stage_b_validator.py",
}


def adapter_paths(script_root: Path) -> dict[str, Path]:
    adapter_dir = script_root / "adapters"
    return {stage: adapter_dir / ADAPTERS[stage] for stage in STAGE_ORDER}


def validator_paths(script_root: Path) -> dict[str, Path]:
    validator_dir = script_root / "validators"
    return {stage: validator_dir / VALIDATORS[stage] for stage in STAGE_ORDER}
