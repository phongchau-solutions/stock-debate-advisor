#!/usr/bin/env python
"""Test API endpoints."""
import sys
import os
os.chdir(os.path.dirname(__file__) + '/data-service')
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("Testing API Endpoints")
print("=" * 70)

# Test 1: Company endpoint
print("\n1. GET /api/v2/company/MBB.VN")
response = client.get("/api/v2/company/MBB.VN")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✓ Company: {data.get('name', 'N/A')}")
else:
    print(f"   ✗ Error: {response.json()}")

# Test 2: Prices endpoint
print("\n2. GET /api/v2/prices/MBB.VN?limit=3")
response = client.get("/api/v2/prices/MBB.VN?limit=3")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    count = len(data.get('prices', []))
    print(f"   ✓ Returned {count} prices")
    if count > 0:
        print(f"      Latest price: ${data['prices'][0]['close']:.2f}")
else:
    print(f"   ✗ Error: {response.json()}")

# Test 3: Metrics endpoint
print("\n3. GET /api/v2/financials/metrics/MBB.VN")
response = client.get("/api/v2/financials/metrics/MBB.VN")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✓ PE Ratio: {data.get('pe_ratio', 'N/A')}")
else:
    print(f"   ✗ Error: {response.json()}")

# Test 4: Dividends endpoint
print("\n4. GET /api/v2/dividends/MBB.VN")
response = client.get("/api/v2/dividends/MBB.VN")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    count = len(data.get('dividends', []))
    print(f"   ✓ Returned {count} dividends")
else:
    print(f"   ✗ Error: {response.json()}")

# Test 5: All data endpoint
print("\n5. GET /api/v2/data/MBB.VN")
response = client.get("/api/v2/data/MBB.VN")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✓ Symbol: {data.get('symbol', 'N/A')}")
    print(f"      Prices: {len(data.get('prices', []))}")
    print(f"      Dividends: {len(data.get('dividends', []))}")
else:
    print(f"   ✗ Error: {response.json()}")

print("\n" + "=" * 70)
print("✅ API TESTING COMPLETE")
print("=" * 70)
