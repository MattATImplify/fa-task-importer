#!/usr/bin/env python3
"""
Test script for FacilityApps Sites, Floors, and Spaces API endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://demouk.facilityapps.com/api/v1"
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIyIiwianRpIjoiN2MxMjc0NzRlNjg4MjAzYjlhOGEyY2E5YTMzNjJjYmIzODU4NGEwODBiNzQ1MzUyMWE3ZDJkNzM3YTc2NzM2NjMxN2E4OTE2ZTg0Nzc2NTIiLCJpYXQiOjE3NTg4OTM0NjYuOTIxNjg0LCJuYmYiOjE3NTg4OTM0NjYuOTIxNjg3LCJleHAiOjE3OTA0Mjk0NjYuOTEyMjU1LCJzdWIiOiIxNSIsInNjb3BlcyI6W119.RSSZg1E8lteBVu7SJPrZUpQWdlDFeuIk3QNQwH_VSJ_3kBtmdyOxy8qEbHw6_kA_W6Ml7u0uWcKu9Dc0_Hp2eGUcaLAR0UQP2x1EpIwO0TZxvQ0Kh0qbkeYe-1P6nEzvq03mVLmcJps6-GWAC0ocax1au9k4FFCn1ym8-B7S7I6Ps0GFh0pwPib4Ai24WvLLFgyVIHEv4Xb4EVibrPtSV-gQjMMWHSaju1yi76JvUyuR0uVaN9J-XvqOK2Ttiv_-aDNapIlvTJbdUqTuKGgNdR3rBhvBbBxLwErQDp0bM5HNviBlzoAnbIE-9QHgGPG_yD40X9Aq7VnWn6IcbIyxINCosIFs56djUMu6t5BRnyhoUu5uhLe82bwngT3GQOJa3n2Z5THIoxulpHW7IahBJc6Qo6ZR6NPnXJ1JXl8vVhEpVt_vlwWM9X50GdKccAuSS2GMbWwjYut-nGIl64-ZjWmEAjab_g-ZSQ3mBOa8VXCZ8Gdh44-kV9isbERFOjgdeUIvKBziZyXcuOC4wp4p_UazybMkhSBCQR93OWuEvPLa4CEDXoG2S__b_GBsMAa9IsGw2W0mmwegSgKbzMIt3zstmhROEG2z_mRNKry70aG6CanmMZXFGan1WfIseAL7ml5cW5I8GLqxz3FiH3vLADAcCAxRYxVdlLhTV7qrSkk"

def make_request(endpoint, name):
    """Make a request to the API endpoint"""
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print(f"\n🔍 Testing {name}...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} {name.lower()}")
            
            if data:
                print(f"Sample {name[:-1]}: {json.dumps(data[0], indent=2)}")
                
                # Check for relationship fields
                if name == "Sites":
                    print("Site fields:", list(data[0].keys()))
                elif name == "Floors":
                    print("Floor fields:", list(data[0].keys()))
                    # Check for site reference field
                    site_ref_fields = [k for k in data[0].keys() if 'site' in k.lower()]
                    print(f"Site reference fields: {site_ref_fields}")
                elif name == "Spaces":
                    print("Space fields:", list(data[0].keys()))
                    # Check for floor reference field
                    floor_ref_fields = [k for k in data[0].keys() if 'floor' in k.lower()]
                    print(f"Floor reference fields: {floor_ref_fields}")
            
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def analyze_relationships(sites, floors, spaces):
    """Analyze the relationships between sites, floors, and spaces"""
    print("\n🔗 Relationship Analysis:")
    
    if not sites or not floors:
        print("❌ Cannot analyze relationships - missing data")
        return
    
    # Analyze site-floor relationships
    print("\n**Site-Floor Relationships:**")
    for site in sites[:3]:  # Show first 3 sites
        site_id = site.get('id')
        site_name = site.get('name', 'Unknown')
        
        # Check all possible site reference fields in floors
        matching_floors = []
        for floor in floors:
            site_ref = floor.get('site_Id') or floor.get('site_id') or floor.get('site') or floor.get('siteId')
            if str(site_ref) == str(site_id):
                matching_floors.append(floor.get('name', 'Unknown'))
        
        print(f"  - Site '{site_name}' (ID: {site_id}) → {len(matching_floors)} floors: {matching_floors}")
    
    # Analyze floor-space relationships
    if spaces:
        print("\n**Floor-Space Relationships:**")
        for floor in floors[:3]:  # Show first 3 floors
            floor_id = floor.get('id')
            floor_name = floor.get('name', 'Unknown')
            
            # Check all possible floor reference fields in spaces
            matching_spaces = []
            for space in spaces:
                floor_ref = space.get('floor_Id') or space.get('floor_id') or space.get('floor') or space.get('floorId')
                if str(floor_ref) == str(floor_id):
                    matching_spaces.append(space.get('name', 'Unknown'))
            
            print(f"  - Floor '{floor_name}' (ID: {floor_id}) → {len(matching_spaces)} spaces: {matching_spaces}")

def main():
    """Main test function"""
    print("🚀 FacilityApps API Test - Sites, Floors & Spaces")
    print("=" * 60)
    
    # Test each endpoint
    sites = make_request("planning/sites", "Sites")
    floors = make_request("planning/floors", "Floors")
    spaces = make_request("planning/spaces", "Spaces")
    
    # Analyze relationships
    if sites and floors:
        analyze_relationships(sites, floors, spaces)
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"  - Sites: {len(sites) if sites else 0}")
    print(f"  - Floors: {len(floors) if floors else 0}")
    print(f"  - Spaces: {len(spaces) if spaces else 0}")

if __name__ == "__main__":
    main()
