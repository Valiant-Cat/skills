#!/usr/bin/env python3
import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="通用 callback 接收服务：记录 GET/POST 请求到 JSONL 日志")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--log-file", default="callback.log")
    args = parser.parse_args()

    log_path = Path(args.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    class Handler(BaseHTTPRequestHandler):
        def write_log(self, payload):
            payload["receivedAt"] = int(time.time() * 1000)
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

        def respond_ok(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

        def do_GET(self):
            self.write_log({"method": "GET", "path": self.path, "headers": dict(self.headers)})
            self.respond_ok()

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8", errors="replace") if length else ""
            self.write_log({"method": "POST", "path": self.path, "headers": dict(self.headers), "body": body})
            self.respond_ok()

        def log_message(self, format, *args):
            return

    HTTPServer((args.host, args.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
