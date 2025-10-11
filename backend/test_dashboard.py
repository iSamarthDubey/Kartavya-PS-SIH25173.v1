#!/usr/bin/env python3
"""
Test dashboard endpoints
"""

import requests
import json

def test_dashboard():
    # Login first
    login_response = requests.post('http://localhost:8000/api/auth/login', json={
        'identifier': 'admin@kartavya.demo', 
        'password': 'Admin!2025'
    })
    token = login_response.json()['token']
    headers = {'Authorization': f'Bearer {token}'}

    print('📊 Testing Dashboard Endpoints:')
    print()

    # Test dashboard metrics
    print('1️⃣ Dashboard Metrics:')
    response = requests.get('http://localhost:8000/api/dashboard/metrics', headers=headers)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Success: {data.get("success")}')
        print(f'Source: {data.get("source")}')
    else:
        print(f'Error: {response.json()}')
    print()

    # Test security alerts
    print('2️⃣ Security Alerts:')
    response = requests.get('http://localhost:8000/api/dashboard/alerts?limit=5', headers=headers)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Success: {data.get("success")}')
        print(f'Total alerts: {data.get("total")}')
        print(f'Source: {data.get("source")}')
    else:
        print(f'Error: {response.json()}')
    print()

    # Test system status
    print('3️⃣ System Status:')
    response = requests.get('http://localhost:8000/api/dashboard/system/status', headers=headers)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Success: {data.get("success")}')
        print(f'Source: {data.get("source")}')
    else:
        print(f'Error: {response.json()}')

if __name__ == "__main__":
    test_dashboard()
