import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = SKILL_ROOT / "scripts"
REPO_ROOT = Path(__file__).resolve().parents[3]
FRAMEWORK_ROOT = REPO_ROOT / "skills" / "pipeline-framework"


class GeneratePipelineSkillTests(unittest.TestCase):
    def make_workspace(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        skills_root = root / "skills"
        skills_root.mkdir(parents=True, exist_ok=True)
        (skills_root / "pipeline-framework").symlink_to(FRAMEWORK_ROOT, target_is_directory=True)
        return root

    def write_spec(self, root: Path) -> Path:
        spec = {
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
                    "template_sections": ["输入来源", "问题摘要", "待确认项"],
                },
                {
                    "id": "synthesize-insights",
                    "title": "Synthesize Insights",
                    "purpose": "归纳核心洞察并输出行动建议。",
                    "artifact_basename": "insight-report",
                    "json_fields": ["theme", "recommendation", "priority"],
                    "template_title": "Insight Report",
                    "template_sections": ["主题", "建议", "优先级"],
                },
            ],
        }
        spec_path = root / "pipeline-spec.json"
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

    def run_generated_skill(self, generated_skill: Path, run_dir: Path, *extra_args: str):
        return subprocess.run(
            ["python3", str(generated_skill / "scripts" / "run_skill.py"), str(run_dir), *extra_args],
            cwd=generated_skill.parents[1],
            capture_output=True,
            text=True,
        )

    def test_generator_creates_runnable_pipeline_skill(self):
        root = self.make_workspace()
        spec_path = self.write_spec(root)

        proc = self.run_generator(root, spec_path)
        self.assertEqual(proc.returncode, 0, proc.stderr)

        generated_skill = root / "skills" / "customer-voice-pipeline"
        self.assertTrue((generated_skill / "SKILL.md").exists())
        self.assertTrue((generated_skill / "agents" / "openai.yaml").exists())
        self.assertTrue((generated_skill / "references" / "pipeline.md").exists())
        self.assertTrue((generated_skill / "scripts" / "pipeline_spec.py").exists())
        self.assertTrue((generated_skill / "tests" / "test_run_skill.py").exists())

        check_dir = root / "runs" / "check-only"
        proc = self.run_generated_skill(generated_skill, check_dir, "--check-only")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["runtime"], "codex-session")
        self.assertIn("customer_voice_intake_feedback", payload["capabilities"])
        self.assertIn("customer_voice_synthesize_insights", payload["capabilities"])

        run_dir = root / "runs" / "full-run"
        proc = self.run_generated_skill(generated_skill, run_dir, "--mode", "dev-mock", "--allow-mock")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((run_dir / "feedback-brief.json").exists())
        self.assertTrue((run_dir / "feedback-brief.md").exists())
        self.assertTrue((run_dir / "insight-report.json").exists())
        self.assertTrue((run_dir / "insight-report.md").exists())

    def test_generator_writes_tests_that_pass_in_generated_workspace(self):
        root = self.make_workspace()
        spec_path = self.write_spec(root)

        proc = self.run_generator(root, spec_path)
        self.assertEqual(proc.returncode, 0, proc.stderr)

        generated_skill = root / "skills" / "customer-voice-pipeline"
        proc = subprocess.run(
            ["python3", "-m", "pytest", str(generated_skill / "tests"), "-q"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
