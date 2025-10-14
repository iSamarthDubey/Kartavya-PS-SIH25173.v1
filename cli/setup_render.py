#!/usr/bin/env python3
"""
Quick setup script for Kartavya CLI to connect to Render-deployed backend.

This script helps you quickly configure your CLI to work with your 
already deployed backend on Render.
"""

import os
import sys
from pathlib import Path

def main():
    print("🚀 Kartavya CLI - Render Backend Setup")
    print("=" * 50)
    print()
    
    print("This script will help you configure your CLI to connect to your")
    print("already deployed Kartavya backend on Render.")
    print()
    
    # Get backend URL
    backend_url = input("Enter your Render backend URL (e.g., https://your-app.onrender.com): ").strip()
    
    if not backend_url:
        print("❌ Backend URL is required!")
        sys.exit(1)
    
    # Clean up URL
    backend_url = backend_url.rstrip('/')
    if not backend_url.startswith(('http://', 'https://')):
        backend_url = f"https://{backend_url}"
    
    print(f"✅ Backend URL: {backend_url}")
    
    # Get authentication method
    print()
    print("Choose authentication method:")
    print("1. API Key (recommended)")
    print("2. Username/Password")
    print("3. No authentication (for testing)")
    
    auth_choice = input("Enter choice (1-3): ").strip()
    
    api_key = None
    username = None
    password = None
    
    if auth_choice == "1":
        api_key = input("Enter your API key: ").strip()
        if not api_key:
            print("❌ API key cannot be empty!")
            sys.exit(1)
        print("✅ API key configured")
    
    elif auth_choice == "2":
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        if not username or not password:
            print("❌ Both username and password are required!")
            sys.exit(1)
        print("✅ Username/password configured")
    
    elif auth_choice == "3":
        print("⚠️ No authentication configured")
    
    else:
        print("❌ Invalid choice!")
        sys.exit(1)
    
    # Create environment variables file
    env_content = f"""# Kartavya CLI Configuration
SYNRGY_API_BASE_URL={backend_url}
"""
    
    if api_key:
        env_content += f"SYNRGY_AUTH_API_KEY={api_key}\n"
    
    if username:
        env_content += f"SYNRGY_AUTH_USERNAME={username}\n"
    
    if password:
        env_content += f"SYNRGY_AUTH_PASSWORD={password}\n"
    
    # Write .env file
    env_file = Path(".env")
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print()
    print("✅ Configuration saved to .env file!")
    
    # Instructions
    print()
    print("🎉 Setup Complete!")
    print("=" * 20)
    print()
    print("Your CLI is now configured to work with your Render backend.")
    print()
    print("Next steps:")
    print("1. Install the CLI: pip install -e .")
    print("2. Test connection: python -m synrgy_cli config test")
    print("3. Get stats: python -m synrgy_cli dashboard stats")
    print("4. Start chatting: python -m synrgy_cli chat ask 'Show me system status'")
    print()
    print("For live dashboard: python -m synrgy_cli dashboard live-stats")
    print("For help: python -m synrgy_cli --help")
    print()
    print("Your backend URL:", backend_url)

if __name__ == "__main__":
    main()
