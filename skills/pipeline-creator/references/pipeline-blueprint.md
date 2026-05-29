# Workflow Blueprint

`pipeline-creator` 的输入是一个 JSON workflow spec。文件名沿用 `pipeline-blueprint.md` 是为了兼容旧引用；内容已经改为工作流 Skill 创建规范。

最小示例：

```json
{
  "skill_slug": "customer-voice-workflow",
  "display_name": "Customer Voice Workflow",
  "description": "Use when 需要把客户反馈整理成结构化洞察、行动建议和可复核交付物。",
  "goal": "把客户反馈输入收敛为洞察报告和行动建议。",
  "workflow_type": "analysis-to-recommendation",
  "stages": [
    {
      "id": "intake-feedback",
      "title": "Intake Feedback",
      "purpose": "收集并整理输入反馈。",
      "inputs": ["客户反馈原文", "来源渠道"],
      "outputs": ["feedback-brief.md"],
      "acceptance_checks": ["反馈来源明确", "待确认项单独列出"],
      "template_sections": ["输入来源", "问题摘要", "待确认项"]
    },
    {
      "id": "synthesize-insights",
      "title": "Synthesize Insights",
      "purpose": "归纳核心洞察并输出行动建议。",
      "inputs": ["feedback-brief.md"],
      "outputs": ["insight-report.md"],
      "acceptance_checks": ["建议可执行", "优先级理由明确"],
      "template_sections": ["主题", "建议", "优先级"]
    }
  ]
}
```

同一示例也保存在 `assets/workflow-spec.example.json`，可直接复制后改写。

字段说明：

- `skill_slug`
  生成目录名与 skill frontmatter `name`
- `display_name`
  `agents/openai.yaml` 展示名
- `description`
  生成 Skill 的触发描述，应以 `Use when` 开头，只描述何时使用
- `goal`
  写入 `SKILL.md` 和 `references/workflow.md`
- `workflow_type`
  工作流类别，用于帮助 Agent 判断阶段粒度
- `stages[].id`
  阶段 id，建议使用连字符命名
- `stages[].inputs`
  本阶段需要的输入、前序产物或上下文
- `stages[].outputs`
  本阶段承诺生成或汇总的产物
- `stages[].acceptance_checks`
  阶段完成前必须逐项核对的验收条件
- `stages[].template_sections`
  阶段 Markdown 模板的默认章节

默认规则：

- `assets/starter/scripts/` 保存通用脚本模板，生成器负责把模板实例化到新 Skill 的 `scripts/`
- starter 包含 `run_skill.py`、`run_pipeline.py`、`pipeline_spec.py`、adapter/validator 骨架、runtime/provider/capability 支持和 `workflow_runtime/`
- `description` 必须以 `Use when ` 开头，只描述触发条件
- 阶段 id 规范化后必须唯一
- 每个 stage 只负责一个清晰收敛动作
- 每个 stage 必须至少有一个 input、output 和 acceptance check
- 同一阶段内不得重复声明 input、output 或 acceptance check
- 不同阶段不得声明同一个 output，避免产物归属不清
- 文件型 input 与所有 output 必须是 run 目录内的相对路径，不能使用绝对路径或 `..`
- 缺失输入必须阻塞并列出缺口
- 未确认信息必须进入“待确认项”
- 工作流完成条件必须以阶段产物和验收项为准
- 生成结果会包含 `references/architecture.md`，把 Runner、Adapter、Input、Output 作为文档契约迁移到新 Skill
- 生成结果会包含 `scripts/workflow_contract.py`，固化阶段注册表、输入、输出、模板路径
- 生成结果会包含 `scripts/validate_workflow.py`，用于本地校验生成 Skill 的结构与契约
- 生成结果会包含可运行的 dev-mock starter，便于先验证阶段顺序、输入输出和 commit 行为
- 阶段模板会包含 Adapter Notes，用于描述输入如何转换为输出、使用了哪些工具和判断依据

建议：

- stage 保持 2 到 6 个
- 每个阶段至少有一个输出和一个验收项
- 先保证 Runner/Adapter/Input/Output 契约清晰，再补充领域模板细节
- 阶段变更后同步更新 workflow contract module，并运行 validator
- 业务化时优先改生成 Skill 中的 `scripts/adapters/`、`scripts/validators/` 和 `assets/templates/`
