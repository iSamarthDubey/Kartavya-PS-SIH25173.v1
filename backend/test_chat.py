#!/usr/bin/env python3
"""
Test chat endpoint
"""

import requests
import json

def test_chat():
    # Login first
    print('🔐 Logging in...')
    login_response = requests.post('http://localhost:8000/api/auth/login', json={
        'identifier': 'admin@kartavya.demo', 
        'password': 'Admin!2025'
    })
    
    if login_response.status_code != 200:
        print(f'❌ Login failed: {login_response.json()}')
        return
        
    token = login_response.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    print('✅ Login successful')
    print()

    # Test chat endpoint
    print('💬 Testing Chat Endpoint:')
    chat_request = {
        "query": "Show me recent security alerts",
        "conversation_id": "test-conversation-123",
        "user_context": {}
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/assistant/chat', 
            json=chat_request,
            headers=headers,
            timeout=30
        )
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'Status: {data.get("status")}')
            print(f'Intent: {data.get("intent")}')
            print(f'Summary: {data.get("summary", "")[:200]}...')
            print(f'Results count: {len(data.get("results", []))}')
            if data.get("error"):
                print(f'Error: {data.get("error")}')
        else:
            print(f'Error: {response.json()}')
    except requests.exceptions.Timeout:
        print('⏰ Request timed out - chat service may be slow due to AI processing')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    test_chat()
