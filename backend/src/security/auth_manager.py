"""Authentication manager for the Kartavya SIEM assistant."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import UTC, datetime
from hashlib import pbkdf2_hmac
from pathlib import Path
from typing import Dict, Optional

from .rbac import RBAC
from .validators import is_strong_password, is_valid_username

_HASH_ITERATIONS = 120_000
_SALT_BYTES = 16


@dataclass
class UserRecord:
    username: str
    password_hash: str
    salt: str
    role: str
    created_at: str


class AuthManager:
    """Handles credential storage, verification, and role lookup."""

    def __init__(self, user_store_path: Optional[os.PathLike[str]] = None, rbac: Optional[RBAC] = None) -> None:
        self.user_store_path = Path(user_store_path) if user_store_path else None
        self.rbac = rbac or RBAC()
        self._users: Dict[str, UserRecord] = {}
        if self.user_store_path and self.user_store_path.exists():
            self._load_users()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def register_user(self, username: str, password: str, role: str) -> UserRecord:
        if not is_valid_username(username):
            raise ValueError("Invalid username. Use 3-32 chars (letters, numbers, _ . -)")
        if not is_strong_password(password):
            raise ValueError("Password does not meet complexity requirements")
        if username in self._users:
            raise ValueError("User already exists")
        self.rbac.assert_valid_role(role)

        salt, password_hash = self._hash_password(password)
        record = UserRecord(
            username=username,
            password_hash=password_hash,
            salt=salt,
            role=role,
            created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )
        self._users[username] = record
        self._persist()
        return record

    def authenticate(self, username: str, password: str) -> bool:
        record = self._users.get(username)
        if not record:
            return False
        return self._verify_password(password, record.salt, record.password_hash)

    def change_password(self, username: str, new_password: str) -> None:
        record = self._require_user(username)
        if not is_strong_password(new_password):
            raise ValueError("Password does not meet complexity requirements")
        salt, password_hash = self._hash_password(new_password)
        record.salt = salt
        record.password_hash = password_hash
        self._persist()

    def remove_user(self, username: str) -> None:
        self._users.pop(username, None)
        self._persist()

    def get_role(self, username: str) -> Optional[str]:
        record = self._users.get(username)
        return record.role if record else None

    def list_users(self) -> Dict[str, UserRecord]:
        return dict(self._users)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        if salt is None:
            salt = os.urandom(_SALT_BYTES).hex()
        salt_bytes = bytes.fromhex(salt)
        digest = pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, _HASH_ITERATIONS)
        return salt, digest.hex()

    def _verify_password(self, password: str, salt: str, expected_hash: str) -> bool:
        salt_bytes = bytes.fromhex(salt)
        digest = pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, _HASH_ITERATIONS)
        return digest.hex() == expected_hash

    def _require_user(self, username: str) -> UserRecord:
        record = self._users.get(username)
        if not record:
            raise KeyError(f"User '{username}' not found")
        return record

    def _persist(self) -> None:
        if not self.user_store_path:
            return
        data = {username: asdict(record) for username, record in self._users.items()}
        self.user_store_path.parent.mkdir(parents=True, exist_ok=True)
        with self.user_store_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def _load_users(self) -> None:
        if not self.user_store_path:
            return
        with self.user_store_path.open("r", encoding="utf-8") as handle:
            raw_users = json.load(handle)
        for username, payload in raw_users.items():
            self._users[username] = UserRecord(**payload)
