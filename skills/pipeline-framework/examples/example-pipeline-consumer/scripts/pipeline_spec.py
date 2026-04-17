from __future__ import annotations

from pathlib import Path


STAGE_ORDER = [
    "seed-note",
    "publish-note",
]

STAGE_INPUTS = {
    "seed-note": [],
    "publish-note": ["seed-note.json"],
}

STAGE_OUTPUTS = {
    "seed-note": ["seed-note.json", "seed-note.md"],
    "publish-note": ["publish-note.json", "publish-note.md"],
}

ADAPTERS = {
    "seed-note": "seed_note_adapter.py",
    "publish-note": "publish_note_adapter.py",
}

VALIDATORS = {
    "seed-note": "seed_note_validator.py",
    "publish-note": "publish_note_validator.py",
}


def adapter_paths(script_root: Path) -> dict[str, Path]:
    adapter_dir = script_root / "adapters"
    return {stage: adapter_dir / ADAPTERS[stage] for stage in STAGE_ORDER}


def validator_paths(script_root: Path) -> dict[str, Path]:
    validator_dir = script_root / "validators"
    return {stage: validator_dir / VALIDATORS[stage] for stage in STAGE_ORDER}
