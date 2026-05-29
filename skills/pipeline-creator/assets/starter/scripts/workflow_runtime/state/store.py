from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from workflow_runtime.adapters.common import framework_dir


PIPELINE_PENDING = "PENDING"
PIPELINE_RUNNING = "RUNNING"
PIPELINE_BLOCKED = "BLOCKED"
PIPELINE_FAILED = "FAILED"
PIPELINE_COMPLETED = "COMPLETED"

STAGE_PENDING = "PENDING"
STAGE_READY = "READY"
STAGE_RUNNING = "RUNNING"
STAGE_BLOCKED = "BLOCKED"
STAGE_FAILED = "FAILED"
STAGE_VALIDATED = "VALIDATED"
STAGE_COMMITTED = "COMMITTED"


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def state_root(run_dir: Path) -> Path:
    path = framework_dir(run_dir) / "state"
    path.mkdir(parents=True, exist_ok=True)
    return path


def stages_state_dir(run_dir: Path) -> Path:
    path = state_root(run_dir) / "stages"
    path.mkdir(parents=True, exist_ok=True)
    return path


def pipeline_state_path(run_dir: Path) -> Path:
    return state_root(run_dir) / "pipeline.json"


def stage_state_path(run_dir: Path, stage: str) -> Path:
    return stages_state_dir(run_dir) / f"{stage}.json"


def initialize_pipeline_state(run_dir: Path, stage_order: list[str]) -> dict:
    payload = {
        "status": PIPELINE_PENDING,
        "stage_order": stage_order,
        "current_stage": None,
        "created_at": _now(),
        "updated_at": _now(),
    }
    _write_json(pipeline_state_path(run_dir), payload)
    for stage in stage_order:
        initialize_stage_state(run_dir, stage)
    return payload


def initialize_stage_state(run_dir: Path, stage: str) -> dict:
    payload = {
        "stage": stage,
        "status": STAGE_PENDING,
        "started_at": None,
        "finished_at": None,
        "provider": None,
        "adapter": None,
        "notes": "",
        "updated_at": _now(),
    }
    _write_json(stage_state_path(run_dir, stage), payload)
    return payload


def load_pipeline_state(run_dir: Path, stage_order: list[str] | None = None) -> dict:
    path = pipeline_state_path(run_dir)
    if not path.exists():
        return initialize_pipeline_state(run_dir, stage_order or [])
    return json.loads(path.read_text(encoding="utf-8"))


def write_pipeline_state(run_dir: Path, payload: dict) -> None:
    payload = dict(payload)
    payload["updated_at"] = _now()
    _write_json(pipeline_state_path(run_dir), payload)


def load_stage_state(run_dir: Path, stage: str) -> dict:
    path = stage_state_path(run_dir, stage)
    if not path.exists():
        return initialize_stage_state(run_dir, stage)
    return json.loads(path.read_text(encoding="utf-8"))


def write_stage_state(run_dir: Path, stage: str, payload: dict) -> None:
    payload = dict(payload)
    payload["stage"] = stage
    payload["updated_at"] = _now()
    _write_json(stage_state_path(run_dir, stage), payload)


def mark_pipeline_running(run_dir: Path, stage: str) -> None:
    payload = load_pipeline_state(run_dir)
    payload["status"] = PIPELINE_RUNNING
    payload["current_stage"] = stage
    write_pipeline_state(run_dir, payload)


def mark_pipeline_blocked(run_dir: Path, stage: str) -> None:
    payload = load_pipeline_state(run_dir)
    payload["status"] = PIPELINE_BLOCKED
    payload["current_stage"] = stage
    write_pipeline_state(run_dir, payload)


def mark_pipeline_failed(run_dir: Path, stage: str) -> None:
    payload = load_pipeline_state(run_dir)
    payload["status"] = PIPELINE_FAILED
    payload["current_stage"] = stage
    write_pipeline_state(run_dir, payload)


def mark_pipeline_completed(run_dir: Path) -> None:
    payload = load_pipeline_state(run_dir)
    payload["status"] = PIPELINE_COMPLETED
    payload["current_stage"] = None
    write_pipeline_state(run_dir, payload)


def mark_stage_ready(run_dir: Path, stage: str) -> None:
    payload = load_stage_state(run_dir, stage)
    payload["status"] = STAGE_READY
    write_stage_state(run_dir, stage, payload)


def mark_stage_running(run_dir: Path, stage: str, *, provider: str | None = None, adapter: str | None = None) -> None:
    payload = load_stage_state(run_dir, stage)
    payload["status"] = STAGE_RUNNING
    payload["started_at"] = payload.get("started_at") or _now()
    payload["provider"] = provider
    payload["adapter"] = adapter
    write_stage_state(run_dir, stage, payload)


def mark_stage_blocked(run_dir: Path, stage: str, notes: str) -> None:
    payload = load_stage_state(run_dir, stage)
    payload["status"] = STAGE_BLOCKED
    payload["finished_at"] = _now()
    payload["notes"] = notes
    write_stage_state(run_dir, stage, payload)


def mark_stage_failed(run_dir: Path, stage: str, notes: str) -> None:
    payload = load_stage_state(run_dir, stage)
    payload["status"] = STAGE_FAILED
    payload["finished_at"] = _now()
    payload["notes"] = notes
    write_stage_state(run_dir, stage, payload)


def mark_stage_validated(run_dir: Path, stage: str) -> None:
    payload = load_stage_state(run_dir, stage)
    payload["status"] = STAGE_VALIDATED
    write_stage_state(run_dir, stage, payload)


def mark_stage_committed(run_dir: Path, stage: str) -> None:
    payload = load_stage_state(run_dir, stage)
    payload["status"] = STAGE_COMMITTED
    payload["finished_at"] = _now()
    write_stage_state(run_dir, stage, payload)


def is_stage_committed(run_dir: Path, stage: str) -> bool:
    return load_stage_state(run_dir, stage).get("status") == STAGE_COMMITTED
