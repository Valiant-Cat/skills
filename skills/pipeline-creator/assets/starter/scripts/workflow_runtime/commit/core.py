from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Sequence

from workflow_runtime.adapters.common import framework_dir, output_path, stage_staging_dir


def commit_dir(run_dir: Path) -> Path:
    path = framework_dir(run_dir) / "commit" / "manifests"
    path.mkdir(parents=True, exist_ok=True)
    return path


def commit_manifest_path(run_dir: Path, stage: str) -> Path:
    return commit_dir(run_dir) / f"{stage}.json"


def load_commit_manifest(run_dir: Path, stage: str) -> dict | None:
    path = commit_manifest_path(run_dir, stage)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def assert_commit_manifest(run_dir: Path, stage: str, expected_outputs: Sequence[str]) -> dict:
    payload = load_commit_manifest(run_dir, stage)
    if payload is None:
        raise RuntimeError(f"contract-violation: stage '{stage}' has no commit manifest")
    if payload.get("stage") != stage:
        raise RuntimeError(
            f"contract-violation: stage '{stage}' commit manifest declared mismatched stage '{payload.get('stage')}'"
        )

    manifest_outputs = payload.get("outputs")
    if not isinstance(manifest_outputs, list):
        raise RuntimeError(f"contract-violation: stage '{stage}' commit manifest has invalid outputs")

    expected_set = set(expected_outputs)
    manifest_set = {str(name) for name in manifest_outputs}
    if manifest_set != expected_set:
        raise RuntimeError(
            f"contract-violation: stage '{stage}' commit manifest outputs do not match expected outputs"
        )

    for name in expected_outputs:
        if not output_path(run_dir, name).exists():
            raise RuntimeError(
                f"contract-violation: committed output '{name}' for stage '{stage}' is missing from outputs"
            )
    return payload


def clear_stage_staging_dir(run_dir: Path, stage: str) -> Path:
    path = stage_staging_dir(run_dir, stage)
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def commit_stage_outputs(run_dir: Path, stage: str, output_names: Sequence[str]) -> dict:
    source_dir = stage_staging_dir(run_dir, stage)
    committed: list[str] = []
    for name in output_names:
        source_path = source_dir / name
        if not source_path.exists():
            raise RuntimeError(f"missing-output: stage '{stage}' staging is missing {name}")
        destination_path = output_path(run_dir, name)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)
        committed.append(name)

    payload = {
        "stage": stage,
        "committed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": f".workflow/staging/{stage}",
        "destination": ".",
        "outputs": committed,
    }
    commit_manifest_path(run_dir, stage).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return payload
