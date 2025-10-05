"""Role-based access control utilities for the SIEM assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Set

DEFAULT_ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "admin": {
        "users:create",
        "users:delete",
        "users:list",
        "queries:run",
        "reports:generate",
        "settings:update",
        "audit:view",
    },
    "analyst": {
        "queries:run",
        "reports:generate",
        "cases:update",
        "audit:view",
    },
    "viewer": {
        "queries:run",
        "reports:view",
    },
}

ROLE_HIERARCHY = {
    "admin": {"analyst", "viewer"},
    "analyst": {"viewer"},
    "viewer": set(),
}


@dataclass
class RBAC:
    """Simple RBAC manager with hierarchical role inheritance."""

    role_permissions: Dict[str, Set[str]] = field(
        default_factory=lambda: {role: perms.copy() for role, perms in DEFAULT_ROLE_PERMISSIONS.items()}
    )
    role_hierarchy: Dict[str, Set[str]] = field(
        default_factory=lambda: {role: children.copy() for role, children in ROLE_HIERARCHY.items()}
    )

    def validate_role(self, role: str) -> bool:
        return role in self.role_permissions

    def assert_valid_role(self, role: str) -> None:
        if not self.validate_role(role):
            raise ValueError(f"Unknown role: {role}")

    def get_permissions(self, role: str, include_inherited: bool = True) -> Set[str]:
        self.assert_valid_role(role)
        permissions = set(self.role_permissions[role])
        if include_inherited:
            for inherited_role in self.role_hierarchy.get(role, set()):
                permissions |= self.get_permissions(inherited_role, include_inherited=True)
        return permissions

    def has_permission(self, role: str, permission: str) -> bool:
        return permission in self.get_permissions(role, include_inherited=True)

    def require_permission(self, role: str, permission: str) -> None:
        if not self.has_permission(role, permission):
            raise PermissionError(f"Role '{role}' lacks permission '{permission}'")

    def add_role(self, role: str, permissions: Optional[Iterable[str]] = None, inherits: Optional[Iterable[str]] = None) -> None:
        if role in self.role_permissions:
            raise ValueError(f"Role '{role}' already exists")
        self.role_permissions[role] = set(permissions or [])
        self.role_hierarchy[role] = set(inherits or [])

    def grant_permission(self, role: str, permission: str) -> None:
        self.assert_valid_role(role)
        self.role_permissions[role].add(permission)

    def revoke_permission(self, role: str, permission: str) -> None:
        self.assert_valid_role(role)
        self.role_permissions[role].discard(permission)
