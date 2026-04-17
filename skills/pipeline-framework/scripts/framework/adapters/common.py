from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

from framework.runtime.runtime_config import build_runtime_config


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def result(ok: bool, stage: str, tool: str, provider: str | None = None, created=None, updated=None, notes="", retryable=False):
    payload = {
        "ok": ok,
        "stage": stage,
        "tool": tool,
        "created": created or [],
        "updated": updated or [],
        "notes": notes,
        "retryable": retryable,
    }
    if provider:
        payload["provider"] = provider
    return payload


def dispatch_dir(run_dir: Path) -> Path:
    path = run_dir / ".dispatch"
    path.mkdir(parents=True, exist_ok=True)
    return path


def framework_dir(run_dir: Path) -> Path:
    path = run_dir / ".framework"
    path.mkdir(parents=True, exist_ok=True)
    return path


def staging_root(run_dir: Path) -> Path:
    path = framework_dir(run_dir) / "staging"
    path.mkdir(parents=True, exist_ok=True)
    return path


def stage_staging_dir(run_dir: Path, stage: str) -> Path:
    path = staging_root(run_dir) / stage
    path.mkdir(parents=True, exist_ok=True)
    return path


def outputs_dir(run_dir: Path) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def output_path(run_dir: Path, name: str) -> Path:
    return outputs_dir(run_dir) / name


def request_path(run_dir: Path, stage: str) -> Path:
    return dispatch_dir(run_dir) / f"{stage}-request.json"


def response_path(run_dir: Path, stage: str) -> Path:
    return dispatch_dir(run_dir) / f"{stage}-response.json"


def runtime_config_path(run_dir: Path) -> Path:
    return dispatch_dir(run_dir) / "runtime-config.json"


def capability_report_path(run_dir: Path) -> Path:
    return dispatch_dir(run_dir) / "capability-report.json"


def load_request(run_dir: Path, stage: str) -> dict:
    path = request_path(run_dir, stage)
    if not path.exists():
        raise FileNotFoundError(f"Missing dispatch request: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_response_if_exists(run_dir: Path, stage: str) -> Optional[dict]:
    path = response_path(run_dir, stage)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_runtime_config(run_dir: Path):
    path = runtime_config_path(run_dir)
    if not path.exists():
        return build_runtime_config("codex-session", allow_mock=False, allow_seed=False, check_only=False)
    payload = json.loads(path.read_text(encoding="utf-8"))
    return build_runtime_config(
        payload.get("mode", "codex-session"),
        allow_mock=payload.get("allow_mock", False),
        allow_seed=payload.get("allow_seed", False),
        check_only=payload.get("check_only", False),
    )


def load_capability_report(run_dir: Path, config) -> dict:
    path = capability_report_path(run_dir)
    if not path.exists():
        return {"runtime": config.mode, "capabilities": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def blocked_result(stage: str, tool: str, failure_type: str, notes: str, retryable: bool = False):
    return result(False, stage, tool, created=[], updated=[], notes=f"{failure_type}: {notes}", retryable=retryable)


def extract_failure_type(exc: Exception) -> str:
    text = str(exc).lower()
    for failure_type in (
        "missing-capability",
        "provider-misconfigured",
        "unsupported-runtime",
        "bridge-not-implemented",
    ):
        if failure_type in text:
            return failure_type
    return "adapter-failure"


def run_cli_command(run_dir: Path, stage: str, env_var: str) -> Optional[dict]:
    command = os.environ.get(env_var, "").strip()
    if not command:
        return None

    req = request_path(run_dir, stage)
    resp = response_path(run_dir, stage)
    env = os.environ.copy()
    env.update({
        "RUN_DIR": str(run_dir),
        "STAGE": stage,
        "REQUEST_PATH": str(req),
        "RESPONSE_PATH": str(resp),
        "STAGING_DIR": str(stage_staging_dir(run_dir, stage)),
        "OUTPUTS_DIR": str(outputs_dir(run_dir)),
    })

    proc = subprocess.run(command, shell=True, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        raise RuntimeError(f"CLI command failed for {stage}: {proc.stderr.strip() or proc.stdout.strip()}")

    if resp.exists():
        return json.loads(resp.read_text(encoding="utf-8"))

    stdout = proc.stdout.strip()
    if stdout:
        try:
            return json.loads(stdout)
        except json.JSONDecodeError as err:
            raise RuntimeError(f"CLI command returned non-JSON output for {stage}: {stdout}") from err
    raise RuntimeError(f"CLI command for {stage} produced neither response file nor JSON stdout")
