#!/usr/bin/env python3
"""
Test login with demo credentials
"""

import requests
import json

# Test credentials from create_demo_users.py
test_users = [
    {'identifier': 'admin@kartavya.demo', 'password': 'Admin!2025', 'name': 'Admin by Email'},
    {'identifier': 'security_admin', 'password': 'Admin!2025', 'name': 'Admin by Username'},
    {'identifier': 'analyst@kartavya.demo', 'password': 'Admin!2025', 'name': 'Analyst by Email'},
    {'identifier': 'security_analyst', 'password': 'Admin!2025', 'name': 'Analyst by Username'}
]

def test_login():
    for user in test_users:
        try:
            response = requests.post('http://localhost:8000/api/auth/login', json=user)
            print(f'{user["name"]}: Status {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                print(f'  ✅ Success! Token: {data.get("token", "")[:20]}...')
                print(f'  User: {data.get("user", {}).get("username", "N/A")} ({data.get("user", {}).get("role", "N/A")})')
            else:
                print(f'  ❌ Failed: {response.json().get("detail", "Unknown error")}')
        except Exception as e:
            print(f'{user["name"]}: Error - {e}')
        print()

if __name__ == "__main__":
    test_login()
