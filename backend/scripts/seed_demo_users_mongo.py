#!/usr/bin/env python3
"""
Seed demo users into MongoDB user_profiles so login works with MongoDB enabled.
Reads MONGODB_URI and MONGODB_DATABASE from environment (.env).
This does NOT store passwords in MongoDB. Password verification still uses data/users.json
created by create_demo_users.py (PBKDF2 via AuthManager).

Usage:
  python seed_demo_users_mongo.py
"""
import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except Exception as e:
    print("❌ pymongo is not installed. Install it with: pip install pymongo")
    sys.exit(1)

DEMO_USERS = [
    {
        "username": "security_admin",
        "email": "admin@kartavya.demo",
        "full_name": "Security Administrator",
        "role": "admin",
        "department": "IT Security",
        "location": "Mumbai, India",
        "security_clearance": "Level 5",
    },
    {
        "username": "security_analyst",
        "email": "analyst@kartavya.demo",
        "full_name": "Security Analyst",
        "role": "analyst",
        "department": "SOC Team",
        "location": "Delhi, India",
        "security_clearance": "Level 3",
    },
    {
        "username": "security_viewer",
        "email": "viewer@kartavya.demo",
        "full_name": "Security Viewer",
        "role": "viewer",
        "department": "Management",
        "location": "Bangalore, India",
        "security_clearance": "Level 2",
    },
]

def main() -> int:
    load_dotenv()
    mongo_uri = os.getenv("MONGODB_URI")
    mongo_db = os.getenv("MONGODB_DATABASE", "kartavya_siem")

    if not mongo_uri:
        print("❌ MONGODB_URI is not set. Set it in .env or environment and retry.")
        return 2

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # test connection
        db = client[mongo_db]
        col = db["user_profiles"]

        # Optional: indexes
        try:
            col.create_index("email", unique=True)
            col.create_index("username", unique=True)
        except Exception:
            pass

        seeded = 0
        for user in DEMO_USERS:
            doc = {
                "_id": user["username"],  # make username the ID for quick lookup
                **user,
                "preferences": {},
                "account_locked": False,
                "created_at": datetime.now(timezone.utc),
                "last_login": None,
                "login_count": 0,
            }
            # upsert by username
            res = col.update_one({"_id": user["username"]}, {"$setOnInsert": doc}, upsert=True)
            if res.upserted_id is not None:
                seeded += 1
                print(f"✅ Inserted: {user['username']}")
            else:
                print(f"ℹ️  Exists:   {user['username']}")

        print(f"\n✅ Seeding complete. Inserted {seeded} new user(s).")
        print("Note: Passwords are still validated against data/users.json (AuthManager).\n"
              "If needed, regenerate demo users: python create_demo_users.py (password: Admin!2025)")
        return 0

    except PyMongoError as e:
        print(f"❌ MongoDB error: {e}")
        return 3
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

