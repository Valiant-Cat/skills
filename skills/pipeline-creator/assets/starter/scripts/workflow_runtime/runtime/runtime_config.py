from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RuntimeMode = Literal["codex-session", "terminal", "dev-mock"]
VALID_RUNTIME_MODES = ("codex-session", "terminal", "dev-mock")


@dataclass(frozen=True)
class RuntimeConfig:
    mode: RuntimeMode = "codex-session"
    allow_mock: bool = False
    allow_seed: bool = False
    check_only: bool = False


def parse_runtime_mode(value: str) -> RuntimeMode:
    if value not in VALID_RUNTIME_MODES:
        joined = ", ".join(VALID_RUNTIME_MODES)
        raise ValueError(f"Unsupported runtime mode '{value}'. Expected one of: {joined}")
    return value


def build_runtime_config(mode: str, allow_mock: bool, allow_seed: bool, check_only: bool) -> RuntimeConfig:
    return RuntimeConfig(
        mode=parse_runtime_mode(mode),
        allow_mock=allow_mock,
        allow_seed=allow_seed,
        check_only=check_only,
    )
