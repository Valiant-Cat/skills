---
name: example-pipeline-consumer
description: Use when 需要查看一个基于 pipeline-framework 搭建的最小业务流水线 consumer 示例，以便复制目录结构、脚本入口、adapter 实现和测试骨架。
---

# Example Pipeline Consumer

`example-pipeline-consumer` 是一个最小可运行的 `pipeline-framework` consumer，用于演示业务 skill 如何复用 framework 的 runtime、runner、bridge 与测试骨架。

它不追求真实业务价值，重点是提供一个可运行、可测试、可复制的参考实现。

## Quick Reference

- 阶段顺序：`seed-note -> publish-note`
- 主要入口：`scripts/run_skill.py`
- pipeline spec：`scripts/pipeline_spec.py`
- 测试目录：`tests/`

## References

- `references/pipeline.md`
- `../../references/consumer-migration.md`
