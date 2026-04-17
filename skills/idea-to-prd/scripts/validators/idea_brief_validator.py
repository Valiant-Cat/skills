from __future__ import annotations

import json
from pathlib import Path


def validate(staging_dir: Path) -> None:
    json_path = staging_dir / "idea-brief.json"
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    if not payload.get("product_name"):
        raise RuntimeError("contract-violation: idea-brief.json is missing product_name")
    if not payload.get("target_users"):
        raise RuntimeError("contract-violation: idea-brief.json is missing target_users")
    if not payload.get("core_scenarios"):
        raise RuntimeError("contract-violation: idea-brief.json is missing core_scenarios")
