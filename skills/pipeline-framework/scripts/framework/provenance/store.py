from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Mapping, Sequence

from framework.adapters.common import framework_dir, output_path, stage_staging_dir


def provenance_dir(run_dir: Path) -> Path:
    path = framework_dir(run_dir) / "provenance"
    path.mkdir(parents=True, exist_ok=True)
    return path


def provenance_path(run_dir: Path, stage: str) -> Path:
    return provenance_dir(run_dir) / f"{stage}.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def describe_files(base_path: Path, names: Sequence[str], *, public_base: str) -> dict:
    payload: dict[str, dict] = {}
    for name in names:
        path = base_path / name
        if not path.exists():
            continue
        payload[name] = {
            "path": f"{public_base}/{name}",
            "sha256": sha256_file(path),
        }
    return payload


def write_stage_provenance(
    run_dir: Path,
    *,
    stage: str,
    provider: str,
    adapter: str,
    runtime_mode: str,
    input_names: Sequence[str],
    output_names: Sequence[str],
    capability_snapshot: Mapping[str, str] | None = None,
) -> dict:
    payload = {
        "stage": stage,
        "status": "COMMITTED",
        "provider": provider,
        "adapter": adapter,
        "runtime_mode": runtime_mode,
        "executed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "inputs": describe_files(run_dir, input_names, public_base="."),
        "staging_outputs": describe_files(stage_staging_dir(run_dir, stage), output_names, public_base=f".framework/staging/{stage}"),
        "committed_outputs": describe_files(run_dir, output_names, public_base="."),
        "capability_snapshot": dict(capability_snapshot or {}),
    }
    path = provenance_path(run_dir, stage)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def load_stage_provenance(run_dir: Path, stage: str) -> dict | None:
    path = provenance_path(run_dir, stage)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def assert_stage_provenance(run_dir: Path, stage: str) -> dict:
    payload = load_stage_provenance(run_dir, stage)
    if payload is None:
        raise RuntimeError(f"contract-violation: stage '{stage}' has no committed provenance")
    if payload.get("status") != "COMMITTED":
        raise RuntimeError(f"contract-violation: stage '{stage}' provenance is not committed")
    return payload


def assert_committed_outputs_intact(run_dir: Path, stage: str) -> dict:
    payload = assert_stage_provenance(run_dir, stage)
    committed_outputs = payload.get("committed_outputs", {})
    for name, meta in committed_outputs.items():
        path = run_dir / name
        if not path.exists():
            raise RuntimeError(
                f"contract-violation: committed output '{name}' for stage '{stage}' is missing from outputs"
            )
        current_hash = sha256_file(path)
        expected_hash = meta.get("sha256")
        if current_hash != expected_hash:
            raise RuntimeError(
                f"contract-violation: committed output '{name}' for stage '{stage}' no longer matches provenance"
            )
    return payload
