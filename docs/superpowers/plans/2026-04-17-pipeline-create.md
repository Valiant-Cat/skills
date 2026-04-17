# Pipeline Create Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个 `pipeline-create` skill，使 Agent 能根据用户需求直接生成一个基于 `pipeline-framework` 的可运行 consumer skill。

**Architecture:** 新 skill 由三部分组成：面向 Agent 的 `SKILL.md` 与参考文档、一个把 pipeline 规格渲染为目录脚手架的 Python 生成器、以及用于验证生成结果的测试。生成器输出的目录结构、运行入口与测试骨架对齐 `pipeline-framework` 与 `idea-to-prd`。

**Tech Stack:** Markdown, YAML, Python 3, unittest, `pipeline-framework`

---

### Task 1: 定义 skill 对外契约

**Files:**
- Create: `skills/pipeline-create/SKILL.md`
- Create: `skills/pipeline-create/agents/openai.yaml`
- Create: `skills/pipeline-create/references/pipeline-blueprint.md`

- [ ] **Step 1: 写出期望的 skill 行为与目录约束**
- [ ] **Step 2: 把生成流程、输入要求、禁止项写入 `SKILL.md`**
- [ ] **Step 3: 补齐 UI 元数据与参考文档**

### Task 2: 先写生成器测试

**Files:**
- Create: `skills/pipeline-create/tests/test_generate_pipeline_skill.py`

- [ ] **Step 1: 写生成器的 failing test**
- [ ] **Step 2: 运行测试，确认因为脚本缺失或行为未实现而失败**

### Task 3: 实现脚手架生成器

**Files:**
- Create: `skills/pipeline-create/scripts/generate_pipeline_skill.py`
- Create: `skills/pipeline-create/scripts/__init__.py`

- [ ] **Step 1: 实现 pipeline spec 解析与 slug/stage 规范化**
- [ ] **Step 2: 实现目录与文件渲染**
- [ ] **Step 3: 生成运行入口、adapter、validator、模板与测试**

### Task 4: 端到端验证

**Files:**
- Modify: `skills/pipeline-create/tests/test_generate_pipeline_skill.py`

- [ ] **Step 1: 运行 `pytest skills/pipeline-create/tests -v`**
- [ ] **Step 2: 生成一个临时 consumer skill 并跑其最小测试**
- [ ] **Step 3: 如有失败，修正生成器并重跑**
