#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from runtime.capability_probe import probe_capabilities  # noqa: E402
from workflow_runtime.runner.core import execute_skill_launcher  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launcher for the __SKILL_SLUG__ workflow skill")
    parser.add_argument("run_dir")
    parser.add_argument("--mode", default="codex-session")
    parser.add_argument("--allow-mock", action="store_true")
    parser.add_argument("--allow-seed", action="store_true")
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
        blocked_report_name="__SKILL_SLUG__-report.md",
        env=os.environ,
    )


if __name__ == "__main__":
    raise SystemExit(main())
