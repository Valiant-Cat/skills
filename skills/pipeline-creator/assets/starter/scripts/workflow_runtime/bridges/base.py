from __future__ import annotations

from pathlib import Path
from typing import Callable

from workflow_runtime.adapters.common import run_cli_command


def execute_provider(
    run_dir: Path,
    stage: str,
    provider: dict,
    env_var: str,
    builtin_handler: Callable[[], dict] | None = None,
    mock_handler: Callable[[], dict] | None = None,
) -> dict:
    if provider["provider"] == "mock":
        if mock_handler is None:
            raise RuntimeError(f"bridge-not-implemented: no mock handler for stage '{stage}'")
        return mock_handler()

    if provider["provider"] == "builtin":
        if builtin_handler is None:
            raise RuntimeError(f"bridge-not-implemented: no builtin handler for stage '{stage}'")
        return builtin_handler()

    response = run_cli_command(run_dir, stage, env_var)
    if response is not None:
        return response

    raise RuntimeError(
        f"bridge-not-implemented: provider '{provider['provider']}' for capability "
        f"'{provider['capability']}' in stage '{stage}'"
    )
