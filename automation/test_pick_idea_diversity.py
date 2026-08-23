#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))
from pick_idea import diversify_candidates, recent_memory  # noqa: E402


def idea(idea_id: str, category: str, shape: str) -> dict[str, str]:
    return {"id": idea_id, "category": category, "shape": shape, "status": "backlog", "strategy": "generate"}


def main() -> None:
    catalog = [
        {"period": "2026-w46", "category": "productivity", "shape": "converter", "lifecycle_status": "built"},
        {"period": "2026-w45", "category": "ecommerce", "shape": "sorter", "lifecycle_status": "built"},
        {"period": "2026-w44", "category": "ecommerce", "shape": "converter", "lifecycle_status": "built"},
        {"period": "2026-w43", "category": "ecommerce", "shape": "checker", "lifecycle_status": "built"},
        {"period": "2026-w47", "category": "ecommerce", "shape": "clarifier", "lifecycle_status": "retired"},
    ]
    memory = recent_memory(catalog)
    assert memory["periods"] == ["2026-w46", "2026-w45", "2026-w44", "2026-w43"]
    assert "ecommerce" in memory["categories"]
    assert "clarifier" not in memory["shapes"]

    candidates = [idea("ecommerce-checker", "ecommerce", "checker"), idea("design-game", "design", "game")]
    selected, selection = diversify_candidates(candidates, "generate", catalog)
    assert [item["id"] for item in selected] == ["design-game"]
    assert selection["category_fallback"] is False

    shape_candidates = [idea("design-checker", "design", "checker"), idea("design-game", "design", "game")]
    selected, selection = diversify_candidates(shape_candidates, "generate", catalog)
    assert [item["id"] for item in selected] == ["design-game"]
    assert selection["shape_fallback"] is False

    no_alternative = [idea("only-ecommerce", "ecommerce", "checker")]
    selected, selection = diversify_candidates(no_alternative, "generate", catalog)
    assert [item["id"] for item in selected] == ["only-ecommerce"]
    assert selection["category_fallback"] is True
    assert selection["shape_fallback"] is True

    templates = [
        {"id": "template-ecommerce", "category": "ecommerce", "shape": "checker", "strategy": "template:converter"},
    ]
    selected, selection = diversify_candidates(templates, "template:converter", catalog)
    assert selected == templates
    assert selection["enabled"] is False

    with tempfile.TemporaryDirectory() as directory:
        invalid_catalog = Path(directory) / "catalog.json"
        invalid_catalog.write_text("not-json", encoding="utf-8")
        command = [
            sys.executable,
            str(ROOT / "automation/pick_idea.py"),
            "--period", "2026-w48",
            "--strategy", "generate",
            "--dry-run",
            "--catalog", str(invalid_catalog),
        ]
        result = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
        payload = json.loads(result.stdout)
        assert payload["dry_run"] is True
        assert payload["selection"]["recent_categories"] == []

    command = [
        sys.executable,
        str(ROOT / "automation/pick_idea.py"),
        "--period", "2026-w48",
        "--strategy", "generate",
        "--dry-run",
    ]
    result = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    payload = json.loads(result.stdout)
    assert payload["idea"]["category"] not in payload["selection"]["recent_categories"]
    assert payload["idea"]["shape"] not in payload["selection"]["recent_shapes"]

    print("pick_idea diversity tests passed")


if __name__ == "__main__":
    main()
