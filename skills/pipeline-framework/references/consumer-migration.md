# Consumer Migration Guide

## Purpose

这份指南用于把一个新的业务 skill 接入 `pipeline-framework`，并复用当前已经抽出的 runtime、bridge、runner 与测试骨架。

## Recommended File Layout

业务 skill 至少建议具备：

```text
skills/<business-skill>/
  SKILL.md
  references/
    pipeline.md
  assets/
    templates/
  scripts/
    pipeline_spec.py
    run_skill.py
    run_pipeline.py
    runtime/
      runtime_config.py
      provider_registry.py
      capability_probe.py
    adapters/
      common.py
      <business adapters>
    bridges/
      base.py
  tests/
    test_run_skill.py
    test_run_pipeline.py
```

## Fastest Starting Point

直接复制：

- `assets/starter/scripts/`
- `assets/starter/tests/`

然后按业务改这些内容：

1. `scripts/pipeline_spec.py`
   - 改 `STAGE_ORDER`
   - 改 `STAGE_INPUTS`
   - 改 `STAGE_OUTPUTS`
   - 改 `ADAPTERS`

2. `scripts/runtime/provider_registry.py`
   - 改 `STAGE_TO_CAPABILITY`

3. `scripts/runtime/capability_probe.py`
   - 改 defaults
   - 改 capability 前缀
   - 改哪些阶段默认 `builtin`

4. `scripts/run_skill.py`
   - 改 skill 描述
   - 改 blocked report 文件名

5. `scripts/adapters/`
   - 实现真实业务 adapter

## Migration Steps

### 1. 先跑 builtin 闭环

至少先让：

- 第一阶段可 `builtin`
- 最后一阶段可 `builtin`

这样能先验证 pipeline skeleton。

### 2. 再接中间 provider

中间阶段优先按正式顺序接：

`skill -> mcp -> cli -> builtin`

### 3. 最后补回归测试

最少保留：

- `test_run_skill.py`
- `test_run_pipeline.py`

如果业务 skill 有自己的 runtime 包装，建议再加：

- `test_provider_registry.py`
- `test_capability_probe.py`

## Current Reference Consumer

当前仓库中有两个可参考 consumer：

- `idea-to-prd`
- `examples/example-pipeline-consumer`

建议优先看：

- `examples/example-pipeline-consumer`
  结构最小，适合先理解 framework 接入方式
- `idea-to-prd`
  业务更完整，适合参考真实多阶段流水线的实现边界
