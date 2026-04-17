from __future__ import annotations

import json
from pathlib import Path


def validate(staging_dir: Path) -> None:
    json_path = staging_dir / "prd.json"
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    features = payload.get("features", [])
    if not features:
        raise RuntimeError("contract-violation: prd.json must include features")
    has_p0 = any(item.get("priority") == "P0" for item in features)
    if not has_p0:
        raise RuntimeError("contract-violation: prd.json must include at least one P0 feature")
    for item in features:
        if item.get("priority") in {"P0", "P1"} and not item.get("acceptance_criteria"):
            raise RuntimeError("contract-violation: P0/P1 features must include acceptance_criteria")
