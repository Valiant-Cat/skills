from __future__ import annotations

import json
from pathlib import Path


def validate(staging_dir: Path) -> None:
    json_path = staging_dir / "competitor-analysis.json"
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    if len(payload.get("competitors", [])) < 3:
        raise RuntimeError("contract-violation: competitor-analysis.json must include at least 3 competitors")
    if not payload.get("borrow_list"):
        raise RuntimeError("contract-violation: competitor-analysis.json is missing borrow_list")
    if not payload.get("avoid_list"):
        raise RuntimeError("contract-violation: competitor-analysis.json is missing avoid_list")
