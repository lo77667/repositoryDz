#!/usr/bin/env python3
"""Regression tests for provider and fallback overwrite protection."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDEA = {
    "id": "audit-no-overwrite",
    "slug": "audit-no-overwrite",
    "title": "اختبار منع الاستبدال",
    "pitch": "فكرة اختبارية آمنة.",
    "strategy": "generate",
    "status": "backlog",
    "difficulty": 1,
    "category": "general",
    "shape": "test",
}

with tempfile.TemporaryDirectory() as directory:
    output = Path(directory) / "index.html"
    output.write_text("ORIGINAL ARTIFACT\n", encoding="utf-8")
    env = os.environ.copy()
    for key in ("LLM_API_KEY", "LLM_FALLBACK_API_KEY", "LLM_SECONDARY_API_KEY"):
        env.pop(key, None)

    chain = subprocess.run(
        [
            sys.executable,
            str(ROOT / "automation/provider_chain.py"),
            "--idea-json",
            json.dumps(IDEA, ensure_ascii=False),
            "--period",
            "2026-w50",
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert chain.returncode != 0
    assert "overwrite" in chain.stderr
    assert output.read_text(encoding="utf-8") == "ORIGINAL ARTIFACT\n"

    fallback = subprocess.run(
        [
            sys.executable,
            str(ROOT / "automation/build_fallback_product.py"),
            "--idea-json",
            json.dumps(IDEA, ensure_ascii=False),
            "--period",
            "2026-w50",
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert fallback.returncode != 0
    assert "overwrite" in fallback.stderr
    assert output.read_text(encoding="utf-8") == "ORIGINAL ARTIFACT\n"

print("no-overwrite tests passed")
