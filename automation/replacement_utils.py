#!/usr/bin/env python3
"""Canonical validation for internal product replacement URLs."""

from __future__ import annotations

import re

from period_utils import require_period

PRODUCT_RE = re.compile(r"^products/(?P<slug>[a-z0-9][a-z0-9-]*)/(?:(?:index\.html))?$", re.I)
WEEKLY_RE = re.compile(r"^products/weekly/(?P<period>\d{4}-w\d{2})/(?:index\.html)?$", re.I)


def normalize_replacement_url(value: str | None) -> str | None:
    """Return the catalog's canonical directory URL or raise for invalid input."""
    if not value:
        return None
    candidate = str(value).strip()
    weekly = WEEKLY_RE.fullmatch(candidate)
    if weekly:
        period = require_period(weekly.group("period").lower())
        return f"products/weekly/{period}/"
    product = PRODUCT_RE.fullmatch(candidate)
    if product:
        return f"products/{product.group('slug').lower()}/"
    raise ValueError("replacement URL must be an internal products/... path")
