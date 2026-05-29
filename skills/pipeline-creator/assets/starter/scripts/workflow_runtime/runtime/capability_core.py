from __future__ import annotations

from typing import Mapping


STATUS_READY = "ready"
STATUS_MISSING = "missing"
STATUS_MISCONFIGURED = "misconfigured"

PROVIDER_SKILL = "skill"
PROVIDER_MCP = "mcp"
PROVIDER_CLI = "cli"
PROVIDER_BUILTIN = "builtin"
PROVIDER_NONE = "none"


def override_capability(env: Mapping[str, str], prefix: str):
    provider = env.get(f"{prefix}_PROVIDER")
    status = env.get(f"{prefix}_STATUS")
    if not provider and not status:
        return None
    return {
        "status": status or STATUS_READY,
        "provider": provider or PROVIDER_NONE,
    }


def capability(status: str, provider: str) -> dict:
    return {"status": status, "provider": provider}


def build_capability_report(runtime: str, env: Mapping[str, str], defaults: Mapping[str, tuple[str, str]], prefixes: Mapping[str, str]) -> dict:
    capabilities = {}
    for capability_name, (default_status, default_provider) in defaults.items():
        prefix = prefixes[capability_name]
        capabilities[capability_name] = (
            override_capability(env, prefix)
            or capability(default_status, default_provider)
        )

    return {
        "runtime": runtime,
        "capabilities": capabilities,
    }
