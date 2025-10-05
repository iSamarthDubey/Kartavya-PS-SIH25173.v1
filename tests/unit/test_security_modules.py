import json
import time
from pathlib import Path

import pytest

from src.security.auth_manager import AuthManager
from src.security.audit_logger import AuditLogger
from src.security.rbac import RBAC
from src.security.rate_limiter import RateLimiter
from src.security.sanitizer import normalize_whitespace, sanitize_query
from src.security.session_manager import SessionManager
from src.security.validators import (
    contains_forbidden_tokens,
    is_safe_query,
    is_strong_password,
    is_valid_username,
)


@pytest.fixture()
def user_store(tmp_path: Path) -> Path:
    return tmp_path / "users.json"


def test_auth_manager_register_and_authenticate(user_store: Path) -> None:
    manager = AuthManager(user_store_path=user_store)
    record = manager.register_user("analyst.user", "Secur3!Pass", "analyst")

    assert record.username == "analyst.user"
    assert manager.authenticate("analyst.user", "Secur3!Pass") is True
    assert manager.authenticate("analyst.user", "WrongPass1!") is False
    assert manager.get_role("analyst.user") == "analyst"

    manager.change_password("analyst.user", "N3w!Password")
    assert manager.authenticate("analyst.user", "N3w!Password") is True


def test_auth_manager_persistence(user_store: Path) -> None:
    first = AuthManager(user_store_path=user_store)
    first.register_user("admin.user", "Adm1n!Pass", "admin")

    restored = AuthManager(user_store_path=user_store)
    assert restored.authenticate("admin.user", "Adm1n!Pass") is True


def test_session_manager_create_and_validate() -> None:
    sessions = SessionManager()
    session = sessions.create_session("analyst.user", "analyst", ttl_seconds=1)
    assert sessions.validate(session.token) is not None

    time.sleep(1.1)
    assert sessions.validate(session.token) is None


def test_rbac_permission_checks() -> None:
    rbac = RBAC()
    assert rbac.has_permission("admin", "users:create")
    assert rbac.has_permission("analyst", "queries:run")
    assert not rbac.has_permission("viewer", "settings:update")

    with pytest.raises(PermissionError):
        rbac.require_permission("viewer", "settings:update")


def test_rate_limiter_allows_within_limits() -> None:
    limiter = RateLimiter()
    limit = 3
    window = 1
    key = "client-1"

    assert limiter.allow(key, limit, window) is True
    assert limiter.allow(key, limit, window) is True
    assert limiter.allow(key, limit, window) is True
    assert limiter.allow(key, limit, window) is False

    time.sleep(window)
    assert limiter.allow(key, limit, window) is True


def test_validators_and_sanitizer() -> None:
    assert is_valid_username("valid.user") is True
    assert is_valid_username("bad user") is False

    assert is_strong_password("Secur3!Pass") is True
    assert is_strong_password("weakpass") is False

    dangerous_query = "DROP TABLE users;"
    assert contains_forbidden_tokens(dangerous_query, ["drop"]) is True
    assert is_safe_query("find failed logins") is True
    assert is_safe_query(dangerous_query) is False

    messy = "  find   failed\nlogins ;"
    sanitized = sanitize_query(messy)
    assert sanitize_query(messy) == sanitized
    assert "  " not in sanitized
    assert ";" not in sanitized
    assert normalize_whitespace("a\t b\n c") == "a b c"


def test_audit_logger_writes_json(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    logger = AuditLogger(log_path=log_path)
    logger.log_event("analyst.user", "login", "success", ip="127.0.0.1")

    assert log_path.exists()
    data = json.loads(log_path.read_text().strip())
    assert data["actor"] == "analyst.user"
    assert data["action"] == "login"
    assert data["status"] == "success"
    assert data["details"]["ip"] == "127.0.0.1"
