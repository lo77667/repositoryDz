#!/usr/bin/env python3
"""Build one deterministic weekly product from the Phase 1 static template."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "products/idea-mashup/index.html"
OUTPUT_ROOT = ROOT / "products/weekly"

IDEAS = [
    {
        "audience": "أصحاب المتاجر الإلكترونية الصغيرة",
        "problem": "يضيّعون وقتًا في تحويل الأسئلة المتكررة من العملاء إلى إجابات مفيدة",
        "format": "بطاقة ردود ذكية",
        "differentiator": "تعمل من الهاتف وتحوّل كل سؤال متكرر إلى قالب قابل للنسخ",
    },
    {
        "audience": "صنّاع المحتوى المستقلين",
        "problem": "يصعب عليهم إعادة استخدام أفضل أفكارهم دون تكرار ممل",
        "format": "مولّد إعادة صياغة قصير",
        "differentiator": "يبدأ من منشور واحد ويقترح ثلاث زوايا جديدة خلال دقيقة",
    },
    {
        "audience": "المستقلين الذين يعملون من الهاتف",
        "problem": "يؤجلون خطوة إدارية صغيرة لأنها موزعة بين عدة تطبيقات",
        "format": "قائمة فحص يومية",
        "differentiator": "تقسم المهمة إلى ثلاث خطوات واضحة بلا تسجيل أو إعداد طويل",
    },
    {
        "audience": "مديري النشرات البريدية الناشئة",
        "problem": "لا يعرفون أي عنوان سيجعل رسالتهم أسهل للفهم",
        "format": "مختبر عناوين بسيط",
        "differentiator": "يقارن بين نبرة مباشرة وتعليمية وقصصية على شاشة واحدة",
    },
    {
        "audience": "الطلاب الذين يبيعون منتجات رقمية",
        "problem": "يجدون صعوبة في تحويل ملاحظات المشترين إلى تحسين واحد قابل للتنفيذ",
        "format": "لوحة قرار صغيرة",
        "differentiator": "تجمع الملاحظات المتشابهة وتخرج بأولوية واحدة فقط كل مرة",
    },
    {
        "audience": "فرق التسويق الصغيرة",
        "problem": "يحتاجون إلى إنجاز تجربة تسويقية صغيرة قبل نهاية اليوم",
        "format": "مولّد تجربة من خمس دقائق",
        "differentiator": "يحوّل الهدف إلى فرضية ومقياس وموعد مراجعة في نموذج واحد",
    },
    {
        "audience": "أصحاب الخدمات المحلية",
        "problem": "ينسون تحديث العروض الموسمية في القنوات المختلفة",
        "format": "مخطط تحديث أسبوعي",
        "differentiator": "يعرض القنوات على هيئة خطوات قصيرة يمكن إنجازها من الهاتف",
    },
    {
        "audience": "المصممين الذين يعملون منفردين",
        "problem": "تتأخر قراراتهم لأن الملاحظات الإبداعية غير مرتبة",
        "format": "مصفاة ملاحظات بصرية",
        "differentiator": "يفصل الملاحظة إلى مشكلة وقرار وتجربة تالية بلا تعقيد",
    },
]


def period_for(today: date) -> str:
    iso_year, iso_week, _ = today.isocalendar()
    return f"{iso_year}-w{iso_week:02d}"


def idea_for(period: str) -> dict[str, str]:
    digest = hashlib.sha256(period.encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(IDEAS)
    return IDEAS[index].copy()


def safe_slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "weekly-idea"


def render(template: str, idea: dict[str, str], period: str) -> str:
    payload = json.dumps(idea, ensure_ascii=False, separators=(",", ":"))
    title = f"شرارة منتج — {idea['format']} لـ {idea['audience']}"
    injection = f"  <script>\n    window.__WEEKLY_IDEA__ = {payload};\n  </script>\n"
    marker = "  <script>\n    (() => {"
    if marker not in template:
        raise RuntimeError("The Phase 1 template script marker was not found")
    html = template.replace(marker, injection + marker, 1)
    html = html.replace("<title>شرارة منتج — مولّد أفكار رقمية</title>", f"<title>{title}</title>", 1)
    html = html.replace("<meta name=\"description\" content=\"شرارة منتج: مولّد أفكار أولية لمنتجات رقمية صغيرة.\">", f"<meta name=\"description\" content=\"نسخة {period} من مولّد شرارة منتج.\">", 1)
    html = html.replace("نسخة يدوية تجريبية — المرحلة 1", f"نسخة أسبوعية {period} — المرحلة 2", 1)
    return html


def write_output(period: str, html: str, overwrite: bool) -> Path:
    output_dir = OUTPUT_ROOT / safe_slug(period)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "index.html"
    if output_path.exists() and output_path.read_text(encoding="utf-8") != html and not overwrite:
        raise RuntimeError(f"Refusing to overwrite an existing different artifact: {output_path}")
    output_path.write_text(html, encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="ISO date used for deterministic selection; defaults to today")
    parser.add_argument("--period", help="Explicit period such as 2026-w34; useful for tests")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing a different existing artifact")
    args = parser.parse_args()

    if not TEMPLATE_PATH.exists():
        raise SystemExit(f"Template missing: {TEMPLATE_PATH}")
    if args.period:
        period = args.period
    elif args.date:
        period = period_for(date.fromisoformat(args.date))
    else:
        period = period_for(date.today())

    if not re.fullmatch(r"\d{4}-w\d{2}", period):
        raise SystemExit("Period must match YYYY-wNN, for example 2026-w34")

    idea = idea_for(period)
    html = render(TEMPLATE_PATH.read_text(encoding="utf-8"), idea, period)
    output_path = write_output(period, html, args.overwrite)
    product_url = f"https://lo77667.github.io/repositoryDz/products/weekly/{output_path.parent.name}/"

    print(json.dumps({"period": period, "path": str(output_path.relative_to(ROOT)), "url": product_url, "idea": idea}, ensure_ascii=False))
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"period={period}\n")
            handle.write(f"path={output_path.relative_to(ROOT)}\n")
            handle.write(f"url={product_url}\n")
            handle.write(f"title={idea['format']} لـ {idea['audience']}\n")


if __name__ == "__main__":
    main()
