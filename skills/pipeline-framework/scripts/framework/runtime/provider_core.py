from __future__ import annotations

from dataclasses import dataclass

from framework.runtime.runtime_config import RuntimeConfig


@dataclass
class ProviderSelectionError(RuntimeError):
    failure_type: str
    stage: str
    capability: str
    reason: str

    def __str__(self) -> str:
        return self.reason


def select_provider_for_capability(stage: str, capability: str, capability_report: dict, config: RuntimeConfig) -> dict:
    cap_info = capability_report.get("capabilities", {}).get(
        capability,
        {"status": "missing", "provider": "none"},
    )
    status = cap_info["status"]
    provider = cap_info["provider"]

    if config.mode == "dev-mock" and config.allow_mock:
        return {
            "runtime": config.mode,
            "capability": capability,
            "provider": "mock",
            "status": "ready",
        }

    if status == "ready":
        return {
            "runtime": config.mode,
            "capability": capability,
            "provider": provider,
            "status": status,
        }

    failure_type = "provider-misconfigured" if status == "misconfigured" else "missing-capability"
    raise ProviderSelectionError(
        failure_type=failure_type,
        stage=stage,
        capability=capability,
        reason=f"Capability '{capability}' is {status} for stage '{stage}'",
    )

