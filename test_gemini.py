"""
Test script to verify Gemini API integration
"""
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY', 'AIzaSyBDgU6zbZ_psD93kPA88lmUVzjwi04vDwk'))

def test_gemini_api():
    """Test Gemini API with a farming question"""
    try:
        # Initialize model
        model = genai.GenerativeModel('gemini-pro')
        
        # Test question
        question = "What crops should I grow in July in India?"
        
        # Create farming-specific prompt
        prompt = f"""You are KrishiAI, a helpful farming assistant for Indian farmers. 
        Provide practical, actionable advice in simple language. Focus on:
        - Crop selection and timing
        - Pest and disease management
        - Weather-based farming tips
        - Sustainable farming practices
        
        Keep responses concise and practical (max 200 words).
        
        Question: {question}"""
        
        print("🌾 Testing KrishiAI with Gemini API...")
        print(f"📝 Question: {question}")
        print("🤖 Generating response...")
        
        # Generate response
        response = model.generate_content(prompt)
        
        print("✅ Success! Gemini API Response:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        print("🎉 Gemini API integration working perfectly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Gemini API: {e}")
        return False

if __name__ == "__main__":
    test_gemini_api()
