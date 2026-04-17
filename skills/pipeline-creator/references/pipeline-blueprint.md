# Pipeline Blueprint

`pipeline-creator` 的输入是一个 JSON spec。最小示例：

```json
{
  "skill_slug": "customer-voice-pipeline",
  "display_name": "Customer Voice Pipeline",
  "description": "Use when 需要把客户反馈从原始输入整理为结构化洞察和行动建议。",
  "goal": "把客户反馈输入收敛为洞察报告和行动建议。",
  "stage_prefix": "customer_voice",
  "stages": [
    {
      "id": "intake-feedback",
      "title": "Intake Feedback",
      "purpose": "收集并整理输入反馈。",
      "artifact_basename": "feedback-brief",
      "json_fields": ["source", "summary", "signals"],
      "template_title": "Feedback Brief",
      "template_sections": ["输入来源", "问题摘要", "待确认项"]
    },
    {
      "id": "synthesize-insights",
      "title": "Synthesize Insights",
      "purpose": "归纳核心洞察并输出行动建议。",
      "artifact_basename": "insight-report",
      "json_fields": ["theme", "recommendation", "priority"],
      "template_title": "Insight Report",
      "template_sections": ["主题", "建议", "优先级"]
    }
  ]
}
```

字段说明：

- `skill_slug`
  生成目录名与 skill frontmatter `name`
- `display_name`
  `agents/openai.yaml` 展示名
- `description`
  生成 skill 的触发描述
- `goal`
  写入 `SKILL.md` 和 `references/pipeline.md`
- `stage_prefix`
  capability key 前缀，建议使用下划线命名
- `stages[].id`
  stage id，保留连字符命名
- `stages[].artifact_basename`
  产物基础名，最终生成 `<name>.json` 和 `<name>.md`
- `stages[].json_fields`
  builtin 阶段默认输出字段，也作为 validator 的最低契约
- `stages[].template_sections`
  `.md` 模板默认标题

默认规则：

- 首阶段无输入
- 第二阶段开始默认依赖上一阶段的 `.json`
- 所有阶段默认 builtin ready，便于先跑通闭环

建议：

- stage 保持 2 到 5 个
- 每个 stage 只负责一个清晰的收敛动作
- 先让 pipeline 跑通，再替换中间 provider
