---
name: idea-to-prd
description: Use when 需要把一个模糊产品想法、需求方向或机会判断系统化沉淀为正式 PRD，并在此之前完成需求梳理、市场调研和竞品分析，产出可供后续设计与研发直接消费的标准化产品定义结果。
---

# Idea To PRD

`idea-to-prd` 是一条将产品想法系统化沉淀为正式 PRD 的产品定义流水线，负责完成需求梳理、市场调研、竞品分析和 PRD 生成，并输出可供后续设计与研发直接消费的标准产物。

这条流水线的目标不是产出零散结论，而是形成一套可追溯、可复核、可继续流转的产品定义结果，包括：

- `idea-brief.json` / `idea-brief.md`
- `market-research.json` / `market-research.md`
- `competitor-analysis.json` / `competitor-analysis.md`
- `prd.json` / `prd.md`

它适用于用户只有一个模糊想法、方向或机会判断，但尚未形成可执行产品定义的场景。通过固定阶段和标准产物，`idea-to-prd` 可以把模糊输入逐步收敛为后续设计、研发和验证阶段可直接消费的正式输入。

如果需要查看这条流水线的正式阶段定义，读取 `references/pipeline.md`。

如果需要查看通用流水线契约，读取 [pipeline-framework](../pipeline-framework/SKILL.md) 及其参考文档，尤其是：

- [provider-contract.md](../pipeline-framework/references/provider-contract.md)
- [runtime-modes.md](../pipeline-framework/references/runtime-modes.md)
- [failure-taxonomy.md](../pipeline-framework/references/failure-taxonomy.md)

`idea-to-prd` 复用该框架的正式 provider priority：

- `skill -> mcp -> cli -> builtin`

## Quick Reference

核心阶段：

- `idea-brief`
- `market-research`
- `competitor-analysis`
- `prd-generation`

核心产物：

- `idea-brief.json` / `idea-brief.md`
- `market-research.json` / `market-research.md`
- `competitor-analysis.json` / `competitor-analysis.md`
- `prd.json` / `prd.md`

主要入口：

- `scripts/run_skill.py`
- `scripts/run_pipeline.py`
- `references/pipeline.md`

## Quick Start

只做 capability probe：

```bash
python3 skills/idea-to-prd/scripts/run_skill.py <run_dir> --check-only
```

执行阻断式预检：

```bash
python3 skills/idea-to-prd/scripts/run_skill.py <run_dir> --check-only --strict-check
```

正常执行整条流水线：

```bash
python3 skills/idea-to-prd/scripts/run_skill.py <run_dir> --mode codex-session
```

开发模式允许 mock：

```bash
python3 skills/idea-to-prd/scripts/run_skill.py <run_dir> --mode dev-mock --allow-mock
```

## 强制执行协议

- 当 Agent 已进入 `idea-to-prd` 执行时，第一条实操命令必须是 `python3 skills/idea-to-prd/scripts/run_skill.py <run_dir> --check-only --strict-check`
- `--strict-check` 未通过时，不得输出任何“阶段已完成”或“PRD 已生成”的结论；只能继续补齐 provider、seed 或 response bundle
- `dev-mock` 仅用于本地联调，不属于正式交付路径；联调时可以使用普通 `--check-only` 或直接运行 `--mode dev-mock --allow-mock`
- `brainstorming` 只能作为 `idea-brief` 阶段内部的需求收敛方法，不能替代流水线入口和阶段落盘
- `idea-brief.*`、`market-research.*`、`competitor-analysis.*`、`prd.*` 未写入 `run_dir` 的正式产物路径时，视为该阶段未完成

## 边界说明

- 本 skill 保证的是进入本 skill 之后的 runtime contract 与阶段落盘契约。
- 本 skill 不单独保证平台级 prompt routing 一定先选择本 skill。
- 若需要验证提示词触发层，应使用本 skill 自带的 prompt regression 验证脚本与样例。

## 何时使用

在这些场景触发本 skill：

- 用户只有一个方向、概念或粗需求，需要先落成正式 PRD
- 需要在写设计稿或开始开发前，先做市场调研和竞品分析
- 需要把“需求 -> 研究 -> 结论 -> PRD”收束成一套固定产物
- 需要为后续 `quality-gate`、`visual-implementation`、`logic-implementation` 提供上游输入

不适用场景：

- 用户已经给出完整 PRD，只需要补 UI 或补代码
- 任务是纯技术实现，没有产品定义或市场分析需求

## 固定产物

本 skill 的标准输出是 4 份核心产物：

- `idea-brief.json` / `idea-brief.md`
- `market-research.json` / `market-research.md`
- `competitor-analysis.json` / `competitor-analysis.md`
- `prd.json` / `prd.md`

默认优先把文件写到当前工作目录。若用户指定了输出目录，则以用户要求为准。

模板路径：

- `assets/templates/idea-brief.md`
- `assets/templates/market-research.md`
- `assets/templates/competitor-analysis.md`
- `assets/templates/prd.md`

## 输出契约

四份核心产物是后续设计与研发的正式输入，不是随手总结。默认要求如下：

- `idea-brief.*`
  必须包含目标用户、核心场景、平台范围、地域范围、约束、成功指标、假设与待确认项
- `market-research.*`
  必须包含调研范围、时间窗口、适用市场、核心证据、机会判断、风险判断
- `competitor-analysis.*`
  必须包含竞品清单、对比维度、借鉴项、规避项、切入建议
- `prd.*`
  必须包含目标用户、核心流程、功能需求、功能级验收标准、边界条件、非功能要求

如果某项信息缺失：

- 先查资料或补充分析
- 仍无法确认时，明确标记为“待确认”
- 不得把假设写成事实

## 执行顺序

### 1. 收敛需求边界

先用最少的问题明确这些信息；若用户没有给全，则做合理假设并在文档中显式记录：

- 产品名称或暂定代号
- 目标用户
- 使用场景
- 平台范围
- 地域范围
- 成功指标
- 明确不做的范围

如果任务仍然高度模糊，不要空转讨论，直接在文档里增加“假设与边界”小节。

这一步的结果必须落到 `idea-brief.md`，并建议同时生成 `idea-brief.json` 供后续阶段消费。

### 2. 做市场调研

目标是回答这几个问题：

- 这个方向是否已有成熟市场
- 用户当前主要通过什么产品解决问题
- 该赛道的主流商业模式是什么
- 是否存在明显供给缺口或体验缺口

调研输出必须落到 `market-research.md`，不要只在对话里给摘要；建议同时生成 `market-research.json`。

### 3. 做竞品分析

至少分析 3 个竞品；如果是成熟赛道，优先给出 5 到 10 个，再抽取核心对比。

竞品分析至少覆盖：

- 定位与目标用户
- 核心功能
- 用户价值主张
- 差评/痛点/抱怨
- 缺失功能或用户请求
- 商业模式
- 可以借鉴的点
- 应避免复制的点

结果写入 `competitor-analysis.md`。

### 4. 归纳机会点

在调研和竞品分析基础上，输出：

- 赛道判断
- 机会窗口
- 差异化切入点
- MVP 范围建议
- 风险与不确定性

这些结论既要写进 `market-research.md`，也要体现在 `prd.md` 的产品目标与范围定义中。

### 5. 写 PRD

`prd.md` 至少包含这些部分：

- 背景与问题定义
- 用户画像
- 目标与成功指标
- 产品定位
- 核心使用流程
- 功能需求列表
- 非功能要求
- 范围边界
- 风险与依赖
- 里程碑或 MVP 切分

PRD 必须可直接作为下游设计或研发输入，避免停留在空泛描述。

每个核心功能至少写清楚：

- 用户价值
- 优先级
- 前置条件
- 触发条件
- 验收标准
- 异常或边界处理

## 工具选择规则

- 移动应用、App Store、Google Play 相关调研：优先使用 `sensortower-research`
- 需要最新公开信息、新闻、官网功能说明、定价或产品更新：优先查官方来源和一手资料
- 高风险结论必须注明来源窗口、时间范围和适用市场

如果没有足够外部数据：

- 明确说明证据不足
- 区分“事实”“推断”“建议”
- 不要把推测写成确定结论

## 写作规则

- 所有输出使用中文，除非用户明确要求其他语言
- 先给证据，再给判断
- 所有关键结论都要能回溯到调研或竞品分析
- 使用具体标题，避免“其他”“杂项”“补充说明”这类低信息密度命名
- 如果做了假设，单独列出“假设与边界”
- 高风险判断要写明来源、日期、市场范围和置信度
- 若引用竞品差评、功能更新或价格信息，标明抓取时间或版本窗口
- 同一结论若来自多个来源，优先合并为证据表而不是散落在正文里

## 完成前自检

交付前逐项检查：

- `idea-brief.*` 是否已经把需求边界、假设和待确认事项收敛清楚
- `market-research.*` 是否回答了市场是否值得做
- `competitor-analysis.md` 是否给出了清晰的借鉴点与规避点
- `prd.md` 是否能直接交给设计或研发继续推进
- 三份文档是否对同一产品定位保持一致
- 是否把不确定项与假设项显式写出
- 是否给所有高风险判断补了来源、日期和市场范围
- 功能需求是否带有明确验收标准，而不是只有功能名
- 竞品数量是否与赛道成熟度匹配，而不是机械停在 3 个
