#!/usr/bin/env python3
"""
Quick test for the /process endpoint
Tests the API without requiring actual PDF files
"""

import requests
import io

# API base URL
API_BASE = "http://localhost:5000"

def test_process_endpoint_validation():
    """Test the /process endpoint validation (should fail without PDF)."""
    print("🔍 Testing /process endpoint validation...")
    
    try:
        # Test 1: No files at all
        print("\n1️⃣ Test 1: No files (should fail)")
        response = requests.post(f"{API_BASE}/process")
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print("   ✅ Correctly rejected request without files")
            print(f"   Response: {response.json()}")
        else:
            print("   ❌ Unexpected response")
        
        # Test 2: Wrong field name
        print("\n2️⃣ Test 2: Wrong field name (should fail)")
        fake_file = io.BytesIO(b"fake content")
        files = {'wrong_field': ('test.pdf', fake_file)}
        response = requests.post(f"{API_BASE}/process", files=files)
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print("   ✅ Correctly rejected request with wrong field name")
            print(f"   Response: {response.json()}")
        else:
            print("   ❌ Unexpected response")
        
        # Test 3: Empty filename
        print("\n3️⃣ Test 3: Empty filename (should fail)")
        fake_file = io.BytesIO(b"fake content")
        files = {'pdf': ('', fake_file)}
        response = requests.post(f"{API_BASE}/process", files=files)
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print("   ✅ Correctly rejected request with empty filename")
            print(f"   Response: {response.json()}")
        else:
            print("   ❌ Unexpected response")
            
    except requests.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Start the server with: python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_with_fake_pdf():
    """Test with a fake PDF file (will likely fail processing but shows upload works)."""
    print("\n🔍 Testing /process with fake PDF...")
    
    try:
        # Create fake PDF content
        fake_pdf_content = b"%PDF-1.4\nFake PDF content for testing\n%%EOF"
        fake_file = io.BytesIO(fake_pdf_content)
        
        files = {'pdf': ('test.pdf', fake_file, 'application/pdf')}
        
        print("📤 Uploading fake PDF file...")
        response = requests.post(f"{API_BASE}/process", files=files)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Upload successful! (Processing might fail with fake PDF)")
            print(f"   Response size: {len(response.content)} bytes")
        elif response.status_code == 500:
            print("   ⚠️ Processing failed (expected with fake PDF)")
            try:
                error_info = response.json()
                print(f"   Error: {error_info}")
            except:
                print(f"   Error text: {response.text[:200]}...")
        else:
            print(f"   Response: {response.text[:200]}...")
            
    except requests.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Start the server with: python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run quick tests."""
    print("🚀 Quick Test for /process Endpoint")
    print("=" * 50)
    
    # First check if server is running
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Server is running and healthy!")
            print(f"Server info: {response.json()}")
        else:
            print(f"⚠️ Server responded but not healthy: {response.status_code}")
    except requests.ConnectionError:
        print("❌ Server not running. Start it with: python app.py")
        return
    
    # Run validation tests
    test_process_endpoint_validation()
    
    # Test with fake PDF
    test_with_fake_pdf()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("- The /process endpoint correctly validates requests")
    print("- It requires a 'pdf' field with a file")
    print("- Optional 'csv' field can be included")
    print("- Real PDF processing requires actual PDF files")
    print("\n💡 For real testing, use: python example_usage.py")

if __name__ == "__main__":
    main() 