#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from adapters.common import (
    blocked_result,
    copy_template,
    ensure_inputs,
    extract_failure_type,
    load_request,
    load_response_if_exists,
    resolve_provider,
    response_path,
    result,
    stage_staging_dir,
    write_json,
)
from bridges.base import execute_provider
from runtime.provider_registry import ProviderSelectionError


STAGE = "market-research"
ENV_VAR = "IDEA_TO_PRD_MARKET_RESEARCH_CLI_CMD"


def builtin_market_research(run_dir: Path):
    created = []
    staging_dir = stage_staging_dir(run_dir, STAGE)
    md_path = staging_dir / "market-research.md"
    json_path = staging_dir / "market-research.json"
    if not md_path.exists():
        copy_template(md_path, "market-research.md")
        created.append("market-research.md")
    if not json_path.exists():
        write_json(
            json_path,
            {
                "market_exists": True,
                "market_maturity": "unknown",
                "user_need_strength": "unknown",
                "business_models": [],
                "opportunities": [],
                "risks": [],
                "evidence": [],
                "evidence_gaps": ["待补充真实市场证据"],
            },
        )
        created.append("market-research.json")
    res = result(True, STAGE, "market-research", provider="mock", created=created, updated=[], notes="Generated mock market research skeleton in staging.", retryable=False)
    write_json(response_path(run_dir, STAGE), res)
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    args = parser.parse_args()
    run_dir = Path(args.run_dir).resolve()

    ensure_inputs(run_dir, ["idea-brief.json"])
    load_request(run_dir, STAGE)
    try:
        _config, _report, provider = resolve_provider(run_dir, STAGE)
        response = execute_provider(
            run_dir,
            STAGE,
            provider,
            ENV_VAR,
            mock_handler=lambda: builtin_market_research(run_dir),
        )
    except ProviderSelectionError as exc:
        response = blocked_result(STAGE, "market-research", exc.failure_type, exc.reason)
    except Exception as exc:
        response = blocked_result(STAGE, "market-research", extract_failure_type(exc), str(exc))

    print(json.dumps(response, ensure_ascii=False))


if __name__ == "__main__":
    main()
