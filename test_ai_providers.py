#!/usr/bin/env python3
"""
Test script to verify both Google Gemini and OpenAI API integration
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_gemini():
    """Test Google Gemini API"""
    print("Testing Google Gemini API...")
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content("What is the best crop to grow in July in India?")
        print("✅ Gemini API working!")
        print(f"Response: {response.text[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return False

def test_openai():
    """Test OpenAI API"""
    print("\nTesting OpenAI API...")
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a farming assistant for Indian farmers."},
                {"role": "user", "content": "What is the best crop to grow in July in India?"}
            ],
            max_tokens=100
        )
        
        print("✅ OpenAI API working!")
        print(f"Response: {response.choices[0].message.content[:100]}...")
        return True
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return False

def main():
    """Main test function"""
    print("🌾 KrishiAI - AI Provider Test")
    print("=" * 40)
    
    # Test both providers
    gemini_works = test_gemini()
    openai_works = test_openai()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"Google Gemini: {'✅ Working' if gemini_works else '❌ Failed'}")
    print(f"OpenAI GPT: {'✅ Working' if openai_works else '❌ Failed'}")
    
    if gemini_works or openai_works:
        print("\n🎉 At least one AI provider is working!")
        print("Your KrishiAI application is ready to use.")
    else:
        print("\n⚠️  No AI providers are working.")
        print("Please check your API keys in the .env file.")
    
    # Show current configuration
    ai_provider = os.getenv('AI_PROVIDER', 'gemini').lower()
    print(f"\n🔧 Current AI Provider: {ai_provider}")
    
    if ai_provider == 'openai' and not openai_works:
        print("⚠️  Warning: OpenAI is configured but not working. Falling back to Gemini.")
    elif ai_provider == 'gemini' and not gemini_works:
        print("⚠️  Warning: Gemini is configured but not working. Consider switching to OpenAI.")

if __name__ == "__main__":
    main()
