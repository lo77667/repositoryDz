#!/usr/bin/env python3
"""Regression tests for complete-document and external-link safety gates."""

from __future__ import annotations

import tempfile
from pathlib import Path

from validate_generated_html import validate

source = (Path(__file__).resolve().parents[1] / "products/weekly/2026-w50/index.html").read_text(encoding="utf-8")

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    valid = root / "valid.html"
    valid.write_text(source, encoding="utf-8")
    assert validate(valid, allow_analytics=True) == []

    trailing = root / "trailing.html"
    trailing.write_text(source + "\nTRAILING_UNTRUSTED_TEXT\n", encoding="utf-8")
    trailing_errors = validate(trailing, allow_analytics=True)
    assert any("complete HTML document" in error for error in trailing_errors)

    protocol_relative = root / "protocol-relative.html"
    protocol_relative.write_text(source.replace("</body>", '<a href="//example.com">رابط اختباري</a></body>'), encoding="utf-8")
    protocol_errors = validate(protocol_relative, allow_analytics=True)
    assert any("External URL" in error for error in protocol_errors)

print("generated HTML contract tests passed")
