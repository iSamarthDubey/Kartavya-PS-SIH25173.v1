"""Integration-level tests for FastAPI security wiring."""

from __future__ import annotations

import importlib
from collections.abc import Generator
from typing import Any, Dict, List, Tuple

import pytest
from fastapi.testclient import TestClient


class DummyContextManager:
    """Minimal async context manager stub used for tests."""

    def __init__(self) -> None:
        self.cleared: List[str] = []
        self.histories: Dict[str, List[Dict[str, Any]]] = {}

    async def clear_conversation(self, conversation_id: str) -> None:
        self.cleared.append(conversation_id)

    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        return self.histories.get(conversation_id, [])


class DummyPipeline:
    """Pipeline stub that mimics the public API used by the app."""

    def __init__(self) -> None:
        self.is_initialized = True
        self.context_manager = DummyContextManager()

    async def initialize(self) -> bool:  # pragma: no cover - not used after override
        self.is_initialized = True
        return True

    def get_health_status(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "components": {"stub": True},
            "health_score": "1/1",
            "is_initialized": True,
        }

    async def process_query(
        self,
        user_input: str,
        conversation_id: str | None = None,
        user_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return {
            "conversation_id": conversation_id or "conv-test",
            "user_query": user_input,
            "intent": "search_logs",
            "entities": [],
            "query_type": "search",
            "siem_query": {"match_all": {}},
            "results": [],
            "visualizations": [],
            "summary": "Processed",
            "metadata": {"processing_time_seconds": 0.01, "context": user_context or {}},
            "status": "success",
        }

    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        return await self.context_manager.get_conversation_history(conversation_id)


@pytest.fixture()
def app_client(tmp_path, monkeypatch) -> Generator[Tuple[TestClient, Any], None, None]:
    """Provide a FastAPI test client with isolated security storage."""

    user_store = tmp_path / "users.json"
    audit_log = tmp_path / "audit.log"
    monkeypatch.setenv("ASSISTANT_USER_STORE", str(user_store))
    monkeypatch.setenv("ASSISTANT_AUDIT_LOG", str(audit_log))
    monkeypatch.setenv("ASSISTANT_ADMIN_PASSWORD", "Admin!2025")

    module = importlib.import_module("assistant.main")
    module = importlib.reload(module)

    dummy_pipeline = DummyPipeline()
    module.pipeline = dummy_pipeline
    module.app.router.on_startup.clear()
    module.app.router.on_shutdown.clear()

    async def override_get_pipeline():
        return dummy_pipeline

    module.app.dependency_overrides[module.get_pipeline] = override_get_pipeline

    with TestClient(module.app) as client:
        yield client, module

    module.app.dependency_overrides.clear()


def _login(client: TestClient, username: str = "admin", password: str = "Admin!2025") -> Tuple[str, Dict[str, Any]]:
    response = client.post(
        "/assistant/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    token = data["access_token"]
    return token, data


def test_login_me_logout_flow(app_client):
    client, _module = app_client
    token, login_payload = _login(client)

    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/assistant/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "admin"

    logout_response = client.post("/assistant/auth/logout", headers=headers)
    assert logout_response.status_code == 200

    me_after_logout = client.get("/assistant/auth/me", headers=headers)
    assert me_after_logout.status_code == 401


def test_register_requires_admin(app_client):
    client, _module = app_client
    token, _payload = _login(client)

    headers = {"Authorization": f"Bearer {token}"}
    register_response = client.post(
        "/assistant/auth/register",
        json={"username": "analyst1", "password": "Analyst!2025", "role": "analyst"},
        headers=headers,
    )
    assert register_response.status_code == 200
    assert register_response.json()["role"] == "analyst"


def test_query_rejects_unsafe_input(app_client):
    client, _module = app_client
    token, _ = _login(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/assistant/ask",
        json={"query": "DROP TABLE users"},
        headers=headers,
    )
    assert response.status_code == 400


def test_query_happy_path_returns_metadata(app_client):
    client, _module = app_client
    token, _ = _login(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/assistant/ask",
        json={"query": "Show me recent alerts"},
        headers=headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["metadata"]["original_query"] == "Show me recent alerts"
    assert payload["metadata"]["actor"] == "admin"