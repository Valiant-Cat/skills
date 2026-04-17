# Provider Contract

## Formal Provider Priority

正常执行模式下，正式 provider priority 统一为：

`skill -> mcp -> cli -> builtin`

说明：

- `mock` 不属于正式 provider priority
- `mock` 只在 `dev-mock` 模式并显式开启 `allow_mock` 时生效

## Capability Override

能力探测层只识别显式 override，不会从 CLI 执行命令自动推断 capability 状态。

每个阶段可通过环境变量显式声明：

- `<PREFIX>_PROVIDER`
- `<PREFIX>_STATUS`

其中：

- `PROVIDER` 用于声明当前阶段走哪类 provider
- `STATUS` 用于声明当前 capability 状态

常见值：

- `PROVIDER`
  - `skill`
  - `mcp`
  - `cli`
  - `builtin`
- `STATUS`
  - `ready`
  - `missing`
  - `misconfigured`

## CLI Provider

当 `PROVIDER=cli` 时，还需要额外提供对应的 CLI 执行命令：

- `<PREFIX>_CLI_CMD`

示例：

```bash
export EXAMPLE_STAGE_PROVIDER=cli
export EXAMPLE_STAGE_STATUS=ready
export EXAMPLE_STAGE_CLI_CMD='<provider-cli-command>'
```

说明：

- 只设置 `PROVIDER` / `STATUS` 只能让 preflight 通过，不能替代真正的执行入口
- 只设置 `CLI_CMD` 不会让 capability probe 自动变成 `ready`
- `builtin` 表示框架或业务 skill 内置实现
