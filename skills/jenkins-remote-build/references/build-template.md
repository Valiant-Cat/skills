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
  --build-endpoint build \
  --token "$TOKEN_NAME" \
  --username "$JENKINS_USER_NAME" \
  --api-token "$JENKINS_API_TOKEN"
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
