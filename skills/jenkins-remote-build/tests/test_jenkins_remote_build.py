import argparse
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from jenkins_remote_build import add_common_trigger_args, build_job_url, build_trigger_url, load_jenkins_config, load_params, parse_callback_record, resolve_value


class JenkinsRemoteBuildTests(unittest.TestCase):
    def test_build_trigger_url_adds_token_callback_and_extra_params(self):
        url = build_trigger_url(
            job_url="https://jenkins.example.com/job/demo/buildWithParameters",
            token="abc 123",
            callback_url="http://host.docker.internal:8000/callback?run=1",
            callback_param="CALLBACK_URL",
            params={"BRANCH": "feature/demo", "ENV": "qa"},
        )

        self.assertTrue(url.startswith("https://jenkins.example.com/job/demo/buildWithParameters?"))
        self.assertIn("token=abc+123", url)
        self.assertIn("CALLBACK_URL=http%3A%2F%2Fhost.docker.internal%3A8000%2Fcallback%3Frun%3D1", url)
        self.assertIn("BRANCH=feature%2Fdemo", url)
        self.assertIn("ENV=qa", url)

    def test_parse_callback_record_merges_json_body_and_normalizes_result(self):
        line = json.dumps(
            {
                "method": "POST",
                "path": "/callback?id=req-1",
                "body": json.dumps(
                    {
                        "requestId": "req-1",
                        "buildNumber": 42,
                        "result": "SUCCESS",
                        "artifacts": ["https://example.com/app.apk"],
                    }
                ),
            }
        )

        parsed = parse_callback_record(line)

        self.assertEqual(parsed["requestId"], "req-1")
        self.assertEqual(parsed["buildNumber"], "42")
        self.assertEqual(parsed["result"], "SUCCESS")
        self.assertEqual(parsed["artifacts"], ["https://example.com/app.apk"])
        self.assertEqual(parsed["rawPayload"]["method"], "POST")

    def test_build_job_url_from_base_url_and_job_name(self):
        url = build_job_url(
            jenkins_url="https://jenkins.example.com/",
            job_name="folder/demo job",
            build_endpoint="build",
        )

        self.assertEqual(url, "https://jenkins.example.com/job/folder/job/demo%20job/build")

    def test_load_config_only_reads_connection_fields(self):
        config_path = ROOT / "tests" / "tmp_jenkins_config.json"
        config_path.write_text(
            json.dumps(
                {
                    "jenkinsUrl": "https://jenkins.example.com",
                    "username": "config-user",
                    "apiToken": "config-token",
                    "token": "config-trigger-token",
                    "jobName": "demo",
                    "params": {"BRANCH": "main"},
                }
            ),
            encoding="utf-8",
        )
        try:
            config = load_jenkins_config(str(config_path), env={})
        finally:
            config_path.unlink()

        self.assertEqual(config["jenkinsUrl"], "https://jenkins.example.com")
        self.assertEqual(config["username"], "config-user")
        self.assertEqual(config["apiToken"], "config-token")
        self.assertNotIn("token", config)
        self.assertNotIn("jobName", config)
        self.assertNotIn("params", config)
        self.assertEqual(resolve_value("cli-user", config, "username", "JENKINS_USER_NAME", {}), "cli-user")
        self.assertEqual(resolve_value("", config, "apiToken", "JENKINS_API_TOKEN", {}), "config-token")

    def test_load_params_ignores_config_params(self):
        params = load_params(["ENV=qa"], config={"params": {"BRANCH": "main"}})

        self.assertEqual(params, {"ENV": "qa"})

    def test_load_config_reads_jenkins_url_config(self):
        config_path = ROOT / "tests" / "tmp_jenkins_url_config.json"
        config_path.write_text(
            json.dumps({"jenkinsUrl": "https://base.example.com"}),
            encoding="utf-8",
        )
        try:
            config = load_jenkins_config(str(config_path), env={})
        finally:
            config_path.unlink()

        self.assertEqual(resolve_value("", config, "jenkinsUrl", "JENKINS_URL", {}), "https://base.example.com")

    def test_load_config_supports_jenkins_url_environment_variable(self):
        config = load_jenkins_config("", env={"JENKINS_URL": "https://env.example.com"})

        self.assertEqual(resolve_value("", config, "jenkinsUrl", "JENKINS_URL", {}), "https://env.example.com")

    def test_common_trigger_args_use_jenkins_url_option(self):
        parser = argparse.ArgumentParser()
        add_common_trigger_args(parser)

        args = parser.parse_args(["--jenkins-url", "https://jenkins.example.com", "--job-name", "demo"])

        self.assertEqual(args.jenkins_url, "https://jenkins.example.com")
        self.assertFalse(hasattr(args, "base_url"))


if __name__ == "__main__":
    unittest.main()
