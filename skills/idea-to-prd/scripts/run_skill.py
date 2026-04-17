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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Runtime-aware launcher for the idea-to-prd skill")
    parser.add_argument("run_dir")
    parser.add_argument("--mode", default="codex-session")
    parser.add_argument("--allow-mock", action="store_true", help="仅在 dev-mock 模式下启用 mock provider，不属于正式 provider priority")
    parser.add_argument("--allow-seed", action="store_true", help="允许以 seed 方式导入已有阶段结果，并由 framework 补写 committed provenance")
    parser.add_argument("--check-only", action="store_true")
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return execute_skill_launcher(
        Path(args.run_dir),
        mode=args.mode,
        allow_mock=args.allow_mock,
        allow_seed=args.allow_seed,
        check_only=args.check_only,
        probe_capabilities=probe_capabilities,
        pipeline_script=SCRIPT_ROOT / "run_pipeline.py",
        blocked_report_name="idea-to-prd-report.md",
        env=os.environ,
    )


if __name__ == "__main__":
    raise SystemExit(main())
