#!/usr/bin/env python3
"""Validate the generated storefront index and its approved analytics pixel."""

from __future__ import annotations

import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from analytics_policy import is_allowed_analytics_url

ROOT = Path(__file__).resolve().parents[1]


class CatalogParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_attrs: dict[str, str] = {}
        self.title = False
        self.body = False
        self.cards = 0
        self.analytics_urls: list[str] = []
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_attrs = values
        elif tag == "title":
            self.title = True
        elif tag == "body":
            self.body = True
        elif tag == "article" and "card" in values.get("class", "").split():
            self.cards += 1
        elif tag == "a" and values.get("href"):
            self.links.append(values["href"])
        elif tag == "img" and values.get("data-factory-analytics") == "counterapi" and values.get("src"):
            self.analytics_urls.append(values["src"])


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"Catalog does not exist: {path}"]
    html = path.read_text(encoding="utf-8")
    parser = CatalogParser()
    parser.feed(html)
    parser.close()
    if parser.html_attrs.get("lang") != "ar" or parser.html_attrs.get("dir") != "rtl":
        errors.append("Catalog must declare lang=ar and dir=rtl")
    if not parser.title or not parser.body:
        errors.append("Catalog title or body is missing")
    if parser.cards == 0:
        errors.append("Catalog must list at least one product card")
    if len(parser.analytics_urls) != 1 or not is_allowed_analytics_url(parser.analytics_urls[0]):
        errors.append("Catalog must contain exactly one approved CounterAPI pixel")
    for link in parser.links:
        if urlparse(link).scheme or link.startswith("//") or not re.fullmatch(r"products(?:/[-a-z0-9]+){1,3}/", link):
            errors.append(f"Catalog contains a non-local product link: {link}")
            continue
        target = ROOT / link / "index.html"
        if not target.is_file():
            errors.append(f"Catalog link target does not exist: {link}")
    for raw_url in re.findall(r"https?://[^\s\"'<>]+", unescape(html), re.I):
        url = raw_url.rstrip(".,)")
        if url not in parser.analytics_urls or not is_allowed_analytics_url(url):
            errors.append("Catalog contains an unapproved external URL")
            break
    if re.search(r"<script\b|<link\b", html, re.I):
        errors.append("Catalog must not load external or inline executable dependencies")
    return errors


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_catalog.py index.html")
    errors = validate(ROOT / sys.argv[1])
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit(1)
    print(f"Catalog validation passed: {sys.argv[1]}")


if __name__ == "__main__":
    main()
