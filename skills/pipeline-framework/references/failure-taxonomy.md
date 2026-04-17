# Failure Taxonomy

## Purpose

`pipeline-framework` 需要让不同业务流水线共享一致的失败语义，避免同类问题在不同 skill 中表现不一致。

## Runtime-Level Failures

- `missing-capability`
  需要的 capability 不存在或未声明为可用
- `provider-misconfigured`
  provider 已声明，但配置不完整或状态错误
- `bridge-not-implemented`
  provider 已选中，但没有实际执行实现
- `unsupported-runtime`
  当前 runtime mode 不支持该路径

## Stage-Level Failures

- `missing-input`
  阶段要求的输入产物不存在
- `missing-output`
  阶段成功返回，但实际产物未生成
- `response-invalid`
  adapter 返回了 JSON，但结构不满足最小 response 契约
- `repair-failed`
  framework 已尝试一次受控自修复，但缺失产物仍未恢复
- `contract-violation`
  request / response 或产物结构不符合约定
- `adapter-failure`
  adapter 内部执行失败，且不属于更具体的失败类型

## Usage Rules

- 失败必须显式暴露，不允许静默 fallback
- 正常模式下 capability 缺失应立即阻断
- `mock` 只能在特定 runtime mode 下启用
- 同一类失败应尽量复用统一 failure type，而不是发明业务私有名字
- 自修复只允许修结构或重试一次，不允许静默伪造成功
