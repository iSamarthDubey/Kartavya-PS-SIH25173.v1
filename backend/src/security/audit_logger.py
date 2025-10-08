"""Structured audit logging utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, Iterable, Iterator, Optional


@dataclass
class AuditEvent:
    timestamp: str
    actor: str
    action: str
    status: str
    details: Dict[str, str]


class AuditLogger:
    """JSON-lines audit logger suitable for offline deployments."""

    def __init__(self, log_path: Optional[Path] = None) -> None:
        self.log_path = Path(log_path or "logs/audit.log")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(
        self,
        actor: str,
        action: str,
        status: str,
        **details: str,
    ) -> AuditEvent:
        event = AuditEvent(
            timestamp=datetime.now(UTC).isoformat(timespec="seconds"),
            actor=actor,
            action=action,
            status=status,
            details=details,
        )
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")
        return event

    def tail(self, limit: int = 50) -> Iterator[AuditEvent]:
        if not self.log_path.exists():
            return iter(())

        with self.log_path.open("r", encoding="utf-8") as handle:
            lines = handle.readlines()[-limit:]
        events = []
        for line in lines:
            try:
                data = json.loads(line)
                events.append(AuditEvent(**data))
            except (json.JSONDecodeError, TypeError):
                continue
        return iter(events)

    def iter_events(self) -> Iterator[AuditEvent]:
        if not self.log_path.exists():
            return iter(())
        with self.log_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    data = json.loads(line)
                    yield AuditEvent(**data)
                except (json.JSONDecodeError, TypeError):
                    continue
