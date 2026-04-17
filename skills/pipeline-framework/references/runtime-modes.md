# Runtime Modes

## Supported Modes

`pipeline-framework` 当前统一支持 3 种运行模式：

| Mode | 说明 | 典型用途 |
| --- | --- | --- |
| `codex-session` | 默认模式，面向当前会话内可用能力和显式 provider 配置 | 正常执行业务流水线 |
| `terminal` | 面向终端环境执行，依赖显式 provider 配置和外部命令入口 | 在脱离会话能力时用 CLI 跑通 |
| `dev-mock` | 开发自测模式，仅在显式开启 `allow_mock` 时允许 mock provider 生效 | 骨架联调、测试状态机、验证 fallback |

## Common Flags

- `--check-only`
  只做 runtime config 构建与 capability probe，不进入阶段执行
- `--allow-mock`
  只对 `dev-mock` 模式有意义，不会改变正式 provider priority

## Behavior Rules

- 正常模式下 capability 缺失必须阻断
- `dev-mock` 模式下只有显式允许时才启用 `mock`
- `mock` 只用于开发和测试，不进入正式 provider 语义

