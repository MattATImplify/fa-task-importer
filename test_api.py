"""
Quick test script to debug FacilityApps API responses
Run this to see what the API is actually returning
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

FA_DOMAIN = os.getenv("FA_DOMAIN", "")
FA_TOKEN = os.getenv("FA_TOKEN", "")

if not FA_DOMAIN or not FA_TOKEN:
    print("❌ Please set FA_DOMAIN and FA_TOKEN in .env file")
    exit(1)

headers = {
    "Authorization": f"Bearer {FA_TOKEN}",
    "Accept": "application/json"
}

print(f"Testing API: {FA_DOMAIN}")
print("=" * 60)

# Test Sites
print("\n1. Testing Sites API...")
try:
    response = requests.get(
        f"https://{FA_DOMAIN}/api/v1/planning/sites",
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response type: {type(data)}")
    if isinstance(data, list) and len(data) > 0:
        print(f"Count: {len(data)}")
        print(f"First item type: {type(data[0])}")
        print(f"First item: {json.dumps(data[0], indent=2)[:300]}...")
    elif isinstance(data, dict):
        print(f"Response is dict with keys: {list(data.keys())}")
        print(f"Full response: {json.dumps(data, indent=2)[:500]}...")
    else:
        print(f"Unexpected format: {data}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test Floors
print("\n2. Testing Floors API...")
try:
    response = requests.get(
        f"https://{FA_DOMAIN}/api/v1/planning/floors",
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response type: {type(data)}")
    if isinstance(data, list) and len(data) > 0:
        print(f"Count: {len(data)}")
        print(f"First item type: {type(data[0])}")
        print(f"First item: {json.dumps(data[0], indent=2)[:300]}...")
    elif isinstance(data, dict):
        print(f"Response is dict with keys: {list(data.keys())}")
        print(f"Full response: {json.dumps(data, indent=2)[:500]}...")
    else:
        print(f"Unexpected format: {data}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test Spaces
print("\n3. Testing Spaces API...")
try:
    response = requests.get(
        f"https://{FA_DOMAIN}/api/v1/planning/spaces",
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response type: {type(data)}")
    if isinstance(data, list) and len(data) > 0:
        print(f"Count: {len(data)}")
        print(f"First item type: {type(data[0])}")
        print(f"First item: {json.dumps(data[0], indent=2)[:300]}...")
    elif isinstance(data, dict):
        print(f"Response is dict with keys: {list(data.keys())}")
        print(f"Full response: {json.dumps(data, indent=2)[:500]}...")
    else:
        print(f"Unexpected format: {data}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test Users
print("\n4. Testing Users API...")
try:
    response = requests.get(
        f"https://{FA_DOMAIN}/api/v1/user",
        headers=headers,
        params={"limit": 5, "page": 1},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response type: {type(data)}")
    if isinstance(data, dict):
        print(f"Response keys: {list(data.keys())}")
        if "data" in data:
            users = data["data"]
            print(f"Users count: {len(users)}")
            if len(users) > 0:
                print(f"First user type: {type(users[0])}")
                print(f"First user: {json.dumps(users[0], indent=2)[:300]}...")
        print(f"Full response (truncated): {json.dumps(data, indent=2)[:500]}...")
    else:
        print(f"Unexpected format: {type(data)}")
        print(f"Data: {str(data)[:500]}...")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Test complete!")

