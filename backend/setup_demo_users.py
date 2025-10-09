#!/usr/bin/env python3
"""
Setup demo users for Kartavya SIEM
This script registers the demo users in the local auth manager
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.security.auth_manager import AuthManager
from src.security.rbac import RBAC

def setup_demo_users():
    """Register demo users in the auth manager"""
    
    # Initialize auth manager with a user store file
    user_store_path = Path("data/users.json")
    user_store_path.parent.mkdir(exist_ok=True)
    
    auth_manager = AuthManager(user_store_path=user_store_path)
    rbac = RBAC()
    
    # Demo users from frontend environment variables
    demo_users = [
        {
            "username": "security_admin",
            "password": "SecureAdmin2025!",
            "role": "admin"
        },
        {
            "username": "security_analyst", 
            "password": "SecureAnalyst2025!",
            "role": "analyst"
        },
        {
            "username": "security_viewer",
            "password": "SecureViewer2025!", 
            "role": "viewer"
        }
    ]
    
    print("🔐 Setting up demo users for Kartavya SIEM...")
    
    for user_data in demo_users:
        try:
            user_record = auth_manager.register_user(
                username=user_data["username"],
                password=user_data["password"], 
                role=user_data["role"]
            )
            print(f"✅ Registered user: {user_data['username']} ({user_data['role']})")
            
        except ValueError as e:
            if "User already exists" in str(e):
                print(f"⚠️ User already exists: {user_data['username']}")
            else:
                print(f"❌ Error registering {user_data['username']}: {e}")
                
    # List all users to verify
    print(f"\n📋 Registered users:")
    users = auth_manager.list_users()
    for username, record in users.items():
        print(f"  • {username} ({record.role}) - created {record.created_at}")
        
    print(f"\n💾 User data saved to: {user_store_path.absolute()}")
    print("🚀 Demo users are ready! You can now login to the frontend.")

if __name__ == "__main__":
    setup_demo_users()
