#!/usr/bin/env python3
import argparse
import base64
import os
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


JsonDict = dict[str, Any]


CONFIG_ALIASES = {
    "jenkinsUrl": ["jenkinsUrl", "jenkins_url", "JENKINS_URL"],
    "username": ["username", "userName", "user_name", "jenkinsUserName", "jenkins_user_name", "JENKINS_USER_NAME"],
    "apiToken": ["apiToken", "api_token", "jenkinsApiToken", "jenkins_api_token", "JENKINS_API_TOKEN"],
}

CONFIG_FILE_KEYS = {"jenkinsUrl", "username", "apiToken"}


def first_config_value(config: JsonDict, canonical_key: str) -> Any:
    for key in CONFIG_ALIASES.get(canonical_key, [canonical_key]):
        value = config.get(key)
        if value not in (None, ""):
            return value
    return ""


def load_jenkins_config(config_file: str = "", env: dict[str, str] | None = None) -> JsonDict:
    config: JsonDict = {}
    if config_file:
        loaded = json.loads(Path(config_file).read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("Jenkins 配置文件必须是 JSON 对象")
        for canonical_key in CONFIG_FILE_KEYS:
            value = first_config_value(loaded, canonical_key)
            if value not in (None, ""):
                config[canonical_key] = value
    environment = os.environ if env is None else env
    for canonical_key, aliases in CONFIG_ALIASES.items():
        if first_config_value(config, canonical_key):
            continue
        for alias in aliases:
            value = environment.get(alias)
            if value:
                config[canonical_key] = value
                break
    return config


def resolve_value(cli_value: str, config: JsonDict, config_key: str, env_key: str = "", env: dict[str, str] | None = None) -> str:
    if cli_value:
        return cli_value
    config_value = first_config_value(config, config_key)
    if config_value:
        return str(config_value)
    if env_key:
        environment = os.environ if env is None else env
        return environment.get(env_key, "")
    return ""


def build_job_url(jenkins_url: str, job_name: str, build_endpoint: str = "buildWithParameters") -> str:
    base = jenkins_url.strip().rstrip("/")
    if not base:
        raise ValueError("缺少 JENKINS_URL，请传 --jenkins-url、--config 或环境变量 JENKINS_URL")
    if not job_name.strip():
        raise ValueError("缺少 JOB_NAME，请传 --job-name、--config 或环境变量 JOB_NAME")
    job_path = "/".join(f"job/{urllib.parse.quote(part, safe='')}" for part in job_name.strip("/").split("/") if part)
    endpoint = build_endpoint.strip("/") or "buildWithParameters"
    return f"{base}/{job_path}/{endpoint}"


def build_trigger_url(
    job_url: str,
    token: str = "",
    callback_url: str = "",
    callback_param: str = "CALLBACK_URL",
    params: dict[str, str] | None = None,
) -> str:
    url_parts = urllib.parse.urlsplit(job_url.strip())
    query_items = urllib.parse.parse_qsl(url_parts.query, keep_blank_values=True)
    if token:
        query_items.append(("token", token))
    if callback_url:
        query_items.append((callback_param, callback_url))
    for key, value in (params or {}).items():
        if key:
            query_items.append((key, value))
    query = urllib.parse.urlencode(query_items)
    return urllib.parse.urlunsplit((url_parts.scheme, url_parts.netloc, url_parts.path, query, url_parts.fragment))


def parse_key_value(items: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"参数必须为 KEY=VALUE 格式: {item}")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"参数名不能为空: {item}")
        params[key] = value
    return params


def load_params(param_items: list[str], params_json: str = "", params_file: str = "", config: JsonDict | None = None) -> dict[str, str]:
    params: dict[str, str] = {}
    if params_file:
        params.update(json.loads(Path(params_file).read_text(encoding="utf-8")))
    if params_json:
        params.update(json.loads(params_json))
    params.update(parse_key_value(param_items))
    return {str(key): str(value) for key, value in params.items()}


def auth_headers(username: str = "", api_token: str = "") -> dict[str, str]:
    if not username and not api_token:
        return {}
    encoded = base64.b64encode(f"{username}:{api_token}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {encoded}"}


def request_json(url: str, username: str = "", api_token: str = "") -> JsonDict:
    request = urllib.request.Request(url, headers=auth_headers(username, api_token))
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def request_text(url: str, username: str = "", api_token: str = "") -> str:
    request = urllib.request.Request(url, headers=auth_headers(username, api_token))
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def post_url(url: str, username: str = "", api_token: str = "") -> JsonDict:
    request = urllib.request.Request(url, data=b"", headers=auth_headers(username, api_token), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            location = response.headers.get("Location", "")
            return {"httpStatus": response.status, "queueUrl": location}
    except urllib.error.HTTPError as error:
        location = error.headers.get("Location", "")
        if error.code in {200, 201, 302}:
            return {"httpStatus": error.code, "queueUrl": location}
        raise


def first_present(payload: JsonDict, names: list[str]) -> Any:
    for name in names:
        value = payload.get(name)
        if value not in (None, ""):
            return value
    return ""


def parse_body(body: Any) -> JsonDict:
    if not isinstance(body, str) or not body.strip():
        return {}
    stripped = body.strip()
    try:
        value = json.loads(stripped)
        return value if isinstance(value, dict) else {"body": value}
    except json.JSONDecodeError:
        parsed = urllib.parse.parse_qs(stripped, keep_blank_values=True)
        if parsed:
            return {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}
    return {"bodyText": body}


def parse_callback_record(line: str) -> JsonDict | None:
    try:
        raw = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(raw, dict):
        return None

    merged: JsonDict = dict(raw)
    merged.update(parse_body(raw.get("body")))

    path = str(raw.get("path") or "")
    query = urllib.parse.urlparse(path).query
    if query:
        for key, values in urllib.parse.parse_qs(query, keep_blank_values=True).items():
            merged.setdefault(key, values[0] if len(values) == 1 else values)

    build_number = first_present(merged, ["buildNumber", "BUILD_NUMBER", "build_number", "number"])
    result = first_present(merged, ["result", "RESULT", "buildResult", "status", "STATUS"])
    request_id = first_present(merged, ["requestId", "request_id", "REQUEST_ID", "id"])
    job_name = first_present(merged, ["jobName", "JOB_NAME", "job", "JOB"])
    build_url = first_present(merged, ["buildUrl", "BUILD_URL", "url"])
    artifacts = first_present(merged, ["artifacts", "artifactUrls", "artifact_urls", "artifactUrl", "downloadUrl"])
    if isinstance(artifacts, str) and artifacts.strip().startswith("["):
        try:
            artifacts = json.loads(artifacts)
        except json.JSONDecodeError:
            artifacts = [artifacts]
    elif isinstance(artifacts, str) and artifacts:
        artifacts = [artifacts]
    elif not artifacts:
        artifacts = []

    return {
        "requestId": str(request_id) if request_id else "",
        "jobName": str(job_name) if job_name else "",
        "buildNumber": str(build_number) if build_number else "",
        "buildUrl": str(build_url) if build_url else "",
        "result": str(result) if result else "",
        "artifacts": artifacts,
        "rawPayload": raw,
    }


def find_callback_result(
    callback_log: Path,
    request_id: str = "",
    build_number: str = "",
    job_name: str = "",
) -> JsonDict | None:
    if not callback_log.is_file():
        return None
    latest: JsonDict | None = None
    for line in callback_log.read_text(encoding="utf-8", errors="replace").splitlines():
        record = parse_callback_record(line.strip())
        if not record:
            continue
        if request_id and record.get("requestId") != request_id:
            continue
        if build_number and record.get("buildNumber") != str(build_number):
            continue
        if job_name and record.get("jobName") != job_name:
            continue
        latest = record
    return latest


def queue_build_url(queue_url: str, username: str = "", api_token: str = "") -> str:
    if not queue_url:
        return ""
    queue_api = queue_url.rstrip("/") + "/api/json"
    data = request_json(queue_api, username, api_token)
    executable = data.get("executable") if isinstance(data, dict) else None
    if isinstance(executable, dict):
        return str(executable.get("url") or "")
    return ""


def fetch_build_result(build_url: str, username: str = "", api_token: str = "", console_tail: int = 0) -> JsonDict:
    api_url = build_url.rstrip("/") + "/api/json?tree=number,result,building,url,duration,timestamp,artifacts[fileName,relativePath]"
    data = request_json(api_url, username, api_token)
    result: JsonDict = {
        "buildNumber": str(data.get("number") or ""),
        "buildUrl": data.get("url") or build_url,
        "building": bool(data.get("building")),
        "result": data.get("result") or "",
        "duration": data.get("duration") or 0,
        "timestamp": data.get("timestamp") or 0,
        "artifacts": data.get("artifacts") or [],
    }
    if console_tail > 0:
        console = request_text(build_url.rstrip("/") + "/consoleText", username, api_token)
        result["consoleTail"] = "\n".join(console.splitlines()[-console_tail:])
    return result


def wait_for_result(args: argparse.Namespace) -> int:
    deadline = time.time() + args.timeout
    build_url = args.build_url.strip()
    while time.time() <= deadline:
        callback = find_callback_result(
            Path(args.callback_log),
            request_id=args.request_id.strip(),
            build_number=args.build_number.strip(),
            job_name=args.job_name.strip(),
        ) if args.callback_log else None
        if callback and callback.get("result"):
            print(json.dumps({"source": "callback", "result": callback}, ensure_ascii=False, indent=2))
            return 0

        if not build_url and args.queue_url:
            build_url = queue_build_url(args.queue_url, args.username, args.api_token)

        if build_url:
            result = fetch_build_result(build_url, args.username, args.api_token, args.console_tail)
            if not result.get("building") and result.get("result"):
                print(json.dumps({"source": "jenkins", "result": result}, ensure_ascii=False, indent=2))
                return 0
        time.sleep(args.interval)

    print(json.dumps({"error": "timeout", "timeoutSeconds": args.timeout}, ensure_ascii=False, indent=2))
    return 2


def add_common_trigger_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", default="", help="Jenkins JSON 配置文件，只包含 jenkinsUrl/username/apiToken")
    parser.add_argument("--job-url", default="", help="完整 Jenkins build/buildWithParameters URL；优先级高于 --jenkins-url + --job-name")
    parser.add_argument("--jenkins-url", default="", help="Jenkins 根地址，也可由 JENKINS_URL 或配置文件提供")
    parser.add_argument("--job-name", default="", help="Jenkins job 名称，也可由 JOB_NAME 或配置文件提供；folder/job 用 / 分隔")
    parser.add_argument("--build-endpoint", default="buildWithParameters", help="构建端点，默认 buildWithParameters；无参数任务可用 build")
    parser.add_argument("--token", default="", help="Jenkins 远程触发 token，可为空")
    parser.add_argument("--callback-url", default="", help="传给 Jenkins 任务的回调地址")
    parser.add_argument("--callback-param", default="CALLBACK_URL", help="回调参数名，默认 CALLBACK_URL")
    parser.add_argument("--param", action="append", default=[], help="额外构建参数，格式 KEY=VALUE，可重复")
    parser.add_argument("--params-json", default="", help="额外构建参数 JSON 对象")
    parser.add_argument("--params-file", default="", help="额外构建参数 JSON 文件")


def main() -> int:
    parser = argparse.ArgumentParser(description="通用 Jenkins 远程构建触发与结果收集工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    url_parser = subparsers.add_parser("url", help="只生成远程构建 URL")
    add_common_trigger_args(url_parser)

    trigger_parser = subparsers.add_parser("trigger", help="触发 Jenkins 远程构建")
    add_common_trigger_args(trigger_parser)
    trigger_parser.add_argument("--username", default="", help="Jenkins 用户名，可为空")
    trigger_parser.add_argument("--api-token", default="", help="Jenkins API Token 或密码，可为空")
    trigger_parser.add_argument("--dry-run", action="store_true", help="只输出 URL，不触发")

    wait_parser = subparsers.add_parser("wait-result", help="等待 callback 或 Jenkins API 返回构建结果")
    wait_parser.add_argument("--config", default="", help="Jenkins JSON 配置文件，可包含 username/apiToken")
    wait_parser.add_argument("--callback-log", default="callback.log", help="callback_server.py 写入的日志文件")
    wait_parser.add_argument("--request-id", default="", help="按 requestId 过滤 callback")
    wait_parser.add_argument("--build-number", default="", help="按 buildNumber 过滤 callback")
    wait_parser.add_argument("--job-name", default="", help="按 jobName 过滤 callback")
    wait_parser.add_argument("--queue-url", default="", help="Jenkins queue URL，用于解析 build URL")
    wait_parser.add_argument("--build-url", default="", help="Jenkins build URL，用于 API 轮询")
    wait_parser.add_argument("--username", default="", help="Jenkins 用户名，可为空")
    wait_parser.add_argument("--api-token", default="", help="Jenkins API Token 或密码，可为空")
    wait_parser.add_argument("--timeout", type=int, default=1800, help="最长等待秒数")
    wait_parser.add_argument("--interval", type=int, default=10, help="轮询间隔秒数")
    wait_parser.add_argument("--console-tail", type=int, default=0, help="Jenkins 结果中附带 consoleText 末尾行数")

    args = parser.parse_args()
    if args.command in {"url", "trigger"}:
        config = load_jenkins_config(args.config)
        params = load_params(args.param, args.params_json, args.params_file, config)
        job_url = args.job_url.strip() or build_job_url(
            jenkins_url=resolve_value(args.jenkins_url, config, "jenkinsUrl", "JENKINS_URL"),
            job_name=resolve_value(args.job_name, config, "jobName", "JOB_NAME"),
            build_endpoint=args.build_endpoint,
        )
        token = resolve_value(args.token, config, "token", "TOKEN_NAME")
        trigger_url = build_trigger_url(job_url, token, args.callback_url, args.callback_param, params)
        if args.command == "url" or args.dry_run:
            print(trigger_url)
            return 0
        username = resolve_value(args.username, config, "username", "JENKINS_USER_NAME")
        api_token = resolve_value(args.api_token, config, "apiToken", "JENKINS_API_TOKEN")
        result = post_url(trigger_url, username, api_token)
        result["triggerUrl"] = trigger_url
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.command == "wait-result":
        config = load_jenkins_config(args.config)
        args.username = resolve_value(args.username, config, "username", "JENKINS_USER_NAME")
        args.api_token = resolve_value(args.api_token, config, "apiToken", "JENKINS_API_TOKEN")
        return wait_for_result(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
