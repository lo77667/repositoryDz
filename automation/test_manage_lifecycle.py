#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))
from manage_lifecycle import transition  # noqa: E402


def data():
    return {"version": 1, "updated_at": "2026-08-23", "ideas": [
        {"id": "built-1", "status": "built", "title": "منتج", "pitch": "وصف"},
        {"id": "backlog-1", "status": "backlog", "title": "فكرة", "pitch": "وصف"},
    ]}


def main() -> None:
    original = data()
    dry = copy.deepcopy(original)
    result = transition(dry, "built-1", "retired", "منتج قديم وله بديل أفضل", "products/weekly/2026-w50/")
    assert result["to"] == "retired"
    assert dry["ideas"][0]["status"] == "retired"
    assert dry["ideas"][0]["replacement_url"] == "products/weekly/2026-w50/"
    assert dry["ideas"][0]["lifecycle_events"][-1]["from"] == "built"

    revisited = copy.deepcopy(dry)
    transition(revisited, "built-1", "revisit", "نحتاج إعادة تقييم بعد قياس جديد")
    assert revisited["ideas"][0]["status"] == "revisit"

    try:
        transition(copy.deepcopy(original), "backlog-1", "built", "تحويل مباشر غير مسموح")
    except ValueError as exc:
        assert "not allowed" in str(exc)
    else:
        raise AssertionError("backlog -> built must not be managed by lifecycle tool")

    try:
        transition(copy.deepcopy(original), "built-1", "retired", "قصير")
    except ValueError as exc:
        assert "at least 8" in str(exc)
    else:
        raise AssertionError("short reason must be rejected")

    normalized = copy.deepcopy(original)
    normalized_result = transition(normalized, "built-1", "retired", "منتج قديم وله بديل أفضل", "products/weekly/2026-w50/index.html")
    assert normalized_result["replacement_url"] == "products/weekly/2026-w50/"
    assert normalized["ideas"][0]["replacement_url"] == "products/weekly/2026-w50/"

    for invalid_period in ("2026-w00", "2026-w54", "2026-w99"):
        try:
            transition(copy.deepcopy(original), "built-1", "retired", "سبب صالح وطويل", f"products/weekly/{invalid_period}/")
        except ValueError as exc:
            assert "ISO week" in str(exc)
        else:
            raise AssertionError(f"invalid ISO period must be rejected: {invalid_period}")

    try:
        transition(copy.deepcopy(original), "built-1", "retired", "سبب صالح وطويل", "products/weekly/")
    except ValueError as exc:
        assert "weekly root" in str(exc)
    else:
        raise AssertionError("weekly root must not be accepted as a product replacement")

    try:
        transition(copy.deepcopy(original), "built-1", "retired", "سبب صالح", "https://example.com")
    except ValueError as exc:
        assert "internal products" in str(exc)
    else:
        raise AssertionError("external replacement URL must be rejected")

    assert original == data()
    print("manage_lifecycle tests passed")


if __name__ == "__main__":
    main()
