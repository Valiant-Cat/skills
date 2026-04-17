import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = SKILL_ROOT / "tests" / "fixtures" / "prompt_cases.json"
SCRIPT_PATH = SKILL_ROOT / "scripts" / "validate_prompt_trigger.py"


class IdeaToPrdPromptContractTests(unittest.TestCase):
    def test_skill_doc_scopes_enforcement_to_in_skill_runtime(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("当 Agent 已进入 `idea-to-prd` 执行时", text)
        self.assertNotIn("用户显式要求使用 `idea-to-prd` 时，第一条实操命令必须是", text)
        self.assertIn("本 skill 不单独保证平台级 prompt routing 一定先选择本 skill。", text)

    def test_pipeline_doc_declares_boundary(self):
        text = (SKILL_ROOT / "references" / "pipeline.md").read_text(encoding="utf-8")
        self.assertIn("Boundary of Enforcement", text)
        self.assertIn("平台 orchestration 行为", text)

    def test_validate_prompt_trigger_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "report.json"
            subprocess.run(
                [
                    "python3",
                    str(SCRIPT_PATH),
                    "--input",
                    str(FIXTURE_PATH),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=True,
            )
            report = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertIsInstance(report, list)
        indexed = {item["case_id"]: item for item in report}
        self.assertEqual(indexed["explicit_idea_to_prd"]["status"], "intercepted")
        self.assertEqual(indexed["explicit_idea_to_prd"]["intercepted_by"], "using-superpowers")
        self.assertEqual(indexed["explicit_idea_to_prd_seed"]["status"], "passed")
        self.assertEqual(indexed["implicit_product_idea"]["status"], "not_selected")


if __name__ == "__main__":
    unittest.main()
