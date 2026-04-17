from __future__ import annotations

from pathlib import Path


STAGE_ORDER = [
    "idea-brief",
    "market-research",
    "competitor-analysis",
    "prd-generation",
]

STAGE_INPUTS = {
    "idea-brief": [],
    "market-research": ["idea-brief.json"],
    "competitor-analysis": ["idea-brief.json", "market-research.json"],
    "prd-generation": ["idea-brief.json", "market-research.json", "competitor-analysis.json"],
}

STAGE_OUTPUTS = {
    "idea-brief": ["idea-brief.json", "idea-brief.md"],
    "market-research": ["market-research.json", "market-research.md"],
    "competitor-analysis": ["competitor-analysis.json", "competitor-analysis.md"],
    "prd-generation": ["prd.json", "prd.md"],
}

ADAPTERS = {
    "idea-brief": "idea_brief_adapter.py",
    "market-research": "market_research_adapter.py",
    "competitor-analysis": "competitor_analysis_adapter.py",
    "prd-generation": "prd_generation_adapter.py",
}

VALIDATORS = {
    "idea-brief": "idea_brief_validator.py",
    "market-research": "market_research_validator.py",
    "competitor-analysis": "competitor_analysis_validator.py",
    "prd-generation": "prd_validator.py",
}


def adapter_paths(script_root: Path) -> dict[str, Path]:
    adapter_dir = script_root / "adapters"
    return {stage: adapter_dir / ADAPTERS[stage] for stage in STAGE_ORDER}


def validator_paths(script_root: Path) -> dict[str, Path]:
    validator_dir = script_root / "validators"
    return {stage: validator_dir / VALIDATORS[stage] for stage in STAGE_ORDER}
