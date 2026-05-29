import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = SKILL_ROOT / "scripts"
STARTER_ROOT = SKILL_ROOT / "assets" / "starter"
EXAMPLE_SPEC = SKILL_ROOT / "assets" / "workflow-spec.example.json"
REPO_ROOT = Path(__file__).resolve().parents[3]


class GenerateWorkflowSkillTests(unittest.TestCase):
    def make_workspace(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "skills").mkdir(parents=True, exist_ok=True)
        return root

    def write_spec(self, root: Path) -> Path:
        spec = {
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
                    "template_sections": ["输入来源", "问题摘要", "待确认项"],
                },
                {
                    "id": "synthesize-insights",
                    "title": "Synthesize Insights",
                    "purpose": "归纳核心洞察并输出行动建议。",
                    "inputs": ["feedback-brief.md"],
                    "outputs": ["insight-report.md"],
                    "acceptance_checks": ["建议可执行", "优先级理由明确"],
                    "template_sections": ["主题", "建议", "优先级"],
                },
            ],
        }
        spec_path = root / "workflow-spec.json"
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return spec_path

    def run_generator(self, root: Path, spec_path: Path):
        return subprocess.run(
            [
                "python3",
                str(SCRIPT_ROOT / "generate_pipeline_skill.py"),
                "--spec",
                str(spec_path),
                "--output-root",
                str(root / "skills"),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

    def run_generator_with_args(self, root: Path, spec_path: Path, *extra_args: str):
        return subprocess.run(
            [
                "python3",
                str(SCRIPT_ROOT / "generate_pipeline_skill.py"),
                "--spec",
                str(spec_path),
                "--output-root",
                str(root / "skills"),
                *extra_args,
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

    def test_generator_creates_standard_workflow_skill(self):
        self.assertTrue(EXAMPLE_SPEC.exists())
        self.assertTrue((STARTER_ROOT / "scripts" / "workflow_contract.py").exists())
        self.assertTrue((STARTER_ROOT / "scripts" / "validate_workflow.py").exists())
        self.assertTrue((STARTER_ROOT / "scripts" / "run_skill.py").exists())
        self.assertTrue((STARTER_ROOT / "scripts" / "workflow_runtime" / "runner" / "core.py").exists())

        root = self.make_workspace()
        spec_path = self.write_spec(root)

        proc = self.run_generator(root, spec_path)
        self.assertEqual(proc.returncode, 0, proc.stderr)

        generated_skill = root / "skills" / "customer-voice-workflow"
        self.assertTrue((generated_skill / "SKILL.md").exists())
        self.assertTrue((generated_skill / "agents" / "openai.yaml").exists())
        self.assertTrue((generated_skill / "references" / "workflow.md").exists())
        self.assertTrue((generated_skill / "references" / "architecture.md").exists())
        self.assertTrue((generated_skill / "assets" / "templates" / "intake-feedback.md").exists())
        self.assertTrue((generated_skill / "scripts" / "workflow_contract.py").exists())
        self.assertTrue((generated_skill / "scripts" / "validate_workflow.py").exists())
        self.assertTrue((generated_skill / "scripts" / "run_skill.py").exists())
        self.assertTrue((generated_skill / "scripts" / "run_pipeline.py").exists())
        self.assertTrue((generated_skill / "scripts" / "pipeline_spec.py").exists())
        self.assertTrue((generated_skill / "scripts" / "adapters" / "intake_feedback_adapter.py").exists())
        self.assertTrue((generated_skill / "scripts" / "validators" / "intake_feedback_validator.py").exists())
        self.assertTrue((generated_skill / "scripts" / "workflow_runtime" / "runner" / "core.py").exists())
        self.assertTrue((generated_skill / "tests" / "test_workflow_contract.py").exists())

        skill_md = (generated_skill / "SKILL.md").read_text(encoding="utf-8")
        workflow_md = (generated_skill / "references" / "workflow.md").read_text(encoding="utf-8")
        architecture_md = (generated_skill / "references" / "architecture.md").read_text(encoding="utf-8")
        combined = skill_md + workflow_md + architecture_md
        self.assertIn("metadata:", skill_md)
        self.assertIn("version: 1.0.0", skill_md)
        self.assertIn("## Workflow Contract", skill_md)
        self.assertIn("## Intake Checklist", skill_md)
        self.assertIn("## Quality Gates", skill_md)
        self.assertIn("## Completion Report", skill_md)
        self.assertIn("references/architecture.md", skill_md)
        self.assertIn("## Version History", skill_md)
        self.assertIn("Intake Feedback", workflow_md)
        self.assertIn("feedback-brief.md", workflow_md)
        self.assertIn("## Handoff Rules", workflow_md)
        self.assertIn("## Blocking Policy", workflow_md)
        self.assertIn("## Global Acceptance Checklist", workflow_md)
        self.assertIn("## Runner Contract", architecture_md)
        self.assertIn("## Adapter Contract", architecture_md)
        self.assertIn("## Input Contract", architecture_md)
        self.assertIn("## Output Contract", architecture_md)
        self.assertIn("## Stage Registry", architecture_md)
        contract_py = (generated_skill / "scripts" / "workflow_contract.py").read_text(encoding="utf-8")
        validator_py = (generated_skill / "scripts" / "validate_workflow.py").read_text(encoding="utf-8")
        self.assertIn("STAGES", contract_py)
        self.assertIn("REQUIRED_REFERENCES", contract_py)
        self.assertIn("validate_skill_root", validator_py)
        template_md = (generated_skill / "assets" / "templates" / "intake-feedback.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("## Stage Context", template_md)
        self.assertIn("## Required Inputs", template_md)
        self.assertIn("## Adapter Notes", template_md)
        self.assertIn("## Work Log", template_md)
        self.assertIn("## Acceptance Evidence", template_md)
        self.assertIn("## Risks And Follow-Ups", template_md)
        self.assertNotIn(".framework", combined)

        validate_proc = subprocess.run(
            [
                "python3",
                str(generated_skill / "scripts" / "validate_workflow.py"),
                "--skill-root",
                str(generated_skill),
                "--run-smoke",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(validate_proc.returncode, 0, validate_proc.stdout + validate_proc.stderr)

        run_dir = root / "runs" / "full"
        run_proc = subprocess.run(
            [
                "python3",
                str(generated_skill / "scripts" / "run_skill.py"),
                str(run_dir),
                "--mode",
                "dev-mock",
                "--allow-mock",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(run_proc.returncode, 0, run_proc.stdout + run_proc.stderr)
        self.assertTrue((run_dir / "feedback-brief.md").exists())
        self.assertTrue((run_dir / "insight-report.md").exists())
        self.assertTrue((run_dir / ".workflow").exists())
        self.assertFalse((run_dir / ".framework").exists())
        manifest = json.loads((run_dir / ".workflow" / "commit" / "manifests" / "intake-feedback.json").read_text())
        self.assertEqual(manifest["source"], ".workflow/staging/intake-feedback")

    def test_generator_writes_contract_tests_that_pass_in_generated_workspace(self):
        root = self.make_workspace()
        spec_path = self.write_spec(root)

        proc = self.run_generator(root, spec_path)
        self.assertEqual(proc.returncode, 0, proc.stderr)

        generated_skill = root / "skills" / "customer-voice-workflow"
        proc = subprocess.run(
            ["python3", "-m", "unittest", "discover", str(generated_skill / "tests")],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_generator_escapes_special_characters_in_generated_python(self):
        root = self.make_workspace()
        spec = {
            "skill_slug": "quoted-workflow",
            "display_name": "Quoted \"Workflow\": Alpha",
            "description": "Use when 需要验证带引号、冒号: 反斜杠和空格的工作流生成结果。",
            "goal": "验证特殊字符不会破坏生成脚本。",
            "stages": [
                {
                    "id": "quote-stage",
                    "title": "Quote \"Stage\" \\ Alpha",
                    "inputs": ["用户输入"],
                    "outputs": ["quote report.json", "quote report.md"],
                    "acceptance_checks": ["产物存在"],
                }
            ],
        }
        spec_path = root / "quoted-spec.json"
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        proc = self.run_generator(root, spec_path)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        generated_skill = root / "skills" / "quoted-workflow"
        validate_proc = subprocess.run(
            [
                "python3",
                str(generated_skill / "scripts" / "validate_workflow.py"),
                "--skill-root",
                str(generated_skill),
                "--run-smoke",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(validate_proc.returncode, 0, validate_proc.stdout + validate_proc.stderr)
        compile_proc = subprocess.run(
            ["python3", "-m", "py_compile", str(generated_skill / "scripts" / "adapters" / "quote_stage_adapter.py")],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(compile_proc.returncode, 0, compile_proc.stdout + compile_proc.stderr)
        run_proc = subprocess.run(
            [
                "python3",
                str(generated_skill / "scripts" / "run_skill.py"),
                str(root / "runs" / "quoted"),
                "--mode",
                "dev-mock",
                "--allow-mock",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(run_proc.returncode, 0, run_proc.stdout + run_proc.stderr)

    def test_generated_runtime_commits_nested_output_paths(self):
        root = self.make_workspace()
        spec = {
            "skill_slug": "nested-output-workflow",
            "description": "Use when 需要验证工作流产物可以稳定写入 run 目录下的子目录。",
            "stages": [
                {
                    "id": "collect",
                    "inputs": ["用户输入"],
                    "outputs": ["brief.md"],
                    "acceptance_checks": ["brief exists"],
                },
                {
                    "id": "publish",
                    "inputs": ["brief.md"],
                    "outputs": ["reports/final-report.md", "data/final-summary.json"],
                    "acceptance_checks": ["nested outputs exist"],
                },
            ],
        }
        spec_path = root / "nested-spec.json"
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        proc = self.run_generator(root, spec_path)
        self.assertEqual(proc.returncode, 0, proc.stderr)

        generated_skill = root / "skills" / "nested-output-workflow"
        run_dir = root / "runs" / "nested"
        run_proc = subprocess.run(
            [
                "python3",
                str(generated_skill / "scripts" / "run_skill.py"),
                str(run_dir),
                "--mode",
                "dev-mock",
                "--allow-mock",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(run_proc.returncode, 0, run_proc.stdout + run_proc.stderr)
        self.assertTrue((run_dir / "reports" / "final-report.md").exists())
        self.assertTrue((run_dir / "data" / "final-summary.json").exists())
        manifest = json.loads((run_dir / ".workflow" / "commit" / "manifests" / "publish.json").read_text())
        self.assertEqual(
            manifest["outputs"],
            ["reports/final-report.md", "data/final-summary.json"],
        )

    def test_generated_validator_smoke_seeds_external_file_inputs(self):
        root = self.make_workspace()
        spec = {
            "skill_slug": "external-input-workflow",
            "description": "Use when 需要验证 validator smoke 会为外部文件输入创建最小样本。",
            "stages": [
                {
                    "id": "parse-source",
                    "inputs": ["source/input.md"],
                    "outputs": ["parsed.md"],
                    "acceptance_checks": ["parsed exists"],
                },
                {
                    "id": "summarize",
                    "inputs": ["parsed.md"],
                    "outputs": ["summary.md"],
                    "acceptance_checks": ["summary exists"],
                },
            ],
        }
        spec_path = root / "external-input-spec.json"
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        proc = self.run_generator(root, spec_path)
        self.assertEqual(proc.returncode, 0, proc.stderr)

        generated_skill = root / "skills" / "external-input-workflow"
        validate_proc = subprocess.run(
            [
                "python3",
                str(generated_skill / "scripts" / "validate_workflow.py"),
                "--skill-root",
                str(generated_skill),
                "--run-smoke",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(validate_proc.returncode, 0, validate_proc.stdout + validate_proc.stderr)

    def test_generator_rejects_existing_skill_without_force_and_force_cleans_managed_files(self):
        root = self.make_workspace()
        spec_path = self.write_spec(root)
        first = self.run_generator(root, spec_path)
        self.assertEqual(first.returncode, 0, first.stderr)
        generated_skill = root / "skills" / "customer-voice-workflow"
        stale_file = generated_skill / "scripts" / "adapters" / "stale_adapter.py"
        stale_file.write_text("# stale\n", encoding="utf-8")

        second = self.run_generator(root, spec_path)
        self.assertNotEqual(second.returncode, 0)
        self.assertTrue(stale_file.exists())

        forced = self.run_generator_with_args(root, spec_path, "--force")
        self.assertEqual(forced.returncode, 0, forced.stderr)
        self.assertFalse(stale_file.exists())

    def test_example_spec_generates_runnable_skill(self):
        root = self.make_workspace()

        proc = self.run_generator(root, EXAMPLE_SPEC)
        self.assertEqual(proc.returncode, 0, proc.stderr)

        generated_skill = root / "skills" / "customer-voice-workflow"
        validate_proc = subprocess.run(
            [
                "python3",
                str(generated_skill / "scripts" / "validate_workflow.py"),
                "--skill-root",
                str(generated_skill),
                "--run-smoke",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(validate_proc.returncode, 0, validate_proc.stdout + validate_proc.stderr)
        self.assertTrue((generated_skill / "assets" / "templates" / "synthesize-insights.md").exists())

    def test_generator_rejects_invalid_workflow_specs(self):
        cases = [
            (
                "duplicate-stage.json",
                {
                    "skill_slug": "bad-workflow",
                    "description": "Use when 需要验证坏 spec 会被拒绝并给出明确错误。",
                    "stages": [
                        {"id": "draft", "outputs": ["draft.md"], "acceptance_checks": ["ok"]},
                        {"id": "draft", "outputs": ["draft-2.md"], "acceptance_checks": ["ok"]},
                    ],
                },
                "duplicate stage id",
            ),
            (
                "empty-output.json",
                {
                    "skill_slug": "bad-workflow",
                    "description": "Use when 需要验证坏 spec 会被拒绝并给出明确错误。",
                    "stages": [
                        {"id": "draft", "outputs": [], "acceptance_checks": ["ok"]},
                    ],
                },
                "at least one output",
            ),
            (
                "path-traversal.json",
                {
                    "skill_slug": "bad-workflow",
                    "description": "Use when 需要验证坏 spec 会被拒绝并给出明确错误。",
                    "stages": [
                        {"id": "draft", "outputs": ["../escape.md"], "acceptance_checks": ["ok"]},
                    ],
                },
                "relative artifact path",
            ),
            (
                "duplicate-output.json",
                {
                    "skill_slug": "bad-workflow",
                    "description": "Use when 需要验证坏 spec 会被拒绝并给出明确错误。",
                    "stages": [
                        {"id": "draft", "outputs": ["shared.md"], "acceptance_checks": ["ok"]},
                        {"id": "publish", "outputs": ["shared.md"], "acceptance_checks": ["ok"]},
                    ],
                },
                "duplicate output",
            ),
            (
                "duplicate-check.json",
                {
                    "skill_slug": "bad-workflow",
                    "description": "Use when 需要验证坏 spec 会被拒绝并给出明确错误。",
                    "stages": [
                        {"id": "draft", "outputs": ["draft.md"], "acceptance_checks": ["ok", "ok"]},
                    ],
                },
                "duplicate acceptance checks",
            ),
            (
                "bad-description.json",
                {
                    "skill_slug": "bad-workflow",
                    "description": "错误触发描述",
                    "stages": [
                        {"id": "draft", "outputs": ["draft.md"], "acceptance_checks": ["ok"]},
                    ],
                },
                "description must start",
            ),
        ]

        for filename, spec, expected_error in cases:
            with self.subTest(filename=filename):
                root = self.make_workspace()
                spec_path = root / filename
                spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                proc = self.run_generator(root, spec_path)
                self.assertNotEqual(proc.returncode, 0)
                self.assertIn(expected_error, proc.stderr)


if __name__ == "__main__":
    unittest.main()
