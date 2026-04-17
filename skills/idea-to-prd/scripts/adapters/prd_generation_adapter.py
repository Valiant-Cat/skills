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


STAGE = "prd-generation"
ENV_VAR = "IDEA_TO_PRD_PRD_GENERATION_CLI_CMD"


def builtin_prd(run_dir: Path):
    created = []
    staging_dir = stage_staging_dir(run_dir, STAGE)
    md_path = staging_dir / "prd.md"
    json_path = staging_dir / "prd.json"
    if not md_path.exists():
        copy_template(md_path, "prd.md")
        created.append("prd.md")
    if not json_path.exists():
        write_json(
            json_path,
            {
                "product_name": "待明确产品名",
                "goals": ["待明确核心目标"],
                "target_users": ["待明确目标用户"],
                "core_scenarios": ["待明确核心场景"],
                "positioning": "待明确定位",
                "mvp_scope": {"in_scope": ["待明确 MVP 范围"], "out_of_scope": ["待明确不做项"]},
                "features": [
                    {
                        "module": "待明确模块",
                        "name": "待明确 P0 功能",
                        "priority": "P0",
                        "user_value": "待明确用户价值",
                        "preconditions": ["待明确前置条件"],
                        "acceptance_criteria": ["待明确验收标准"],
                        "edge_cases": ["待明确边界情况"],
                        "dependencies": ["待明确依赖"],
                    }
                ],
                "non_functional_requirements": ["待明确非功能要求"],
                "risks": ["待明确风险"],
                "open_questions": ["待明确问题"],
                "source_summary": ["待补充来源摘要"],
            },
        )
        created.append("prd.json")
    res = result(True, STAGE, "prd-generation", provider="builtin", created=created, updated=[], notes="Generated builtin PRD skeleton in staging.", retryable=False)
    write_json(response_path(run_dir, STAGE), res)
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    args = parser.parse_args()
    run_dir = Path(args.run_dir).resolve()

    ensure_inputs(run_dir, ["idea-brief.json", "market-research.json", "competitor-analysis.json"])
    load_request(run_dir, STAGE)
    try:
        _config, _report, provider = resolve_provider(run_dir, STAGE)
        response = execute_provider(
            run_dir,
            STAGE,
            provider,
            ENV_VAR,
            builtin_handler=lambda: builtin_prd(run_dir),
            mock_handler=lambda: builtin_prd(run_dir),
        )
    except ProviderSelectionError as exc:
        response = blocked_result(STAGE, "prd-generation", exc.failure_type, exc.reason)
    except Exception as exc:
        response = blocked_result(STAGE, "prd-generation", extract_failure_type(exc), str(exc))

    print(json.dumps(response, ensure_ascii=False))


if __name__ == "__main__":
    main()
