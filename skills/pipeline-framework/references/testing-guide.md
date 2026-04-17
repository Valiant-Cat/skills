# Testing Guide

## Purpose

`pipeline-framework` 应提供一套最小但稳定的测试骨架，确保不同业务 skill 在复用框架时能够验证关键运行行为。

## Minimum Test Set

建议至少覆盖：

### 1. Capability Probe

验证：

- 默认 capability 状态
- `PROVIDER / STATUS` override
- 缺 capability 时的默认行为

### 2. Provider Registry

验证：

- `stage -> capability` 映射
- ready provider 的正常选择
- 缺 capability 时的阻断
- `dev-mock` 模式下 `mock` 的特殊行为

### 3. Adapter Runtime

验证：

- builtin provider 可正常生成产物
- cli provider 能实际执行外部命令
- 缺输入时正确失败
- adapter 只写 staging，不直接写正式 outputs

### 4. Pipeline Runner

验证：

- 阶段按顺序执行
- 正常模式下 response bundle 不能直接视为完成执行
- `allow_seed` 打开时可通过 seed import 合法导入阶段结果
- 某阶段失败时整条流水线阻断
- 成功阶段后 framework 会写 state / provenance / commit manifest
- 已 `COMMITTED` 阶段的正式产物被篡改时，下游会被阻断
- 缺 provenance 或缺 commit manifest 时，下游会被阻断
- 未 `COMMITTED` 阶段的声明式输出如果提前出现在 `outputs/`，framework 会在运行前阻断

## Testing Principle

- 优先测试框架行为，而不是业务文案内容
- 对同类业务 skill 复用相同测试模式
- 每个框架级能力至少有一条正向测试和一条阻断测试

## Current Framework Test Files

当前 `pipeline-framework` 已落地的最小测试骨架：

- `tests/test_capability_core.py`
- `tests/test_provider_core.py`
- `tests/test_runner_core.py`

starter consumer 测试模板位于：

- `assets/starter/tests/test_run_skill.py`
- `assets/starter/tests/test_run_pipeline.py`

这些测试覆盖：

- capability 默认值与 override 合成
- provider 选择与 `dev-mock` 语义
- runtime metadata 写入
- skill launcher 执行骨架
- stage request 生成
- pipeline stage loop 与输出校验

## Suggested Commands

单独运行 framework 测试：

```bash
python3 -m unittest discover skills/pipeline-framework/tests
```

以 consumer skill 回归验证 framework 集成：

```bash
python3 -m unittest discover skills/idea-to-prd/tests
```
