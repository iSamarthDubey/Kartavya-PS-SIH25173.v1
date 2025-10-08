"""Lightweight rate limiting for the SIEM assistant API."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict


@dataclass
class RateLimiter:
    """Token bucket style limiter suitable for single-process usage."""

    _buckets: Dict[str, Deque[float]] = field(default_factory=lambda: defaultdict(deque))

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        """Return True if the caller identified by *key* may proceed."""

        if limit <= 0:
            return False
        now = time.time()
        window_start = now - window_seconds
        bucket = self._buckets[key]

        # Drop timestamps that are outside the window
        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= limit:
            return False

        bucket.append(now)
        return True

    def remaining(self, key: str, limit: int, window_seconds: int) -> int:
        """Return the remaining allowance for *key* within the window."""

        now = time.time()
        window_start = now - window_seconds
        bucket = self._buckets[key]

        while bucket and bucket[0] < window_start:
            bucket.popleft()

        return max(limit - len(bucket), 0)

    def reset(self, key: str) -> None:
        self._buckets.pop(key, None)
