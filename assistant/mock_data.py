"""Synthetic SIEM records for offline demos and tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from itertools import cycle
from typing import Dict, Iterable, List, Tuple

_SEVERITY_SEQUENCE: Tuple[str, ...] = ("critical", "high", "medium", "low")
_EVENT_TYPES: Tuple[str, ...] = (
    "failed_login",
    "successful_login",
    "network_connection",
    "malware_alert",
    "policy_violation",
)
_IP_POOL: Tuple[str, ...] = (
    "10.10.1.10",
    "10.10.1.24",
    "10.10.5.4",
    "172.16.0.8",
    "192.168.1.12",
    "192.168.5.54",
)
_USER_POOL: Tuple[str, ...] = (
    "admin",
    "analyst",
    "john.doe",
    "jane.smith",
    "svc-reporter",
)
_SOURCE_POOL: Tuple[str, ...] = (
    "auth_service",
    "vpn_gateway",
    "ids_sensor",
    "firewall",
    "edr_agent",
)


def _timestamp_series(limit: int) -> Iterable[str]:
    now = datetime.now(UTC)
    for offset in range(limit):
        yield (now - timedelta(minutes=offset * 5)).isoformat(timespec="seconds")


def _rotate(values: Iterable[str]) -> Iterable[str]:
    return cycle(values)


def _choose_entities(entities: Dict[str, List[str]], key: str, fallback: Iterable[str]) -> Iterable[str]:
    values = entities.get(key)
    if values:
        return cycle(values)
    return cycle(fallback)


def generate_mock_logs(intent: str, entities: Dict[str, List[str]], limit: int = 10) -> List[Dict[str, str]]:
    """Return deterministic mock SIEM records tailored to the incoming intent."""

    limit = max(1, min(limit, 100))
    severity_iter = _rotate(_SEVERITY_SEQUENCE)
    timestamp_iter = _timestamp_series(limit)
    ip_iter = _choose_entities(entities, "ip_address", _IP_POOL)
    user_iter = _choose_entities(entities, "user", _USER_POOL)
    source_iter = _rotate(_SOURCE_POOL)

    intent_label = (intent or "search_events").lower()

    records: List[Dict[str, str]] = []
    for _ in range(limit):
        timestamp = next(timestamp_iter)
        severity = next(severity_iter)
        source_ip = next(ip_iter)
        username = next(user_iter)
        source = next(source_iter)

        records.append(
            {
                "@timestamp": timestamp,
                "event.category": "authentication" if "login" in intent_label else "network",
                "event.type": intent_label,
                "event.severity": severity,
                "source.ip": source_ip,
                "source.address": source_ip,
                "user.name": username,
                "observer.name": source,
                "message": _format_message(intent_label, username, source_ip, severity),
            }
        )

    return records


def _format_message(intent: str, username: str, ip_address: str, severity: str) -> str:
    if intent.startswith("failed_login") or "failed" in intent:
        return f"{severity.title()} failed login for user {username} from {ip_address}"
    if intent.startswith("successful_login"):
        return f"Successful login for user {username} from {ip_address}"
    if "network" in intent:
        return f"{severity.title()} network event observed on {ip_address}"
    if "malware" in intent:
        return f"Malware alert ({severity}) detected by endpoint agent for {username}"
    return f"{severity.title()} event for user {username} from {ip_address}"


__all__ = ["generate_mock_logs"]
