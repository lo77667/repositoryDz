#!/usr/bin/env python3
"""Regression tests for real ISO-week period validation."""

from __future__ import annotations

from period_utils import is_valid_period, parse_period, require_period


assert parse_period("2026-w35") == (2026, 35)
assert parse_period("2026-w53") == (2026, 53)
assert parse_period("2027-w53") is None  # 2027 has no ISO week 53.
assert parse_period("2020-w53") == (2020, 53)
assert parse_period("2027-W01") is None
assert parse_period("2026-w00") is None
assert parse_period("2026-w54") is None
assert parse_period("2026-w99") is None
assert parse_period("phase-1") is None
assert is_valid_period("2026-w35")
assert not is_valid_period("2026-w99")
assert require_period(" 2026-w35 ") == "2026-w35"

try:
    require_period("2026-w99")
except ValueError as exc:
    assert "ISO week" in str(exc)
else:
    raise AssertionError("invalid ISO period must be rejected")

print("period_utils tests passed")
