#!/usr/bin/env python3
"""Pick and mark one not-yet-built backlog idea for a weekly run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKLOG_PATH = ROOT / "ideas/backlog.json"


def current_period(today: date) -> str:
    year, week, _ = today.isocalendar()
    return f"{year}-w{week:02d}"


def stable_index(period: str, size: int) -> int:
    digest = hashlib.sha256(period.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % size


def load_backlog() -> dict:
    data = json.loads(BACKLOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data.get("ideas"), list):
        raise ValueError("backlog must contain an ideas list")
    return data


def write_backlog(data: dict) -> None:
    BACKLOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="backlog-", suffix=".json", dir=BACKLOG_PATH.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, BACKLOG_PATH)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--period", help="Explicit period such as 2026-w36")
    parser.add_argument("--dry-run", action="store_true", help="Select without marking the idea built")
    args = parser.parse_args()
    period = args.period or current_period(date.today())
    if not __import__("re").fullmatch(r"\d{4}-w\d{2}", period):
        raise SystemExit("Period must match YYYY-wNN")

    data = load_backlog()
    available = [idea for idea in data["ideas"] if idea.get("status") == "backlog"]
    if not available:
        raise SystemExit("No backlog ideas are available; refusing to repeat a built idea")
    selected = available[stable_index(period, len(available))].copy()
    if not args.dry_run:
        for idea in data["ideas"]:
            if idea.get("id") == selected.get("id"):
                idea["status"] = "built"
                idea["built_period"] = period
                break
        data["updated_at"] = date.today().isoformat()
        write_backlog(data)

    result = {"period": period, "idea": selected, "dry_run": args.dry_run}
    print(json.dumps(result, ensure_ascii=False))
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"period={period}\n")
            handle.write(f"idea_json={json.dumps(selected, ensure_ascii=False, separators=(',', ':'))}\n")
            handle.write(f"idea_id={selected['id']}\n")
            handle.write(f"idea_slug={selected['slug']}\n")
            handle.write(f"strategy={selected['strategy']}\n")


if __name__ == "__main__":
    main()
