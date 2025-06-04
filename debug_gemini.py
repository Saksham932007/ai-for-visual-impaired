#!/usr/bin/env python3

import sys
import os
sys.path.append('/app/backend')

# Test the import and Gemini setup
try:
    print("Testing imports...")
    import google.generativeai as genai
    print("✅ google.generativeai imported successfully")
    
    from PIL import Image
    print("✅ PIL imported successfully")
    
    # Test API key
    api_key = os.environ.get('GEMINI_API_KEY')
    print(f"API Key present: {'Yes' if api_key else 'No'}")
    
    if api_key:
        print("Configuring Gemini...")
        genai.configure(api_key=api_key)
        
        print("Creating model...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Model created successfully")
        
        # Test with a simple text prompt
        print("Testing text generation...")
        response = model.generate_content("Say hello")
        print(f"✅ Text generation works: {response.text}")
        
        print("✅ All tests passed!")
    else:
        print("❌ No API key found")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()