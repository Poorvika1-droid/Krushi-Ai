# 🌾 KrishiAI - Voice Chatbot for Farmers

**Real social innovation helping non-English rural users with AI-powered farming assistance**

## 🎯 Problem Statement
Farmers in rural India face language barriers when seeking farming advice. They need answers in simple, local languages about crops, pests, diseases, and farming practices.

## 💡 Solution
KrishiAI is a voice-based chatbot that:
- 🎤 **Voice Interface**: Speak in your local language (Hindi, Kannada, Tamil, Telugu, Marathi)
- 🤖 **AI-Powered**: Uses ChatGPT-like technology for intelligent responses
- 🔊 **Text-to-Speech**: Get spoken replies in your language
- 📱 **SMS Support**: Works offline via SMS for areas with poor internet
- 🌐 **Multi-language**: Supports 6 Indian languages + English
- 💾 **Offline Mode**: Basic responses available without internet

## 🚀 Features

### Core Features
- **Voice Recognition**: Ask questions by speaking
- **Multi-language Support**: Hindi, Kannada, Tamil, Telugu, Marathi, English
- **AI Responses**: Powered by Google Gemini OR OpenAI GPT for intelligent farming advice
- **Text-to-Speech**: Hear responses in your preferred language
- **SMS Integration**: Get answers via SMS when offline
- **Conversation History**: Track your farming queries

### Farming Expertise
- 🌱 **Crop Guidance**: What to grow based on season and location
- 🐛 **Pest Control**: Identify and treat common pests
- 🦠 **Disease Management**: Diagnose and treat plant diseases
- 🌧️ **Weather Advice**: Weather-based farming recommendations
- 💰 **Government Schemes**: Information about farmer support programs

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework
- **Google Gemini API**: AI-powered responses (primary)
- **OpenAI GPT API**: Alternative AI provider
- **Google Cloud TTS/STT**: Voice processing
- **SQLite**: Local database for conversations
- **Twilio**: SMS integration

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Voice recognition and UI interactions
- **Service Worker**: Offline functionality
- **Web Speech API**: Browser-based voice recognition

## 📋 Prerequisites

1. **Python 3.8+**
2. **AI Provider** (choose one or both):
   - **Google Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
3. **Google Cloud Account** - For TTS/STT services
4. **Twilio Account** - For SMS functionality (optional)

## 🔧 Installation & Setup

### 1. Clone and Setup Environment
```bash
cd "c:\Users\poorv\OneDrive\Desktop\Krushi Ai"
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```env
# AI Provider Configuration (choose: 'gemini' or 'openai')
AI_PROVIDER=gemini

# Google Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google Cloud Configuration  
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google-credentials.json

# Twilio Configuration (Optional - for SMS)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

### 3. Setup Google Cloud Services

#### Enable APIs:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Text-to-Speech API** and **Speech-to-Text API**
3. Create a service account and download JSON credentials
4. Set the path in your `.env` file

### 4. Setup Google Gemini API
1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add to `.env` file (already configured with your key)

### 5. Run the Application
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## 🎮 Usage

### Web Interface
1. **Select Language**: Choose your preferred language from dropdown
2. **Voice Input**: Click microphone button and speak your question
3. **Text Input**: Or type your question in the text box
4. **Get Response**: Receive AI-generated answer in text and audio
5. **User Profile**: Track your farming questions and conversation history
6. **Authentication**: Secure login/signup system for personalized experience

### SMS Interface (Optional)
Send SMS to your Twilio number with farming questions and get responses back.

## 🌟 Detailed Features

### 🌱 Crop Guidance
- **Seasonal Recommendations**: Get advice on what crops to grow based on current season
- **Location-Based Advice**: Crop suggestions tailored to your geographic location
- **Timing Guidance**: Best planting and harvesting times for different crops
- **Variety Selection**: Choose the right crop varieties for your conditions

### 🐛 Pest Control
- **Pest Identification**: Describe symptoms and get pest identification
- **Treatment Recommendations**: Organic and chemical treatment options
- **Prevention Tips**: How to prevent common pest infestations
- **Integrated Pest Management**: Sustainable pest control strategies

### 🌧️ Weather Tips
- **Weather-Based Farming**: Advice based on current weather conditions
- **Monsoon Preparation**: How to prepare crops for monsoon season
- **Drought Management**: Water conservation and drought-resistant practices
- **Seasonal Planning**: Plan your farming activities around weather patterns

### 📱 SMS Support

KrishiAI offers comprehensive SMS-based support to reach farmers in areas with limited internet connectivity. The SMS service works on any basic mobile phone and supports multiple regional languages.

### Key Features

- **Offline Access**: Get farming advice without needing an internet connection
- **Multi-language Support**: Available in English, Hindi, Kannada, Tamil, Telugu, and Marathi
- **Simple Commands**: Easy-to-use text commands for quick access to information
- **No App Required**: Works on any mobile phone with SMS capability
- **Rural Friendly**: Optimized for areas with poor internet but good mobile coverage

### How to Use

1. **Send an SMS** to the KrishiAI number with your farming question
2. **Start with a language code** (optional, defaults to English):
   - `hi` for Hindi
   - `kn` for Kannada
   - `ta` for Tamil
   - `te` for Telugu
   - `mr` for Marathi
   - `en` for English (default)

**Examples**:
- `hi मेरी फसल में कीड़े लग गए हैं` (Get help with pests in Hindi)
- `kn ಬೆಳೆಗೆ ಕೀಟಗಳು ಬಂದಿದೆ` (Get pest control advice in Kannada)
- `What's the best time to plant rice?` (English is default)

### Available Commands

- `help` - Show help menu in your language
- `lang [code]` - Change language (e.g., `lang hi` for Hindi)
- `crop [name]` - Get crop-specific guidance
- `pest [name]` - Get pest control information
- `weather` - Get weather-based farming tips

### Setup for Development

1. **Twilio Account**
   - Sign up at [Twilio](https://www.twilio.com/)
   - Get your Account SID, Auth Token, and Twilio phone number

2. **Environment Variables**
   Add these to your `.env` file:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+1234567890  # Your Twilio phone number
   ```

3. **Webhook Setup**
   - Set your webhook URL in Twilio to: `https://your-domain.com/api/sms`
   - For local testing, use ngrok: `ngrok http 5000`
   - Update Twilio webhook to: `https://your-ngrok-url.ngrok.io/api/sms`

### Testing SMS Locally

1. Install required packages:
   ```bash
   pip install twilio
   ```

2. Run the Flask app:
   ```bash
   python app.py
   ```

3. Test using curl:
   ```bash
   curl -X POST http://localhost:5000/api/sms \
        -d "Body=hi मेरी फसल में कीड़े लग गए हैं" \
        -d "From=+919876543210"
   ```

### Error Handling

- If the service is unavailable, users will receive a message in their language
- Responses are automatically truncated to fit SMS character limits
- Fallback to English if translation is not available

### Note
- Standard SMS rates may apply based on your mobile carrier
- For best results, keep questions concise and specific

## 📱 Example Questions

### English
- "What crop should I grow in July?"
- "How to control aphids on my cotton crop?"
- "What are the symptoms of rice blast disease?"

### Hindi
- "जुलाई में कौन सी फसल उगानी चाहिए?"
- "कपास में माहू कैसे नियंत्रित करें?"

### Kannada
- "ಜುಲೈನಲ್ಲಿ ಯಾವ ಬೆಳೆ ಬೆಳೆಯಬೇಕು?"

## 🏗️ Project Structure
```
KrishiAI/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── krishi_ai.db          # SQLite database (auto-created)
├── templates/
│   └── index.html        # Main web interface
└── static/
    └── js/
        ├── main.js       # Frontend JavaScript

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google for the Gemini API
- OpenAI for the GPT API
- All the farmers who provided valuable insights
- Open source community for various libraries and tools

## Support

For support and queries:
- Create an issue on GitHub
- Email: support@krishiai.com (placeholder)

---

**Made with ❤️ for Indian Farmers**

*Empowering rural communities through AI and voice technology*
