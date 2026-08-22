#!/usr/bin/env python3
"""Generate, verify, repair, and accept an LLM HTML candidate without publishing it."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from generate_html_with_llm import request_candidate, build_prompt, DEFAULT_BASE_URL, DEFAULT_MODEL
from validate_generated_html import validate

ROOT = Path(__file__).resolve().parents[1]
MAX_REPAIR_ATTEMPTS = 2


def browser_errors(path: Path) -> list[str]:
    command = [sys.executable, str(ROOT / "automation/verify_generated_browser.py"), str(path)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        return []
    try:
        payload = json.loads(result.stdout.strip().splitlines()[-1])
        failures: list[str] = []
        failures.extend(f"console error: {item}" for item in payload.get("console_errors", []))
        failures.extend(f"page error: {item}" for item in payload.get("page_errors", []))
        failures.extend(f"network request: {item}" for item in payload.get("network_requests", []))
        if payload.get("failure"):
            failures.append(str(payload["failure"]))
        return failures or [result.stderr.strip() or "Headless browser verification failed"]
    except (json.JSONDecodeError, IndexError):
        return [result.stderr.strip() or "Headless browser verification failed"]


def verify(path: Path) -> list[str]:
    static_errors = validate(path)
    if static_errors:
        return static_errors
    return browser_errors(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--idea-json", required=True)
    parser.add_argument("--period", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-repairs", type=int, default=MAX_REPAIR_ATTEMPTS)
    args = parser.parse_args()

    api_key = os.environ.get("LLM_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("LLM_API_KEY is missing")
    base_url = os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    idea = json.loads(args.idea_json)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(idea, args.period)
    repair_context: str | None = None
    attempts = 0
    history: list[dict[str, object]] = []

    while attempts <= args.max_repairs:
        attempts += 1
        try:
            candidate = request_candidate(api_key, base_url, model, prompt, repair_context)
            output.write_text(candidate + "\n", encoding="utf-8")
            failures = verify(output)
        except Exception as exc:  # A provider failure is recorded and handled by the caller.
            failures = [str(exc)]
        history.append({"attempt": attempts, "failures": failures})
        if not failures:
            result = {"status": "accepted", "attempts": attempts, "path": str(output), "model": model, "history": history}
            print(json.dumps(result, ensure_ascii=False))
            return
        repair_context = "\n".join(f"- {failure}" for failure in failures[:20])

    result = {"status": "rejected", "attempts": attempts, "path": str(output), "model": model, "history": history}
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(2)


if __name__ == "__main__":
    main()
