#!/usr/bin/env python3
"""
Test AuthManager directly
"""

from src.security.auth_manager import AuthManager

def main():
    # Create AuthManager with the users.json file
    auth_manager = AuthManager(user_store_path="data/users.json")
    
    # Test authentication
    username = "security_admin"
    password = "Admin!2025"
    
    print(f"Testing authentication for {username} with password: {password}")
    
    # Check if user exists
    role = auth_manager.get_role(username)
    print(f"User {username} role: {role}")
    
    # List all users
    users = auth_manager.list_users()
    print(f"\nAvailable users: {list(users.keys())}")
    
    # Test authentication
    is_authenticated = auth_manager.authenticate(username, password)
    print(f"Authentication result: {is_authenticated}")
    
    # Test with wrong password
    is_authenticated_wrong = auth_manager.authenticate(username, "WrongPassword")
    print(f"Authentication with wrong password: {is_authenticated_wrong}")
    
    # Check user details
    if username in users:
        user = users[username]
        print(f"\nUser details:")
        print(f"  Username: {user.username}")
        print(f"  Role: {user.role}")
        print(f"  Salt: {user.salt}")
        print(f"  Hash: {user.password_hash}")
        print(f"  Type: {type(user)}")
        print(f"  Dict: {user.__dict__}")

if __name__ == "__main__":
    main()
