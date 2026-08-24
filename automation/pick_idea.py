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
from typing import Any

from period_utils import parse_period, require_period

ROOT = Path(__file__).resolve().parents[1]
BACKLOG_PATH = ROOT / "ideas/backlog.json"
CATALOG_PATH = ROOT / "catalog.json"
RECENT_MEMORY_SIZE = 4

def current_period(today: date) -> str:
    year, week, _ = today.isocalendar()
    return f"{year}-w{week:02d}"


def stable_index(period: str, size: int) -> int:
    digest = hashlib.sha256(period.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % size


def load_backlog() -> dict[str, Any]:
    data = json.loads(BACKLOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data.get("ideas"), list):
        raise ValueError("backlog must contain an ideas list")
    return data


def load_catalog(path: Path = CATALOG_PATH) -> list[dict[str, Any]]:
    """Load catalog history defensively; missing/corrupt memory must not stop picking."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    products = data.get("products") if isinstance(data, dict) else None
    if not isinstance(products, list):
        return []
    return [item for item in products if isinstance(item, dict)]


def period_key(value: Any) -> tuple[int, int]:
    return parse_period(value) or (0, 0)


def recent_memory(catalog: list[dict[str, Any]], size: int = RECENT_MEMORY_SIZE) -> dict[str, Any]:
    active_products = [
        product for product in catalog
        if period_key(product.get("period")) != (0, 0)
        and str(product.get("lifecycle_status", "built")) != "retired"
    ]
    recent = sorted(active_products, key=lambda item: period_key(item.get("period")), reverse=True)[:size]
    return {
        "periods": [str(item.get("period")) for item in recent],
        "categories": sorted({str(item.get("category")) for item in recent if item.get("category")}),
        "shapes": sorted({str(item.get("shape")) for item in recent if item.get("shape")}),
    }


def diversify_candidates(
    available: list[dict[str, Any]],
    strategy: str | None,
    catalog: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Prefer candidates outside recent category and shape without making picking brittle."""
    memory = recent_memory(catalog)
    selection = {
        "enabled": strategy == "generate",
        "recent_periods": memory["periods"],
        "recent_categories": memory["categories"],
        "recent_shapes": memory["shapes"],
        "category_fallback": False,
        "shape_fallback": False,
    }
    if strategy != "generate":
        selection["reason"] = "diversity memory applies only to exact generate strategy"
        return available, selection

    category_candidates = [
        idea for idea in available if str(idea.get("category", "")) not in memory["categories"]
    ]
    if category_candidates:
        candidates = category_candidates
    else:
        candidates = available
        selection["category_fallback"] = True

    known_shapes = bool(memory["shapes"] and any(idea.get("shape") for idea in candidates))
    if known_shapes:
        shape_candidates = [
            idea for idea in candidates if str(idea.get("shape", "")) not in memory["shapes"]
        ]
        if shape_candidates:
            candidates = shape_candidates
        else:
            selection["shape_fallback"] = True
    selection["candidate_count"] = len(candidates)
    selection["reason"] = "recent category and shape avoidance"
    return candidates, selection


def write_backlog(data: dict[str, Any]) -> None:
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
    parser.add_argument("--strategy", help="Select only an exact strategy, such as generate")
    parser.add_argument("--strategy-prefix", help="Select only strategies beginning with this prefix")
    parser.add_argument("--dry-run", action="store_true", help="Select without marking the idea built")
    parser.add_argument("--catalog", default=str(CATALOG_PATH), help="Catalog JSON used as diversity memory")
    args = parser.parse_args()
    try:
        period = require_period(args.period or current_period(date.today()))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    data = load_backlog()
    available = [
        idea for idea in data["ideas"]
        if idea.get("status") == "backlog"
        and (not args.strategy or idea.get("strategy") == args.strategy)
        and (not args.strategy_prefix or str(idea.get("strategy", "")).startswith(args.strategy_prefix))
    ]
    if not available:
        raise SystemExit("No backlog ideas are available; refusing to repeat a built idea")

    catalog = load_catalog(Path(args.catalog))
    candidates, selection = diversify_candidates(available, args.strategy, catalog)
    selected = candidates[stable_index(period, len(candidates))].copy()
    if not args.dry_run:
        for idea in data["ideas"]:
            if idea.get("id") == selected.get("id"):
                idea["status"] = "built"
                idea["built_period"] = period
                break
        data["updated_at"] = date.today().isoformat()
        write_backlog(data)

    result = {"period": period, "idea": selected, "dry_run": args.dry_run, "selection": selection}
    print(json.dumps(result, ensure_ascii=False))
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"period={period}\n")
            handle.write(f"idea_json={json.dumps(selected, ensure_ascii=False, separators=(',', ':'))}\n")
            handle.write(f"idea_id={selected['id']}\n")
            handle.write(f"idea_slug={selected['slug']}\n")
            handle.write(f"idea_title={selected['title']}\n")
            handle.write(f"strategy={selected['strategy']}\n")
            handle.write(f"selection_reason={selection['reason']}\n")


if __name__ == "__main__":
    main()
