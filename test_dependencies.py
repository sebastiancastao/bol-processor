#!/usr/bin/env python3
"""
Test script to verify all dependencies are properly installed
"""

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import flask
        print("✅ Flask imported successfully")
        
        import pandas as pd
        print("✅ Pandas imported successfully")
        
        import numpy as np
        print("✅ Numpy imported successfully")
        
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
        
        import pdfplumber
        print("✅ pdfplumber imported successfully")
        
        import pdf2image
        print("✅ pdf2image imported successfully")
        
        import PIL
        print("✅ Pillow imported successfully")
        
        import openai
        print("✅ OpenAI imported successfully")
        
        import requests
        print("✅ Requests imported successfully")
        
        print("\n🎉 All dependencies imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of key modules"""
    try:
        # Test pandas
        df = pd.DataFrame({'test': [1, 2, 3]})
        print("✅ Pandas basic functionality works")
        
        # Test numpy
        arr = np.array([1, 2, 3])
        print("✅ Numpy basic functionality works")
        
        # Test Flask
        app = flask.Flask(__name__)
        print("✅ Flask basic functionality works")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing dependencies...")
    imports_ok = test_imports()
    
    if imports_ok:
        print("\nTesting basic functionality...")
        functionality_ok = test_basic_functionality()
        
        if functionality_ok:
            print("\n✅ All tests passed! Ready for deployment.")
        else:
            print("\n❌ Some functionality tests failed.")
    else:
        print("\n❌ Import tests failed.") 