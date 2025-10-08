"""Query sanitisation helpers.

We favour deterministic string manipulation so the behaviour is predictable in
restricted environments.
"""

from __future__ import annotations

import re
from typing import Iterable

_WHITESPACE_RE = re.compile(r"\s+")
_FORBIDDEN_CHARS = set("\r\0\x00\x1a")


def normalize_whitespace(text: str) -> str:
    """Collapse repeated whitespace and strip the ends."""

    if not isinstance(text, str):
        return ""
    return _WHITESPACE_RE.sub(" ", text).strip()


def strip_forbidden_chars(text: str) -> str:
    """Remove characters that could break downstream parsers."""

    return "".join(ch for ch in text if ch not in _FORBIDDEN_CHARS)


def remove_tokens(text: str, tokens: Iterable[str]) -> str:
    """Remove the provided tokens from *text* (case-insensitive)."""

    sanitized = text
    for token in tokens:
        sanitized = re.sub(token, "", sanitized, flags=re.IGNORECASE)
    return sanitized


def sanitize_query(query: str) -> str:
    """Apply a conservative sanitisation pipeline to *query*."""

    if not isinstance(query, str):
        return ""

    sanitized = strip_forbidden_chars(query)
    sanitized = sanitized.replace(";", " ")
    sanitized = normalized = normalize_whitespace(sanitized)
    return normalized
