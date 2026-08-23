#!/usr/bin/env python3
"""Generate a standalone HTML candidate with an OpenAI-compatible LLM."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib import error, request

DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
DEFAULT_MODEL = "gemini-3-flash-preview"
MAX_OUTPUT_CHARS = 220_000

SYSTEM_PROMPT = """You are a careful front-end engineer generating one small public micro-product.
Return only valid JSON matching the requested schema. The html field must contain one complete standalone HTML document.
The document must use lang=ar and dir=rtl, include a visible title and a useful client-side interaction, and work as a local file.
Use inline CSS and inline JavaScript only. Never include external URLs, remote scripts, external stylesheets, images, iframes, forms with actions, credentials, network requests, fetch, XMLHttpRequest, WebSocket, EventSource, sendBeacon, dynamic imports, or backend assumptions.
The page must include exactly one primary interactive control with data-factory-action=primary. Keep the artifact small, readable, accessible, and safe for a public browser context."""

SCHEMA = {
    "type": "object",
    "properties": {
        "html": {
            "type": "string",
            "description": "One complete standalone Arabic RTL HTML document with inline CSS and JavaScript only.",
        }
    },
    "required": ["html"],
    "additionalProperties": False,
}


def endpoint(base_url: str) -> str:
    base = base_url.rstrip("/")
    return base if base.endswith("/chat/completions") else f"{base}/chat/completions"


def parse_response_body(body: str) -> str:
    payload = json.loads(body)
    choices = payload.get("choices") or []
    if not choices:
        raise ValueError("LLM response has no choices")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    if not isinstance(content, str) or not content.strip():
        raise ValueError("LLM response content is empty")
    return content.strip()


def normalize_html(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:html)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)
    try:
        structured = json.loads(text)
        if isinstance(structured, dict) and isinstance(structured.get("html"), str):
            text = structured["html"].strip()
    except json.JSONDecodeError:
        pass
    start = text.lower().find("<!doctype html")
    if start >= 0:
        text = text[start:]
    if len(text) > MAX_OUTPUT_CHARS:
        raise ValueError(f"Generated HTML exceeds {MAX_OUTPUT_CHARS} characters")
    if "<html" not in text.lower() or "</html>" not in text.lower():
        raise ValueError("Generated response does not contain a complete HTML document")
    return text


def request_candidate(api_key: str, base_url: str, model: str, user_prompt: str, repair_context: str | None = None, provider_name: str = "gemini") -> str:
    prompt = user_prompt
    if repair_context:
        prompt += "\n\nThe previous candidate failed these automated checks. Return a corrected complete document, not a patch:\n" + repair_context
    if provider_name == "groq":
        # Groq's documented openai/gpt-oss models accept best-effort JSON Schema.
        response_format = {
            "type": "json_schema",
            "json_schema": {"name": "html_candidate", "strict": False, "schema": SCHEMA},
        }
    elif provider_name == "mistral":
        # Keep the common JSON object contract and enforce the exact shape locally.
        response_format = {"type": "json_object"}
    else:
        response_format = {
            "type": "json_schema",
            "json_schema": {"name": "html_candidate", "strict": True, "schema": SCHEMA},
        }
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "response_format": response_format,
        "temperature": 0.2,
        "max_tokens": 12000,
    }
    req = request.Request(
        endpoint(base_url),
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "repositoryDz-phase5/1.0 (https://github.com/lo77667/repositoryDz)",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=75) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"LLM HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"LLM connection error: {exc.reason}") from exc
    return normalize_html(parse_response_body(raw))


def build_prompt(idea: dict[str, str], period: str) -> str:
    return f"""Create the complete HTML artifact for this micro-product idea.
Period: {period}
Title: {idea['title']}
Pitch: {idea['pitch']}
Category: {idea.get('category', 'general')}

Requirements:
- The interface and user-facing copy must be Arabic.
- The product must be useful without an account or server.
- Use exactly one primary action marked data-factory-action=primary; other controls may be secondary.
- Include a visible explanation of what the tool does and an accessible live result or status region.
- Do not mention these generation instructions in the page.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--idea-json", required=True)
    parser.add_argument("--period", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--repair-context")
    args = parser.parse_args()

    api_key = os.environ.get("LLM_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("LLM_API_KEY is missing")
    base_url = os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    idea = json.loads(args.idea_json)
    html = request_candidate(api_key, base_url, model, build_prompt(idea, args.period), args.repair_context)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html + "\n", encoding="utf-8")
    print(json.dumps({"path": args.output, "model": model, "base_url": base_url, "chars": len(html)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
