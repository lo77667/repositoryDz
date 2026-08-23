#!/usr/bin/env python3
"""Shared allowlist and markup for the Phase 6 page-view counter."""

from __future__ import annotations

from html import escape
from urllib.parse import parse_qs, urlencode, urlparse

COUNTER_HOST = "counterapi.com"
COUNTER_PATH = "/pixel.gif"
COUNTER_NAMESPACE = "lo77667.github.io/repositoryDz"
COUNTER_BASE_URL = f"https://{COUNTER_HOST}{COUNTER_PATH}"


def is_valid_key(key: str) -> bool:
    return key == "catalog" or key.startswith("weekly-") or key.startswith("product-")


def analytics_url(key: str) -> str:
    if not is_valid_key(key):
        raise ValueError("Analytics key must be catalog, product-*, or weekly-*")
    query = urlencode({"ns": COUNTER_NAMESPACE, "action": "view", "key": key})
    return f"{COUNTER_BASE_URL}?{query}"


def is_allowed_analytics_url(raw_url: str) -> bool:
    parsed = urlparse(raw_url)
    if parsed.scheme != "https" or parsed.netloc != COUNTER_HOST or parsed.path != COUNTER_PATH:
        return False
    query = parse_qs(parsed.query, keep_blank_values=True)
    if set(query) != {"ns", "action", "key"}:
        return False
    if query.get("ns") != [COUNTER_NAMESPACE] or query.get("action") != ["view"]:
        return False
    return is_valid_key(query.get("key", [""])[0])


def analytics_pixel(key: str) -> str:
    url = escape(analytics_url(key), quote=True)
    return (
        f'<img data-factory-analytics="counterapi" src="{url}" width="1" height="1" '
        'alt="" aria-hidden="true" '
        'style="position:absolute;width:1px;height:1px;opacity:0;pointer-events:none">'
    )
