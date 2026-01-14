#!/usr/bin/env python3
"""
Test script for Stock Debate Advisor AI Service
Verifies FastAPI endpoints and Docker integration
"""

import sys
import time
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
TIMEOUT = 10

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
    
    def test_health(self) -> bool:
        """Test health endpoint"""
        print("\n📋 Testing Health Endpoint")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=TIMEOUT)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("   ✅ Health check passed")
                return True
            else:
                print("   ❌ Health check failed")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_root(self) -> bool:
        """Test root endpoint"""
        print("\n📋 Testing Root Endpoint")
        try:
            response = self.session.get(f"{self.base_url}/", timeout=TIMEOUT)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("   ✅ Root endpoint works")
                return True
            else:
                print("   ❌ Root endpoint failed")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_docs(self) -> bool:
        """Test OpenAPI docs"""
        print("\n📋 Testing OpenAPI Documentation")
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=TIMEOUT)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ OpenAPI docs available at /docs")
                return True
            else:
                print("   ❌ OpenAPI docs failed")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_symbols(self) -> bool:
        """Test symbols endpoint"""
        print("\n📋 Testing Symbols Endpoint")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/symbols", timeout=TIMEOUT)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Available symbols: {data.get('count', 0)}")
                if data.get('symbols'):
                    print(f"   Sample: {data['symbols'][:5]}")
                print("   ✅ Symbols endpoint works")
                return True
            else:
                print(f"   ❌ Symbols endpoint failed: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_start_debate(self, symbol: str = "MBB.VN", rounds: int = 20) -> bool:
        """Test debate start endpoint"""
        print(f"\n📋 Testing Debate Start Endpoint")
        print(f"   Symbol: {symbol}, Rounds: {rounds}")
        
        try:
            payload = {
                "symbol": symbol,
                "rounds": rounds
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/debate/start",
                json=payload,
                timeout=TIMEOUT
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   Session ID: {data.get('session_id', 'N/A')}")
                print(f"   Status: {data.get('status', 'N/A')}")
                print("   ✅ Debate start works")
                return True
            else:
                print(f"   ❌ Debate start failed: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests"""
        print("=" * 60)
        print("🧪 Stock Debate Advisor API - Test Suite")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health),
            ("Root Endpoint", self.test_root),
            ("OpenAPI Docs", self.test_docs),
            ("Symbols Endpoint", self.test_symbols),
            ("Debate Start", self.test_start_debate),
        ]
        
        results = {}
        for name, test_func in tests:
            try:
                results[name] = test_func()
            except Exception as e:
                print(f"\n❌ Test {name} failed with exception: {e}")
                results[name] = False
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for name, result in results.items():
            status = "✅" if result else "❌"
            print(f"{status} {name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed! API is ready for use.")
            return True
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
            return False


def main():
    """Main test runner"""
    print("\n🚀 Starting API Tests...")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Timeout: {TIMEOUT}s")
    
    # Check if service is reachable
    print("\n⏳ Waiting for service to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            print(f"   ✅ Service is ready!")
            break
        except requests.exceptions.ConnectionError:
            if i < max_retries - 1:
                print(f"   ⏳ Attempt {i+1}/{max_retries}... service not ready yet")
                time.sleep(1)
            else:
                print(f"   ❌ Service not responding after {max_retries} attempts")
                print(f"   Make sure the service is running at {BASE_URL}")
                sys.exit(1)
    
    # Run tests
    tester = APITester(BASE_URL)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
