#!/usr/bin/env python3
"""Build the static Phase 6 storefront from committed products and backlog metadata."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PRODUCT_ROOT = ROOT / "products"
WEEKLY_RE = re.compile(r"products/weekly/(\d{4}-w\d{2})/index\.html$")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
DESCRIPTION_RE = re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', re.I | re.S)
PITCH_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.I | re.S)
SLUG_RE = re.compile(r"[^a-z0-9-]+")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", value)).strip()


def product_key(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    weekly = WEEKLY_RE.fullmatch(relative)
    if weekly:
        return weekly.group(1)
    return path.parent.name


def parse_html(path: Path) -> tuple[str, str]:
    content = path.read_text(encoding="utf-8")
    title_match = TITLE_RE.search(content)
    title = clean_text(html.unescape(title_match.group(1))) if title_match else path.parent.name
    description_match = DESCRIPTION_RE.search(content)
    if description_match:
        pitch = clean_text(html.unescape(description_match.group(1)))
    else:
        paragraphs = [clean_text(html.unescape(match.group(1))) for match in PITCH_RE.finditer(content)]
        pitch = next((item for item in paragraphs if item and item != title), "منتج صغير يعمل مباشرة من المتصفح.")
    return title, pitch


def load_backlog() -> dict[str, dict[str, Any]]:
    raw = json.loads((ROOT / "ideas/backlog.json").read_text(encoding="utf-8"))
    by_period: dict[str, dict[str, Any]] = {}
    for idea in raw.get("ideas", []):
        period = idea.get("built_period")
        if period:
            by_period[str(period)] = dict(idea)
    return by_period


def collect_products() -> list[dict[str, Any]]:
    by_period = load_backlog()
    products: list[dict[str, Any]] = []
    for path in sorted(PRODUCT_ROOT.glob("*/index.html")) + sorted((PRODUCT_ROOT / "weekly").glob("*/index.html")):
        relative = path.relative_to(ROOT).as_posix()
        title, pitch = parse_html(path)
        key = product_key(path)
        idea = by_period.get(key, {})
        if idea.get("title"):
            title = idea["title"]
        if idea.get("pitch"):
            pitch = idea["pitch"]
        if relative.startswith("products/weekly/"):
            url = f"products/weekly/{key}/"
            period = key
        else:
            url = f"products/{path.parent.name}/"
            period = str(idea.get("built_period", "phase-1"))
        lifecycle_status = str(idea.get("status", "built"))
        if lifecycle_status not in {"built", "retired", "revisit"}:
            lifecycle_status = "built"
        products.append(
            {
                "title": title,
                "pitch": pitch,
                "period": period,
                "category": str(idea.get("category", "general")),
                "url": url,
                "source": relative,
                "lifecycle_status": lifecycle_status,
                "lifecycle_reason": str(idea.get("lifecycle_reason", "")),
                "replacement_url": str(idea.get("replacement_url", "")),
            }
        )
    unique = {item["url"]: item for item in products}
    return sorted(unique.values(), key=lambda item: (item["period"], item["title"]), reverse=True)


def render_catalog(products: list[dict[str, Any]]) -> str:
    status_labels = {"retired": "متقاعد", "revisit": "قيد المراجعة"}
    cards = []
    for item in products:
        lifecycle_status = str(item.get("lifecycle_status", "built"))
        status_markup = ""
        if lifecycle_status in status_labels:
            reason = html.escape(str(item.get("lifecycle_reason", "")))
            status_markup = f'<span class="lifecycle lifecycle-{html.escape(lifecycle_status)}">{status_labels[lifecycle_status]}</span>'
            if reason:
                status_markup += f'<small class="lifecycle-reason">{reason}</small>'
        replacement_url = str(item.get("replacement_url", ""))
        replacement_markup = ""
        if replacement_url and re.fullmatch(r"products/(?:weekly/\d{4}-w\d{2}|[a-z0-9][a-z0-9-]*)/?", replacement_url, re.I):
            replacement_markup = f'<a class="replacement" href="{html.escape(replacement_url, quote=True)}">فتح البديل</a>'
        cards.append(
            """<article class="card" data-lifecycle="{lifecycle}"><div class="meta"><span>{period}</span><span>{category}</span></div>
            {status}<h2>{title}</h2><p>{pitch}</p><div class="actions"><a class="open" href="{url}">فتح المنتج</a>{replacement}</div></article>""".format(
                lifecycle=html.escape(lifecycle_status, quote=True),
                period=html.escape(str(item["period"])),
                category=html.escape(str(item["category"])),
                status=status_markup,
                title=html.escape(str(item["title"])),
                pitch=html.escape(str(item["pitch"])),
                url=html.escape(str(item["url"]), quote=True),
                replacement=replacement_markup,
            )
        )
    card_markup = "\n".join(cards) or '<p class="empty">لم تُنشر منتجات بعد.</p>'
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="كتالوج منتجات صغيرة منشورة من مصنع repositoryDz.">
  <title>مصنع المنتجات — الكتالوج</title>
  <style>
    :root{{--bg:#f5f1e8;--ink:#1e2935;--muted:#65717d;--accent:#b84b2a;--card:#fffdf8;--line:#e5dacb}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 100% 0,#ead9c6 0,transparent 34rem),var(--bg);color:var(--ink);font-family:Tahoma,"Segoe UI",Arial,sans-serif;line-height:1.7}}.wrap{{width:min(1100px,calc(100% - 32px));margin:auto}}header{{padding:54px 0 30px;display:flex;justify-content:space-between;gap:22px;align-items:end}}.eyebrow{{color:var(--accent);font-weight:800;font-size:.82rem;margin:0 0 9px}}h1{{font-size:clamp(2.2rem,6vw,4.7rem);line-height:1.08;letter-spacing:-.05em;margin:0;max-width:730px}}.lede{{color:var(--muted);max-width:650px;margin:18px 0 0;font-size:1.05rem}}.stat{{background:var(--ink);color:#fff;border-radius:20px;padding:18px 20px;min-width:150px;text-align:center}}.stat strong{{display:block;font-size:2rem;color:#ffd39d}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;padding:20px 0 58px}}.card{{background:color-mix(in srgb,var(--card) 93%,transparent);border:1px solid var(--line);border-radius:22px;padding:21px;display:flex;flex-direction:column;min-height:235px;box-shadow:0 14px 35px #6345290f}}.meta{{display:flex;justify-content:space-between;gap:10px;color:var(--accent);font-size:.78rem;font-weight:800}}.lifecycle{{display:inline-block;color:#fff;background:var(--accent);border-radius:999px;padding:2px 9px;font-size:.76rem;font-weight:800;margin:12px 0 3px}}.lifecycle-reason{{display:block;color:var(--muted);font-size:.78rem}}h2{{font-size:1.35rem;line-height:1.25;margin:18px 0 8px}}.card p{{color:var(--muted);margin:0 0 20px}}.actions{{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin-top:auto}}.open,.replacement{{color:var(--accent);font-weight:800;text-decoration:none;border-bottom:2px solid #e8a080;padding-bottom:2px}}footer{{border-top:1px solid var(--line);padding:20px 0 42px;color:var(--muted);font-size:.85rem}}.empty{{grid-column:1/-1}}@media(max-width:850px){{.grid{{grid-template-columns:repeat(2,1fr)}}header{{display:block}}.stat{{display:inline-block;margin-top:22px}}}}@media(max-width:560px){{.grid{{grid-template-columns:1fr}}}}
  </style>
</head>
<body>
  <div class="wrap">
    <header><div><p class="eyebrow">repositoryDz · كتالوج مفتوح</p><h1>منتجات صغيرة، منشورة كل أسبوع.</h1><p class="lede">استكشف الأدوات التي يبنيها المصنع من قوالب حتمية وتوليد محكوم ببوابات أمان.</p></div><div class="stat"><strong>{len(products)}</strong><span>منتجًا منشورًا</span></div></header>
    <main><section class="grid" aria-label="المنتجات المنشورة">{card_markup}</section></main>
    <footer>المنتجات تعمل من المتصفح ولا تتطلب حسابًا. القياس الخفيف يستخدم عداد زيارات مجهولًا معتمدًا للكتالوج والمنتجات.</footer>
  </div>
</body>
</html>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="index.html")
    parser.add_argument("--json-output", default="catalog.json")
    args = parser.parse_args()
    products = collect_products()
    html_output = render_catalog(products)
    (ROOT / args.output).write_text(html_output, encoding="utf-8")
    payload = {"version": 1, "products": products}
    (ROOT / args.json_output).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"products": len(products), "output": args.output, "json_output": args.json_output}, ensure_ascii=False))


if __name__ == "__main__":
    main()
