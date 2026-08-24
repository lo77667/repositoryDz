#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))
from build_catalog import render_catalog  # noqa: E402


def main() -> None:
    products = [
        {
            "title": "منتج قديم",
            "pitch": "وصف قديم",
            "period": "2026-w01",
            "category": "general",
            "url": "products/weekly/2026-w01/",
            "source": "products/weekly/2026-w01/index.html",
            "lifecycle_status": "retired",
            "lifecycle_reason": "تم استبداله بنسخة أدق",
            "replacement_url": "products/weekly/2026-w50/",
        },
        {
            "title": "منتج قيد التقييم",
            "pitch": "وصف",
            "period": "2026-w02",
            "category": "general",
            "url": "products/weekly/2026-w02/",
            "source": "products/weekly/2026-w02/index.html",
            "lifecycle_status": "revisit",
            "lifecycle_reason": "نحتاج قياسًا إضافيًا",
            "replacement_url": "https://evil.example",
        },
    ]
    html = render_catalog(products)
    assert 'data-lifecycle="retired"' in html
    assert 'متقاعد' in html and 'قيد المراجعة' in html
    assert 'products/weekly/2026-w50/' in html
    assert 'evil.example' not in html
    assert html.count('class="open"') == 2
    print("catalog lifecycle tests passed")


if __name__ == "__main__":
    main()
