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


STAGE = "competitor-analysis"
ENV_VAR = "IDEA_TO_PRD_COMPETITOR_ANALYSIS_CLI_CMD"


def builtin_competitor_analysis(run_dir: Path):
    created = []
    staging_dir = stage_staging_dir(run_dir, STAGE)
    md_path = staging_dir / "competitor-analysis.md"
    json_path = staging_dir / "competitor-analysis.json"
    if not md_path.exists():
        copy_template(md_path, "competitor-analysis.md")
        created.append("competitor-analysis.md")
    if not json_path.exists():
        write_json(
            json_path,
            {
                "competitors": [],
                "common_patterns": [],
                "differentiators": [],
                "borrow_list": [],
                "avoid_list": [],
                "mvp_recommendations": [],
            },
        )
        created.append("competitor-analysis.json")
    res = result(True, STAGE, "competitor-analysis", provider="mock", created=created, updated=[], notes="Generated mock competitor analysis skeleton in staging.", retryable=False)
    write_json(response_path(run_dir, STAGE), res)
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    args = parser.parse_args()
    run_dir = Path(args.run_dir).resolve()

    ensure_inputs(run_dir, ["idea-brief.json", "market-research.json"])
    load_request(run_dir, STAGE)
    try:
        _config, _report, provider = resolve_provider(run_dir, STAGE)
        response = execute_provider(
            run_dir,
            STAGE,
            provider,
            ENV_VAR,
            mock_handler=lambda: builtin_competitor_analysis(run_dir),
        )
    except ProviderSelectionError as exc:
        response = blocked_result(STAGE, "competitor-analysis", exc.failure_type, exc.reason)
    except Exception as exc:
        response = blocked_result(STAGE, "competitor-analysis", extract_failure_type(exc), str(exc))

    print(json.dumps(response, ensure_ascii=False))


if __name__ == "__main__":
    main()
