#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from adapters.common import (  # noqa: E402
    blocked_result,
    copy_template,
    ensure_inputs,
    extract_failure_type,
    load_request,
    load_response_if_exists,
    resolve_provider,
    output_path,
    stage_staging_dir,
    result,
    write_json,
)
from bridges.base import execute_provider  # noqa: E402


STAGE = "publish-note"
TOOL = "publish-note"
CLI_ENV_VAR = "EXAMPLE_PUBLISH_NOTE_CLI_CMD"


def builtin_handler(run_dir: Path) -> dict:
    ensure_inputs(run_dir, ["seed-note.json"])
    seed_payload = json.loads(output_path(run_dir, "seed-note.json").read_text(encoding="utf-8"))
    staging_dir = stage_staging_dir(run_dir, STAGE)
    md_path = staging_dir / "publish-note.md"
    json_path = staging_dir / "publish-note.json"
    if not md_path.exists():
        copy_template(md_path, "publish-note.md")
    write_json(
        json_path,
        {
            "title": seed_payload["topic"],
            "status": "published",
            "source": "seed-note",
        },
    )
    return result(True, STAGE, TOOL, provider="builtin", created=["publish-note.md", "publish-note.json"], notes="builtin publish note generated to staging")


def main(argv: list[str] | None = None) -> int:
    run_dir = Path((argv or sys.argv[1:])[0]).resolve()
    try:
        request = load_request(run_dir, STAGE)
        del request
        _, _, provider = resolve_provider(run_dir, STAGE)
        payload = execute_provider(
            run_dir,
            STAGE,
            provider,
            CLI_ENV_VAR,
            builtin_handler=lambda: builtin_handler(run_dir),
        )
    except Exception as exc:
        payload = blocked_result(STAGE, TOOL, extract_failure_type(exc), str(exc))
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
