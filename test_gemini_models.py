#!/usr/bin/env python3
"""
Test script to check available Gemini models
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found in environment variables")
    exit(1)

genai.configure(api_key=api_key)

print("🔍 Checking available Gemini models...")
print("=" * 50)

try:
    # List all available models
    models = genai.list_models()
    
    print("📋 Available Models:")
    for model in models:
        print(f"  • {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"    Methods: {model.supported_generation_methods}")
        print()
    
    # Test different model names
    test_models = [
        'gemini-pro',
        'gemini-1.5-pro',
        'gemini-1.5-flash',
        'models/gemini-pro',
        'models/gemini-1.5-pro',
        'models/gemini-1.5-flash'
    ]
    
    print("🧪 Testing model names:")
    print("=" * 50)
    
    for model_name in test_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, test message")
            print(f"✅ {model_name}: Working")
            print(f"   Response: {response.text[:50]}...")
            break
        except Exception as e:
            print(f"❌ {model_name}: {str(e)}")
    
except Exception as e:
    print(f"❌ Error listing models: {e}")
