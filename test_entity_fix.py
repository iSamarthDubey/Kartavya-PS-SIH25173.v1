"""
Quick test script to verify the entity serialization fix
"""

import requests
import json

API_URL = "http://localhost:8001/assistant/ask"

# Test query
payload = {
    "query": "Show failed login attempts from the last hour",
    "conversation_id": "test_conv_001"
}

print("🧪 Testing API with entity extraction...")
print(f"Query: {payload['query']}\n")

try:
    response = requests.post(API_URL, json=payload, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! No validation errors\n")
        
        data = response.json()
        
        # Show key fields
        print(f"Intent: {data.get('intent')}")
        print(f"Entities: {len(data.get('entities', []))} extracted")
        print(f"Results: {len(data.get('results', []))} records")
        print(f"Summary: {data.get('summary')}")
        print(f"\nEntities Details:")
        
        for entity in data.get('entities', []):
            print(f"  - Type: {entity.get('type')}, Value: {entity.get('value')}, Confidence: {entity.get('confidence')}")
        
        print(f"\nMetadata:")
        metadata = data.get('metadata', {})
        print(f"  Processing Time: {metadata.get('processing_time_seconds')}s")
        print(f"  Confidence: {metadata.get('confidence_score')}")
        
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Exception: {e}")
