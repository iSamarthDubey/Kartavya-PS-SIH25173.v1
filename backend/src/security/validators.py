"""Input validation helpers for the Kartavya SIEM Assistant.

The goal is to keep validation lightweight, deterministic, and free from
third-party dependencies so it works in air‑gapped hackathon environments.
"""

from __future__ import annotations

import re
from typing import Iterable, Pattern

_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
# Require at least 8 chars, one upper, one lower, one digit, one symbol
_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=\-\[\]{};:'\",.<>/?]).{8,64}$"
)
# Disallow obvious destructive tokens to protect downstream query builders
_QUERY_DENYLIST: tuple[Pattern[str], ...] = (
    re.compile(r"\bDROP\b", re.IGNORECASE),
    re.compile(r"\bDELETE\b", re.IGNORECASE),
    re.compile(r"\bTRUNCATE\b", re.IGNORECASE),
    re.compile(r"\bSHUTDOWN\b", re.IGNORECASE),
    re.compile(r";--"),
    re.compile(r"/\*"),
    re.compile(r"\*/"),
)


def is_valid_username(username: str) -> bool:
    """Return True if *username* satisfies our lightweight policy."""

    if not isinstance(username, str):
        return False
    return bool(_USERNAME_PATTERN.fullmatch(username))


def is_strong_password(password: str) -> bool:
    """Return True if *password* satisfies the strong password policy."""

    if not isinstance(password, str):
        return False
    return bool(_PASSWORD_PATTERN.fullmatch(password))


def contains_forbidden_tokens(text: str, tokens: Iterable[str]) -> bool:
    """Check if *text* contains any forbidden *tokens* (case-insensitive)."""

    if not isinstance(text, str):
        return True

    upper_text = text.upper()
    for token in tokens:
        if token.upper() in upper_text:
            return True
    return False


def is_safe_query(query: str) -> bool:
    """Return True if *query* is unlikely to be malicious or destructive."""

    if not isinstance(query, str):
        return False

    for pattern in _QUERY_DENYLIST:
        if pattern.search(query):
            return False
    return True
