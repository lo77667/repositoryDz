#!/usr/bin/env python3
"""Regression tests for safe HTML and inline JSON serialization."""

from __future__ import annotations

from pathlib import Path

from build_weekly_product import render

root = Path(__file__).resolve().parents[1]
template = (root / "templates/text-tool.html").read_text(encoding="utf-8")
idea = {
    "id": "encoding-test",
    "slug": "encoding-test",
    "title": "عنوان </title><script>window.__BAD__=1</script> & اختبار",
    "pitch": "وصف آمن",
    "strategy": "template:text-tool",
    "status": "backlog",
    "difficulty": "1",
    "category": "general",
    "shape": "editor",
}
output = render(template, idea, "2026-w50")
assert "</title><script>window.__BAD__" not in output
assert "\\u003c/title\\u003e\\u003cscript\\u003ewindow.__BAD__" in output
assert "&lt;/title&gt;&lt;script&gt;" in output

print("builder output encoding tests passed")
