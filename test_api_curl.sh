#!/bin/bash

# FacilityApps API Test Script - Sites, Floors & Spaces
# Replace YOUR_TOKEN_HERE with your actual Bearer token

TOKEN="YOUR_TOKEN_HERE"
BASE_URL="https://demouk.facilityapps.com/api/v1"

echo "🚀 FacilityApps API Test - Sites, Floors & Spaces"
echo "============================================================"

echo ""
echo "🔍 Testing Sites..."
echo "URL: $BASE_URL/planning/sites"
curl -X GET "$BASE_URL/planning/sites" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -w "\nStatus Code: %{http_code}\n" \
  -s

echo ""
echo "🔍 Testing Floors..."
echo "URL: $BASE_URL/planning/floors"
curl -X GET "$BASE_URL/planning/floors" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -w "\nStatus Code: %{http_code}\n" \
  -s

echo ""
echo "🔍 Testing Spaces..."
echo "URL: $BASE_URL/planning/spaces"
curl -X GET "$BASE_URL/planning/spaces" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -w "\nStatus Code: %{http_code}\n" \
  -s

echo ""
echo "============================================================"
echo "✅ Test completed!"
echo ""
echo "📝 Instructions:"
echo "1. Replace YOUR_TOKEN_HERE with your actual Bearer token"
echo "2. Run: chmod +x test_api_curl.sh"
echo "3. Run: ./test_api_curl.sh"
