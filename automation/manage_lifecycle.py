#!/usr/bin/env python3
"""Safely manage idea lifecycle metadata without deleting published artifacts."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALID_STATUSES = {"backlog", "built", "retired", "revisit"}
INTERNAL_PRODUCT_RE = re.compile(r"^products/[a-z0-9][a-z0-9-]*/(?:index\.html)?$|^products/weekly/\d{4}-w\d{2}/$", re.I)
ALLOWED_TRANSITIONS = {
    "backlog": {"retired", "revisit"},
    "built": {"retired", "revisit"},
    "retired": {"revisit", "backlog"},
    "revisit": {"retired", "backlog"},
}


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("ideas"), list):
        raise ValueError("backlog must contain an ideas list")
    return data


def write_atomic(path: Path, data: dict[str, Any]) -> None:
    fd, temporary = tempfile.mkstemp(prefix="backlog-lifecycle-", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def find_idea(data: dict[str, Any], idea_id: str) -> dict[str, Any]:
    for idea in data["ideas"]:
        if isinstance(idea, dict) and idea.get("id") == idea_id:
            return idea
    raise ValueError(f"idea not found: {idea_id}")


def validate_replacement(value: str | None) -> str | None:
    if not value:
        return None
    if not INTERNAL_PRODUCT_RE.fullmatch(value):
        raise ValueError("replacement URL must be an internal products/... path")
    return value


def transition(data: dict[str, Any], idea_id: str, new_status: str, reason: str, replacement_url: str | None = None) -> dict[str, Any]:
    if new_status not in VALID_STATUSES:
        raise ValueError(f"status must be one of: {', '.join(sorted(VALID_STATUSES))}")
    reason = " ".join(reason.strip().split())
    if len(reason) < 8:
        raise ValueError("reason must contain at least 8 non-space characters")
    idea = find_idea(data, idea_id)
    old_status = str(idea.get("status", ""))
    if old_status not in VALID_STATUSES:
        raise ValueError(f"idea has unsupported current status: {old_status}")
    if new_status == old_status:
        raise ValueError("new status is the same as the current status")
    if new_status not in ALLOWED_TRANSITIONS[old_status]:
        raise ValueError(f"transition {old_status} -> {new_status} is not allowed")
    replacement = validate_replacement(replacement_url)
    if replacement and new_status not in {"retired", "revisit"}:
        raise ValueError("replacement URL is only meaningful for retired or revisit ideas")
    event = {
        "from": old_status,
        "to": new_status,
        "reason": reason,
        "changed_at": date.today().isoformat(),
    }
    history = idea.get("lifecycle_events", [])
    if not isinstance(history, list):
        raise ValueError("lifecycle_events must be a list when present")
    history.append(event)
    idea["lifecycle_events"] = history
    idea["status"] = new_status
    idea["lifecycle_reason"] = reason
    idea["lifecycle_changed_at"] = event["changed_at"]
    if replacement:
        idea["replacement_url"] = replacement
    elif new_status == "backlog":
        idea.pop("replacement_url", None)
    data["updated_at"] = event["changed_at"]
    return {"id": idea_id, "from": old_status, "to": new_status, "reason": reason, "replacement_url": replacement}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True, help="backlog idea id")
    parser.add_argument("--status", required=True, choices=sorted(VALID_STATUSES))
    parser.add_argument("--reason", required=True)
    parser.add_argument("--replacement-url")
    parser.add_argument("--backlog", default="ideas/backlog.json")
    parser.add_argument("--confirm", action="store_true", help="required before writing the backlog")
    args = parser.parse_args()
    path = ROOT / args.backlog
    data = load(path)
    result = transition(data, args.id, args.status, args.reason, args.replacement_url)
    if not args.confirm:
        print(json.dumps({"dry_run": True, **result}, ensure_ascii=False))
        return
    write_atomic(path, data)
    print(json.dumps({"dry_run": False, **result}, ensure_ascii=False))


if __name__ == "__main__":
    main()
