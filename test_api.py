#!/usr/bin/env python3
"""
Test script for BOL Processing API - Approach 1
"""

import requests
import os
import tempfile
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:5000"
TEST_PDF_PATH = "../test_file.pdf"  # Adjust path as needed

def test_health_endpoint():
    """Test the health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    print("Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Root endpoint failed: {e}")
        return False

def create_test_pdf():
    """Create a simple test PDF for testing."""
    # Create a minimal PDF content (this is a very basic PDF)
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test BOL Document) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000203 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
295
%%EOF"""
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as tmp:
        tmp.write(pdf_content)
        return tmp.name

def test_process_endpoint():
    """Test the process endpoint with a PDF file."""
    print("Testing process endpoint...")
    
    # Create or use test PDF
    if os.path.exists(TEST_PDF_PATH):
        pdf_path = TEST_PDF_PATH
        cleanup_pdf = False
    else:
        pdf_path = create_test_pdf()
        cleanup_pdf = True
    
    try:
        # Test with PDF file
        with open(pdf_path, 'rb') as pdf_file:
            files = {
                'pdf': ('test.pdf', pdf_file, 'application/pdf')
            }
            
            print(f"Sending PDF file: {pdf_path}")
            response = requests.post(f"{API_BASE_URL}/process", files=files)
            
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            
            if response.status_code == 200:
                print("✓ Process endpoint successful!")
                print(f"Response size: {len(response.content)} bytes")
                return True
            else:
                print(f"✗ Process endpoint failed!")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"Process endpoint test failed: {e}")
        return False
    finally:
        # Clean up test PDF if we created it
        if cleanup_pdf and os.path.exists(pdf_path):
            os.unlink(pdf_path)

def test_docs_endpoint():
    """Test the docs endpoint."""
    print("Testing docs endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/docs")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Docs endpoint failed: {e}")
        return False

def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("BOL Processing API - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("API Docs", test_docs_endpoint),
        ("Process Endpoint", test_process_endpoint),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
        print(f"Result: {'PASS' if result else 'FAIL'}")
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 