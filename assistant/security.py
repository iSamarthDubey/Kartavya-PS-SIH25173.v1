"""Security integration helpers for the FastAPI assistant layer."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from fastapi import Depends, Header, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param

from src.security import (
    AuditLogger,
    AuthManager,
    RateLimiter,
    RBAC,
    SessionManager,
    is_safe_query,
    sanitize_query,
)
from src.security.session_manager import Session

logger = logging.getLogger(__name__)


@dataclass
class SecurityContext:
    """Holds the assistant's lightweight security primitives."""

    auth_manager: AuthManager
    sessions: SessionManager
    audit_logger: AuditLogger
    rate_limiter: RateLimiter
    token_ttl: int
    query_rate: Tuple[int, int]
    login_rate: Tuple[int, int]

    @classmethod
    def build_from_env(cls) -> "SecurityContext":
        """Initialise a context using environment-based overrides."""

        user_store = Path(os.environ.get("ASSISTANT_USER_STORE", "config/security_users.json"))
        audit_log = Path(os.environ.get("ASSISTANT_AUDIT_LOG", "logs/audit.log"))
        token_ttl = int(os.environ.get("ASSISTANT_TOKEN_TTL", "3600"))
        query_limit = int(os.environ.get("ASSISTANT_QUERY_RATE", "30"))
        query_window = int(os.environ.get("ASSISTANT_QUERY_WINDOW", "60"))
        login_limit = int(os.environ.get("ASSISTANT_LOGIN_RATE", "5"))
        login_window = int(os.environ.get("ASSISTANT_LOGIN_WINDOW", "300"))

        rbac = RBAC()
        auth_manager = AuthManager(user_store_path=user_store, rbac=rbac)
        sessions = SessionManager()
        audit_logger = AuditLogger(log_path=audit_log)
        rate_limiter = RateLimiter()

        context = cls(
            auth_manager=auth_manager,
            sessions=sessions,
            audit_logger=audit_logger,
            rate_limiter=rate_limiter,
            token_ttl=token_ttl,
            query_rate=(query_limit, query_window),
            login_rate=(login_limit, login_window),
        )
        context._bootstrap_defaults()
        return context

    def _bootstrap_defaults(self) -> None:
        """Ensure the system always has an administrative user."""

        admin_password = os.environ.get("ASSISTANT_ADMIN_PASSWORD", "Admin!2025")
        if not self.auth_manager.get_role("admin"):
            try:
                self.auth_manager.register_user("admin", admin_password, "admin")
                self.audit_logger.log_event("system", "users.bootstrap", "success", username="admin")
                if admin_password == "Admin!2025":
                    logger.warning(
                        "Bootstrap admin user created with default password. "
                        "Set ASSISTANT_ADMIN_PASSWORD to override and rotate immediately."
                    )
            except ValueError as exc:
                logger.error("Failed to bootstrap admin user: %s", exc)

    def get_session_from_token(self, token: str) -> Optional[Session]:
        session = self.sessions.validate(token)
        if session:
            self.sessions.touch(token, self.token_ttl)
        return session

    def create_session(self, username: str, role: str, metadata: Optional[dict[str, str]] = None) -> Session:
        return self.sessions.create_session(username=username, role=role, ttl_seconds=self.token_ttl, metadata=metadata)

    def revoke_session(self, token: str) -> None:
        self.sessions.revoke(token)

    def enforce_rate_limit(self, key: str, *, limit: int, window_seconds: int, detail: str) -> None:
        if not self.rate_limiter.allow(key, limit=limit, window_seconds=window_seconds):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=detail,
                headers={"Retry-After": str(window_seconds)},
            )

    def sanitize_or_reject(self, raw_query: str, actor: str) -> str:
        sanitized = sanitize_query(raw_query)
        if not sanitized:
            self.audit_logger.log_event(actor, "query.rejected", "denied", reason="empty_after_sanitize")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty after sanitization.")

        if not is_safe_query(sanitized):
            self.audit_logger.log_event(actor, "query.rejected", "denied", reason="unsafe_tokens")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query rejected by safety policy.")
        return sanitized


security_context = SecurityContext.build_from_env()


async def require_session(authorization: str = Header(default=None)) -> Session:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, token = get_authorization_scheme_param(authorization)
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session = security_context.get_session_from_token(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return session


def require_permission(permission: str):
    async def dependency(session: Session = Depends(require_session)) -> Session:
        if not security_context.auth_manager.rbac.has_permission(session.role, permission):
            security_context.audit_logger.log_event(
                session.username,
                "authz.denied",
                "denied",
                permission=permission,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return session

    return dependency


def require_rate_limited_permission(permission: str, limit_override: Optional[Tuple[int, int]] = None):
    async def dependency(session: Session = Depends(require_session)) -> Session:
        if not security_context.auth_manager.rbac.has_permission(session.role, permission):
            security_context.audit_logger.log_event(
                session.username,
                "authz.denied",
                "denied",
                permission=permission,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        limit, window = limit_override or security_context.query_rate
        security_context.enforce_rate_limit(
            key=f"{session.username}:{permission}",
            limit=limit,
            window_seconds=window,
            detail="Rate limit exceeded for requested operation",
        )
        return session

    return dependency


__all__ = [
    "SecurityContext",
    "security_context",
    "require_session",
    "require_permission",
    "require_rate_limited_permission",
]
