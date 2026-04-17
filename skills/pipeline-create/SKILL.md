---
name: pipeline-create
description: Use when 需要根据用户给出的业务阶段、产物和约束，直接生成一个基于 pipeline-framework 的可运行流水线 skill，目录结构、运行入口与测试骨架对齐 idea-to-prd。
---

# Pipeline Create

`pipeline-create` 用来把用户的业务编排需求直接落成一个新的 `pipeline-framework` consumer skill。

它不是只给建议，也不是只生成一份说明文档。标准目标是产出一个可运行、可继续修改、可补充 provider 的业务 skill 目录，至少包含：

- `SKILL.md`
- `agents/openai.yaml`
- `references/pipeline.md`
- `assets/templates/`
- `scripts/`
- `tests/`

## 何时使用

在这些场景触发：

- 用户要新建一个和 `idea-to-prd` 同类型的流水线 skill
- 用户已经有明确阶段定义，想直接生成可运行骨架
- 用户需要把一条业务工作流接入 `pipeline-framework`

不适用场景：

- 只是想理解 `pipeline-framework` 如何工作
- 只是修改现有 consumer skill 的某个 stage

## 前置要求

- 目标工作区内必须已经有 `skills/pipeline-framework`
- 生成前先把需求收敛成正式 spec
- 不得静默编造业务事实；缺失项必须标记为“待确认”

## 工作流程

1. 先把用户输入整理为 spec，字段格式参考 `references/pipeline-blueprint.md`
2. 确认这些字段：
   - `skill_slug`
   - `display_name`
   - `description`
   - `goal`
   - `stage_prefix`
   - `stages[]`
3. 运行生成器：

```bash
python3 skills/pipeline-create/scripts/generate_pipeline_skill.py \
  --spec <spec.json> \
  --output-root skills
```

4. 检查生成结果是否包含：
   - `SKILL.md`
   - `agents/openai.yaml`
   - `references/pipeline.md`
   - `scripts/run_skill.py`
   - `scripts/run_pipeline.py`
   - `tests/`
5. 立即验证：

```bash
python3 skills/<skill-slug>/scripts/run_skill.py <run_dir> --check-only
python3 skills/<skill-slug>/scripts/run_skill.py <run_dir> --mode dev-mock --allow-mock
python3 -m pytest skills/<skill-slug>/tests -q
```

## 默认生成策略

- 所有阶段默认生成 `builtin` provider，先保证 pipeline skeleton 可跑通
- capability key 使用 `<stage_prefix>_<stage_id>` 的下划线形式
- 第二阶段起默认依赖上一阶段的 `.json` 产物
- 每个阶段默认生成：
  - 一个 adapter
  - 一个 validator
  - 一对 `.json` / `.md` 产物
  - 一个模板文件

## 生成后必须做的事

- 根据真实业务补充 `SKILL.md` 和 `references/pipeline.md`
- 把占位模板改成真实字段与真实输出格式
- 如需接入 `skill -> mcp -> cli -> builtin` 的正式 provider，按阶段逐个替换 builtin

## 禁止项

- 不得跳过测试直接宣称“可用”
- 不得绕开 `pipeline-framework` 自创 runtime 语义
- 不得把“猜测”写成业务事实
- 不得把所有复杂度都塞进一个大 adapter
