#!/usr/bin/env python3
import argparse
import base64
import os
import json
import subprocess
import sys
import tempfile
import time
import uuid
import urllib.error
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


def default_config_path() -> Path:
    return Path.home() / ".config" / "jenkins-remote-build" / "config.json"


def first_config_value(config: JsonDict, canonical_key: str) -> Any:
    for key in CONFIG_ALIASES.get(canonical_key, [canonical_key]):
        value = config.get(key)
        if value not in (None, ""):
            return value
    return ""


def read_config_file(config_file: Path) -> JsonDict:
    loaded = json.loads(config_file.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("Jenkins 配置文件必须是 JSON 对象")
    config: JsonDict = {}
    for canonical_key in CONFIG_FILE_KEYS:
        value = first_config_value(loaded, canonical_key)
        if value not in (None, ""):
            config[canonical_key] = value
    return config


def load_jenkins_config(
    config_file: str = "",
    env: dict[str, str] | None = None,
    default_config: Path | None = None,
) -> JsonDict:
    config: JsonDict = {}
    config_path = Path(config_file).expanduser() if config_file else (default_config or default_config_path())
    if config_path.is_file():
        config.update(read_config_file(config_path))
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


def save_jenkins_config(config_file: str, jenkins_url: str, username: str, api_token: str) -> Path:
    path = Path(config_file).expanduser() if config_file else default_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "jenkinsUrl": jenkins_url.rstrip("/") + "/" if jenkins_url else "",
        "username": username,
        "apiToken": api_token,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return path


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


def build_job_base_url(jenkins_url: str, job_name: str) -> str:
    base = jenkins_url.strip().rstrip("/")
    if not base:
        raise ValueError("缺少 JENKINS_URL，请传 --jenkins-url、--config 或环境变量 JENKINS_URL")
    if not job_name.strip():
        raise ValueError("缺少 JOB_NAME，请传 --job-name、--config 或环境变量 JOB_NAME")
    job_path = "/".join(f"job/{urllib.parse.quote(part, safe='')}" for part in job_name.strip("/").split("/") if part)
    return f"{base}/{job_path}"


def job_api_url(jenkins_url: str, job_name: str) -> str:
    tree = "name,url,buildable,property[parameterDefinitions[name,type,defaultParameterValue[value]]],actions[parameterDefinitions[name,type,defaultParameterValue[value]]]"
    return build_job_base_url(jenkins_url, job_name) + "/api/json?tree=" + urllib.parse.quote(tree, safe=",[]")


def fetch_job_metadata(jenkins_url: str, job_name: str, username: str = "", api_token: str = "") -> JsonDict:
    return request_json(job_api_url(jenkins_url, job_name), username, api_token)


def iter_parameter_definitions(metadata: JsonDict) -> list[JsonDict]:
    definitions: list[JsonDict] = []
    for section_name in ("property", "actions"):
        sections = metadata.get(section_name) or []
        if not isinstance(sections, list):
            continue
        for section in sections:
            if not isinstance(section, dict):
                continue
            values = section.get("parameterDefinitions") or []
            if isinstance(values, list):
                definitions.extend(value for value in values if isinstance(value, dict))
    return definitions


def extract_parameter_defaults(metadata: JsonDict) -> dict[str, str]:
    defaults: dict[str, str] = {}
    for definition in iter_parameter_definitions(metadata):
        name = str(definition.get("name") or "")
        if not name:
            continue
        default_value = definition.get("defaultParameterValue")
        value = ""
        if isinstance(default_value, dict):
            value = default_value.get("value", "")
        defaults[name] = "" if value is None else str(value)
    return defaults


def infer_missing_required_parameters(metadata: JsonDict, parameter_defaults: dict[str, str]) -> list[str]:
    missing: list[str] = []
    optional_names = {"REMARK", "CALLBACK_URL"}
    optional_types = {"BooleanParameterDefinition"}
    for definition in iter_parameter_definitions(metadata):
        name = str(definition.get("name") or "")
        if not name or name in optional_names:
            continue
        param_type = str(definition.get("type") or definition.get("_class") or "")
        if any(optional_type in param_type for optional_type in optional_types):
            continue
        has_default = "defaultParameterValue" in definition
        default_value = parameter_defaults.get(name, "")
        if not has_default or default_value == "":
            missing.append(name)
    return missing


def cli_param_args(params: dict[str, str]) -> list[str]:
    return [f"--param {key}={value}" for key, value in params.items()]


def build_parameter_prompt(
    job_name: str,
    build_endpoint: str,
    parameter_defaults: dict[str, str],
    missing_required: list[str] | None = None,
) -> JsonDict:
    names = list(parameter_defaults.keys())
    override_examples = [f"{name}=xxx" for name in names]
    return {
        "jobName": job_name,
        "buildEndpoint": build_endpoint,
        "defaultBuildParams": parameter_defaults,
        "missingRequiredParameters": missing_required or [],
        "allowedUserReplies": [
            "使用默认参数构建",
            "覆盖一个或多个参数，例如 BUILD_BRANCH=xxx",
            "取消构建",
        ],
        "overrideExamples": override_examples,
        "defaultParamsAsCliArgs": cli_param_args(parameter_defaults),
        "agentInstruction": "必须等待用户选择。用户选择默认参数时，将 defaultBuildParams 全量展开为显式 --param；用户给出覆盖参数时，用覆盖值合并默认值后再全量展开为显式 --param。",
    }


def resolve_build_endpoint(requested_endpoint: str, metadata: JsonDict | None = None) -> str:
    requested = (requested_endpoint or "auto").strip("/")
    if requested == "auto" and not metadata:
        return "buildWithParameters"
    has_parameters = bool(iter_parameter_definitions(metadata or {}))
    if requested in {"auto", "build"} and has_parameters:
        return "buildWithParameters"
    if requested == "auto":
        return "build"
    return requested or "buildWithParameters"


def user_supplied_parameters(args: argparse.Namespace) -> bool:
    return bool(args.param or args.params_json or args.params_file)


def default_parameter_confirmation_required(args: argparse.Namespace, metadata: JsonDict, build_endpoint: str = "") -> bool:
    if user_supplied_parameters(args):
        return False
    if build_endpoint == "buildWithParameters":
        return True
    return bool(iter_parameter_definitions(metadata))


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


def load_params(
    param_items: list[str],
    params_json: str = "",
    params_file: str = "",
    config: JsonDict | None = None,
    default_params: dict[str, str] | None = None,
) -> dict[str, str]:
    params: dict[str, str] = dict(default_params or {})
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


def http_error_result(error: urllib.error.HTTPError) -> JsonDict:
    return {
        "httpStatus": error.code,
        "reason": error.reason,
        "body": error.read().decode("utf-8", errors="replace")[:4000],
    }


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


def redacted_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    redacted = []
    for key, value in urllib.parse.parse_qsl(parts.query, keep_blank_values=True):
        if key.lower() in {"token", "api_token", "apitoken", "password"}:
            value = "***"
        redacted.append((key, value))
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(redacted), parts.fragment))


def prepare_trigger(args: argparse.Namespace) -> JsonDict:
    config = load_jenkins_config(args.config)
    username = resolve_value(getattr(args, "username", ""), config, "username", "JENKINS_USER_NAME")
    api_token = resolve_value(getattr(args, "api_token", ""), config, "apiToken", "JENKINS_API_TOKEN")
    jenkins_url = resolve_value(args.jenkins_url, config, "jenkinsUrl", "JENKINS_URL")
    job_name = resolve_value(args.job_name, config, "jobName", "JOB_NAME")

    metadata: JsonDict = {}
    if not args.job_url.strip() and jenkins_url and job_name:
        try:
            metadata = fetch_job_metadata(jenkins_url, job_name, username, api_token)
        except Exception:
            metadata = {}

    build_endpoint = args.build_endpoint
    if not args.job_url.strip():
        build_endpoint = resolve_build_endpoint(args.build_endpoint, metadata)

    default_params = extract_parameter_defaults(metadata) if not getattr(args, "no_default_params", False) else {}
    if default_parameter_confirmation_required(args, metadata, build_endpoint):
        missing_required = infer_missing_required_parameters(metadata, default_params)
        return {
            "confirmationRequired": True,
            "reason": "job has parameters but no user-supplied parameters were provided",
            "buildEndpoint": build_endpoint,
            "parameterDefaults": default_params,
            "parameterPrompt": build_parameter_prompt(job_name, build_endpoint, default_params, missing_required),
            "jobName": job_name,
        }
    if args.callback_url and args.callback_param in default_params:
        default_params.pop(args.callback_param)
    params = load_params(args.param, args.params_json, args.params_file, default_params=default_params)
    job_url = args.job_url.strip() or build_job_url(jenkins_url=jenkins_url, job_name=job_name, build_endpoint=build_endpoint)
    token = resolve_value(args.token, config, "token", "TOKEN_NAME")
    trigger_url = build_trigger_url(job_url, token, args.callback_url, args.callback_param, params)
    return {
        "triggerUrl": trigger_url,
        "username": username,
        "apiToken": api_token,
        "buildEndpoint": build_endpoint,
        "jobMetadata": metadata,
        "parameterDefaults": default_params,
        "parameters": params,
        "jobName": job_name,
    }


def print_confirmation_required(prepared: JsonDict) -> int:
    print(json.dumps({
        "confirmationRequired": True,
        "reason": prepared.get("reason", ""),
        "jobName": prepared.get("jobName", ""),
        "buildEndpoint": prepared.get("buildEndpoint", ""),
        "parameterDefaults": prepared.get("parameterDefaults", {}),
        "parameterPrompt": prepared.get("parameterPrompt", {}),
        "nextStep": "请把 parameterPrompt 展示给用户。用户选择默认参数时，将 defaultBuildParams 全量展开为显式 --param；用户覆盖部分参数时，先合并默认值和覆盖值，再全量展开为显式 --param。",
    }, ensure_ascii=False, indent=2))
    return 3


def start_callback_server(host: str, port: int, log_file: str) -> subprocess.Popen:
    script = Path(__file__).with_name("callback_server.py")
    return subprocess.Popen(
        [sys.executable, str(script), "--host", host, "--port", str(port), "--log-file", log_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def run_trigger_and_wait(args: argparse.Namespace) -> int:
    request_id = args.request_id or f"jenkins-{uuid.uuid4().hex}"
    callback_log = args.callback_log or str(Path(tempfile.gettempdir()) / f"jenkins-remote-build-{request_id}.jsonl")
    callback_process: subprocess.Popen | None = None
    if not args.no_callback:
        callback_process = start_callback_server(args.callback_host, args.callback_port, callback_log)
        time.sleep(args.callback_startup_delay)
        if not args.callback_url:
            callback_base = args.callback_public_base.rstrip("/")
            args.callback_url = f"{callback_base}/callback?requestId={urllib.parse.quote(request_id)}"
    try:
        prepared = prepare_trigger(args)
        if prepared.get("confirmationRequired"):
            return print_confirmation_required(prepared)
        result = post_url(prepared["triggerUrl"], prepared["username"], prepared["apiToken"])
        result.update(
            {
                "triggerUrl": redacted_url(prepared["triggerUrl"]),
                "buildEndpoint": prepared["buildEndpoint"],
                "requestId": request_id,
                "callbackLog": callback_log,
                "parameters": prepared["parameters"],
            }
        )
        print(json.dumps({"trigger": result}, ensure_ascii=False, indent=2))

        wait_args = argparse.Namespace(
            config=args.config,
            callback_log=callback_log,
            request_id=request_id,
            build_number="",
            job_name=prepared["jobName"],
            queue_url=result.get("queueUrl", ""),
            build_url="",
            username=prepared["username"],
            api_token=prepared["apiToken"],
            timeout=args.timeout,
            interval=args.interval,
            console_tail=args.console_tail,
        )
        return wait_for_result(wait_args)
    finally:
        if callback_process:
            callback_process.terminate()
            try:
                callback_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                callback_process.kill()


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
    parser.add_argument("--build-endpoint", default="auto", help="构建端点，默认 auto；参数化任务自动使用 buildWithParameters")
    parser.add_argument("--token", default="", help="Jenkins 远程触发 token，可为空")
    parser.add_argument("--callback-url", default="", help="传给 Jenkins 任务的回调地址")
    parser.add_argument("--callback-param", default="CALLBACK_URL", help="回调参数名，默认 CALLBACK_URL")
    parser.add_argument("--param", action="append", default=[], help="额外构建参数，格式 KEY=VALUE，可重复")
    parser.add_argument("--params-json", default="", help="额外构建参数 JSON 对象")
    parser.add_argument("--params-file", default="", help="额外构建参数 JSON 文件")
    parser.add_argument("--no-default-params", action="store_true", help="不从 Jenkins job 参数定义中自动带入默认值")


def main() -> int:
    parser = argparse.ArgumentParser(description="通用 Jenkins 远程构建触发与结果收集工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    save_parser = subparsers.add_parser("save-config", help="保存用户级 Jenkins 连接配置")
    save_parser.add_argument("--config", default="", help="保存路径，默认 ~/.config/jenkins-remote-build/config.json")
    save_parser.add_argument("--jenkins-url", default="", help="Jenkins 根地址")
    save_parser.add_argument("--username", default="", help="Jenkins 用户名")
    save_parser.add_argument("--api-token", default="", help="Jenkins API Token 或密码")

    info_parser = subparsers.add_parser("job-info", help="读取 Jenkins job 元数据和参数默认值")
    info_parser.add_argument("--config", default="", help="Jenkins JSON 配置文件，只包含 jenkinsUrl/username/apiToken")
    info_parser.add_argument("--jenkins-url", default="", help="Jenkins 根地址")
    info_parser.add_argument("--job-name", default="", help="Jenkins job 名称")
    info_parser.add_argument("--username", default="", help="Jenkins 用户名，可为空")
    info_parser.add_argument("--api-token", default="", help="Jenkins API Token 或密码，可为空")

    url_parser = subparsers.add_parser("url", help="只生成远程构建 URL")
    add_common_trigger_args(url_parser)

    trigger_parser = subparsers.add_parser("trigger", help="触发 Jenkins 远程构建")
    add_common_trigger_args(trigger_parser)
    trigger_parser.add_argument("--username", default="", help="Jenkins 用户名，可为空")
    trigger_parser.add_argument("--api-token", default="", help="Jenkins API Token 或密码，可为空")
    trigger_parser.add_argument("--dry-run", action="store_true", help="只输出 URL，不触发")

    run_parser = subparsers.add_parser("run", help="一键触发 Jenkins 构建，自动启动 callback 并等待结果")
    add_common_trigger_args(run_parser)
    run_parser.add_argument("--username", default="", help="Jenkins 用户名，可为空")
    run_parser.add_argument("--api-token", default="", help="Jenkins API Token 或密码，可为空")
    run_parser.add_argument("--request-id", default="", help="callback requestId，默认自动生成")
    run_parser.add_argument("--callback-host", default="0.0.0.0", help="本地 callback 监听地址")
    run_parser.add_argument("--callback-port", type=int, default=8000, help="本地 callback 监听端口")
    run_parser.add_argument("--callback-public-base", default="http://127.0.0.1:8000", help="Jenkins 可访问的 callback 基础地址")
    run_parser.add_argument("--callback-log", default="", help="callback JSONL 日志路径，默认临时文件")
    run_parser.add_argument("--callback-startup-delay", type=float, default=0.3, help="callback 服务启动等待秒数")
    run_parser.add_argument("--no-callback", action="store_true", help="不启动 callback，仅用 Jenkins API 等待结果")
    run_parser.add_argument("--timeout", type=int, default=1800, help="最长等待秒数")
    run_parser.add_argument("--interval", type=int, default=10, help="轮询间隔秒数")
    run_parser.add_argument("--console-tail", type=int, default=80, help="Jenkins 结果中附带 consoleText 末尾行数")

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
    if args.command == "save-config":
        config = load_jenkins_config(args.config)
        jenkins_url = resolve_value(args.jenkins_url, config, "jenkinsUrl", "JENKINS_URL")
        username = resolve_value(args.username, config, "username", "JENKINS_USER_NAME")
        api_token = resolve_value(args.api_token, config, "apiToken", "JENKINS_API_TOKEN")
        path = save_jenkins_config(args.config, jenkins_url, username, api_token)
        print(json.dumps({"configPath": str(path), "savedKeys": sorted(CONFIG_FILE_KEYS)}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "job-info":
        config = load_jenkins_config(args.config)
        username = resolve_value(args.username, config, "username", "JENKINS_USER_NAME")
        api_token = resolve_value(args.api_token, config, "apiToken", "JENKINS_API_TOKEN")
        jenkins_url = resolve_value(args.jenkins_url, config, "jenkinsUrl", "JENKINS_URL")
        job_name = resolve_value(args.job_name, config, "jobName", "JOB_NAME")
        try:
            metadata = fetch_job_metadata(jenkins_url, job_name, username, api_token)
        except urllib.error.HTTPError as error:
            print(json.dumps({"error": "job-info failed", "jenkins": http_error_result(error)}, ensure_ascii=False, indent=2))
            return 2
        defaults = extract_parameter_defaults(metadata)
        print(json.dumps({
            "name": metadata.get("name", ""),
            "url": metadata.get("url", ""),
            "buildable": metadata.get("buildable", None),
            "parameterDefaults": defaults,
            "autoBuildEndpoint": resolve_build_endpoint("auto", metadata),
        }, ensure_ascii=False, indent=2))
        return 0
    if args.command in {"url", "trigger"}:
        prepared = prepare_trigger(args)
        if prepared.get("confirmationRequired"):
            return print_confirmation_required(prepared)
        trigger_url = prepared["triggerUrl"]
        if args.command == "url" or args.dry_run:
            print(redacted_url(trigger_url))
            return 0
        result = post_url(trigger_url, prepared["username"], prepared["apiToken"])
        result["triggerUrl"] = redacted_url(trigger_url)
        result["buildEndpoint"] = prepared["buildEndpoint"]
        result["parameters"] = prepared["parameters"]
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.command == "run":
        return run_trigger_and_wait(args)
    if args.command == "wait-result":
        config = load_jenkins_config(args.config)
        args.username = resolve_value(args.username, config, "username", "JENKINS_USER_NAME")
        args.api_token = resolve_value(args.api_token, config, "apiToken", "JENKINS_API_TOKEN")
        return wait_for_result(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
