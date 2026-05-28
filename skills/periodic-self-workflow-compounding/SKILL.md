---
name: periodic-self-workflow-compounding
description: 定期自我流程沉淀. Use when the user asks Codex to review recent work, identify repeated manual workflows, and package high-confidence missing items as skills, custom subagents, or automations. Trigger phrases include "定期自我流程沉淀", "review my recent work for workflows", "find workflows worth packaging", "create reusable skills from recent sessions", and similar requests.
---

# 定期自我流程沉淀

## Overview

Execute the workflow below directly. Review recent work, find repeated manual workflows worth packaging, produce a compact evidence-backed shortlist, then create only high-confidence missing items.

## Source Prompt

Look back over my recent work from the last 30 days, or all available history if shorter, and identify repeated manual workflows worth packaging.

Use available evidence in this order:

1. Recent Codex sessions and task summaries.
2. Codex Memories and rollout summaries to find patterns repeated across sessions.
3. Chronicle, if enabled, to spot repeated work outside Codex. Use Chronicle for discovery only; confirm important details in the relevant source system when possible.
4. Existing skills, custom agents, and automations, so you reuse or extend what already exists instead of duplicating it.

Look broadly for work that is repeated, time-consuming, error-prone, context-heavy, or benefits from a consistent process. Include workflows across coding, research, writing, planning, communication, operations, analysis, and personal administration.

Only act on a candidate when it:

- occurred at least twice, or is clearly likely to recur and costly to repeat;
- has stable inputs, a repeatable procedure, and a clear output or stopping condition;
- would materially improve speed, quality, consistency, or reliability;
- is not already adequately covered.

Choose the smallest appropriate form:

- Skill: a reusable workflow or playbook.
- Custom subagent: a bounded specialist role or investigation task suitable for delegation.
- Automation: a scheduled or recurring check, report, reminder, or monitor.
- Skip: work that is too one-off, ambiguous, sensitive, or poorly evidenced to package.

First produce a compact shortlist with:

- repeated workflow
- supporting evidence and dates
- frequency/confidence
- recommended form: skill, subagent, automation, extend existing, or skip
- why it is or is not worth creating

Then create only the high-confidence missing items. Keep them narrow, practical, source-aware, and easy to validate. Do not create speculative, overlapping, or overly broad assets.

Finish with:

- what you created or extended
- what you deliberately skipped
- what needs more evidence before packaging

## Execution Rules

- Treat the source prompt as the task to perform, not as text to rewrite.
- Inspect available local session history, summaries, memories, skills, agents, and automations before proposing new assets.
- Prefer evidence already available locally. If a source system or connector is unavailable, state that limitation and continue with the available evidence.
- Do not use Chronicle as final authority; use it only to discover candidates and confirm important details in the source system when possible.
- Reuse or extend existing skills, custom agents, and automations when coverage is close enough.
- Before creating or editing assets, state the shortlist and the specific high-confidence items selected for creation.
- Keep new assets minimal and specific to the evidenced workflow.
- Validate created skills or automations with the relevant local validator or inspection step whenever available.
- Do not package sensitive, one-off, speculative, or poorly evidenced workflows.

## Output Format

Use these sections:

1. `Shortlist`
2. `Created Or Extended`
3. `Skipped`
4. `Needs More Evidence`

Keep the shortlist compact, but include enough evidence and dates to justify each recommendation.
