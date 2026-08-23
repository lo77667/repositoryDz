#!/usr/bin/env python3
"""Shared static security rules for untrusted product HTML and issue text."""

from __future__ import annotations

import re

BLOCKED_CAPABILITY_PATTERNS = (
    ("fetch(", re.compile(r"\bfetch\s*\(", re.I)),
    ("XMLHttpRequest", re.compile(r"\bXMLHttpRequest\b", re.I)),
    ("WebSocket", re.compile(r"\bWebSocket\b", re.I)),
    ("EventSource", re.compile(r"\bEventSource\b", re.I)),
    ("sendBeacon", re.compile(r"\bsendBeacon\b", re.I)),
    ("service worker", re.compile(r"\bserviceWorker\b", re.I)),
    ("import()", re.compile(r"\bimport\s*\(", re.I)),
    ("javascript URL", re.compile(r"\bjavascript\s*:", re.I)),
    ("data HTML URL", re.compile(r"\bdata\s*:\s*(?:text/html|application/xhtml\+xml)", re.I)),
    ("WebSocket URL", re.compile(r"\b(?:ws|wss)\s*://", re.I)),
    ("document.cookie", re.compile(r"\bdocument\s*\.\s*cookie\b", re.I)),
)
SECRET_PATTERNS = (
    re.compile(r"(?:sk|ghp|gho|github_pat|xox[baprs])[-_][A-Za-z0-9_\-]{10,}", re.I),
    re.compile(r"AIza[A-Za-z0-9_\-]{20,}", re.I),
    re.compile(r"\b\d{8,}:[A-Za-z0-9_\-]{20,}\b"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
)
DANGEROUS_MARKUP_PATTERNS = (
    ("external frame/object", re.compile(r"<\s*(?:iframe|object|embed|applet|portal)\b", re.I)),
    ("base URL override", re.compile(r"<\s*base\b", re.I)),
    ("meta redirect", re.compile(r"<\s*meta\b[^>]+http-equiv\s*=\s*[\"']?refresh", re.I)),
    ("srcdoc content", re.compile(r"\bsrcdoc\s*=", re.I)),
    ("inline event handler", re.compile(r"\bon[a-z][a-z0-9_-]*\s*=", re.I)),
)


def blocked_capabilities(text: str) -> list[str]:
    return sorted({name for name, pattern in BLOCKED_CAPABILITY_PATTERNS if pattern.search(text)})


def dangerous_markup(text: str) -> list[str]:
    return sorted({name for name, pattern in DANGEROUS_MARKUP_PATTERNS if pattern.search(text)})


def has_credential_like_literal(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)
