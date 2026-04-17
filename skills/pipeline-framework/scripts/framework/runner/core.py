from __future__ import annotations

import json
import subprocess
import shutil
from pathlib import Path
from typing import Callable, Mapping, Sequence

from framework.adapters.common import (
    dispatch_dir,
    framework_dir,
    output_path,
    response_path,
    stage_staging_dir,
)
from framework.commit.core import assert_commit_manifest, clear_stage_staging_dir, commit_stage_outputs
from framework.provenance.store import assert_committed_outputs_intact, write_stage_provenance
from framework.runtime.runtime_config import build_runtime_config
from framework.state.store import (
    PIPELINE_PENDING,
    initialize_pipeline_state,
    is_stage_committed,
    load_pipeline_state,
    mark_pipeline_blocked,
    mark_pipeline_completed,
    mark_pipeline_failed,
    mark_pipeline_running,
    mark_stage_blocked,
    mark_stage_committed,
    mark_stage_failed,
    mark_stage_ready,
    mark_stage_running,
    mark_stage_validated,
)
from framework.validation.core import validate_stage_artifacts, validate_stage_content


def write_runtime_metadata(run_dir: Path, config, capability_report: dict) -> None:
    target = dispatch_dir(run_dir)
    (target / "runtime-config.json").write_text(
        json.dumps(
            {
                "mode": config.mode,
                "allow_mock": config.allow_mock,
                "allow_seed": config.allow_seed,
                "check_only": config.check_only,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (target / "capability-report.json").write_text(
        json.dumps(capability_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize_stage_request(stage: str, inputs: Sequence[str], outputs: Sequence[str]) -> dict:
    return {
        "stage": stage,
        "inputs": list(inputs),
        "outputs": list(outputs),
    }


def _normalize_list_value(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    return [str(value)]


def normalize_stage_response(stage: str, response: dict) -> dict:
    if not isinstance(response, dict):
        raise RuntimeError(f"response-invalid: stage '{stage}' returned non-object JSON payload")
    if "ok" not in response or not isinstance(response["ok"], bool):
        raise RuntimeError(f"response-invalid: stage '{stage}' response is missing a boolean 'ok'")

    response_stage = response.get("stage")
    if response_stage and response_stage != stage:
        raise RuntimeError(
            f"contract-violation: stage '{stage}' response declared mismatched stage '{response_stage}'"
        )

    normalized = {
        "ok": response["ok"],
        "stage": stage,
        "tool": str(response.get("tool") or stage),
        "created": _normalize_list_value(response.get("created")),
        "updated": _normalize_list_value(response.get("updated")),
        "notes": str(response.get("notes") or ""),
        "retryable": bool(response.get("retryable", False)),
    }
    if response.get("provider"):
        normalized["provider"] = str(response["provider"])
    return normalized


def write_stage_request(
    run_dir: Path,
    stage: str,
    stage_inputs: Mapping[str, Sequence[str]],
    stage_outputs: Mapping[str, Sequence[str]],
) -> None:
    payload = normalize_stage_request(stage, stage_inputs[stage], stage_outputs[stage])
    (dispatch_dir(run_dir) / f"{stage}-request.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run_stage_adapter(run_dir: Path, stage: str, adapter_path: Path) -> dict:
    proc = subprocess.run(
        ["python3", str(adapter_path), str(run_dir)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"adapter process failed for {stage}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as err:
        raise RuntimeError(f"adapter returned non-json for {stage}: {proc.stdout}") from err


def _load_runtime_mode(run_dir: Path) -> str:
    payload = json.loads((dispatch_dir(run_dir) / "runtime-config.json").read_text(encoding="utf-8"))
    return payload.get("mode", "codex-session")


def _seed_import_stage(
    run_dir: Path,
    stage: str,
    stage_outputs: Mapping[str, Sequence[str]],
) -> dict:
    bundle_path = response_path(run_dir, stage)
    if not bundle_path.exists():
        raise RuntimeError(f"missing-output: seed bundle for stage '{stage}' does not exist")
    response = normalize_stage_response(stage, json.loads(bundle_path.read_text(encoding='utf-8')))
    if not response.get("ok"):
        raise RuntimeError(f"contract-violation: seed bundle for stage '{stage}' is not successful")
    staging_dir = clear_stage_staging_dir(run_dir, stage)
    missing = []
    for name in stage_outputs[stage]:
        src = output_path(run_dir, name)
        if not src.exists():
            missing.append(name)
            continue
        shutil.copy2(src, staging_dir / name)
    if missing:
        raise RuntimeError(f"missing-output: seed import for stage '{stage}' is missing {', '.join(missing)}")
    response["provider"] = "seed"
    response["notes"] = (
        f"{response['notes']} | imported from seed bundle"
        if response["notes"]
        else "imported from seed bundle"
    )
    return response


def _producer_stage_for_input(
    input_name: str,
    stage_order: Sequence[str],
    stage_outputs: Mapping[str, Sequence[str]],
    current_stage: str,
) -> str | None:
    for stage in stage_order:
        if stage == current_stage:
            break
        if input_name in stage_outputs.get(stage, []):
            return stage
    return None


def _producer_stage_for_output(
    output_name: str,
    stage_order: Sequence[str],
    stage_outputs: Mapping[str, Sequence[str]],
) -> str | None:
    for stage in stage_order:
        if output_name in stage_outputs.get(stage, []):
            return stage
    return None


def assert_outputs_view_integrity(
    run_dir: Path,
    stage_order: Sequence[str],
    stage_outputs: Mapping[str, Sequence[str]],
    *,
    allow_seed: bool = False,
) -> None:
    declared_outputs = []
    for stage in stage_order:
        declared_outputs.extend(stage_outputs.get(stage, ()))

    for output_name in declared_outputs:
        path = output_path(run_dir, output_name)
        if not path.exists():
            continue
        producer_stage = _producer_stage_for_output(output_name, stage_order, stage_outputs)
        if producer_stage is None:
            continue
        if allow_seed and response_path(run_dir, producer_stage).exists():
            continue
        if not is_stage_committed(run_dir, producer_stage):
            raise RuntimeError(
                f"contract-violation: output '{output_name}' exists in outputs but producer stage '{producer_stage}' is not committed"
            )
        assert_commit_manifest(run_dir, producer_stage, stage_outputs.get(producer_stage, ()))
        assert_committed_outputs_intact(run_dir, producer_stage)


def assert_stage_dependencies_committed(
    run_dir: Path,
    stage: str,
    stage_order: Sequence[str],
    stage_inputs: Mapping[str, Sequence[str]],
    stage_outputs: Mapping[str, Sequence[str]],
) -> None:
    for input_name in stage_inputs.get(stage, []):
        producer_stage = _producer_stage_for_input(input_name, stage_order, stage_outputs, stage)
        if producer_stage is None:
            continue
        if not is_stage_committed(run_dir, producer_stage):
            raise RuntimeError(
                f"contract-violation: stage '{stage}' requires committed upstream stage '{producer_stage}' for input '{input_name}'"
            )
        assert_commit_manifest(run_dir, producer_stage, stage_outputs.get(producer_stage, ()))
        assert_committed_outputs_intact(run_dir, producer_stage)


def run_pipeline_stages(
    run_dir: Path,
    stage_order: Sequence[str],
    stage_inputs: Mapping[str, Sequence[str]],
    stage_outputs: Mapping[str, Sequence[str]],
    adapter_paths: Mapping[str, Path],
    validator_paths: Mapping[str, Path | None] | None = None,
) -> dict:
    load_pipeline_state(run_dir, list(stage_order))
    runtime_payload = json.loads((dispatch_dir(run_dir) / "runtime-config.json").read_text(encoding="utf-8"))
    allow_seed = bool(runtime_payload.get("allow_seed", False))
    runtime_mode = runtime_payload.get("mode", "codex-session")
    assert_outputs_view_integrity(run_dir, stage_order, stage_outputs, allow_seed=allow_seed)
    validator_paths = validator_paths or {}
    for stage in stage_order:
        if is_stage_committed(run_dir, stage):
            assert_commit_manifest(run_dir, stage, stage_outputs.get(stage, ()))
            assert_committed_outputs_intact(run_dir, stage)
            continue
        mark_stage_ready(run_dir, stage)
        assert_stage_dependencies_committed(run_dir, stage, stage_order, stage_inputs, stage_outputs)
        write_stage_request(run_dir, stage, stage_inputs, stage_outputs)
        clear_stage_staging_dir(run_dir, stage)
        mark_pipeline_running(run_dir, stage)
        if allow_seed and response_path(run_dir, stage).exists():
            response = _seed_import_stage(run_dir, stage, stage_outputs)
        else:
            response = normalize_stage_response(stage, run_stage_adapter(run_dir, stage, adapter_paths[stage]))
        if not response.get("ok"):
            mark_stage_blocked(run_dir, stage, response.get("notes", "blocked"))
            mark_pipeline_blocked(run_dir, stage)
            return response
        mark_stage_running(
            run_dir,
            stage,
            provider=response.get("provider"),
            adapter=adapter_paths[stage].name,
        )
        validate_stage_artifacts(run_dir, stage, stage_outputs[stage])
        validate_stage_content(
            run_dir,
            stage,
            validator_paths.get(stage),
            runtime_mode=runtime_mode,
            provider=response.get("provider", "unknown"),
        )
        mark_stage_validated(run_dir, stage)
        commit_stage_outputs(run_dir, stage, stage_outputs[stage])
        write_stage_provenance(
            run_dir,
            stage=stage,
            provider=response.get("provider", "unknown"),
            adapter=adapter_paths[stage].name,
            runtime_mode=runtime_mode,
            input_names=stage_inputs[stage],
            output_names=stage_outputs[stage],
            capability_snapshot={"provider": response.get("provider", "unknown"), "status": "ready"},
        )
        mark_stage_committed(run_dir, stage)

    mark_pipeline_completed(run_dir)
    return {"ok": True, "stages": list(stage_order)}


def invoke_pipeline_script(script_path: Path, run_dir: Path) -> int:
    cmd = ["python3", str(script_path), str(run_dir)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "pipeline invocation failed")
    if proc.stdout.strip():
        print(proc.stdout.strip())
    return proc.returncode


def write_blocked_report(run_dir: Path, title: str, exc: Exception) -> None:
    report = run_dir / title
    if report.exists():
        return
    report.write_text(
        "# Pipeline Report\n\n"
        "- Overall status: blocked\n"
        f"- Reason: {exc}\n",
        encoding="utf-8",
    )


def _strict_preflight_failures(
    capability_report: dict,
    required_capabilities: Sequence[str] | None,
) -> list[str]:
    capabilities = capability_report.get("capabilities", {})
    names = list(required_capabilities or capabilities.keys())
    failures = []
    for capability_name in names:
        cap_info = capabilities.get(capability_name, {"status": "missing", "provider": "none"})
        if cap_info.get("status") != "ready":
            failures.append(capability_name)
    return failures


def _display_capability_name(capability_name: str) -> str:
    return capability_name.replace("_", "-")


def execute_skill_launcher(
    run_dir: Path,
    *,
    mode: str,
    allow_mock: bool,
    allow_seed: bool,
    check_only: bool,
    strict_check: bool = False,
    required_capabilities: Sequence[str] | None = None,
    strict_check_failures: Callable[[Path, Mapping[str, str], dict], Sequence[str]] | None = None,
    probe_capabilities,
    pipeline_script: Path,
    blocked_report_name: str,
    env: Mapping[str, str],
) -> int:
    run_dir = run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    framework_dir(run_dir)

    config = build_runtime_config(mode, allow_mock=allow_mock, allow_seed=allow_seed, check_only=check_only)
    capability_report = probe_capabilities(config, env=env)
    print(json.dumps(capability_report, ensure_ascii=False, indent=2))

    failures = []
    custom_failures = False
    if strict_check:
        if strict_check_failures is not None:
            custom_failures = True
            failures = list(strict_check_failures(run_dir, env, capability_report))
        else:
            failures = _strict_preflight_failures(capability_report, required_capabilities)
    if failures:
        if custom_failures:
            missing = "; ".join(failures)
        else:
            missing = ", ".join(_display_capability_name(name) for name in failures)
        exc = RuntimeError(f"strict-preflight-failed: missing or misconfigured capabilities: {missing}")
        write_blocked_report(run_dir, blocked_report_name, exc)
        return 2

    if config.check_only:
        return 0

    write_runtime_metadata(run_dir, config, capability_report)

    try:
        return invoke_pipeline_script(pipeline_script, run_dir)
    except Exception as exc:
        initialize_pipeline_state(run_dir, load_pipeline_state(run_dir, []).get("stage_order", []))
        mark_pipeline_failed(run_dir, load_pipeline_state(run_dir, []).get("current_stage") or "unknown")
        write_blocked_report(run_dir, blocked_report_name, exc)
        return 2
