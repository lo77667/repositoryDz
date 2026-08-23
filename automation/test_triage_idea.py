#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))
from triage_idea import triage  # noqa: E402

BACKLOG = json.loads((ROOT / "ideas/backlog.json").read_text(encoding="utf-8"))


def body(**overrides: str) -> str:
    fields = {
        "عنوان الفكرة": "حاسبة تكلفة الشحن",
        "المشكلة التي يحلها المنتج": "يحتاج صاحب المتجر إلى معرفة أثر تكلفة الشحن على قرار الشراء قبل إطلاق العرض.",
        "وصف المنتج المقترح": "أداة صغيرة تحسب التكلفة النهائية وتوضح الحد المناسب للشحن المجاني.",
        "الجمهور المستهدف": "أصحاب المتاجر الصغيرة",
        "الشكل الأقرب للأداة": "محول أو حاسبة",
        "دليل الحاجة أو مثال استخدام": "تتكرر الأسئلة حول الشحن عند مقارنة عروض المتاجر، ويحتاج صاحب المتجر إلى جواب سريع قبل النشر.",
        "قيود أو ملاحظات إضافية": "تعمل محليًا داخل المتصفح ولا تحتاج حسابًا.",
        "الإقرار": "- [x] أفهم أن هذا الاقتراح عام وسيُراجع قبل إدخاله إلى backlog أو بناء منتج منه.\n- [x] لم أرسل أسرارًا أو مفاتيح أو بيانات شخصية أو بيانات عملاء.",
    }
    fields.update(overrides)
    return "\n\n".join(f"### {heading}\n{value}" for heading, value in fields.items())


def issue(text: str, number: int = 501) -> dict[str, object]:
    return {"number": number, "title": "[فكرة] اختبار", "body": text}


def main() -> None:
    result = triage(issue(body()), BACKLOG)
    assert result["status"] == "ready-for-review", result
    assert result["strategy"] == "template:converter", result
    assert result["proposed_idea"]["id"].startswith("community-501-"), result
    assert result["score"]["total"] >= 70, result

    missing = triage(issue(body(**{"دليل الحاجة أو مثال استخدام": ""}), 502), BACKLOG)
    assert missing["status"] == "needs-info", missing
    assert missing["proposed_idea"] is None, missing

    duplicate = triage(issue(body(**{
        "عنوان الفكرة": "شرارة العرض اليومي",
        "وصف المنتج المقترح": "مولّد سريع لأفكار عروض يومية تناسب المتاجر الصغيرة.",
    }), 503), BACKLOG)
    assert duplicate["status"] == "duplicate", duplicate
    assert duplicate["duplicate"]["id"] == "idea-mashup-001", duplicate

    unsafe = triage(issue(body(**{"وصف المنتج المقترح": "استخدم https://example.com لتنفيذ fetch()"}), 504), BACKLOG)
    assert unsafe["status"] == "rejected", unsafe
    assert "unsafe-content" in unsafe["reasons"], unsafe

    sparse = triage(issue("### عنوان الفكرة\nفكرة فقط", 505), BACKLOG)
    assert sparse["status"] == "needs-info", sparse
    assert sparse["score"]["total"] >= 0, sparse

    before = copy.deepcopy(BACKLOG)
    triage(issue(body(), 506), BACKLOG)
    assert BACKLOG == before
    print("triage_idea tests passed")


if __name__ == "__main__":
    main()
