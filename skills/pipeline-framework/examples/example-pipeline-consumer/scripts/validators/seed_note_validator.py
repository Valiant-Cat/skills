from __future__ import annotations

import json
from pathlib import Path


def validate(staging_dir: Path) -> None:
    payload = json.loads((staging_dir / "seed-note.json").read_text(encoding="utf-8"))
    if not payload.get("topic"):
        raise RuntimeError("contract-violation: seed-note.json is missing topic")
