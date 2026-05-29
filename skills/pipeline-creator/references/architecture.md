# Generated Workflow Architecture

`pipeline-creator` 生成的工作流 Skill 会包含 `references/architecture.md`。该文件用于把流水线架构里的稳定概念迁移成工作流契约，并配套一个可运行的 starter runtime。

## Runner

Runner 是 Agent 执行工作流时的编排角色。它负责按阶段顺序推进、检查输入、调用阶段 Adapter 的说明、处理阻塞，并在完成后汇总产物和验证结果。

## Adapter

Adapter 是阶段转换单元。它说明一个阶段如何把输入转成输出，可以对应人工整理、CLI、MCP、API、脚本或模型调用。生成物会生成可执行的 starter adapter，默认产出模板化 dev-mock 结果；业务化时替换生成 Skill 自己的 `scripts/adapters/`，不要改通用 runtime。

## Input

Input Contract 要求每个输入都有来源，缺失输入必须阻塞，事实、假设和待确认信息必须分开记录。

## Output

Output Contract 要求每个输出对应阶段目标和验收项，能够被下游阶段引用，并记录变更影响。

## Failure Semantics

生成的 architecture reference 默认包含 `missing-input`、`contract-conflict`、`validation-failed` 和 `external-blocked` 四类失败语义，帮助 Agent 稳定汇报阻塞原因。

## Script Modules

`pipeline-creator` 自身的 `assets/starter/scripts/` 保存这些通用脚本模板。生成器会把 starter 中的模板实例化到新工作流 Skill 的 `scripts/` 目录。

生成的工作流 Skill 会包含这些脚本模块：

- `scripts/workflow_contract.py`
  固化 `STAGES`、`REQUIRED_REFERENCES`、阶段输入、阶段输出和模板路径。
- `scripts/validate_workflow.py`
  读取 contract module，检查必备文件、架构章节、阶段输出、模板和禁用依赖文本。
- `scripts/run_skill.py`
  面向 Agent 的入口，支持 capability check 和 dev-mock starter 执行。
- `scripts/run_pipeline.py`
  按 stage registry 执行阶段 adapter、validator 和产物提交。
- `scripts/workflow_runtime/`
  通用 runner、adapter helper、provider selection、state、validation、commit 和 provenance 支持。

这些脚本让新 Skill 先具备可验证的 starter 闭环。业务化时应修改生成 Skill 自己的 adapters、validators 和 templates。
