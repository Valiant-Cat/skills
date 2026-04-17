# Pipeline Spec Contract

## Purpose

业务 skill 使用 `pipeline-framework` 时，至少需要提供一份明确的 pipeline spec，用来声明这条流水线的阶段顺序、输入输出和 adapter 映射关系。

## Required Definitions

一条业务流水线至少应定义：

- `STAGE_ORDER`
- `STAGE_INPUTS`
- `STAGE_OUTPUTS`
- `ADAPTERS`
- `adapter_paths(...)`

建议形态：

```python
STAGE_ORDER = [
    "stage-a",
    "stage-b",
    "stage-c",
]

STAGE_INPUTS = {
    "stage-a": [],
    "stage-b": ["a.json"],
    "stage-c": ["b.json"],
}

STAGE_OUTPUTS = {
    "stage-a": ["a.json"],
    "stage-b": ["b.json"],
    "stage-c": ["c.json"],
}

ADAPTERS = {
    "stage-a": "stage_a_adapter.py",
    "stage-b": "stage_b_adapter.py",
    "stage-c": "stage_c_adapter.py",
}


def adapter_paths(script_root: Path) -> dict[str, Path]:
    adapter_dir = script_root / "adapters"
    return {stage: adapter_dir / ADAPTERS[stage] for stage in STAGE_ORDER}
```

建议把这部分单独放在业务 skill 的 `scripts/pipeline_spec.py` 中，由业务 `run_pipeline.py` 只负责加载 spec 并调用 framework runner。

如需快速起步，可直接参考：

- `assets/starter/scripts/pipeline_spec.py`

如需启用内容级强校验，业务 skill 还应补充：

- `VALIDATORS`
- `validator_paths(...)`

## Stage Rules

每个阶段都应满足：

- `stage id` 唯一且稳定
- 输入和输出显式列出
- adapter 有唯一映射
- 阶段失败时可明确定位到对应 `stage id`

## Request Bundle

每个阶段都使用统一 request 结构：

```json
{
  "stage": "market-research",
  "run_dir": "<run-dir>",
  "inputs": ["idea-brief.json"],
  "outputs": ["market-research.json", "market-research.md"],
  "context": {}
}
```

## Response Bundle

每个阶段都返回统一 response 结构：

```json
{
  "ok": true,
  "stage": "market-research",
  "tool": "market-research",
  "provider": "cli",
  "created": ["market-research.json", "market-research.md"],
  "updated": [],
  "notes": "Generated market research artifacts.",
  "retryable": false
}
```

## Validation Expectations

pipeline runner 至少应验证：

- request bundle 已生成
- 阶段返回的是合法 response
- response 中 `ok=false` 时立即阻断
- 阶段成功后其 staging 产物确实存在
- staging 产物通过内容 validator
- framework 已写入 commit manifest
- framework 已写入 provenance
- 下游阶段只消费 `COMMITTED` 上游阶段
