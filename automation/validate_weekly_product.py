#!/usr/bin/env python3
"""Validate one generated weekly product artifact."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_weekly_product.py products/weekly/YYYY-wNN/index.html")

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
    soup = BeautifulSoup(html, "html.parser")
    for selector in ("#generate-btn", "#copy-btn", "#reset-btn", "#idea-title", "#idea-body", "#idea-tags", "#status"):
        if soup.select_one(selector) is None:
            errors.append(f"Missing required selector: {selector}")
    if soup.html is None or soup.html.get("lang") != "ar" or soup.html.get("dir") != "rtl":
        errors.append("HTML language or direction is incorrect")
    if re.search(r"<(?:script|link)[^>]+(?:src|href)=", html, re.I):
        errors.append("External script or stylesheet dependency found")
    if re.search(r"https?://", html, re.I):
        errors.append("External URL found in weekly artifact")
    if any(token in html for token in ("fetch(", "XMLHttpRequest", "WebSocket")):
        errors.append("Network-capable browser API found")
    if "window.__WEEKLY_IDEA__" not in html:
        errors.append("Weekly idea payload is missing")
    scripts = [script.string or "" for script in soup.find_all("script")]
    js_path = ROOT / ".phase2_weekly_inline.js"
    js_path.write_text("\n".join(scripts), encoding="utf-8")
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

    print(f"Weekly artifact validation passed: {relative}")


if __name__ == "__main__":
    main()
