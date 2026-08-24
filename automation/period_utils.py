#!/usr/bin/env python3
"""Shared validation helpers for ISO week period identifiers."""

from __future__ import annotations

import re
from datetime import date

PERIOD_RE = re.compile(r"^(\d{4})-w(\d{2})$")


def parse_period(value: object) -> tuple[int, int] | None:
    """Return (ISO year, week) only for a real ISO week period."""
    match = PERIOD_RE.fullmatch(str(value or "").strip())
    if not match:
        return None
    year, week = int(match.group(1)), int(match.group(2))
    try:
        date.fromisocalendar(year, week, 1)
    except ValueError:
        return None
    return year, week


def is_valid_period(value: object) -> bool:
    return parse_period(value) is not None


def require_period(value: object) -> str:
    """Normalize and validate a period, raising a user-facing ValueError."""
    normalized = str(value or "").strip()
    if not is_valid_period(normalized):
        raise ValueError("Period must be a real ISO week in YYYY-wNN format (week 01 through 52 or 53)")
    return normalized
