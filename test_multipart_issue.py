#!/usr/bin/env python3
"""
Test script specifically for multipart form data parsing issue
"""

import requests
import tempfile
import os

# Test configuration
API_BASE_URL = "http://localhost:5000"

def create_simple_pdf():
    """Create a minimal PDF for testing."""
    pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000053 00000 n 
0000000100 00000 n 
trailer<</Size 4/Root 1 0 R>>
startxref
166
%%EOF"""
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as tmp:
        tmp.write(pdf_content)
        return tmp.name

def test_debug_endpoint():
    """Test the debug endpoint to diagnose multipart parsing."""
    print("=" * 60)
    print("TESTING DEBUG ENDPOINT")
    print("=" * 60)
    
    pdf_path = create_simple_pdf()
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            files = {'pdf': ('test.pdf', pdf_file, 'application/pdf')}
            
            print(f"Sending request to: {API_BASE_URL}/debug/multipart")
            print(f"PDF file size: {os.path.getsize(pdf_path)} bytes")
            
            response = requests.post(f"{API_BASE_URL}/debug/multipart", files=files)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response:")
            print("-" * 40)
            
            if response.status_code == 200:
                import json
                debug_info = response.json()
                
                # Pretty print the debug info
                for key, value in debug_info.items():
                    print(f"{key}: {value}")
                
                # Analyze the results
                print("\n" + "=" * 40)
                print("ANALYSIS:")
                print("=" * 40)
                
                if debug_info.get('files_received'):
                    print("✅ FILES RECEIVED: Flask is parsing files correctly!")
                    print(f"   Files: {debug_info['files_received']}")
                else:
                    print("❌ NO FILES RECEIVED: Flask is not parsing files")
                    
                if debug_info.get('has_raw_data'):
                    print(f"✅ RAW DATA PRESENT: {debug_info['raw_data_length']} bytes")
                else:
                    print("❌ NO RAW DATA: Request body is empty")
                
                if debug_info.get('parsing_issue'):
                    print("⚠️  PARSING ISSUE DETECTED")
                    print("   Suggestions:")
                    for suggestion in debug_info.get('suggestions', []):
                        print(f"   - {suggestion}")
                
                return debug_info.get('files_received', []) != []
            else:
                print(f"Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"Test failed: {e}")
        return False
    finally:
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)

def test_different_methods():
    """Test different ways to send multipart data."""
    print("\n" + "=" * 60)
    print("TESTING DIFFERENT METHODS")
    print("=" * 60)
    
    pdf_path = create_simple_pdf()
    
    methods = [
        ("Method 1: Standard files parameter", lambda f: requests.post(
            f"{API_BASE_URL}/debug/multipart", 
            files={'pdf': f}
        )),
        ("Method 2: With explicit filename", lambda f: requests.post(
            f"{API_BASE_URL}/debug/multipart", 
            files={'pdf': ('test.pdf', f, 'application/pdf')}
        )),
        ("Method 3: With different content-type", lambda f: requests.post(
            f"{API_BASE_URL}/debug/multipart", 
            files={'pdf': ('test.pdf', f, 'application/octet-stream')}
        ))
    ]
    
    results = []
    
    for method_name, method_func in methods:
        print(f"\n{method_name}:")
        print("-" * 40)
        
        try:
            with open(pdf_path, 'rb') as pdf_file:
                response = method_func(pdf_file)
                
                if response.status_code == 200:
                    debug_info = response.json()
                    files_received = debug_info.get('files_received', [])
                    
                    if files_received:
                        print(f"✅ SUCCESS: {files_received}")
                        results.append((method_name, True))
                    else:
                        print("❌ FAILED: No files received")
                        results.append((method_name, False))
                else:
                    print(f"❌ ERROR: {response.status_code}")
                    results.append((method_name, False))
                    
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results.append((method_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("SUMMARY:")
    print("=" * 40)
    
    for method_name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {method_name}")
    
    # Clean up
    if os.path.exists(pdf_path):
        os.unlink(pdf_path)
    
    return any(success for _, success in results)

def main():
    """Main test function."""
    print("MULTIPART FORM DATA DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Test 1: Debug endpoint
    debug_success = test_debug_endpoint()
    
    # Test 2: Different methods
    methods_success = test_different_methods()
    
    # Final analysis
    print("\n" + "=" * 60)
    print("FINAL DIAGNOSIS:")
    print("=" * 60)
    
    if debug_success or methods_success:
        print("✅ GOOD NEWS: At least one method works!")
        print("   The issue is likely with Thunder Client configuration.")
        print("   Try recreating your request or using curl/Postman.")
    else:
        print("❌ ISSUE CONFIRMED: Flask is not parsing multipart data.")
        print("   This could be a server configuration issue.")
        print("   Check Flask version, dependencies, and server setup.")
    
    print("\n📋 NEXT STEPS:")
    if debug_success or methods_success:
        print("1. Try the debug endpoint in Thunder Client")
        print("2. Recreate your Thunder Client request from scratch")
        print("3. Ensure Body type is 'form-data' not 'raw'")
        print("4. Verify file is actually selected")
    else:
        print("1. Check server logs for detailed error messages")
        print("2. Verify Flask and dependencies are installed correctly")
        print("3. Try restarting the server")
        print("4. Check if firewall or antivirus is interfering")

if __name__ == "__main__":
    main() 