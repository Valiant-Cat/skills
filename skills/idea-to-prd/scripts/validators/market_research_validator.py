from __future__ import annotations

import json
from pathlib import Path


def validate(staging_dir: Path) -> None:
    json_path = staging_dir / "market-research.json"
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    if len(payload.get("evidence", [])) < 3:
        raise RuntimeError("contract-violation: market-research.json must include at least 3 evidence items")
    if not payload.get("opportunities"):
        raise RuntimeError("contract-violation: market-research.json is missing opportunities")
    if not payload.get("risks"):
        raise RuntimeError("contract-violation: market-research.json is missing risks")
