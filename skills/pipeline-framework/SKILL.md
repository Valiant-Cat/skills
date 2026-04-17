---
name: pipeline-framework
description: Use when 需要为一个多阶段任务建立或复用统一流水线框架，且任务包含固定阶段顺序、provider 选择、adapter 执行、失败阻断、runtime 模式或标准 request/response 契约。
---

# Pipeline Framework

`pipeline-framework` 是一个用于定义、运行和复用多阶段流水线的基础框架 skill。  
它不关心具体业务领域，只关心流水线本身如何组织、如何执行、如何选择 provider、如何处理失败，以及如何让不同业务 skill 的运行方式保持一致。

它适用于这类场景：

- 需要把一个复杂任务拆成多个固定阶段
- 每个阶段都有输入、输出和验收条件
- 每个阶段可能通过 `skill`、`mcp`、`cli` 或 `builtin` 执行
- 需要统一 runtime mode、provider priority、adapter contract 和 failure taxonomy
- 需要让多个业务 skill 共用同一套流水线机制

## Quick Reference

框架层负责：

- pipeline spec
- runtime mode
- provider priority
- capability probe
- provider registry
- adapter request / response contract
- bridge / cli / builtin execution
- failure taxonomy
- pipeline-level tests

框架层不负责：

- 业务阶段命名
- 业务模板内容
- 业务字段定义
- 业务验收规则
- 业务报告正文

主要参考文档：

- `references/framework-overview.md`
- `references/pipeline-spec.md`
- `references/provider-contract.md`
- `references/failure-taxonomy.md`
- `references/runtime-modes.md`
- `references/testing-guide.md`
- `references/consumer-migration.md`

## Core Contract

正式 provider priority：

`skill -> mcp -> cli -> builtin`

特殊模式：

- `mock` 仅在 `dev-mock + allow_mock` 时生效
- `check-only` 仅做 capability probe，不进入阶段执行

统一执行语义：

- 每个阶段有固定 `stage id`
- 每个阶段都有 request bundle
- 每个阶段都返回 response bundle
- 阶段失败要显式阻断，不允许静默降级

## What Business Skills Keep

业务 skill 应该保留：

- `STAGE_ORDER`
- `STAGE_INPUTS`
- `STAGE_OUTPUTS`
- 业务 adapter
- 模板
- 业务校验规则
- 业务文档

## What Framework Provides

框架 skill 提供：

- runner skeleton
- runtime config
- capability probe
- provider registry
- adapter common helpers
- bridge base
- failure taxonomy
- test scaffolding

当前代码骨架位于：

- `scripts/framework/runtime/`
- `scripts/framework/adapters/`
- `scripts/framework/bridges/`
- `scripts/framework/runner/`

starter consumer 模板位于：

- `assets/starter/scripts/`
- `assets/starter/tests/`

当前真实 consumer：

- `../idea-to-prd/`
- `examples/example-pipeline-consumer/`
