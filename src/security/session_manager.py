"""Session management utilities for issued auth tokens."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Dict, Optional


@dataclass
class Session:
    token: str
    username: str
    role: str
    expires_at: datetime
    metadata: Dict[str, str]

    @property
    def is_expired(self) -> bool:
        return datetime.now(UTC) >= self.expires_at


class SessionManager:
    """In-memory session store with TTL support."""

    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = {}

    def create_session(
        self,
        username: str,
        role: str,
        ttl_seconds: int = 3600,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Session:
        token = secrets.token_urlsafe(32)
        session = Session(
            token=token,
            username=username,
            role=role,
            expires_at=datetime.now(UTC) + timedelta(seconds=ttl_seconds),
            metadata=metadata or {},
        )
        self._sessions[token] = session
        return session

    def validate(self, token: str) -> Optional[Session]:
        session = self._sessions.get(token)
        if not session:
            return None
        if session.is_expired:
            self._sessions.pop(token, None)
            return None
        return session

    def touch(self, token: str, ttl_seconds: int) -> Optional[Session]:
        session = self.validate(token)
        if not session:
            return None
        session.expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
        return session

    def revoke(self, token: str) -> None:
        self._sessions.pop(token, None)

    def cleanup(self) -> None:
        expired_tokens = [token for token, session in self._sessions.items() if session.is_expired]
        for token in expired_tokens:
            self._sessions.pop(token, None)

    def active_sessions(self) -> Dict[str, Session]:
        self.cleanup()
        return dict(self._sessions)
