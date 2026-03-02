# Skills

> 本仓库为 Agent Skills 的公开技能库（Powered by ValiantCat）。关于 Agent Skills 标准，可参阅 [agentskills.io](https://agentskills.io)。

## 什么是 Skills？

Skills 是以文件夹形式组织的指令、脚本与资源，供 AI Agent 动态加载，用于在特定任务上表现更好。每个 Skill 教 Agent 如何**可重复地**完成一类任务，例如：按品牌规范生成文档、用既定工作流分析数据、或自动化个人/团队流程。

## 关于本仓库

本仓库用于存放与分享可在 Cursor、Claude Code、CodeX、OpenClaw 等环境中使用的 Agent Skills。每个技能自成一个文件夹，内含 `SKILL.md`（YAML 前导元数据 + 使用说明），Agent 会据此执行对应能力。

- 欢迎贡献新技能或改进现有技能
- 使用前建议在本地或目标环境中充分测试

## 目录结构

- **本仓库根目录**：各技能以子文件夹形式存放，每个技能文件夹内包含 `SKILL.md` 及可选脚本、资源
- 后续可在此列出具体技能列表与分类（如：开发、设计、文档、工作流等）

## 如何创建基础 Skill

只需一个文件夹和其中的 `SKILL.md`，包含 YAML 前导元数据与说明即可。最小示例：

```markdown
---
name: my-skill-name
description: 简要说明该技能做什么、在什么场景下使用
---

# 技能名称

[在此编写 Agent 激活该技能时会遵循的指令]

## 示例
- 使用场景 1
- 使用场景 2

## 规范
- 规范 1
- 规范 2
```

前导元数据至少需要两个字段：
- **name**：技能唯一标识（小写，单词间用连字符）
- **description**：完整描述该技能的作用与适用场景

更多自定义技能写法可参考 [ValiantCat 技能仓库](https://github.com/Valiant-Cat/skills) 与 [如何创建自定义技能](https://support.claude.com/en/articles/12512198-creating-custom-skills)。

## 参考链接

- [Agent Skills 规范与社区](https://agentskills.io)
- [ValiantCat Skills 技能仓库](https://github.com/Valiant-Cat/skills)
- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
