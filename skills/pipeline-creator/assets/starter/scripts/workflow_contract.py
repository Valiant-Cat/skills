#!/usr/bin/env python3
from __future__ import annotations

WORKFLOW_NAME = "__WORKFLOW_NAME__"
WORKFLOW_TYPE = "__WORKFLOW_TYPE__"
GOAL = "__WORKFLOW_GOAL__"

REQUIRED_REFERENCES = (
    "references/workflow.md",
    "references/architecture.md",
)

STAGES = __STAGES_JSON__


def stage_ids() -> list[str]:
    return [stage["id"] for stage in STAGES]


def expected_outputs() -> list[str]:
    outputs: list[str] = []
    for stage in STAGES:
        outputs.extend(stage["outputs"])
    return outputs


def templates() -> list[str]:
    return [stage["template"] for stage in STAGES]
