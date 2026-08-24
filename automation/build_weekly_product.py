#!/usr/bin/env python3
"""Build one deterministic weekly product from a selected backlog idea."""

from __future__ import annotations

import argparse
import html as html_module
import json
import os
import re
from datetime import date
from pathlib import Path

from period_utils import require_period

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "templates"
OUTPUT_ROOT = ROOT / "products/weekly"
STRATEGY_TO_TEMPLATE = {
    "template:idea-mashup": ROOT / "products/idea-mashup/index.html",
    "template:converter": TEMPLATE_ROOT / "converter.html",
    "template:visual-toy": TEMPLATE_ROOT / "visual-toy.html",
    "template:text-tool": TEMPLATE_ROOT / "text-tool.html",
}


def period_for(today: date) -> str:
    iso_year, iso_week, _ = today.isocalendar()
    return f"{iso_year}-w{iso_week:02d}"


def safe_slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "weekly-idea"


def load_idea(raw: str | None) -> dict[str, str]:
    if raw:
        idea = json.loads(raw)
    else:
        raise SystemExit("An idea JSON payload is required")
    required = ("id", "slug", "title", "pitch", "strategy", "status")
    missing = [key for key in required if not idea.get(key)]
    if missing:
        raise SystemExit(f"Selected idea is missing fields: {', '.join(missing)}")
    if idea["status"] != "backlog":
        raise SystemExit("Selected idea is not in backlog status")
    if idea["strategy"] not in STRATEGY_TO_TEMPLATE:
        raise SystemExit(f"Unsupported template strategy: {idea['strategy']}")
    return {key: str(value) for key, value in idea.items()}


def render(template: str, idea: dict[str, str], period: str) -> str:
    payload = json.dumps(idea, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    injection = f"  <script>\n    window.__WEEKLY_IDEA__ = {payload};\n  </script>\n"
    marker = "  <script>\n    (() => {"
    if marker not in template:
        raise RuntimeError("The selected template script marker was not found")
    html = template.replace(marker, injection + marker, 1)
    escaped_title = html_module.escape(idea["title"])
    html = html.replace("<title>شرارة منتج — مولّد أفكار رقمية</title>", f"<title>{escaped_title} — منتج أسبوعي</title>", 1)
    html = html.replace("<title>محول رقمي — منتج أسبوعي</title>", f"<title>{escaped_title} — منتج أسبوعي</title>", 1)
    html = html.replace("<title>لعبة بصرية — منتج أسبوعي</title>", f"<title>{escaped_title} — منتج أسبوعي</title>", 1)
    html = html.replace("<title>أداة نصية — منتج أسبوعي</title>", f"<title>{escaped_title} — منتج أسبوعي</title>", 1)
    html = html.replace("نسخة يدوية تجريبية — المرحلة 1", f"نسخة أسبوعية {period} — المرحلة 3", 1)
    html = html.replace("نسخة ثابتة من مصنع المنتجات — <span id=\"period-label\">فترة أسبوعية</span>", f"نسخة أسبوعية من مصنع المنتجات — <span id=\"period-label\">{period}</span>", 1)
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
    parser.add_argument("--period", help="Explicit period such as 2026-w36")
    parser.add_argument("--idea-json", required=True, help="Selected backlog idea as a JSON object")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing a different existing artifact")
    args = parser.parse_args()

    try:
        period = require_period(args.period or period_for(date.today()))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    idea = load_idea(args.idea_json)
    template_path = STRATEGY_TO_TEMPLATE[idea["strategy"]]
    if not template_path.exists():
        raise SystemExit(f"Template missing: {template_path}")

    html = render(template_path.read_text(encoding="utf-8"), idea, period)
    output_path = write_output(period, html, args.overwrite)
    product_url = f"https://lo77667.github.io/repositoryDz/products/weekly/{output_path.parent.name}/"
    result = {"period": period, "path": str(output_path.relative_to(ROOT)), "url": product_url, "idea": idea, "template": str(template_path.relative_to(ROOT))}
    print(json.dumps(result, ensure_ascii=False))
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"period={period}\n")
            handle.write(f"path={output_path.relative_to(ROOT)}\n")
            handle.write(f"url={product_url}\n")
            handle.write(f"title={idea['title']}\n")
            handle.write(f"idea_id={idea['id']}\n")
            handle.write(f"strategy={idea['strategy']}\n")
            handle.write(f"template={template_path.relative_to(ROOT)}\n")


if __name__ == "__main__":
    main()
