#!/usr/bin/env python3
"""Regression tests for catalog link target validation."""

from __future__ import annotations

import tempfile
from pathlib import Path

import build_catalog
import validate_catalog
from analytics_policy import analytics_pixel


PRODUCT = {
    "title": "اختبار",
    "pitch": "وصف",
    "period": "2026-w50",
    "category": "general",
    "shape": "test",
    "url": "products/weekly/2026-w50/",
    "source": "products/weekly/2026-w50/index.html",
    "lifecycle_status": "built",
    "lifecycle_reason": "",
    "replacement_url": "",
}


def with_pixel(html: str) -> str:
    return html.replace("</body>", f"  {analytics_pixel('catalog')}\n</body>")


with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    target = root / "products/weekly/2026-w50/index.html"
    target.parent.mkdir(parents=True)
    target.write_text("<!doctype html>", encoding="utf-8")

    validate_catalog.ROOT = root
    valid_path = root / "index.html"
    valid_path.write_text(with_pixel(build_catalog.render_catalog([PRODUCT])), encoding="utf-8")
    assert validate_catalog.validate(valid_path) == []

    target.unlink()
    errors = validate_catalog.validate(valid_path)
    assert any("target does not exist" in error for error in errors)

print("validate_catalog link tests passed")
