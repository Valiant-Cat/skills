---
name: jenkins-remote-build
description: 通用 Jenkins 远程构建执行与结果收集。用于用户需要触发任意 Jenkins build/buildWithParameters 任务、传入 CALLBACK_URL、启动本地 callback 服务、等待 Jenkins 构建完成、从 callback 日志或 Jenkins API 获取构建结果、构建号、构建 URL、产物和状态时。
---

# Jenkins Remote Build

## 功能边界

本 skill 只负责通用 Jenkins 远程构建链路：

- 启动本地 HTTP callback 服务并记录 JSONL 日志
- 生成 Jenkins `build` / `buildWithParameters` 远程触发 URL
- 通过 token、用户名/API Token 和参数触发 Jenkins 构建
- 将 `CALLBACK_URL` 或自定义回调参数传给 Jenkins job
- 等待 callback 日志或 Jenkins API 返回构建结果
- 输出结构化 JSON 结果，包含构建状态、构建号、构建 URL、产物、耗时等信息

不要在本 skill 中执行业务专用逻辑，例如下载特定业务产物、替换项目依赖、修改源码、修改构建配置或写业务接入信息。

## 前置条件

- Jenkins job 已允许远程触发，或当前账号具备触发权限。
- 如需 callback，Jenkins job/pipeline 必须显式读取 `CALLBACK_URL` 参数并在结束时请求该 URL；Jenkins 本身不会自动调用该参数。
- 如果本机 callback 要被 Jenkins 访问，确认网络可达：同网段 IP、内网穿透、反向代理或 Jenkins 节点可访问的地址。
- Jenkins 需要鉴权时，使用 `--username` 与 `--api-token`，不要把凭据写进 skill 文档或仓库文件。

## 用户需要提供的信息

最少需要用户提供以下内容：

1. Jenkins 鉴权信息：`USER_NAME` 与 `API_TOKEN`。
2. 构建入口与参数：`JENKINS_URL`、`JOB_NAME`、`TOKEN_NAME`，以及所有构建参数。

等价 curl 形式为：

```bash
curl -X POST -u "USER_NAME:API_TOKEN" "JENKINS_URL/job/JOB_NAME/build?token=TOKEN_NAME"
```

可以把 Jenkins 连接信息放在配置文件或环境变量中，但构建相关内容必须运行时提供：

- 配置字段只允许：`jenkinsUrl`、`username`、`apiToken`。
- 不要从配置文件加载：`token`、`jobName`、`params` / `parameters`。
- 环境变量：`JENKINS_URL`、`JENKINS_USER_NAME`、`JENKINS_API_TOKEN`、`TOKEN_NAME`、`JOB_NAME`。
- 运行时参数优先级最高，其次配置文件中的连接信息，最后环境变量。

## 推荐流程

1. 明确 Jenkins 构建入口：
   - 无参数任务通常是 `https://jenkins.example.com/job/<job>/build`
   - 参数化任务通常是 `https://jenkins.example.com/job/<job>/buildWithParameters`
2. 启动 callback 服务：

```bash
python scripts/callback_server.py --host 0.0.0.0 --port 8000 --log-file callback.log
```

3. 准备 Jenkins 可访问的 callback 地址，例如：

```text
http://<本机可访问IP>:8000/callback?requestId=<唯一请求ID>
```

4. 先生成并检查触发 URL：

```bash
python scripts/jenkins_remote_build.py url \
  --jenkins-url "https://jenkins.example.com" \
  --job-name "demo" \
  --token "<jenkins-trigger-token>" \
  --callback-url "http://<本机可访问IP>:8000/callback?requestId=req-001" \
  --param BRANCH=main \
  --param ENV=qa
```

5. 触发构建：

```bash
python scripts/jenkins_remote_build.py trigger \
  --jenkins-url "https://jenkins.example.com" \
  --job-name "demo" \
  --token "<jenkins-trigger-token>" \
  --callback-url "http://<本机可访问IP>:8000/callback?requestId=req-001" \
  --param BRANCH=main \
  --param ENV=qa
```

如果 Jenkins 需要登录：

```bash
python scripts/jenkins_remote_build.py trigger \
  --jenkins-url "https://jenkins.example.com" \
  --job-name "demo" \
  --username "$JENKINS_USER" \
  --api-token "$JENKINS_API_TOKEN" \
  --callback-url "http://<本机可访问IP>:8000/callback?requestId=req-001" \
  --param BRANCH=main
```

如果 job 是无参数任务，使用 `--build-endpoint build`，等价于用户提供的 curl 中 `/build?token=TOKEN_NAME`：

```bash
python scripts/jenkins_remote_build.py trigger \
  --jenkins-url "$JENKINS_URL" \
  --job-name "$JOB_NAME" \
  --build-endpoint build \
  --token "$TOKEN_NAME" \
  --username "$JENKINS_USER_NAME" \
  --api-token "$JENKINS_API_TOKEN"
```

也可以使用配置文件：

```json
{
  "jenkinsUrl": "https://jenkins.example.com",
  "username": "USER_NAME",
  "apiToken": "API_TOKEN"
}
```

```bash
python scripts/jenkins_remote_build.py trigger \
  --config jenkins.config.json \
  --job-name "$JOB_NAME" \
  --token "$TOKEN_NAME" \
  --param BRANCH=main \
  --param ENV=qa \
  --callback-url "http://<本机可访问IP>:8000/callback?requestId=req-001"
```

6. 等待结果，优先使用 callback 日志；如果触发响应拿到 `queueUrl` 或已知 `buildUrl`，可同时启用 Jenkins API 兜底：

```bash
python scripts/jenkins_remote_build.py wait-result \
  --callback-log callback.log \
  --request-id req-001 \
  --queue-url "https://jenkins.example.com/queue/item/123/" \
  --timeout 1800 \
  --interval 10
```

或者：

```bash
python scripts/jenkins_remote_build.py wait-result \
  --callback-log callback.log \
  --request-id req-001 \
  --build-url "https://jenkins.example.com/job/demo/42/" \
  --console-tail 80
```

## Jenkins Callback 约定

推荐 Jenkins job 在 `post` 阶段向 `CALLBACK_URL` 发送 JSON：

```groovy
post {
  always {
    script {
      if (params.CALLBACK_URL?.trim()) {
        def payload = groovy.json.JsonOutput.toJson([
          requestId: params.REQUEST_ID ?: '',
          jobName: env.JOB_NAME,
          buildNumber: env.BUILD_NUMBER,
          buildUrl: env.BUILD_URL,
          result: currentBuild.currentResult,
          artifacts: []
        ])
        sh """curl -sS -X POST -H 'Content-Type: application/json' --data '${payload}' '${params.CALLBACK_URL}' || true"""
      }
    }
  }
}
```

如果无法修改 pipeline，也可以只依赖 Jenkins API 轮询 `queueUrl` 或 `buildUrl`。

## 脚本说明

- `scripts/callback_server.py`：启动本地 HTTP 服务，记录所有 GET/POST 到 JSONL 日志。
- `scripts/jenkins_remote_build.py url`：只生成 URL，不触发构建。
- `scripts/jenkins_remote_build.py trigger`：触发 Jenkins 构建，输出 HTTP 状态、`queueUrl` 和触发 URL。
- `scripts/jenkins_remote_build.py wait-result`：等待 callback 或 Jenkins API 结果，输出结构化 JSON。

常用参数：

- `--job-url`：Jenkins `build` / `buildWithParameters` 地址。
- `--jenkins-url`：Jenkins 根地址；可由配置文件 `jenkinsUrl` 或环境变量 `JENKINS_URL` 提供。
- `--job-name`：Jenkins job 名；多级 folder 用 `/` 分隔；运行时传入，或由环境变量 `JOB_NAME` 提供。
- `--build-endpoint`：构建端点，默认 `buildWithParameters`；无参数任务使用 `build`。
- `--config`：Jenkins JSON 配置文件，只支持 `jenkinsUrl`、`username`、`apiToken`。
- `--token`：Jenkins 远程触发 token，可为空。
- `--callback-url`：传给 Jenkins job 的回调地址。
- `--callback-param`：回调参数名，默认 `CALLBACK_URL`。
- `--param KEY=VALUE`：构建参数，可重复。
- `--params-json` / `--params-file`：批量传入构建参数。
- `--username` / `--api-token`：Jenkins Basic Auth 凭据。

## 安全规则

- 不要硬编码 Jenkins 用户名、密码、API Token 或内网地址到仓库文件。
- 配置文件只保存 Jenkins 连接信息，不保存 `token`、`jobName` 或构建参数。
- 不要重复触发同一构建，除非用户明确要求重新触发。
- callback 日志必须按 `requestId`、`buildNumber` 或 `jobName` 过滤，不能盲取最后一行。
- 触发前先用 `url` 子命令展示最终 URL，确认参数、token 和 callback 编码正确。
- 如果 callback 超时，先检查 Jenkins 是否真的调用了 `CALLBACK_URL`，再用 Jenkins API 轮询兜底。
