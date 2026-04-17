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


STAGE = "idea-brief"
ENV_VAR = "IDEA_TO_PRD_IDEA_BRIEF_CLI_CMD"


def builtin_idea_brief(run_dir: Path):
    created = []
    staging_dir = stage_staging_dir(run_dir, STAGE)
    md_path = staging_dir / "idea-brief.md"
    json_path = staging_dir / "idea-brief.json"
    if not md_path.exists():
        copy_template(md_path, "idea-brief.md")
        created.append("idea-brief.md")
    if not json_path.exists():
        write_json(
            json_path,
            {
                "product_name": "待明确产品名",
                "problem_statement": "待整理",
                "target_users": ["待明确目标用户"],
                "core_scenarios": ["待明确核心场景"],
                "platforms": ["待明确平台"],
                "geographies": ["待明确市场"],
                "constraints": ["待补充约束"],
                "success_metrics": ["待补充成功指标"],
                "out_of_scope": ["待补充不做项"],
                "assumptions": ["待补充关键假设"],
                "open_questions": ["待确认问题"],
            },
        )
        created.append("idea-brief.json")
    res = result(True, STAGE, "idea-brief", provider="builtin", created=created, updated=[], notes="Generated builtin idea brief skeleton in staging.", retryable=False)
    write_json(response_path(run_dir, STAGE), res)
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    args = parser.parse_args()
    run_dir = Path(args.run_dir).resolve()

    load_request(run_dir, STAGE)
    try:
        _config, _report, provider = resolve_provider(run_dir, STAGE)
        response = execute_provider(
            run_dir,
            STAGE,
            provider,
            ENV_VAR,
            builtin_handler=lambda: builtin_idea_brief(run_dir),
            mock_handler=lambda: builtin_idea_brief(run_dir),
        )
    except ProviderSelectionError as exc:
        response = blocked_result(STAGE, "idea-brief", exc.failure_type, exc.reason)
    except Exception as exc:
        response = blocked_result(STAGE, "idea-brief", extract_failure_type(exc), str(exc))

    print(json.dumps(response, ensure_ascii=False))


if __name__ == "__main__":
    main()
