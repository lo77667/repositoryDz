#!/usr/bin/env python3
"""Try configured LLM providers in order, then let the caller use deterministic fallback."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from generate_and_verify import verify
from generate_html_with_llm import DEFAULT_BASE_URL, DEFAULT_MODEL, build_prompt, request_candidate
from period_utils import require_period

MAX_REPAIRS = 2


def configured_providers() -> list[dict[str, str]]:
    return [
        {
            "name": "gemini",
            "key": os.environ.get("LLM_API_KEY", "").strip(),
            "base_url": os.environ.get("LLM_BASE_URL", "").strip() or DEFAULT_BASE_URL,
            "model": os.environ.get("LLM_MODEL", "").strip() or DEFAULT_MODEL,
        },
        {
            "name": "groq",
            "key": os.environ.get("LLM_FALLBACK_API_KEY", "").strip(),
            "base_url": os.environ.get("LLM_FALLBACK_BASE_URL", "").strip() or "https://api.groq.com/openai/v1",
            "model": os.environ.get("LLM_FALLBACK_MODEL", "").strip() or "openai/gpt-oss-20b",
        },
        {
            "name": "mistral",
            "key": os.environ.get("LLM_SECONDARY_API_KEY", "").strip(),
            "base_url": os.environ.get("LLM_SECONDARY_BASE_URL", "").strip() or "https://api.mistral.ai/v1",
            "model": os.environ.get("LLM_SECONDARY_MODEL", "").strip() or "mistral-small-latest",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--idea-json", required=True)
    parser.add_argument("--period", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-repairs", type=int, default=MAX_REPAIRS)
    args = parser.parse_args()

    try:
        period = require_period(args.period)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    idea = json.loads(args.idea_json)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise RuntimeError(f"Refusing to overwrite an existing artifact: {output}")
    candidate_path = output.with_name(f".{output.stem}.provider-candidate.html")
    prompt = build_prompt(idea, period)
    history: list[dict[str, object]] = []
    provider_attempted = False

    providers = configured_providers()
    if os.environ.get("PHASE5_FORCE_PRIMARY_FAILURE", "").lower() in {"1", "true", "yes"} and providers:
        providers[0] = {**providers[0], "base_url": "http://127.0.0.1:9", "model": "forced-primary-failure"}

    for provider in providers:
        if not provider["key"]:
            history.append({"provider": provider["name"], "status": "skipped", "reason": "not configured"})
            continue
        provider_attempted = True
        repair_context: str | None = None
        provider_history: list[dict[str, object]] = []
        for attempt in range(1, args.max_repairs + 2):
            try:
                candidate = request_candidate(
                    provider["key"], provider["base_url"], provider["model"], prompt, repair_context, provider["name"]
                )
                candidate_path.write_text(candidate + "\n", encoding="utf-8")
                failures = verify(candidate_path)
            except Exception as exc:  # Provider failures move immediately to the next configured provider.
                provider_history.append({"attempt": attempt, "failures": [str(exc)], "provider_error": True})
                break
            provider_history.append({"attempt": attempt, "failures": failures})
            if not failures:
                if output.exists():
                    raise RuntimeError(f"Refusing to overwrite an artifact created during this run: {output}")
                output.write_text(candidate + "\n", encoding="utf-8")
                try:
                    candidate_path.unlink()
                except FileNotFoundError:
                    pass
                result = {
                    "status": "accepted",
                    "provider": provider["name"],
                    "model": provider["model"],
                    "attempts": attempt,
                    "history": provider_history,
                    "providers": history + [{"provider": provider["name"], "status": "accepted", "attempts": attempt}],
                }
                history.append({"provider": provider["name"], "status": "accepted", "attempts": attempt})
                print(json.dumps(result, ensure_ascii=False))
                github_output = os.environ.get("GITHUB_OUTPUT")
                if github_output:
                    with open(github_output, "a", encoding="utf-8") as handle:
                        handle.write(f"provider={provider['name']}\n")
                        handle.write(f"model={provider['model']}\n")
                        handle.write(f"attempts={attempt}\n")
                        handle.write("mode=generated\n")
                return
            repair_context = "\n".join(f"- {failure}" for failure in failures[:20])
        history.append({"provider": provider["name"], "status": "rejected", "attempts": len(provider_history), "checks": provider_history})

    try:
        candidate_path.unlink()
    except FileNotFoundError:
        pass
    result = {
        "status": "rejected",
        "provider": None,
        "attempts": sum(item.get("attempts", 0) for item in history if isinstance(item, dict)),
        "providers": history,
        "reason": "no configured provider accepted a candidate" if provider_attempted else "no provider configured",
    }
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(2)


if __name__ == "__main__":
    main()
