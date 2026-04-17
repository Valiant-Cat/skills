#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_cases(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("input must be a JSON array")
    cases: list[dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict):
            cases.append(item)
    return cases


def normalize_events(events: object) -> list[dict[str, Any]]:
    if not isinstance(events, list):
        return []
    normalized: list[dict[str, Any]] = []
    for item in events:
        if isinstance(item, dict):
            normalized.append(item)
    return normalized


def detect_first_action(events: list[dict[str, Any]]) -> str | None:
    for event in events:
        target = event.get("target")
        if isinstance(target, str) and target.strip():
            return target
    return None


def is_strict_preflight(action: str | None) -> bool:
    if not action:
        return False
    return (
        "skills/idea-to-prd/scripts/run_skill.py" in action
        and "--check-only" in action
        and "--strict-check" in action
    )


def detect_interceptor(action: str | None) -> str | None:
    if not action:
        return None
    if "/using-superpowers/SKILL.md" in action:
        return "using-superpowers"
    if "/brainstorming/SKILL.md" in action:
        return "brainstorming"
    if action.endswith("/SKILL.md"):
        return Path(action).parent.name
    return None


def classify_case(case: dict[str, Any]) -> dict[str, Any]:
    events = normalize_events(case.get("events"))
    first_action = detect_first_action(events)
    preflight_first = is_strict_preflight(first_action)
    intercepted_by = detect_interceptor(first_action)
    selected = bool(case.get("selected_idea_to_prd", False))
    prompt = str(case.get("prompt", ""))

    if preflight_first:
        status = "passed"
    elif selected and intercepted_by:
        status = "intercepted"
    elif not selected:
        status = "not_selected"
    else:
        status = "unknown"

    return {
        "case_id": case.get("case_id", ""),
        "prompt": prompt,
        "idea_to_prd_explicit": "idea-to-prd" in prompt,
        "selected_idea_to_prd": selected,
        "first_action": first_action,
        "preflight_first": preflight_first,
        "intercepted_by": intercepted_by,
        "status": status,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    cases = load_cases(Path(args.input))
    results = [classify_case(case) for case in cases]
    Path(args.output).write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
