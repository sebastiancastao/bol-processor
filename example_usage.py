#!/usr/bin/env python3
"""
Example usage of the /process endpoint
Shows how to upload PDF and CSV files to the API
"""

import requests
import os

# API base URL
API_BASE = "http://localhost:5000"

def example_1_pdf_only():
    """Example 1: Process PDF file only."""
    print("📄 Example 1: Processing PDF only")
    
    # You'll need to have a PDF file to test
    pdf_file_path = "sample.pdf"  # Replace with your PDF file path
    
    if not os.path.exists(pdf_file_path):
        print(f"❌ PDF file not found: {pdf_file_path}")
        print("   Please provide a valid PDF file path")
        return
    
    try:
        with open(pdf_file_path, 'rb') as pdf_file:
            files = {'pdf': pdf_file}
            
            print(f"📤 Uploading: {pdf_file_path}")
            response = requests.post(f"{API_BASE}/process", files=files)
            
            if response.status_code == 200:
                # Save the processed CSV
                with open('processed_result.csv', 'wb') as output_file:
                    output_file.write(response.content)
                print("✅ Success! Downloaded: processed_result.csv")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def example_2_pdf_and_csv():
    """Example 2: Process PDF with additional CSV data."""
    print("\n📄 Example 2: Processing PDF + CSV")
    
    pdf_file_path = "sample.pdf"      # Replace with your PDF file path
    csv_file_path = "additional.csv"  # Replace with your CSV file path
    
    if not os.path.exists(pdf_file_path):
        print(f"❌ PDF file not found: {pdf_file_path}")
        return
        
    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file not found: {csv_file_path}")
        return
    
    try:
        with open(pdf_file_path, 'rb') as pdf_file, \
             open(csv_file_path, 'rb') as csv_file:
            
            files = {
                'pdf': pdf_file,
                'csv': csv_file
            }
            
            print(f"📤 Uploading: {pdf_file_path} + {csv_file_path}")
            response = requests.post(f"{API_BASE}/process", files=files)
            
            if response.status_code == 200:
                # Save the processed CSV
                with open('processed_with_csv.csv', 'wb') as output_file:
                    output_file.write(response.content)
                print("✅ Success! Downloaded: processed_with_csv.csv")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def example_3_check_server():
    """Example 3: Check if server is running before processing."""
    print("\n🔍 Example 3: Server health check first")
    
    try:
        # Check if server is running
        health_response = requests.get(f"{API_BASE}/health")
        if health_response.status_code == 200:
            print("✅ Server is healthy")
            print(f"   Response: {health_response.json()}")
            
            # Now you can safely process files
            print("🚀 Server ready for processing!")
        else:
            print(f"❌ Server not healthy: {health_response.status_code}")
            
    except requests.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Start the server with: python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def example_4_error_handling():
    """Example 4: Demonstrate error handling."""
    print("\n⚠️ Example 4: Error handling")
    
    try:
        # Try to send request without PDF file (should fail)
        files = {'wrong_field': ('test.txt', 'not a pdf')}
        response = requests.post(f"{API_BASE}/process", files=files)
        
        if response.status_code != 200:
            print(f"✅ Expected error caught: {response.status_code}")
            error_info = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"   Error details: {error_info}")
        else:
            print("❌ Unexpected success")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all examples."""
    print("🚀 BOL Processing API - Usage Examples")
    print("=" * 50)
    
    # Check server first
    example_3_check_server()
    
    # Try processing examples
    example_1_pdf_only()
    example_2_pdf_and_csv()
    example_4_error_handling()
    
    print("\n" + "=" * 50)
    print("💡 Tips:")
    print("- Make sure the server is running: python app.py")
    print("- Replace file paths with your actual files")
    print("- Check the API docs: GET /api/docs")

if __name__ == "__main__":
    main() 