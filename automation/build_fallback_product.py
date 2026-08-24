#!/usr/bin/env python3
"""Build a safe deterministic placeholder when Tier B generation is rejected."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from period_utils import require_period


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--idea-json", required=True)
    parser.add_argument("--period", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    idea = json.loads(args.idea_json)
    try:
        period_value = require_period(args.period)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    title = html.escape(str(idea["title"]))
    pitch = html.escape(str(idea["pitch"]))
    period = html.escape(period_value)
    document = f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#171717">
  <title>{title} — قيد التجهيز</title>
  <style>
    :root {{ color-scheme: dark; --bg:#101010; --panel:#1b1b1b; --line:#3a3a3a; --text:#f4f4f4; --muted:#b8b8b8; --accent:#f5c451; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; min-height:100vh; display:grid; place-items:center; background:radial-gradient(circle at 50% 0,#3c3219,transparent 28rem),var(--bg); color:var(--text); font-family:Tahoma,"Segoe UI",Arial,sans-serif; line-height:1.7; }}
    .card {{ width:min(680px,calc(100% - 30px)); padding:clamp(24px,6vw,52px); background:var(--panel); border:1px solid var(--line); border-radius:24px; box-shadow:0 25px 80px #0008; }}
    .eyebrow {{ color:var(--accent); font-size:.8rem; font-weight:800; }} h1 {{ font-size:clamp(2rem,5vw,3.8rem); line-height:1.15; margin:10px 0 16px; }} p {{ color:var(--muted); }} button {{ border:0; border-radius:12px; padding:12px 17px; cursor:pointer; background:var(--accent); color:#201b0f; font:inherit; font-weight:800; }} button:focus-visible {{ outline:3px solid #fff; outline-offset:3px; }} #result {{ min-height:28px; color:var(--accent); }} footer {{ margin-top:30px; color:#888; font-size:.78rem; }}
  </style>
</head>
<body>
  <main class="card">
    <span class="eyebrow">نسخة آمنة احتياطية — {period}</span>
    <h1>{title}</h1>
    <p>{pitch}</p>
    <p>هذه النسخة المختصرة تحافظ على الفكرة إلى أن تنجح بوابة التحقق في قبول نسخة تفاعلية كاملة.</p>
    <button data-factory-action="primary" id="start" type="button">سجّل اهتمامي</button>
    <p id="result" aria-live="polite">لم يُسجّل شيء بعد.</p>
    <footer>لا اتصال خارجي، ولا بيانات تغادر جهازك.</footer>
  </main>
  <script>
    (() => {{
      "use strict";
      document.querySelector("#start").addEventListener("click", () => {{
        document.querySelector("#result").textContent = "تم تسجيل الاهتمام محليًا لهذه الجلسة.";
      }});
    }})();
  </script>
</body>
</html>
'''
    output = Path(args.output)
    if output.exists():
        raise SystemExit(f"Refusing to overwrite an existing artifact: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    print(json.dumps({"status": "fallback", "path": args.output, "period": args.period}, ensure_ascii=False))


if __name__ == "__main__":
    main()
