#!/usr/bin/env python3
"""Static safety gate for an LLM-generated standalone HTML artifact."""

from __future__ import annotations

import re
import subprocess
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from analytics_policy import is_allowed_analytics_url
from security_policy import blocked_capabilities, dangerous_markup, has_credential_like_literal

MAX_BYTES = 220_000


class SafetyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_attrs: dict[str, str] = {}
        self.ids: set[str] = set()
        self.primary_actions = 0
        self.has_title = False
        self.has_body = False
        self.script_contents: list[str] = []
        self.external_dependency = False
        self.analytics_urls: list[str] = []
        self.bad_form = False
        self._in_script = False
        self._script_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_attrs = values
        if tag == "title":
            self.has_title = True
        if tag == "body":
            self.has_body = True
        if "id" in values:
            self.ids.add(values["id"])
        if values.get("data-factory-action") == "primary":
            self.primary_actions += 1
        if tag == "img" and values.get("data-factory-analytics") == "counterapi" and values.get("src"):
            self.analytics_urls.append(values["src"])
        if (tag == "script" and "src" in values) or (tag == "link" and "href" in values):
            self.external_dependency = True
        if tag == "form" and values.get("action"):
            self.bad_form = True
        if tag == "script":
            self._in_script = True
            self._script_buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_script:
            self.script_contents.append("".join(self._script_buffer))
            self._in_script = False
            self._script_buffer = []

    def handle_data(self, data: str) -> None:
        if self._in_script:
            self._script_buffer.append(data)


def validate(path: Path, allow_analytics: bool = False) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"Generated artifact does not exist: {path}"]
    if path.stat().st_size > MAX_BYTES:
        errors.append(f"Generated artifact exceeds {MAX_BYTES} bytes")
    html = path.read_text(encoding="utf-8")
    parser = SafetyParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:
        errors.append(f"HTML parsing failed: {exc}")

    if parser.html_attrs.get("lang") != "ar":
        errors.append("Document must declare lang=ar")
    if parser.html_attrs.get("dir") != "rtl":
        errors.append("Document must declare dir=rtl")
    if not parser.has_title:
        errors.append("Document title is missing")
    if not parser.has_body:
        errors.append("Document body is missing")
    if parser.external_dependency:
        errors.append("External script or stylesheet dependency found")
    if parser.bad_form:
        errors.append("Forms with an external action are not allowed")
    if parser.primary_actions != 1:
        errors.append(f"Expected exactly one data-factory-action=primary control; found {parser.primary_actions}")

    for token in blocked_capabilities(html):
        errors.append(f"Blocked capability found: {token}")
    for markup in dangerous_markup(html):
        errors.append(f"Dangerous markup found: {markup}")
    for raw_url in re.findall(r"https?://[^\s\"'<>]+", unescape(html), re.I):
        url = raw_url.rstrip(".,)")
        if not (allow_analytics and url in parser.analytics_urls and is_allowed_analytics_url(url)):
            errors.append("External URL found")
            break
    if any(not is_allowed_analytics_url(url) for url in parser.analytics_urls):
        errors.append("Analytics URL is not on the approved CounterAPI allowlist")
    if parser.analytics_urls and not allow_analytics:
        errors.append("Analytics instrumentation is not allowed before the final gate")
    if has_credential_like_literal(html):
        errors.append("Credential-like literal found")

    js_path = path.with_suffix(".generated.js")
    js_path.write_text("\n".join(parser.script_contents), encoding="utf-8")
    try:
        check = subprocess.run(["node", "--check", str(js_path)], capture_output=True, text=True, timeout=20)
        if check.returncode != 0:
            errors.append("Inline JavaScript syntax check failed: " + check.stderr.strip())
    except (OSError, subprocess.SubprocessError) as exc:
        errors.append(f"Unable to run JavaScript syntax check: {exc}")
    finally:
        try:
            js_path.unlink()
        except FileNotFoundError:
            pass
    return errors


def main() -> None:
    if len(sys.argv) not in {2, 3} or (len(sys.argv) == 3 and sys.argv[2] != "--allow-analytics"):
        raise SystemExit("usage: validate_generated_html.py path/to/index.html [--allow-analytics]")
    errors = validate(Path(sys.argv[1]), allow_analytics=len(sys.argv) == 3)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit(1)
    print(f"Generated HTML static safety gate passed: {sys.argv[1]}")


if __name__ == "__main__":
    main()
