---
name: pipeline-creator
description: Use when 需要把一条业务流程、协作流程、交付流程或多阶段任务沉淀成标准化工作流 Skill，明确目标、阶段、产物、阻塞条件和验收规则。
metadata:
  version: 1.6.0
---

# Pipeline Creator

`pipeline-creator` 是工作流 Skill 创建器。它帮助用户把一条流水线、业务流程或多阶段任务写成稳定、可复用、可验收的 Skill。

它的目标是产出一个标准化工作流 Skill 目录，至少包含：

- `SKILL.md`
- `agents/openai.yaml`
- 生成 Skill 内的 workflow reference
- 生成 Skill 内的 architecture reference
- `scripts/workflow_contract.py`
- `scripts/validate_workflow.py`
- `scripts/run_skill.py`
- `scripts/run_pipeline.py`
- `scripts/workflow_runtime/`
- `assets/templates/`
- `tests/test_workflow_contract.py`

## 何时使用

在这些场景触发：

- 用户要把一个流程、流水线或协作方式沉淀成 Skill
- 用户已经有阶段、输入、输出或验收标准，需要整理成稳定规范
- 用户想创建“工作流创建器”式的 Skill
- 用户需要让其他 Agent 按固定阶段执行并产出可复核结果

不适用场景：

- 只想临时跑一次没有固定阶段、产物或验收项的普通任务
- 只是修改现有工作流 Skill 的一个文案字段

## 工作流程

1. 先把用户输入整理为 workflow spec，字段格式参考 `references/pipeline-blueprint.md`。
2. 确认这些字段：
   - `skill_slug`
   - `display_name`
   - `description`
   - `goal`
   - `workflow_type`
   - `stages[]`
3. 运行生成器：

```bash
python3 skills/pipeline-creator/scripts/generate_pipeline_skill.py \
  --spec <spec.json> \
  --output-root skills
```

没有现成 spec 时，可以先复制 `assets/workflow-spec.example.json`，再按业务阶段改写。

4. 检查生成结果是否包含：
   - `SKILL.md`
   - `agents/openai.yaml`
   - 生成 Skill 内的 workflow reference
   - 生成 Skill 内的 architecture reference
   - `scripts/workflow_contract.py`
   - `scripts/validate_workflow.py`
   - `scripts/run_skill.py`
   - `scripts/run_pipeline.py`
   - `scripts/workflow_runtime/`
   - `assets/templates/`
   - `tests/test_workflow_contract.py`
5. 立即验证：

```bash
python3 skills/<skill-slug>/scripts/validate_workflow.py --skill-root skills/<skill-slug> --run-smoke
python3 -m unittest discover skills/<skill-slug>/tests
```

## 默认生成策略

- 通用脚本模板维护在 `assets/starter/scripts/`，生成器会把 starter 实例化到目标 Skill 的 `scripts/`
- starter 包含可运行入口、阶段 spec、adapter/validator 骨架、runtime/provider/capability 支持和 workflow runtime
- 每个阶段都有明确的 `purpose`、`inputs`、`outputs` 和 `acceptance_checks`
- 生成器会拒绝重复阶段、重复产物、重复验收项、空输入/输出/验收项、非 `Use when` 描述和越界产物路径
- 每个阶段生成一个 Markdown 模板，用于稳定组织阶段产物
- 生成 `references/architecture.md`，把 Runner、Adapter、Input 和 Output 作为文档契约迁移进新 Skill
- 生成 `scripts/workflow_contract.py`，把阶段注册表、输入、输出、模板路径固化成可导入模块
- 生成 `scripts/validate_workflow.py`，让生成 Skill 可以自检结构、引用和禁用依赖
- 生成 `scripts/run_skill.py` 和 `scripts/run_pipeline.py`，让 starter 能先在 dev-mock 模式跑通
- `SKILL.md` 中写入 Workflow Contract，约束 Agent 不跳阶段、不伪造事实、不忽略阻塞
- 生成 Skill 的 workflow reference 作为工作流真相源，记录阶段顺序、产物和完成规则
- 契约测试验证 Skill 结构、脚本模块、文档契约、本地 validator 和 dev-mock starter runtime

## 生成后必须做的事

- 根据真实业务补充生成 Skill 的 workflow reference 阶段细节
- 检查 architecture reference 中 Runner/Adapter/Input/Output 契约是否符合真实业务
- 如阶段变化，同步更新 `scripts/workflow_contract.py` 并运行 `scripts/validate_workflow.py`
- 如需要业务化执行逻辑，优先修改生成 Skill 内的 `scripts/adapters/` 与 `scripts/validators/`；通用 `workflow_runtime/` 默认保持稳定
- 把 `assets/templates/` 改成真实输出格式
- 检查 `description` 是否只描述触发条件，不总结执行流程
- 运行生成 Skill 自带的 validator smoke 和契约测试

## 禁止项

- 不得生成无法通过 smoke 的 `scripts/run_skill.py` 或 `scripts/run_pipeline.py`，却宣称它们可运行
- 不得把缺失输入、业务规则或验收项静默编造成事实
- 不得跳过契约测试直接宣称“可用”

## Version

Current version: 1.6.0

## Version History

- 1.6.0 - Harden runtime smoke for external file inputs, nested artifact paths, and duplicate output validation.
- 1.5.0 - Add reusable workflow spec example, spec validation, and smoke-first generated Skill verification guidance.
- 1.4.0 - Move runnable starter scripts and workflow runtime into assets/starter and instantiate them into generated skills.
- 1.3.0 - Generate concrete workflow contract and validation script modules.
- 1.2.0 - Add generated architecture templates for Runner, Adapter, Input, and Output contracts.
- 1.1.0 - Reposition pipeline-creator as a standard workflow Skill creator.
