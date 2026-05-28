---
name: goal-command-generator
description: Generate a copy-ready Codex Goal command from the user's stated objective plus any unfinished, partially implemented, or not-yet-landed requirements in the current session. Use when the user asks to create, draft, rewrite, or output a "/goal达成..." command, Goal prompt, Codex Goal command, or wants session requirements summarized into an executable Goal command.
---

# Goal Command Generator

## Overview

Generate one detailed Codex Goal command in Chinese. The final response must be directly copyable and must not execute the goal, edit files, or include commentary outside the command unless the user explicitly asks for explanation.

## Workflow

1. Identify the objective from the latest user request.
2. Review the current session context for requirements that were provided but not fully landed, verified, or implemented.
3. Merge those requirements into one concrete final outcome.
4. Fill the command template with explicit success evidence, constraints, allowed scope, iteration strategy, and blocking report requirements.
5. Output only the command text.

## Command Template

Use this exact shape, replacing every bracketed clause with concrete content:

```text
/goal达成<你希望 Codex 最终完成的目标>，并通过<具体可验证的证据>来确认结果有效，同时保持<必须遵守的限制条件>不被破坏。只能使用<允许使用的输入、工具、文件范围或操作边界>。在每一轮迭代之间，Codex 需要根据<如何判断下一步最优行动>来选择下一步。如果遇到阻塞，或者已经没有有效路径可以继续尝试，Codex 必须停止，并报告<已经尝试过的方法、已获得的证据、当前阻塞点，以及还需要什么信息或权限才能继续推进>。
```

## Filling Rules

- Start the final answer with `/goal达成`.
- Write in Chinese unless the user explicitly requests another language.
- Make the goal operational: include what to build, fix, research, verify, or deliver.
- Include all known unfinished session requirements that are relevant to the same objective. Do not invent unrelated requirements.
- Define evidence as observable artifacts, passing commands, tests, screenshots, diffs, generated files, user-visible behavior, logs, or other verifiable outputs.
- Preserve constraints from the user, AGENTS.md, system/developer instructions, repo conventions, sandbox limits, and any explicit "do not" requirements.
- Define allowed scope narrowly: mention permitted inputs, tools, paths, commands, external sources, or operations. If the user did not provide a scope, use the current workspace/session context and non-destructive local operations.
- Define iteration strategy in terms of evidence: inspect current state, choose the highest-risk or most-blocking gap first, implement the smallest coherent change, verify, then repeat.
- Define blocking behavior clearly: stop only when no meaningful path remains, then report attempts, evidence, current blocker, and the exact missing info, credentials, permissions, files, or decisions needed.
- Do not include Markdown fences around the final command unless the user asks for a code block.
- Do not add prefaces such as "下面是" or explanations after the command.

## Quality Bar

The command should be detailed enough that a fresh Codex instance can run it without reconstructing intent from the old conversation. Prefer one precise, longer command over a vague short one.

## Example

User request:

```text
把当前还没完成的登录页需求整理成一个 Goal 命令。
```

Output:

```text
/goal达成完成当前会话中尚未完全落地的登录页需求，包括表单交互、错误状态、响应式布局和已提到但未验证的视觉细节，并通过相关测试通过、页面在目标视口截图正常、关键登录流程可手动走通、以及最终 diff 仅包含必要改动来确认结果有效，同时保持既有路由、认证接口契约、设计系统约束和用户未授权的文件不被破坏。只能使用当前仓库、当前会话已提供的需求、项目内已有工具链、必要的本地命令和非破坏性文件编辑；不得重置或覆盖用户已有改动。在每一轮迭代之间，Codex 需要根据当前最高风险缺口、失败证据、未验证需求和最小可验证改动来选择下一步。如果遇到阻塞，或者已经没有有效路径可以继续尝试，Codex 必须停止，并报告已经尝试过的方法、已获得的测试或运行证据、当前阻塞点，以及还需要什么信息、权限、依赖、凭据或产品决策才能继续推进。
```
