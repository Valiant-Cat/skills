# Example Pipeline

这是一个用于验证 `pipeline-framework` 可复用性的最小业务流水线。

阶段顺序：

1. `seed-note`
2. `publish-note`

产物：

- `seed-note.json`
- `seed-note.md`
- `publish-note.json`
- `publish-note.md`

设计目标：

- 尽量少的业务复杂度
- 尽量完整地覆盖 framework 接入边界
- 能独立运行并通过测试
