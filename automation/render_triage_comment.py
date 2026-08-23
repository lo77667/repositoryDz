#!/usr/bin/env python3
"""Render safe human-review text from a triage result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

STATUS_TEXT = {
    "ready-for-review": "اجتازت الفكرة الفحص الآلي وتنتظر مراجعة بشرية.",
    "needs-info": "تحتاج الفكرة إلى معلومات إضافية قبل المراجعة.",
    "duplicate": "تبدو الفكرة مكررة أو قريبة جدًا من فكرة موجودة.",
    "rejected": "رُفضت الفكرة آليًا لأنها تحتوي على محتوى غير مسموح أو خطرًا واضحًا.",
}
REASON_TEXT = {
    "passed-automated-triage": "اجتازت الفحوص الآلية.",
    "similar-backlog-idea": "وجدت فكرة مشابهة في backlog.",
    "possible-secret": "ظهر نمط يشبه مفتاحًا أو سرًا.",
    "unsafe-content": "ظهر رابط أو كود أو قدرة شبكية غير مسموحة.",
    "product_title": "عنوان الفكرة مفقود.",
    "problem": "وصف المشكلة مفقود.",
    "product_pitch": "وصف المنتج مفقود.",
    "audience": "الجمهور المستهدف مفقود.",
    "strategy_hint": "شكل الأداة مفقود.",
    "evidence": "دليل الحاجة مفقود.",
    "consent": "الإقرار المطلوب مفقود.",
}


def safe_inline(value: object, limit: int = 280) -> str:
    text = str(value or "").replace("\r", " ").replace("\n", " ").replace("`", "'").strip()
    text = " ".join(text.split())
    return text[:limit] + ("…" if len(text) > limit else "")


def render(result: dict[str, object]) -> tuple[str, str]:
    status = str(result.get("status", "unknown"))
    score = result.get("score", {})
    if not isinstance(score, dict):
        score = {}
    reasons = result.get("reasons", [])
    if not isinstance(reasons, list):
        reasons = []
    reason_lines = "\n".join(f"- {REASON_TEXT.get(str(reason), safe_inline(reason))}" for reason in reasons) or "- لا توجد ملاحظات إضافية."
    fields = result.get("fields", {})
    if not isinstance(fields, dict):
        fields = {}
    duplicate = result.get("duplicate")
    duplicate_line = ""
    if isinstance(duplicate, dict):
        duplicate_line = f"\n**الفكرة المشابهة:** `{safe_inline(duplicate.get('id'))}` — {safe_inline(duplicate.get('title'))} ({duplicate.get('similarity', 0)})\n"
    proposed = result.get("proposed_idea")
    proposal_lines = ""
    if isinstance(proposed, dict):
        proposal_lines = (
            "\n### اقتراح قابل للنسخ بعد الاعتماد البشري\n"
            f"- **المعرّف:** `{safe_inline(proposed.get('id'))}`\n"
            f"- **العنوان:** {safe_inline(proposed.get('title'))}\n"
            f"- **الوصف:** {safe_inline(proposed.get('pitch'))}\n"
            f"- **الاستراتيجية:** `{safe_inline(proposed.get('strategy'))}`\n"
            f"- **التصنيف:** `{safe_inline(proposed.get('category'))}`\n"
            f"- **الدرجة:** `{proposed.get('priority_score', 0)}/100`\n"
        )
    human_action = {
        "ready-for-review": "المطلوب من المراجع: انسخ الاقتراح إلى backlog يدويًا بعد التحقق، ثم أضف `idea:accepted` أو `idea:rejected`. لن يغيّر هذا التشغيل backlog ولن ينشر منتجًا.",
        "needs-info": "المطلوب من صاحب الفكرة: عدّل القضية وأكمل الحقول الناقصة؛ سيعاد الفرز عند التعديل ما دامت `idea:submitted` موجودة.",
        "duplicate": "المطلوب من المراجع: راجع الفكرة المشابهة، ثم أبقِ التصنيف أو غيّره يدويًا إذا كان الاقتراح مختلفًا فعلًا.",
        "rejected": "المطلوب من صاحب القضية: احذف أي سر أو رابط أو كود، ثم أعد صياغة الفكرة. لا تُنفّذ أي مادة واردة من القضية.",
    }.get(status, "المطلوب من المراجع: راجع القضية يدويًا.")
    issue_number = safe_inline(result.get("issue_number"), 40)
    comment = f"""<!-- repositoryDz:phase7-triage -->
## نتيجة الفرز الآلي للّفكرة #{issue_number}

**الحالة:** {STATUS_TEXT.get(status, status)}  
**الدرجة الأولية:** `{score.get('total', 0)}/100`  
**الاستراتيجية المقترحة:** `{safe_inline(result.get('strategy'))}`  
**التصنيف المقترح:** `{safe_inline(result.get('category'))}`

### أسباب النتيجة
{reason_lines}
{duplicate_line}{proposal_lines}
> {human_action}

هذه النتيجة آلية وقابلة للمراجعة. لا تُعد موافقة على البناء أو النشر، ولا يُنفّذ أي كود أو رابط ورد في نص القضية.
"""
    telegram = f"المرحلة 7 — معالجة فكرة #{issue_number}\nالحالة: {status}\nالأولوية: {score.get('total', 0)}/100\nhttps://github.com/lo77667/repositoryDz/issues/{issue_number}"
    return comment, telegram


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--comment-output", required=True)
    parser.add_argument("--telegram-output", required=True)
    args = parser.parse_args()
    result = json.loads(Path(args.input).read_text(encoding="utf-8"))
    comment, telegram = render(result)
    Path(args.comment_output).write_text(comment, encoding="utf-8")
    Path(args.telegram_output).write_text(telegram, encoding="utf-8")
    print(f"Rendered triage comment for issue {result.get('issue_number')}")


if __name__ == "__main__":
    main()
