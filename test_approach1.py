#!/usr/bin/env python3
"""
Test script for Approach 1 (Minimal Refactoring) API
This script demonstrates how to use the simple API endpoints.
"""

import requests
import time
import json

# API base URL
API_BASE = "http://localhost:5000"

def test_root_endpoint():
    """Test the root endpoint."""
    print("🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"📋 Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_health_check():
    """Test the health check endpoint."""
    print("\n🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"📋 Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_process_endpoint():
    """Test the main process endpoint."""
    print("\n🔍 Testing process endpoint...")
    try:
        # Test with sample data (this would normally be a PDF file)
        test_data = {
            "message": "Test processing request",
            "format": "json"
        }
        
        response = requests.post(f"{API_BASE}/process", json=test_data)
        print(f"✅ Process endpoint: {response.status_code}")
        print(f"📋 Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Process endpoint failed: {e}")
        return False

def test_api_docs():
    """Test the API documentation endpoint."""
    print("\n🔍 Testing API documentation...")
    try:
        response = requests.get(f"{API_BASE}/api/docs")
        print(f"✅ API docs: {response.status_code}")
        docs = response.json()
        print(f"📚 API Name: {docs.get('name', 'Unknown')}")
        print(f"📚 Version: {docs.get('version', 'Unknown')}")
        print(f"📚 Available endpoints: {len(docs.get('endpoints', {}))}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API docs failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Approach 1 (Minimal Refactoring) API")
    print("=" * 50)
    
    # Wait for server to start
    print("⏳ Waiting for API server to start...")
    time.sleep(3)
    
    # Run tests
    tests = [
        ("Root Endpoint", test_root_endpoint),
        ("Health Check", test_health_check),
        ("Process Endpoint", test_process_endpoint),
        ("API Documentation", test_api_docs),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running test: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Approach 1 API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the API server and try again.")

if __name__ == "__main__":
    main() 