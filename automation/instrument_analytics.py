#!/usr/bin/env python3
"""Inject the trusted Phase 6 CounterAPI pixel into a published artifact."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from analytics_policy import analytics_pixel

ROOT = Path(__file__).resolve().parents[1]
WEEKLY_PATH = re.compile(r"products/weekly/(\d{4}-w\d{2})/index\.html$")
PRODUCT_PATH = re.compile(r"products/([a-z0-9-]+)/index\.html$")


def key_for_path(path: Path) -> str:
    relative = path.resolve().relative_to(ROOT).as_posix()
    if relative == "index.html":
        return "catalog"
    match = WEEKLY_PATH.fullmatch(relative)
    if match:
        return f"weekly-{match.group(1)}"
    match = PRODUCT_PATH.fullmatch(relative)
    if match:
        return f"product-{match.group(1)}"
    raise ValueError("Only index.html or products/**/index.html may be instrumented")


def inject(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    if 'data-factory-analytics="counterapi"' in html:
        return False
    marker = "</body>"
    if marker not in html.lower():
        raise ValueError(f"HTML body closing tag is missing: {path}")
    pixel = analytics_pixel(key_for_path(path))
    position = html.lower().rfind(marker)
    html = html[:position] + f"  {pixel}\n" + html[position:]
    path.write_text(html, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="HTML paths to instrument")
    args = parser.parse_args()
    changed = 0
    for raw_path in args.paths:
        path = (ROOT / raw_path).resolve()
        if not path.exists():
            raise SystemExit(f"Artifact does not exist: {raw_path}")
        changed += int(inject(path))
    print(f"Analytics instrumentation complete: {changed} changed, {len(args.paths) - changed} already instrumented")


if __name__ == "__main__":
    main()
