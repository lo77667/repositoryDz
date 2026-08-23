#!/usr/bin/env python3
"""Deterministic local mock for testing the Phase 4 LLM pipeline."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


class Handler(BaseHTTPRequestHandler):
    responses: list[str] = []
    cursor = 0

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        if self.path.rstrip("/") != "/chat/completions":
            self.send_error(404)
            return
        if Handler.cursor >= len(Handler.responses):
            encoded = b'{"error":{"message":"mock response queue exhausted"}}'
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return
        content = Handler.responses[Handler.cursor]
        Handler.cursor += 1
        body = {"choices": [{"message": {"role": "assistant", "content": content}}]}
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--responses", type=Path, required=True, help="JSON array of response content strings")
    args = parser.parse_args()
    Handler.responses = json.loads(args.responses.read_text(encoding="utf-8"))
    if not isinstance(Handler.responses, list) or not all(isinstance(item, str) for item in Handler.responses):
        raise SystemExit("responses file must contain a JSON array of strings")
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    print(f"mock LLM listening on {args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
