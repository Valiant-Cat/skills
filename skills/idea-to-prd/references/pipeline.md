# Idea To PRD Pipeline

`idea-to-prd` 是一条将产品想法系统化沉淀为正式 PRD 的产品定义流水线。它的职责不是直接做设计或开发，而是输出一组可追溯、可复核、可继续流转的产品定义产物，供后续设计与研发阶段直接消费。

这条流水线的执行脚本位于 `skills/idea-to-prd/scripts/`，用于保持 skill 定义、模板和执行逻辑处于同一独立目录边界内。

## Stage Order

1. `idea-brief`
2. `market-research`
3. `competitor-analysis`
4. `prd-generation`

## Framework Rules

这条业务流水线复用 [pipeline-framework 概览](../../pipeline-framework/references/framework-overview.md) 的通用执行机制。

涉及通用运行规则时，优先读取：

- [provider-contract.md](../../pipeline-framework/references/provider-contract.md)
- [runtime-modes.md](../../pipeline-framework/references/runtime-modes.md)
- [failure-taxonomy.md](../../pipeline-framework/references/failure-taxonomy.md)
- [pipeline-spec.md](../../pipeline-framework/references/pipeline-spec.md)

`idea-to-prd` 只在这里补充该业务流水线自身的常见配置组合和阶段定义。

## Common Configurations

## Operator Gate

所有正式执行都先经过同一个门禁：

```bash
python3 skills/idea-to-prd/scripts/run_skill.py <run_dir> --check-only --strict-check
```

放行规则：

- 返回 `0`：关键 capability 已就绪，可以继续正式执行
- 返回非 `0`：必须先补齐 provider、seed 或 response bundle，禁止把聊天内容当成正式阶段结果

推荐执行路径：

1. `strict-check -> codex-session`
   - 适用于中间阶段已接入 `skill` / `mcp` / `cli` / `builtin`
2. `strict-check -> --allow-seed`
   - 适用于中间阶段结果先由外部系统、人工调研或上游流程产出，再由 framework 接管 provenance 与 commit
3. `check-only -> dev-mock --allow-mock`
   - 仅用于联调 adapter、runner 和状态机；不属于正式交付路径，默认不会通过 strict preflight

### 1. 最小 builtin + response bundle 组合

适用场景：

- 只想先跑通首尾阶段
- 中间两段由外部预制结果提供

特点：

- `idea-brief` 和 `prd-generation` 默认走 `builtin`
- `market-research` / `competitor-analysis` 通过 `.dispatch/*-response.json` 提供结果

示例：

```bash
python3 skills/idea-to-prd/scripts/run_skill.py <run_dir> --check-only --strict-check
python3 skills/idea-to-prd/scripts/run_skill.py <run_dir> --mode codex-session --allow-seed
```

### 2. 市场调研走 CLI，竞品分析走 response bundle

适用场景：

- 已有市场调研 CLI
- 竞品分析结果先由人工或上游系统产出

示例：

```bash
python3 skills/idea-to-prd/scripts/run_skill.py <run_dir> --check-only --strict-check

export IDEA_TO_PRD_MARKET_RESEARCH_PROVIDER=cli
export IDEA_TO_PRD_MARKET_RESEARCH_STATUS=ready
export IDEA_TO_PRD_MARKET_RESEARCH_CLI_CMD='<market-research-cli-command>'
```

### 3. 市场调研和竞品分析都走 CLI

适用场景：

- 两个中间阶段都已经接入外部命令
- 希望整条流水线在正常模式下独立跑通

示例：

```bash
python3 skills/idea-to-prd/scripts/run_skill.py <run_dir> --check-only --strict-check

export IDEA_TO_PRD_MARKET_RESEARCH_PROVIDER=cli
export IDEA_TO_PRD_MARKET_RESEARCH_STATUS=ready
export IDEA_TO_PRD_MARKET_RESEARCH_CLI_CMD='<market-research-cli-command>'

export IDEA_TO_PRD_COMPETITOR_ANALYSIS_PROVIDER=cli
export IDEA_TO_PRD_COMPETITOR_ANALYSIS_STATUS=ready
export IDEA_TO_PRD_COMPETITOR_ANALYSIS_CLI_CMD='<competitor-analysis-cli-command>'
```

### 4. dev-mock 联调模式

适用场景：

- 调 adapter、runner、状态机
- 验证产物路径和阶段串联

示例：

```bash
python3 skills/idea-to-prd/scripts/run_skill.py <run_dir> --mode dev-mock --allow-mock
```

说明：

- 该模式只用于开发和测试
- `mock` 不会参与正常模式下的 provider 选择

## Stage Summary

| Stage | 中文名 | 目标 | 主要输入 | 主要输出 | Adapter |
| --- | --- | --- | --- | --- | --- |
| `idea-brief` | 需求梳理 | 把模糊 idea 收敛成结构化 brief | 用户原始需求、平台、地域、约束、目标 | `idea-brief.json`、`idea-brief.md` | `idea_brief_adapter.py` |
| `market-research` | 市场调研 | 形成市场判断、商业模式和机会窗口 | `idea-brief.json` | `market-research.json`、`market-research.md` | `market_research_adapter.py` |
| `competitor-analysis` | 竞品分析 | 识别竞品、抽取借鉴点和切入空间 | `idea-brief.json`、`market-research.json` | `competitor-analysis.json`、`competitor-analysis.md` | `competitor_analysis_adapter.py` |
| `prd-generation` | PRD 生成 | 把研究结论转成可执行 PRD | `idea-brief.json`、`market-research.json`、`competitor-analysis.json` | `prd.json`、`prd.md` | `prd_generation_adapter.py` |

## Stage Details

### 1. `idea-brief`

中文名：需求梳理

目标：

- 把用户给出的模糊想法、需求方向或机会判断整理成统一的结构化 brief
- 明确后续调研和 PRD 生成所需的边界、约束与待确认事项

输入：

- 用户原始需求
- 产品方向
- 平台范围
- 地域范围
- 成功指标
- 已知约束
- 不做项

输出：

- `idea-brief.json`
- `idea-brief.md`

最低验收标准：

- 目标用户明确
- 核心场景明确
- 平台与地域范围明确
- 约束、不做项、假设项明确
- 待确认问题显式列出

建议字段：

```json
{
  "product_name": "string",
  "problem_statement": "string",
  "target_users": ["string"],
  "core_scenarios": ["string"],
  "platforms": ["ios", "android", "web"],
  "geographies": ["US"],
  "constraints": ["string"],
  "success_metrics": ["string"],
  "out_of_scope": ["string"],
  "assumptions": ["string"],
  "open_questions": ["string"]
}
```

### 2. `market-research`

中文名：市场调研

目标：

- 判断这个方向是否存在明确市场需求
- 识别赛道成熟度、用户问题、商业模式与机会窗口

输入：

- `idea-brief.json`

输出：

- `market-research.json`
- `market-research.md`

最低验收标准：

- 包含市场判断
- 包含机会与风险
- 包含证据表
- 每条高风险结论有来源、日期、市场范围
- 包含对 PRD 的直接输入建议

建议字段：

```json
{
  "market_exists": true,
  "market_maturity": "high|medium|low",
  "user_need_strength": "high|medium|low",
  "business_models": ["subscription", "freemium"],
  "opportunities": ["string"],
  "risks": ["string"],
  "evidence": [
    {
      "id": "E1",
      "claim": "string",
      "source": "string",
      "captured_at": "2026-04-16",
      "market": "US",
      "time_range": "2025-Q4 to 2026-Q1",
      "confidence": "high|medium|low"
    }
  ],
  "evidence_gaps": ["string"]
}
```

### 3. `competitor-analysis`

中文名：竞品分析

目标：

- 找到核心竞品和替代竞品
- 输出对比、借鉴、规避和切入建议

输入：

- `idea-brief.json`
- `market-research.json`

输出：

- `competitor-analysis.json`
- `competitor-analysis.md`

最低验收标准：

- 至少 3 个竞品
- 成熟赛道优先 5 个以上
- 有对比矩阵
- 有借鉴项与规避项
- 每个核心竞品有来源和日期
- 有对 PRD 的直接建议

建议字段：

```json
{
  "competitors": [
    {
      "name": "string",
      "tier": "core|secondary",
      "positioning": "string",
      "target_users": ["string"],
      "platforms": ["ios", "android"],
      "pricing": "string",
      "strengths": ["string"],
      "weaknesses": ["string"],
      "complaints": ["string"],
      "feature_gaps": ["string"],
      "sources": [
        {
          "type": "official|review|store|article",
          "url_or_ref": "string",
          "captured_at": "2026-04-16"
        }
      ]
    }
  ],
  "common_patterns": ["string"],
  "differentiators": ["string"],
  "borrow_list": ["string"],
  "avoid_list": ["string"],
  "mvp_recommendations": ["string"]
}
```

### 4. `prd-generation`

中文名：PRD 生成

目标：

- 严格基于上游证据生成 PRD
- 不允许脱离 `idea-brief`、`market-research`、`competitor-analysis` 重新发明结论

输入：

- `idea-brief.json`
- `market-research.json`
- `competitor-analysis.json`

输出：

- `prd.json`
- `prd.md`

最低验收标准：

- 每个 P0/P1 功能有验收标准
- 有异常/边界处理
- 有待确认事项
- 有来源摘要
- 与市场调研、竞品分析结论不冲突

建议字段：

```json
{
  "product_name": "string",
  "goals": ["string"],
  "target_users": ["string"],
  "core_scenarios": ["string"],
  "positioning": "string",
  "mvp_scope": {
    "in_scope": ["string"],
    "out_of_scope": ["string"]
  },
  "features": [
    {
      "module": "string",
      "name": "string",
      "priority": "P0|P1|P2",
      "user_value": "string",
      "preconditions": ["string"],
      "acceptance_criteria": ["string"],
      "edge_cases": ["string"],
      "dependencies": ["string"]
    }
  ],
  "non_functional_requirements": ["string"],
  "risks": ["string"],
  "open_questions": ["string"],
  "source_summary": ["E1", "E2", "competitor:A"]
}
```

## Request Contract

每个阶段都使用统一 request 结构：

```json
{
  "stage": "market-research",
  "run_dir": "<run-dir>",
  "inputs": ["idea-brief.json"],
  "outputs": ["market-research.json", "market-research.md"],
  "context": {
    "product_name": "Example",
    "platforms": ["ios", "android"],
    "geographies": ["US"],
    "time_window": {
      "start": "2025-01-01",
      "end": "2026-04-16"
    },
    "analysis_focus": [
      "market maturity",
      "user pain points",
      "monetization"
    ]
  }
}
```

## Response Contract

```json
{
  "ok": true,
  "stage": "market-research",
  "tool": "market-research",
  "provider": "skill",
  "created": ["market-research.json", "market-research.md"],
  "updated": [],
  "sources": ["sensortower", "official-sites"],
  "notes": "Generated market research pack.",
  "retryable": false,
  "confidence": "medium"
}
```

## Failure Types

运行时错误：

- `missing-capability`
- `provider-misconfigured`
- `unsupported-runtime`
- `bridge-not-implemented`

阶段执行错误：

- `missing-input`
- `missing-output`
- `adapter-failure`
- `evidence-insufficient`
- `contract-violation`
- `schema-failure`

## Validation Rules

### `idea-brief`

- 必填字段完整
- 假设与待确认项不能缺失

### `market-research`

- 必须包含证据表
- 必须记录来源、日期、市场范围
- 必须输出机会与风险

### `competitor-analysis`

- 必须包含竞品清单和对比矩阵
- 核心竞品必须带来源信息
- 必须输出借鉴项和规避项

### `prd-generation`

- P0/P1 功能必须有验收标准
- 必须写边界和异常处理
- 必须写待确认事项
- 必须带来源摘要

## MVP Execution Path

第一版先实现最小闭环：

- `idea-brief`: `skill` / `builtin`
- `market-research`: `skill` / `cli`
- `competitor-analysis`: `skill` / `cli`
- `prd-generation`: `builtin` / `skill`

后续再逐步接入 `mcp` 和更多 provider。

## Position In Larger Orchestrator

`idea-to-prd` 是更大产品交付流程里的产品定义阶段：

```text
idea-to-prd
  -> quality-gate
  -> visual-implementation
  -> logic-implementation
  -> validation
```

它的职责到 `prd.*` 为止，不负责设计稿生成和代码实现。
