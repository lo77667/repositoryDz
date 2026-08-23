#!/usr/bin/env python3
"""Validate one generated weekly product artifact using only the Python standard library."""

from __future__ import annotations

import re
import subprocess
import sys
from html import unescape
from html.parser import HTMLParser

from analytics_policy import is_allowed_analytics_url
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ArtifactParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.script_contents: list[str] = []
        self._in_script = False
        self._script_buffer: list[str] = []
        self.html_attrs: dict[str, str] = {}
        self.external_dependency = False
        self.analytics_urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_attrs = attr_map
        if "id" in attr_map:
            self.ids.add(attr_map["id"])
        if tag == "img" and attr_map.get("data-factory-analytics") == "counterapi" and attr_map.get("src"):
            self.analytics_urls.append(attr_map["src"])
        if (tag == "script" and "src" in attr_map) or (tag == "link" and "href" in attr_map):
            self.external_dependency = True
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


def strategy_requirements(strategy: str) -> tuple[str, ...]:
    common = ("idea-title",)
    specific = {
        "template:idea-mashup": ("generate-btn", "copy-btn", "reset-btn", "idea-body", "idea-tags", "status"),
        "template:converter": ("idea-pitch", "converter-form", "cost", "rate", "result-value", "formula"),
        "template:visual-toy": ("idea-pitch", "visual-stage", "orb", "intensity", "shuffle", "readout"),
        "template:text-tool": ("idea-pitch", "source", "mode", "transform", "result", "count", "state"),
    }
    return common + specific.get(strategy, ())


def main() -> None:
    if len(sys.argv) not in {2, 3} or (len(sys.argv) == 3 and sys.argv[2] != "--allow-analytics"):
        raise SystemExit("usage: validate_weekly_product.py products/weekly/YYYY-wNN/index.html [--allow-analytics]")
    allow_analytics = len(sys.argv) == 3

    relative = Path(sys.argv[1])
    path = ROOT / relative
    errors: list[str] = []
    if not path.exists():
        errors.append(f"Artifact does not exist: {relative}")
        print("\n".join(errors))
        raise SystemExit(1)

    if not re.fullmatch(r"products/weekly/\d{4}-w\d{2}/index\.html", relative.as_posix()):
        errors.append("Artifact path is not a weekly YYYY-wNN product path")

    html = path.read_text(encoding="utf-8")
    parser = ArtifactParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:
        errors.append(f"HTML parsing failed: {exc}")

    strategy_match = re.search(r'"strategy":"(template:[^"]+)"', html)
    strategy = strategy_match.group(1) if strategy_match else ""
    legacy_artifact = not strategy and relative.as_posix() in {
        "products/weekly/2026-w34/index.html",
        "products/weekly/2026-w35/index.html",
    }
    if not strategy and not legacy_artifact:
        errors.append("Weekly strategy payload is missing")
    if legacy_artifact:
        strategy = "template:idea-mashup"
    for required_id in strategy_requirements(strategy):
        if required_id not in parser.ids:
            errors.append(f"Missing required id for {strategy or 'unknown strategy'}: {required_id}")
    if parser.html_attrs.get("lang") != "ar" or parser.html_attrs.get("dir") != "rtl":
        errors.append("HTML language or direction is incorrect")
    if parser.external_dependency:
        errors.append("External script or stylesheet dependency found")
    for raw_url in re.findall(r"https?://[^\s\"'<>]+", unescape(html), re.I):
        url = raw_url.rstrip(".,)")
        if not (allow_analytics and url in parser.analytics_urls and is_allowed_analytics_url(url)):
            errors.append("External URL found in weekly artifact")
            break
    if any(not is_allowed_analytics_url(url) for url in parser.analytics_urls):
        errors.append("Analytics URL is not on the approved CounterAPI allowlist")
    if parser.analytics_urls and not allow_analytics:
        errors.append("Analytics instrumentation is not allowed before the final gate")
    if any(token in html for token in ("fetch(", "XMLHttpRequest", "WebSocket")):
        errors.append("Network-capable browser API found")
    js_path = ROOT / ".phase2_weekly_inline.js"
    js_path.write_text("\n".join(parser.script_contents), encoding="utf-8")
    check = subprocess.run(["node", "--check", str(js_path)], capture_output=True, text=True)
    if check.returncode != 0:
        errors.append("Generated JavaScript syntax check failed: " + check.stderr.strip())
    try:
        js_path.unlink()
    except FileNotFoundError:
        pass

    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit(1)

    print(f"Weekly artifact validation passed: {relative} ({strategy})")


if __name__ == "__main__":
    main()
