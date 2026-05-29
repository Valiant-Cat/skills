from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Sequence

from workflow_runtime.adapters.common import stage_staging_dir


def validate_stage_artifacts(run_dir: Path, stage: str, expected_outputs: Sequence[str]) -> None:
    staging_dir = stage_staging_dir(run_dir, stage)
    missing = [name for name in expected_outputs if not (staging_dir / name).exists()]
    if missing:
        raise RuntimeError(f"missing-output: stage '{stage}' staging is missing {', '.join(missing)}")


def load_validator_callable(validator_path: Path):
    spec = importlib.util.spec_from_file_location(f"validator_{validator_path.stem}", validator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"contract-violation: unable to load validator module {validator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    validate = getattr(module, "validate", None)
    if validate is None:
        raise RuntimeError(f"contract-violation: validator {validator_path} does not export validate()")
    return validate


def validate_stage_content(
    run_dir: Path,
    stage: str,
    validator_path: Path | None,
    *,
    runtime_mode: str,
    provider: str,
) -> None:
    if validator_path is None:
        return
    if runtime_mode == "dev-mock" or provider == "mock":
        return
    validate = load_validator_callable(validator_path)
    validate(stage_staging_dir(run_dir, stage))
