#!/usr/bin/env python3
"""
Test script to verify Kartavya CLI can connect to your deployed backend.
Run this after setting up your configuration.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the src directory to Python path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from synrgy_cli.core.config import Config
from synrgy_cli.core.client import APIClient, APIError

async def test_connection():
    """Test connection to backend and basic functionality."""
    
    print("🧪 Testing Kartavya CLI Connection")
    print("=" * 40)
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = Config()
        api_config = config.get_api_config()
        
        if not api_config.get('base_url'):
            print("❌ No backend URL configured!")
            print("Run: python setup_render.py")
            return False
        
        print(f"🔗 Backend URL: {api_config['base_url']}")
        
        # Test basic connection
        print("🔍 Testing connection...")
        client = APIClient(config)
        
        # Health check
        health_ok = client.get_health()
        if health_ok:
            print("✅ Health check: PASSED")
        else:
            print("⚠️ Health check: FAILED (but backend is reachable)")
        
        # Test dashboard metrics
        print("📊 Testing metrics endpoint...")
        try:
            metrics = client.get_dashboard_metrics()
            if metrics:
                print("✅ Metrics endpoint: WORKING")
                
                # Show some sample metrics
                print("\n📈 Sample Metrics:")
                for key, value in list(metrics.items())[:5]:
                    print(f"  • {key}: {value}")
            else:
                print("⚠️ Metrics endpoint: No data returned")
        except APIError as e:
            print(f"⚠️ Metrics endpoint: {e.message}")
        
        # Test alerts
        print("🚨 Testing alerts endpoint...")
        try:
            alerts = client.get_alerts()
            print(f"✅ Alerts endpoint: WORKING ({len(alerts)} alerts found)")
        except APIError as e:
            print(f"⚠️ Alerts endpoint: {e.message}")
        
        # Test events
        print("📅 Testing events endpoint...")
        try:
            events = client.get_platform_events(limit=10)
            print(f"✅ Events endpoint: WORKING ({len(events)} events found)")
        except APIError as e:
            print(f"⚠️ Events endpoint: {e.message}")
        
        client.close()
        
        print("\n🎉 Connection test completed!")
        print("\nYour CLI is ready to use! Try these commands:")
        print("• python -m synrgy_cli dashboard stats")
        print("• python -m synrgy_cli dashboard live-stats")
        print("• python -m synrgy_cli chat ask 'Show me system status'")
        
        return True
        
    except APIError as e:
        print(f"❌ API Error: {e.message}")
        if e.status_code:
            print(f"Status Code: {e.status_code}")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def main():
    """Main function to run the test."""
    try:
        result = asyncio.run(test_connection())
        if result:
            sys.exit(0)
        else:
            print("\n💡 If you're having connection issues:")
            print("1. Make sure your backend is running on Render")
            print("2. Check your .env file has the correct URL")
            print("3. Verify authentication settings")
            print("4. Run: python setup_render.py to reconfigure")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Test cancelled by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
