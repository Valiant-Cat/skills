#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


FRAMEWORK_SCRIPT_ROOT = Path(__file__).resolve().parents[3] / "scripts"
if str(FRAMEWORK_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_SCRIPT_ROOT))

from framework.runner.core import run_pipeline_stages  # noqa: E402
from pipeline_spec import STAGE_INPUTS, STAGE_ORDER, STAGE_OUTPUTS, adapter_paths, validator_paths  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    response = run_pipeline_stages(
        run_dir,
        STAGE_ORDER,
        STAGE_INPUTS,
        STAGE_OUTPUTS,
        adapter_paths(Path(__file__).resolve().parent),
        validator_paths(Path(__file__).resolve().parent),
    )
    if not response.get("ok"):
        print(json.dumps(response, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "stages": STAGE_ORDER}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
