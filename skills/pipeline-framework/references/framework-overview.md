# Pipeline Framework Overview

## Purpose

`pipeline-framework` 的目标是把“多阶段任务如何运行”从具体业务 skill 中抽出来，形成一套可复用的执行框架。

它解决的问题不是“业务做什么”，而是：

- 阶段如何编排
- provider 如何选择
- request / response 如何统一
- 阶段失败如何阻断
- runtime mode 如何定义
- 业务 skill 如何共享同一套执行机制

## Scope

框架层覆盖：

- pipeline orchestration
- runtime model
- provider model
- adapter contract
- bridge execution model
- failure taxonomy
- verification hooks

框架层不覆盖：

- 业务模板
- 业务字段 schema
- 业务报告内容
- 业务验收规则
- 业务研究逻辑

## Layering

建议分成 3 层：

### 1. Framework Layer

职责：

- 定义通用 pipeline 运行模型
- 提供 `run_skill.py` / `run_pipeline.py` 可复用骨架
- 统一 `RuntimeConfig`
- 统一 capability report
- 统一 provider selection
- 统一 adapter helpers
- 统一 bridge behavior

当前已抽出的通用代码形态：

- `scripts/framework/runtime/runtime_config.py`
- `scripts/framework/runtime/provider_core.py`
- `scripts/framework/runtime/capability_core.py`
- `scripts/framework/adapters/common.py`
- `scripts/framework/bridges/base.py`
- `scripts/framework/runner/core.py`
- `scripts/framework/state/store.py`
- `scripts/framework/provenance/store.py`
- `scripts/framework/commit/core.py`
- `scripts/framework/validation/core.py`

其中 `runner/core.py` 当前已承载：

- runtime metadata 写入
- skill launcher 执行骨架
- pipeline script 调用
- stage request 写入
- stage loop 执行
- staging 验证与正式 commit
- provenance 写入
- `COMMITTED` 完整性校验
- blocked report 写入

当前 framework 已采用强约束执行模型：

- adapter / provider 只能写 `.framework/staging/<stage>/`
- framework 独占正式产物 commit 权
- 下游阶段只认上游 `COMMITTED`
- 合法 committed 产物必须同时具备：
  - stage state
  - provenance
  - commit manifest
- `outputs/` 只应出现已 `COMMITTED` 阶段的登记产物
- 声明式 stage outputs 如果出现在 `outputs/`，但其 producer stage 尚未 `COMMITTED`，framework 会直接阻断

### 2. Pipeline Spec Layer

职责：

- 声明这条业务流水线有哪些阶段
- 声明每阶段输入输出
- 声明 adapter 映射关系
- 声明可选校验器

典型内容：

- `STAGE_ORDER`
- `STAGE_INPUTS`
- `STAGE_OUTPUTS`
- `ADAPTERS`
- `adapter_paths(...)`

推荐在业务 skill 中独立放置：

- `scripts/pipeline_spec.py`

### 3. Business Layer

职责：

- 提供每个阶段的业务实现
- 提供模板
- 提供业务校验规则
- 定义产物内容与验收标准

## Suggested Migration Strategy

### Phase 1

先抽文档契约：

- framework overview
- provider contract
- failure taxonomy
- pipeline spec contract

### Phase 2

抽公共代码：

- runtime config
- provider registry
- capability probe
- bridge base
- adapter common

### Phase 3

让业务 skill 引用 framework：

- 保留自己的 pipeline spec
- 保留自己的 business adapters
- 保留自己的模板和校验规则

### Phase 4

将业务入口压薄为框架包装层：

- `run_skill.py` 只保留业务 probe 与 CLI 参数
- `run_pipeline.py` 只保留 pipeline spec 装配
- 具体执行循环由 framework runner 接管

## Success Criteria

如果抽象成功，应满足：

- 新业务流水线不需要重复实现 runtime / bridge / common
- provider 语义在不同 skill 中保持一致
- 同一类失败在不同 skill 中表现一致
- 业务 skill 只关注自己的阶段和产物
