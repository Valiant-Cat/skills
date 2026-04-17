from __future__ import annotations

import json
from pathlib import Path


def validate(staging_dir: Path) -> None:
    payload = json.loads((staging_dir / "publish-note.json").read_text(encoding="utf-8"))
    if payload.get("status") != "published":
        raise RuntimeError("contract-violation: publish-note.json must have status=published")
