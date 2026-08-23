#!/usr/bin/env python3
"""Deterministically triage a public GitHub product-idea issue.

This tool never writes to ideas/backlog.json and never executes user-supplied text.
It emits a review proposal for a human maintainer or a workflow to comment on.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIELD_HEADINGS = {
    "product_title": "عنوان الفكرة",
    "problem": "المشكلة التي يحلها المنتج",
    "product_pitch": "وصف المنتج المقترح",
    "audience": "الجمهور المستهدف",
    "strategy_hint": "الشكل الأقرب للأداة",
    "evidence": "دليل الحاجة أو مثال استخدام",
    "constraints": "قيود أو ملاحظات إضافية",
    "consent": "الإقرار",
}
REQUIRED_FIELDS = ("product_title", "problem", "product_pitch", "audience", "strategy_hint", "evidence", "consent")
MAX_LENGTHS = {
    "product_title": 120,
    "problem": 2000,
    "product_pitch": 1500,
    "audience": 300,
    "strategy_hint": 100,
    "evidence": 2000,
    "constraints": 1500,
    "consent": 3000,
}
SECRET_PATTERNS = (
    re.compile(r"(?:sk|ghp|gho|github_pat)_[A-Za-z0-9_\-]{12,}", re.I),
    re.compile(r"AIza[A-Za-z0-9_\-]{20,}", re.I),
    re.compile(r"\b\d{8,}:[A-Za-z0-9_\-]{20,}\b"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
)
UNSAFE_PATTERNS = (
    re.compile(r"https?://", re.I),
    re.compile(r"<\s*(script|iframe|object|embed|form)\b", re.I),
    re.compile(r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon)\s*\(", re.I),
)
STRATEGY_MAP = {
    "محول أو حاسبة": "template:converter",
    "أداة نصية": "template:text-tool",
    "لعبة أو تجربة بصرية": "template:visual-toy",
    "مولد أفكار أو محتوى": "generate",
    "أداة أخرى": "generate",
}
CATEGORY_KEYWORDS = {
    "ecommerce": ("متجر", "تجارة", "شحن", "دفع", "منتج", "عميل", "استرجاع", "سعر"),
    "content": ("محتوى", "كاتب", "صانع", "نشر", "فيديو", "تسويق"),
    "services": ("خدمة", "مستقل", "استشارة", "موعد", "حجز"),
}


def normalize(value: str) -> str:
    value = value.casefold().strip()
    value = re.sub(r"[\u064B-\u065F\u0670]", "", value)
    value = value.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي")
    value = re.sub(r"[^\w\u0600-\u06FF]+", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def parse_issue_form(body: str) -> dict[str, str]:
    headings = {f"### {heading}": key for key, heading in FIELD_HEADINGS.items()}
    lines = body.replace("\r\n", "\n").split("\n")
    values: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        heading = line.strip()
        if heading in headings:
            current = headings[heading]
            values.setdefault(current, [])
            continue
        if current is not None:
            values[current].append(line)
    return {key: "\n".join(items).strip() for key, items in values.items()}


def read_issue_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Issue payload must be a JSON object")
    issue = payload.get("issue", payload)
    if not isinstance(issue, dict):
        raise ValueError("Issue payload does not contain an issue object")
    return issue


def check_safety(fields: dict[str, str]) -> list[str]:
    problems: list[str] = []
    combined = "\n".join(fields.values())
    for pattern in SECRET_PATTERNS:
        if pattern.search(combined):
            problems.append("possible-secret")
            break
    for pattern in UNSAFE_PATTERNS:
        if pattern.search(combined):
            problems.append("unsafe-content")
            break
    for key, value in fields.items():
        if len(value) > MAX_LENGTHS.get(key, 2000):
            problems.append(f"{key}-too-long")
    return sorted(set(problems))


def missing_fields(fields: dict[str, str]) -> list[str]:
    missing = []
    for key in REQUIRED_FIELDS:
        value = fields.get(key, "").strip()
        if not value:
            missing.append(key)
    for key in ("product_title", "problem", "product_pitch", "audience", "evidence"):
        if fields.get(key, "").strip() and len(normalize(fields[key])) < 3:
            missing.append(f"{key}-too-short")
    return sorted(set(missing))


def similarity(left: str, right: str) -> float:
    left_norm = normalize(left)
    right_norm = normalize(right)
    if not left_norm or not right_norm:
        return 0.0
    sequence = difflib.SequenceMatcher(None, left_norm, right_norm).ratio()
    left_tokens = set(left_norm.split())
    right_tokens = set(right_norm.split())
    union = left_tokens | right_tokens
    jaccard = len(left_tokens & right_tokens) / len(union) if union else 0.0
    return max(sequence, jaccard)


def find_duplicate(title: str, pitch: str, backlog: dict[str, Any]) -> dict[str, Any] | None:
    strongest: dict[str, Any] | None = None
    for idea in backlog.get("ideas", []):
        if not isinstance(idea, dict):
            continue
        title_score = similarity(title, str(idea.get("title", "")))
        pitch_score = similarity(pitch, str(idea.get("pitch", "")))
        combined_score = max(title_score, pitch_score, (title_score + pitch_score) / 2)
        if combined_score >= 0.84 and (strongest is None or combined_score > strongest["similarity"]):
            strongest = {"id": idea.get("id", ""), "title": idea.get("title", ""), "similarity": round(combined_score, 3)}
    return strongest


def map_strategy(hint: str) -> str:
    return STRATEGY_MAP.get(hint.strip(), "generate")


def map_category(fields: dict[str, str]) -> str:
    combined = normalize(" ".join(fields.get(key, "") for key in ("problem", "product_pitch", "audience", "evidence")))
    for category, words in CATEGORY_KEYWORDS.items():
        if any(normalize(word) in combined for word in words):
            return category
    return "general"


def score(fields: dict[str, str], strategy: str, duplicate: dict[str, Any] | None, safety: list[str]) -> dict[str, int]:
    product_title = fields.get("product_title", "")
    problem = fields.get("problem", "")
    product_pitch = fields.get("product_pitch", "")
    audience_text = fields.get("audience", "")
    evidence_text = fields.get("evidence", "")
    clarity = min(20, 8 + (4 if len(normalize(product_title)) >= 8 else 0) + (4 if len(normalize(problem)) >= 40 else 0) + (4 if len(normalize(product_pitch)) >= 30 else 0))
    audience = 15 if len(normalize(audience_text)) >= 8 else 8
    evidence = min(20, 8 + (6 if len(normalize(evidence_text)) >= 60 else 0) + (6 if len(normalize(evidence_text)) >= 140 else 0))
    feasibility = 20 if strategy.startswith("template:") else 12
    novelty = 0 if duplicate else 15
    safety_score = 0 if safety else 10
    return {"clarity": clarity, "audience": audience, "evidence": evidence, "feasibility": feasibility, "novelty": novelty, "safety": safety_score}


def triage(issue: dict[str, Any], backlog: dict[str, Any]) -> dict[str, Any]:
    body = str(issue.get("body", ""))
    fields = parse_issue_form(body)
    missing = missing_fields(fields)
    safety = check_safety(fields)
    title = fields.get("product_title", "").strip()
    pitch = fields.get("product_pitch", "").strip()
    duplicate = find_duplicate(title, pitch, backlog) if title and pitch else None
    if safety:
        status = "rejected"
        reasons = safety
    elif missing:
        status = "needs-info"
        reasons = missing
    elif duplicate:
        status = "duplicate"
        reasons = ["similar-backlog-idea"]
    else:
        status = "ready-for-review"
        reasons = ["passed-automated-triage"]
    strategy = map_strategy(fields.get("strategy_hint", ""))
    scores = score(fields or {key: "" for key in REQUIRED_FIELDS}, strategy, duplicate, safety)
    total = sum(scores.values())
    issue_number = str(issue.get("number", "unknown"))
    digest = hashlib.sha256(f"{issue_number}\n{normalize(title)}\n{normalize(pitch)}".encode("utf-8")).hexdigest()[:8]
    proposed = None
    if status == "ready-for-review":
        proposed = {
            "id": f"community-{issue_number}-{digest}",
            "slug": f"community-{issue_number}-{digest}",
            "title": title,
            "pitch": pitch,
            "strategy": strategy,
            "status": "backlog",
            "difficulty": 2 if strategy.startswith("template:") else 3,
            "category": map_category(fields),
            "source_issue": int(issue["number"]) if str(issue.get("number", "")).isdigit() else issue_number,
            "priority_score": total,
        }
    return {
        "version": 1,
        "issue_number": issue.get("number"),
        "issue_title": str(issue.get("title", "")),
        "status": status,
        "reasons": reasons,
        "fields": fields,
        "strategy": strategy,
        "category": map_category(fields),
        "score": {**scores, "total": total},
        "duplicate": duplicate,
        "proposed_idea": proposed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue-json", required=True, help="GitHub issue JSON payload")
    parser.add_argument("--backlog", default="ideas/backlog.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    issue = read_issue_payload(Path(args.issue_json))
    backlog = json.loads((ROOT / args.backlog).read_text(encoding="utf-8"))
    result = triage(issue, backlog)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "score": result["score"]["total"], "reasons": result["reasons"]}, ensure_ascii=False))
    if result["status"] == "rejected":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
