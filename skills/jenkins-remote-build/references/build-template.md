# Jenkins Remote Build Template

## 参数化构建 URL

```text
https://jenkins.example.com/job/<job-name>/buildWithParameters?token=<token>&CALLBACK_URL=<urlencoded-callback-url>&BRANCH=main
```

## 无参数构建 URL

```text
https://jenkins.example.com/job/<job-name>/build?token=<token>
```

## 用户提供的 curl 形式

```bash
curl -X POST -u "USER_NAME:API_TOKEN" "JENKINS_URL/job/JOB_NAME/build?token=TOKEN_NAME"
```

对应 CLI：

```bash
python scripts/jenkins_remote_build.py trigger \
  --jenkins-url "$JENKINS_URL" \
  --job-name "$JOB_NAME" \
  --token "$TOKEN_NAME" \
  --username "$JENKINS_USER_NAME" \
  --api-token "$JENKINS_API_TOKEN"
```

默认 `--build-endpoint auto` 会读取 job 元数据；参数化任务会自动切到 `buildWithParameters`。

## 保存连接配置

```bash
python scripts/jenkins_remote_build.py save-config \
  --jenkins-url "$JENKINS_URL" \
  --username "$JENKINS_USER_NAME" \
  --api-token "$JENKINS_API_TOKEN"
```

默认保存到 `~/.config/jenkins-remote-build/config.json`，只保存连接字段，不保存 `JOB_NAME`、`TOKEN_NAME` 和构建参数。

## 查看参数默认值

```bash
python scripts/jenkins_remote_build.py job-info --job-name "$JOB_NAME"
```

输出示例：

```json
{
  "parameterDefaults": {
    "BUILD_BRANCH": "dev",
    "BIND_PACKAGE": "com.hotpotgames.happysave.global",
    "CALLBACK_URL": "",
    "JIAGU_MODE": "在线加固"
  },
  "autoBuildEndpoint": "buildWithParameters"
}
```

参数化 job 或最终端点是 `buildWithParameters`，且用户没有显式传 `--param` / `--params-json` / `--params-file` 时，不要直接触发；先展示可获取到的 `parameterDefaults`、`missingRequiredParameters` 和可选回复方式。如果用户回复 `使用默认参数构建`，Agent 再把默认参数全量展开成显式 `--param KEY=VALUE` 传入。如果用户只覆盖部分参数，Agent 先合并默认参数和覆盖参数，再把完整参数集全量展开为显式 `--param KEY=VALUE`。即使 Jenkins 元数据不可用、`parameterDefaults` 为空，也仍需用户显式传参。

推荐给用户的提示格式：

```text
已按 jenkins-remote-build skill 检查到 Jenkins job：

<JOB_NAME> 是参数化任务，默认参数为：

KEY=value

缺失必填参数：无 / <PARAM_NAME>

请选择：
- 使用默认参数构建
- 或给出覆盖参数：KEY=xxx
- 取消构建
```

如果是参数化构建，把 `--build-endpoint` 省略或设为 `buildWithParameters`，并追加：

```bash
--param BRANCH=main --param ENV=qa --callback-url "http://<host>:8000/callback?requestId=req-001"
```

## 配置文件示例

配置文件只保存 Jenkins 连接信息，不保存 `token`、`jobName` 或构建参数。

```json
{
  "jenkinsUrl": "https://jenkins.example.com",
  "username": "USER_NAME",
  "apiToken": "API_TOKEN"
}
```

`TOKEN_NAME`、`JOB_NAME` 和构建参数需运行时传入，例如：

```bash
python scripts/jenkins_remote_build.py trigger \
  --config jenkins.config.json \
  --job-name "$JOB_NAME" \
  --token "$TOKEN_NAME" \
  --param BRANCH=main \
  --param ENV=qa
```

连接信息也可以用环境变量：`JENKINS_URL`、`JENKINS_USER_NAME`、`JENKINS_API_TOKEN`。

## 本地 callback

```bash
python scripts/callback_server.py --host 0.0.0.0 --port 8000 --log-file callback.log
```

Jenkins 可访问的 callback 示例：

```text
http://<本机可访问IP>:8000/callback?requestId=<唯一请求ID>
```

一键模式：

```bash
python scripts/jenkins_remote_build.py run \
  --job-name "$JOB_NAME" \
  --token "$TOKEN_NAME" \
  --param BUILD_BRANCH=dev \
  --param BIND_PACKAGE=com.hotpotgames.happysave.global \
  --param JIAGU_MODE=在线加固 \
  --callback-public-base "http://<本机可访问IP>:8000" \
  --console-tail 120
```

`run` 会启动本地 callback 服务、生成 requestId、触发构建、等待 callback/Jenkins API 结果并关闭 callback 服务。

## 推荐 callback JSON

```json
{
  "requestId": "req-001",
  "jobName": "demo",
  "buildNumber": "42",
  "buildUrl": "https://jenkins.example.com/job/demo/42/",
  "result": "SUCCESS",
  "artifacts": ["https://example.com/artifact.zip"]
}
```

`jenkins_remote_build.py wait-result` 会从 callback 日志中归一化 `requestId`、`jobName`、`buildNumber`、`buildUrl`、`result` 和 `artifacts` 字段。
