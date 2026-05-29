#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from workflow_contract import REQUIRED_REFERENCES, STAGES, templates


def external_file_inputs() -> list[str]:
    produced_outputs: set[str] = set()
    external_inputs: list[str] = []
    for stage in STAGES:
        for input_name in stage["inputs"]:
            path = Path(input_name)
            if path.suffix and input_name not in produced_outputs and input_name not in external_inputs:
                external_inputs.append(input_name)
        produced_outputs.update(stage["outputs"])
    return external_inputs


def seed_external_inputs(run_dir: Path) -> None:
    for input_name in external_file_inputs():
        path = run_dir / input_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# Smoke Input\n\nSeeded input for `{input_name}`.\n", encoding="utf-8")


def run_smoke_checks(skill_root: Path) -> list[str]:
    errors: list[str] = []
    run_skill = skill_root / "scripts" / "run_skill.py"
    if not run_skill.exists():
        return [f"missing smoke entrypoint: {run_skill}"]

    with tempfile.TemporaryDirectory(prefix="workflow-smoke-") as tmp:
        tmp_root = Path(tmp)
        check_dir = tmp_root / "check"
        run_dir = tmp_root / "run"
        seed_external_inputs(run_dir)
        commands = [
            [sys.executable, str(run_skill), str(check_dir), "--check-only"],
            [
                sys.executable,
                str(run_skill),
                str(run_dir),
                "--mode",
                "dev-mock",
                "--allow-mock",
            ],
        ]
        for command in commands:
            proc = subprocess.run(command, cwd=skill_root, capture_output=True, text=True)
            if proc.returncode != 0:
                errors.append(
                    "smoke command failed: "
                    + " ".join(command)
                    + "\nstdout:\n"
                    + proc.stdout
                    + "\nstderr:\n"
                    + proc.stderr
                )

        if (run_dir / ".framework").exists():
            errors.append("smoke run created deprecated .framework directory")
        if not (run_dir / ".workflow").exists():
            errors.append("smoke run did not create .workflow runtime directory")

    return errors


def validate_skill_root(skill_root: Path, *, run_smoke: bool = False) -> dict:
    errors: list[str] = []
    required_files = [
        "SKILL.md",
        "agents/openai.yaml",
        "scripts/workflow_contract.py",
        "scripts/validate_workflow.py",
        "scripts/run_skill.py",
        "scripts/run_pipeline.py",
        "scripts/pipeline_spec.py",
        "scripts/adapters/common.py",
        "scripts/bridges/base.py",
        "scripts/runtime/capability_probe.py",
        "scripts/runtime/provider_registry.py",
        "scripts/runtime/runtime_config.py",
        "scripts/workflow_runtime/runner/core.py",
        "tests/test_workflow_contract.py",
        *REQUIRED_REFERENCES,
        *templates(),
    ]
    for relative in required_files:
        if not (skill_root / relative).exists():
            errors.append(f"missing required file: {relative}")

    skill_md = (skill_root / "SKILL.md").read_text(encoding="utf-8") if (skill_root / "SKILL.md").exists() else ""
    architecture_md = (
        (skill_root / "references" / "architecture.md").read_text(encoding="utf-8")
        if (skill_root / "references" / "architecture.md").exists()
        else ""
    )
    workflow_md = (
        (skill_root / "references" / "workflow.md").read_text(encoding="utf-8")
        if (skill_root / "references" / "workflow.md").exists()
        else ""
    )
    combined = skill_md + architecture_md + workflow_md
    for token in (".framework",):
        if token in combined:
            errors.append(f"forbidden runtime dependency text found: {token}")

    for heading in ("## Runner Contract", "## Adapter Contract", "## Input Contract", "## Output Contract"):
        if heading not in architecture_md:
            errors.append(f"architecture reference missing heading: {heading}")

    for stage in STAGES:
        if stage["id"] not in workflow_md:
            errors.append(f"workflow reference missing stage: {stage['id']}")
        if not stage["inputs"]:
            errors.append(f"stage has no inputs: {stage['id']}")
        if not stage["outputs"]:
            errors.append(f"stage has no outputs: {stage['id']}")
        if not stage["acceptance_checks"]:
            errors.append(f"stage has no acceptance checks: {stage['id']}")

    if run_smoke:
        errors.extend(run_smoke_checks(skill_root))

    return {"ok": not errors, "errors": errors, "stage_count": len(STAGES)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate generated workflow Skill contract files.")
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--run-smoke", action="store_true", help="Run check-only and dev-mock entrypoint smoke tests.")
    args = parser.parse_args(argv)
    result = validate_skill_root(args.skill_root.resolve(), run_smoke=args.run_smoke)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
