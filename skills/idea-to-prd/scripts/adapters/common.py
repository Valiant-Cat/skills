from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[2].parent / "pipeline-framework" / "scripts"
if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))

from framework.adapters.common import (  # noqa: E402
    blocked_result,
    capability_report_path,
    dispatch_dir,
    extract_failure_type,
    load_capability_report,
    load_request,
    load_response_if_exists,
    load_runtime_config,
    output_path,
    request_path,
    response_path,
    result,
    run_cli_command,
    runtime_config_path,
    stage_staging_dir,
    write_json,
    write_text,
)
from runtime.provider_registry import select_provider


def skill_root() -> Path:
    return Path(__file__).resolve().parents[2]


def template_path(name: str) -> Path:
    return skill_root() / "assets" / "templates" / name


def ensure_inputs(run_dir: Path, inputs: Iterable[str]):
    missing = [name for name in inputs if not (run_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing required inputs: {', '.join(missing)}")


def copy_template(path: Path, template_name: str):
    write_text(path, template_path(template_name).read_text(encoding="utf-8"))


def resolve_provider(run_dir: Path, stage: str):
    config = load_runtime_config(run_dir)
    capability_report = load_capability_report(run_dir, config)
    provider = select_provider(stage, capability_report, config)
    return config, capability_report, provider
