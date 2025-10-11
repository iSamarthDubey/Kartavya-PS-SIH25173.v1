#!/usr/bin/env python3
"""
Debug auth manager and demo user authentication
"""

from src.security.auth_manager import AuthManager

# Initialize auth manager (same as in auth route)
auth_manager = AuthManager(user_store_path="data/users.json")

print("🔍 Debug Auth Manager")
print(f"User store path: {auth_manager.user_store_path}")
print(f"Users loaded: {len(auth_manager._users)}")

# List all users
print("\n📋 Loaded Users:")
for username, user in auth_manager.list_users().items():
    role = auth_manager.get_role(username)
    print(f"  - {username}: role={role}")

# Test password authentication
print("\n🔐 Testing Password Authentication:")
test_creds = [
    ("security_admin", "Admin!2025"),
    ("security_analyst", "Admin!2025"),
    ("security_viewer", "Admin!2025")
]

for username, password in test_creds:
    is_valid = auth_manager.authenticate(username, password)
    print(f"  {username}: {'✅ Valid' if is_valid else '❌ Invalid'}")

# Test the demo user mapping logic (from auth.py)
print("\n🗺️ Testing Demo User Mapping:")
demo_user_mapping = {
    "admin@kartavya.demo": "security_admin",
    "analyst@kartavya.demo": "security_analyst", 
    "viewer@kartavya.demo": "security_viewer",
    "security_admin": "security_admin",
    "security_analyst": "security_analyst",
    "security_viewer": "security_viewer"
}

for identifier, expected_username in demo_user_mapping.items():
    actual_username = demo_user_mapping.get(identifier)
    role = auth_manager.get_role(actual_username) if actual_username else None
    print(f"  {identifier} -> {actual_username}: role={role}")
