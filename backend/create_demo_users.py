#!/usr/bin/env python3
"""
Create demo users for Kartavya SIEM Assistant
"""

import json
import hashlib
import os
from datetime import datetime

# Configuration
HASH_ITERATIONS = 120_000
SALT_BYTES = 16

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash password using the same method as AuthManager"""
    if salt is None:
        salt = os.urandom(SALT_BYTES).hex()
    salt_bytes = bytes.fromhex(salt)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, HASH_ITERATIONS)
    return salt, digest.hex()

def create_user(username: str, password: str, role: str) -> dict:
    """Create a user record"""
    salt, password_hash = hash_password(password)
    return {
        "username": username,
        "password_hash": password_hash,
        "salt": salt,
        "role": role,
        "created_at": datetime.utcnow().isoformat() + "+00:00"
    }

def main():
    # Demo users with the correct password
    password = "Admin!2025"
    
    users = {
        "security_admin": create_user("security_admin", password, "admin"),
        "security_analyst": create_user("security_analyst", password, "analyst"),
        "security_viewer": create_user("security_viewer", password, "viewer")
    }
    
    # Write to users.json
    output_file = "data/users.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(users, f, indent=2)
    
    print(f"✅ Created demo users in {output_file}")
    print(f"Password for all users: {password}")
    print("\nDemo users:")
    for username, user_data in users.items():
        print(f"  - {username} (role: {user_data['role']})")
    
    # Test verification
    print("\n🔍 Testing password verification...")
    for username, user_data in users.items():
        salt_bytes = bytes.fromhex(user_data['salt'])
        digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_bytes, HASH_ITERATIONS)
        computed_hash = digest.hex()
        is_valid = computed_hash == user_data['password_hash']
        print(f"  {username}: {'✅' if is_valid else '❌'}")

if __name__ == "__main__":
    main()
