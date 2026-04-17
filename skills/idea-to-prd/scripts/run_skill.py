#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from runtime.capability_probe import probe_capabilities
from framework.runner.core import execute_skill_launcher


STRICT_STAGE_REQUIREMENTS = (
    {
        "stage": "market-research",
        "capability": "idea_to_prd_market_research",
        "cli_cmd_env": "IDEA_TO_PRD_MARKET_RESEARCH_CLI_CMD",
        "outputs": ("market-research.json", "market-research.md"),
    },
    {
        "stage": "competitor-analysis",
        "capability": "idea_to_prd_competitor_analysis",
        "cli_cmd_env": "IDEA_TO_PRD_COMPETITOR_ANALYSIS_CLI_CMD",
        "outputs": ("competitor-analysis.json", "competitor-analysis.md"),
    },
)

STRICT_REQUIRED_CAPABILITIES = (
    "idea_to_prd_idea_brief",
    "idea_to_prd_market_research",
    "idea_to_prd_competitor_analysis",
    "idea_to_prd_prd_generation",
)


def strict_check_failures(run_dir: Path, env: dict[str, str], capability_report: dict) -> list[str]:
    failures: list[str] = []
    capabilities = capability_report.get("capabilities", {})
    dispatch_dir = run_dir / ".dispatch"
    for requirement in STRICT_STAGE_REQUIREMENTS:
        capability_name = requirement["capability"]
        stage = requirement["stage"]
        cap_info = capabilities.get(capability_name, {"status": "missing", "provider": "none"})
        status = cap_info.get("status")
        provider = cap_info.get("provider")
        outputs = [run_dir / name for name in requirement["outputs"]]
        bundle_path = dispatch_dir / f"{stage}-response.json"

        if status == "ready":
            if provider == "cli" and not env.get(requirement["cli_cmd_env"]):
                failures.append(f"stage '{stage}' uses cli provider but missing {requirement['cli_cmd_env']}")
            continue

        if env.get("ALLOW_SEED_FOR_STRICT_CHECK") == "1" and bundle_path.exists() and all(path.exists() for path in outputs):
            continue

        failures.append(stage)

    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Runtime-aware launcher for the idea-to-prd skill")
    parser.add_argument("run_dir")
    parser.add_argument("--mode", default="codex-session")
    parser.add_argument("--allow-mock", action="store_true", help="仅在 dev-mock 模式下启用 mock provider，不属于正式 provider priority")
    parser.add_argument("--allow-seed", action="store_true", help="允许以 seed 方式导入已有阶段结果，并由 framework 补写 committed provenance")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--strict-check", action="store_true", help="对关键 capability 执行阻断式预检；失败时返回非 0 并写入 blocked report")
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    strict_env = dict(os.environ)
    if args.allow_seed:
        strict_env["ALLOW_SEED_FOR_STRICT_CHECK"] = "1"
    return execute_skill_launcher(
        Path(args.run_dir),
        mode=args.mode,
        allow_mock=args.allow_mock,
        allow_seed=args.allow_seed,
        check_only=args.check_only,
        strict_check=args.strict_check,
        required_capabilities=STRICT_REQUIRED_CAPABILITIES,
        strict_check_failures=strict_check_failures,
        probe_capabilities=probe_capabilities,
        pipeline_script=SCRIPT_ROOT / "run_pipeline.py",
        blocked_report_name="idea-to-prd-report.md",
        env=strict_env,
    )


if __name__ == "__main__":
    raise SystemExit(main())
