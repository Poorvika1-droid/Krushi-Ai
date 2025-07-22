from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI not available. Only Gemini will be used.")
try:
    from google.cloud import texttospeech, speech
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    print("Google Cloud TTS/STT not available. Audio features will be disabled.")

try:
    from googletrans import Translator
    translator = Translator()
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("Google Translator not available. Translation features will be limited.")

import sqlite3
import json
from datetime import datetime
import base64
import io

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("Twilio not available. SMS features will be disabled.")

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'krishi-ai-secret-key-2024')
CORS(app)

# Initialize AI services
AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini').lower()

# Initialize Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY', 'AIzaSyBDgU6zbZ_psD93kPA88lmUVzjwi04vDwk'))

# Initialize OpenAI
openai_client = None
if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Twilio setup for SMS (optional)
if TWILIO_AVAILABLE:
    try:
        twilio_client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
    except:
        twilio_client = None
else:
    twilio_client = None

# Language mappings
LANGUAGE_CODES = {
    'hindi': 'hi',
    'kannada': 'kn',
    'english': 'en',
    'tamil': 'ta',
    'telugu': 'te',
    'marathi': 'mr'
}

class KrishiAI:
    def __init__(self):
        self.init_database()
        self.farming_knowledge = self.load_farming_knowledge()
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        
    def get_weather_data(self, lat, lon):
        """Fetch current weather data from OpenWeatherMap API"""
        if not self.weather_api_key:
            return None
            
        try:
            import requests
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None
            
    def get_weather_forecast(self, lat, lon):
        """Fetch weather forecast from OpenWeatherMap API"""
        if not self.weather_api_key:
            return None
            
        try:
            import requests
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching weather forecast: {e}")
            return None
            
    def get_weather_recommendations(self, weather_data):
        """Generate farming recommendations based on weather data"""
        if not weather_data:
            return "Weather data not available. Please check your connection or try again later."
            
        try:
            temp = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            condition = weather_data['weather'][0]['main'].lower()
            wind_speed = weather_data['wind']['speed']
            
            recommendations = []
            
            # Temperature-based recommendations
            if temp > 35:
                recommendations.append("High temperature warning: Consider irrigating in the evening to reduce water loss.")
            elif temp < 10:
                recommendations.append("Low temperature alert: Protect sensitive crops from frost.")
                
            # Rainfall/condition based
            if 'rain' in condition:
                recommendations.append("Rain expected: Delay fertilizer application to prevent runoff.")
            elif 'clear' in condition and temp > 30:
                recommendations.append("Hot and clear: Ensure adequate irrigation and consider shade for sensitive crops.")
                
            # Wind conditions
            if wind_speed > 15:  # m/s
                recommendations.append(f"High winds ({wind_speed} m/s): Protect young plants and secure greenhouses.")
                
            # Humidity considerations
            if humidity > 80:
                recommendations.append("High humidity: Watch for fungal diseases. Consider applying fungicide if needed.")
            elif humidity < 30:
                recommendations.append("Low humidity: Increase irrigation frequency to prevent water stress.")
                
            if not recommendations:
                return "Weather conditions are generally favorable for most crops. No special actions needed at this time."
                
            return "\n".join(recommendations)
            
        except Exception as e:
            print(f"Error generating weather recommendations: {e}")
            return "Unable to generate weather-specific recommendations at this time."
    
    def init_database(self):
        """Initialize SQLite database for storing conversations and knowledge"""
        conn = sqlite3.connect('krishi_ai.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                phone TEXT,
                location TEXT,
                farm_size TEXT,
                crops TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            )
        ''')
        
        # Create conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question TEXT,
                answer TEXT,
                language TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create knowledge base table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                question TEXT,
                answer TEXT,
                language TEXT,
                keywords TEXT
            )
        ''')
        
        # Create crop_guidance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crop_guidance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_name TEXT NOT NULL,
                season TEXT,
                location TEXT,
                soil_type TEXT,
                planting_time TEXT,
                harvesting_time TEXT,
                water_requirements TEXT,
                fertilizer_needs TEXT,
                common_varieties TEXT,
                special_notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create pest_control table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pest_control (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pest_name TEXT NOT NULL,
                affected_crops TEXT,
                symptoms TEXT,
                organic_control TEXT,
                chemical_control TEXT,
                prevention TEXT,
                image_url TEXT,
                severity TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create weather_tips table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_tips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weather_condition TEXT NOT NULL,
                crop_impact TEXT,
                recommended_actions TEXT,
                protection_measures TEXT,
                timing_considerations TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create user_farms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_farms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                farm_name TEXT,
                location TEXT,
                size REAL,
                soil_type TEXT,
                current_crops TEXT,
                irrigation_type TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create crop_calendar table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crop_calendar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                crop_name TEXT,
                planting_date DATE,
                expected_harvest_date DATE,
                actual_harvest_date DATE,
                notes TEXT,
                status TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create index for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_crop_season ON crop_guidance(season, location)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pest_crop ON pest_control(affected_crops)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_condition ON weather_tips(weather_condition)')
        
        conn.commit()
        conn.close()
    
    def load_farming_knowledge(self):
        """Load basic farming knowledge for offline access"""
        return {
            'crops': {
                'july': ['rice', 'cotton', 'sugarcane', 'maize', 'pulses'],
                'monsoon': ['rice', 'cotton', 'jute', 'sugarcane'],
                'winter': ['wheat', 'barley', 'mustard', 'peas']
            },
            'pests': {
                'aphids': 'Small green insects that suck plant juices. Use neem oil spray.',
                'bollworm': 'Caterpillars that damage cotton. Use pheromone traps.',
                'stem_borer': 'Affects rice stems. Use resistant varieties.'
            },
            'diseases': {
                'blight': 'Fungal disease causing leaf spots. Use copper fungicide.',
                'rust': 'Orange spots on leaves. Improve air circulation.',
                'wilt': 'Plant drooping. Check soil drainage.'
            }
        }
    
    def get_ai_response(self, question, language='english'):
        """Get AI response from configured AI provider (Gemini or OpenAI) with farming context"""
        try:
            # Detect language and create appropriate prompt
            language_instructions = {
                'hindi': 'हिंदी में जवाब दें। सरल भाषा का उपयोग करें।',
                'kannada': 'ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ। ಸರಳ ಭಾಷೆಯನ್ನು ಬಳಸಿ।',
                'tamil': 'தமிழில் பதிலளிக்கவும். எளிய மொழியைப் பயன்படுத்தவும்।',
                'telugu': 'తెలుగులో సమాధానం ఇవ్వండి. సరళమైన భాష ఉపయోగించండి।',
                'marathi': 'मराठीत उत्तर द्या. सोप्या भाषेचा वापर करा।',
                'english': 'Respond in English. Use simple language.'
            }
            
            lang_instruction = language_instructions.get(language, language_instructions['english'])
            
            # Create farming-specific prompt with language instruction
            system_prompt = f"""You are KrishiAI, a helpful farming assistant for Indian farmers.
            
            CRITICAL INSTRUCTIONS:
            1. {lang_instruction}
            2. ALWAYS analyze the specific question asked
            3. Provide different answers for different questions
            4. Be specific to the farmer's actual query
            
            Question Analysis:
            - Question: "{question}"
            - Language: {language}
            - Context: Indian farming
            
            Provide practical, actionable advice focusing on:
            - Crop selection and timing for Indian conditions
            - Pest and disease management  
            - Weather-based farming tips
            - Sustainable farming practices
            - Government schemes for farmers
            - Local Indian farming techniques
            
            IMPORTANT: 
            - Keep responses concise (max 100 words)
            - Always respond in {language} language
            - Give specific answers to specific questions
            - Don't give generic responses
            
            Farmer's Question: {question}"""
            
            # Use configured AI provider
            if AI_PROVIDER == 'openai' and openai_client:
                return self._get_openai_response(system_prompt)
            else:
                return self._get_gemini_response(system_prompt)
        
        except Exception as e:
            print(f"AI API Error: {e}")
            # Fallback to local knowledge with language support
            return self.get_offline_response(question, language)
    
    def _get_gemini_response(self, prompt):
        """Get response from Google Gemini"""
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    
    def _get_openai_response(self, prompt):
        """Get response from OpenAI GPT"""
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are KrishiAI, a helpful farming assistant for Indian farmers."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
        
    # Crop Guidance Methods
    def add_crop_guidance(self, crop_name, season=None, location=None, soil_type=None, planting_time=None, 
                         harvesting_time=None, water_requirements=None, fertilizer_needs=None, 
                         common_varieties=None, special_notes=None):
        """Add or update crop guidance information"""
        conn = sqlite3.connect('krishi_ai.db')
        cursor = conn.cursor()
        
        # Check if entry already exists
        cursor.execute('''
            SELECT id FROM crop_guidance 
            WHERE crop_name = ? AND (season = ? OR season IS NULL) AND (location = ? OR location IS NULL)
        ''', (crop_name, season, location))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing entry
            cursor.execute('''
                UPDATE crop_guidance SET
                    soil_type = COALESCE(?, soil_type),
                    planting_time = COALESCE(?, planting_time),
                    harvesting_time = COALESCE(?, harvesting_time),
                    water_requirements = COALESCE(?, water_requirements),
                    fertilizer_needs = COALESCE(?, fertilizer_needs),
                    common_varieties = COALESCE(?, common_varieties),
                    special_notes = COALESCE(?, special_notes)
                WHERE id = ?
            ''', (soil_type, planting_time, harvesting_time, water_requirements, 
                 fertilizer_needs, common_varieties, special_notes, existing[0]))
        else:
            # Insert new entry
            cursor.execute('''
                INSERT INTO crop_guidance 
                (crop_name, season, location, soil_type, planting_time, harvesting_time, 
                 water_requirements, fertilizer_needs, common_varieties, special_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (crop_name, season, location, soil_type, planting_time, harvesting_time,
                 water_requirements, fertilizer_needs, common_varieties, special_notes))
        
        conn.commit()
        conn.close()
        return True
    
    def get_crop_guidance(self, crop_name=None, season=None, location=None):
        """Get crop guidance information"""
        conn = sqlite3.connect('krishi_ai.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM crop_guidance WHERE 1=1'
        params = []
        
        if crop_name:
            query += ' AND LOWER(crop_name) = LOWER(?)'
            params.append(crop_name)
        if season:
            query += ' AND LOWER(season) = LOWER(?)'
            params.append(season)
        if location:
            query += ' AND LOWER(location) LIKE ?'
            params.append(f'%{location.lower()}%')
            
        query += ' ORDER BY crop_name, season, location'
        cursor.execute(query, params)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    # Pest Control Methods
    def add_pest_info(self, pest_name, affected_crops=None, symptoms=None, organic_control=None, 
                      chemical_control=None, prevention=None, image_url=None, severity=None):
        """Add or update pest control information"""
        conn = sqlite3.connect('krishi_ai.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM pest_control WHERE LOWER(pest_name) = LOWER(?)', (pest_name,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE pest_control SET
                    affected_crops = COALESCE(?, affected_crops),
                    symptoms = COALESCE(?, symptoms),
                    organic_control = COALESCE(?, organic_control),
                    chemical_control = COALESCE(?, chemical_control),
                    prevention = COALESCE(?, prevention),
                    image_url = COALESCE(?, image_url),
                    severity = COALESCE(?, severity)
                WHERE id = ?
            ''', (affected_crops, symptoms, organic_control, chemical_control, 
                 prevention, image_url, severity, existing[0]))
        else:
            cursor.execute('''
                INSERT INTO pest_control 
                (pest_name, affected_crops, symptoms, organic_control, chemical_control, prevention, image_url, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (pest_name, affected_crops, symptoms, organic_control, 
                 chemical_control, prevention, image_url, severity))
        
        conn.commit()
        conn.close()
        return True
    
    def get_pest_info(self, pest_name=None, crop_name=None, severity=None):
        """Get pest control information"""
        conn = sqlite3.connect('krishi_ai.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM pest_control WHERE 1=1'
        params = []
        
        if pest_name:
            query += ' AND LOWER(pest_name) LIKE ?'
            params.append(f'%{pest_name.lower()}%')
        if crop_name:
            query += ' AND LOWER(affected_crops) LIKE ?'
            params.append(f'%{crop_name.lower()}%')
        if severity:
            query += ' AND LOWER(severity) = LOWER(?)'
            params.append(severity)
            
        query += ' ORDER BY pest_name'
        cursor.execute(query, params)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    # Weather Tips Methods
    def add_weather_tip(self, weather_condition, crop_impact=None, recommended_actions=None, 
                       protection_measures=None, timing_considerations=None):
        """Add or update weather-based farming tips"""
        conn = sqlite3.connect('krishi_ai.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM weather_tips WHERE LOWER(weather_condition) = LOWER(?)', 
                      (weather_condition,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE weather_tips SET
                    crop_impact = COALESCE(?, crop_impact),
                    recommended_actions = COALESCE(?, recommended_actions),
                    protection_measures = COALESCE(?, protection_measures),
                    timing_considerations = COALESCE(?, timing_considerations)
                WHERE id = ?
            ''', (crop_impact, recommended_actions, protection_measures, 
                 timing_considerations, existing[0]))
        else:
            cursor.execute('''
                INSERT INTO weather_tips 
                (weather_condition, crop_impact, recommended_actions, protection_measures, timing_considerations)
                VALUES (?, ?, ?, ?, ?)
            ''', (weather_condition, crop_impact, recommended_actions, 
                 protection_measures, timing_considerations))
        
        conn.commit()
        conn.close()
        return True
    
    def get_weather_tips(self, weather_condition=None):
        """Get weather-based farming tips"""
        conn = sqlite3.connect('krishi_ai.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if weather_condition:
            cursor.execute('''
                SELECT * FROM weather_tips 
                WHERE LOWER(weather_condition) LIKE ?
                ORDER BY weather_condition
            ''', (f'%{weather_condition.lower()}%',))
        else:
            cursor.execute('SELECT * FROM weather_tips ORDER BY weather_condition')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    # User Farm Management
    def add_user_farm(self, user_id, farm_name, location=None, size=None, 
                     soil_type=None, current_crops=None, irrigation_type=None):
        """Add or update user's farm information"""
        conn = sqlite3.connect('krishi_ai.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM user_farms 
            WHERE user_id = ? AND LOWER(farm_name) = LOWER(?)
        ''', (user_id, farm_name))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE user_farms SET
                    location = COALESCE(?, location),
                    size = COALESCE(?, size),
                    soil_type = COALESCE(?, soil_type),
                    current_crops = COALESCE(?, current_crops),
                    irrigation_type = COALESCE(?, irrigation_type)
                WHERE id = ?
            ''', (location, size, soil_type, current_crops, irrigation_type, existing[0]))
        else:
            cursor.execute('''
                INSERT INTO user_farms 
                (user_id, farm_name, location, size, soil_type, current_crops, irrigation_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, farm_name, location, size, soil_type, current_crops, irrigation_type))
        
        conn.commit()
        conn.close()
        return True
    
    def get_user_farms(self, user_id):
        """Get all farms for a user"""
        conn = sqlite3.connect('krishi_ai.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_farms WHERE user_id = ?', (user_id,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    # Crop Calendar Methods
    def add_crop_calendar_entry(self, user_id, crop_name, planting_date, 
                              expected_harvest_date=None, notes=None, status='Planned'):
        """Add or update crop calendar entry"""
        conn = sqlite3.connect('krishi_ai.db')
        cursor = conn.cursor()
        
        # Convert string dates to date objects if needed
        if isinstance(planting_date, str):
            planting_date = datetime.strptime(planting_date, '%Y-%m-%d').date()
        if expected_harvest_date and isinstance(expected_harvest_date, str):
            expected_harvest_date = datetime.strptime(expected_harvest_date, '%Y-%m-%d').date()
        
        cursor.execute('''
            INSERT INTO crop_calendar 
            (user_id, crop_name, planting_date, expected_harvest_date, notes, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, crop_name, planting_date, expected_harvest_date, notes, status))
        
        conn.commit()
        conn.close()
        return True
    
    def update_crop_calendar_entry(self, entry_id, actual_harvest_date=None, notes=None, status=None):
        """Update crop calendar entry with harvest information"""
        conn = sqlite3.connect('krishi_ai.db')
        cursor = conn.cursor()
        
        update_fields = []
        params = []
        
        if actual_harvest_date:
            if isinstance(actual_harvest_date, str):
                actual_harvest_date = datetime.strptime(actual_harvest_date, '%Y-%m-%d').date()
            update_fields.append('actual_harvest_date = ?')
            params.append(actual_harvest_date)
        if notes is not None:
            update_fields.append('notes = ?')
            params.append(notes)
        if status:
            update_fields.append('status = ?')
            params.append(status)
        
        if update_fields:
            query = f'UPDATE crop_calendar SET {", ".join(update_fields)} WHERE id = ?'
            params.append(entry_id)
            cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        return True
    
    def get_crop_calendar(self, user_id, status=None, start_date=None, end_date=None):
        """Get user's crop calendar entries with optional filters"""
        conn = sqlite3.connect('krishi_ai.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM crop_calendar WHERE user_id = ?'
        params = [user_id]
        
        if status:
            query += ' AND LOWER(status) = LOWER(?)'
            params.append(status)
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query += ' AND (planting_date >= ? OR expected_harvest_date >= ? OR actual_harvest_date >= ?)'
            params.extend([start_date, start_date, start_date])
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query += ' AND (planting_date <= ? OR expected_harvest_date <= ? OR actual_harvest_date <= ?)'
            params.extend([end_date, end_date, end_date])
        
        query += ' ORDER BY COALESCE(actual_harvest_date, expected_harvest_date, planting_date) DESC'
        cursor.execute(query, params)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_offline_response(self, question, language='english'):
        """Provide offline responses based on local knowledge with language support"""
        question_lower = question.lower()
        
        # Language-specific responses
        responses = {
            'english': {
                'crop': "For July/Monsoon season, consider growing: Rice, Cotton, Sugarcane, Maize, or Pulses. These crops do well with monsoon rains.",
                'pest': "Common pests include aphids (small green insects), bollworm (caterpillars), and stem borer. Use neem oil, pheromone traps, or consult your local agricultural officer.",
                'disease': "Common plant diseases include blight (leaf spots), rust (orange spots), and wilt (drooping). Improve drainage, use copper fungicide, or contact agricultural experts.",
                'default': "I'm here to help with farming questions! Ask me about crops, pests, diseases, or farming practices. For complex issues, consult your local agricultural extension officer."
            },
            'hindi': {
                'crop': "जुलाई/मानसून के मौसम में धान, कपास, गन्ना, मक्का या दालें उगाएं। ये फसलें मानसूनी बारिश में अच्छी होती हैं।",
                'pest': "आम कीट हैं माहू (छोटे हरे कीड़े), बॉलवर्म (कैटरपिलर), और तना छेदक। नीम का तेल, फेरोमोन ट्रैप का उपयोग करें या स्थानीय कृषि अधिकारी से सलाह लें।",
                'disease': "आम पौधों की बीमारियां हैं झुलसा (पत्ती के धब्बे), रतुआ (नारंगी धब्बे), और मुरझाना। जल निकासी सुधारें, कॉपर फंगीसाइड का उपयोग करें।",
                'default': "मैं खेती के सवालों में आपकी मदद के लिए यहां हूं! फसल, कीट, बीमारी या खेती की प्रथाओं के बारे में पूछें।"
            },
            'kannada': {
                'crop': "ಜುಲೈ/ಮಾನ್ಸೂನ್ ಋತುವಿನಲ್ಲಿ ಅಕ್ಕಿ, ಹತ್ತಿ, ಕಬ್ಬು, ಮೆಕ್ಕೆಜೋಳ ಅಥವಾ ದಾಲ್ ಬೆಳೆಗಳನ್ನು ಬೆಳೆಯಿರಿ। ಈ ಬೆಳೆಗಳು ಮಾನ್ಸೂನ್ ಮಳೆಯಲ್ಲಿ ಚೆನ್ನಾಗಿ ಬೆಳೆಯುತ್ತವೆ।",
                'pest': "ಸಾಮಾನ್ಯ ಕೀಟಗಳೆಂದರೆ ಅಫಿಡ್‌ಗಳು (ಸಣ್ಣ ಹಸಿರು ಕೀಟಗಳು), ಬಾಲ್‌ವರ್ಮ್ (ಕ್ಯಾಟರ್‌ಪಿಲ್ಲರ್), ಮತ್ತು ಕಾಂಡ ಕೊರೆಯುವ ಕೀಟ। ಬೇವಿನ ಎಣ್ಣೆ, ಫೆರೋಮೋನ್ ಟ್ರ್ಯಾಪ್ ಬಳಸಿ।",
                'disease': "ಸಾಮಾನ್ಯ ಸಸ್ಯ ರೋಗಗಳೆಂದರೆ ಬ್ಲೈಟ್ (ಎಲೆ ಕಲೆಗಳು), ರಸ್ಟ್ (ಕಿತ್ತಳೆ ಕಲೆಗಳು), ಮತ್ತು ವಿಲ್ಟ್ (ಬಾಡುವಿಕೆ)। ನೀರು ಹರಿವನ್ನು ಸುಧಾರಿಸಿ।",
                'default': "ನಾನು ಕೃಷಿ ಪ್ರಶ್ನೆಗಳಿಗೆ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿದ್ದೇನೆ! ಬೆಳೆ, ಕೀಟ, ರೋಗ ಅಥವಾ ಕೃಷಿ ಪದ್ಧತಿಗಳ ಬಗ್ಗೆ ಕೇಳಿ।"
            }
        }
        
        # Get language-specific responses, fallback to English
        lang_responses = responses.get(language, responses['english'])
        
        # More specific keyword matching
        question_words = question_lower.split()
        
        # Check for specific crop names
        crop_names = ['rice', 'wheat', 'cotton', 'sugarcane', 'maize', 'corn', 'tomato', 'potato', 'onion', 
                     'धान', 'गेहूं', 'कपास', 'गन्ना', 'मक्का', 'ಅಕ್ಕಿ', 'ಹತ್ತಿ']
        
        # Check for crop-related questions
        if (any(word in question_lower for word in ['crop', 'grow', 'plant', 'july', 'monsoon', 'season', 'farming',
                                                   'फसल', 'उगा', 'बो', 'खेती', 'मौसम',
                                                   'ಬೆಳೆ', 'ಬೆಳೆಯ', 'ಕೃಷಿ']) or
            any(crop in question_lower for crop in crop_names)):
            return lang_responses['crop']
        
        # Check for pest-related questions
        if any(word in question_lower for word in ['pest', 'insect', 'bug', 'damage', 'attack', 'control',
                                                  'कीट', 'कीड़', 'माहू', 'नुकसान',
                                                  'ಕೀಟ', 'ಹಾನಿ']):
            return lang_responses['pest']
        
        # Check for disease-related questions
        if any(word in question_lower for word in ['disease', 'sick', 'spots', 'yellow', 'dying', 'fungus', 'virus',
                                                  'बीमारी', 'रोग', 'पीला', 'मर',
                                                  'ರೋಗ', 'ಬಾಡು']):
            return lang_responses['disease']
        
        # Check for weather-related questions
        if any(word in question_lower for word in ['weather', 'rain', 'drought', 'water', 'irrigation',
                                                  'मौसम', 'बारिश', 'सूखा', 'पानी',
                                                  'ಹವಾಮಾನ', 'ಮಳೆ']):
            # Add weather responses
            weather_responses = {
                'english': "Monitor weather forecasts regularly. During monsoon, ensure proper drainage. In dry periods, use drip irrigation to conserve water.",
                'hindi': "मौसम की जानकारी नियमित रूप से देखें। मानसून में पानी की निकासी का ध्यान रखें।",
                'kannada': "ಹವಾಮಾನ ವರದಿಯನ್ನು ನಿಯಮಿತವಾಗಿ ನೋಡಿರಿ। ಮಳೆಕಾಲದಲ್ಲಿ ಸರಿಯಾದ ನೀರು ಹರಿವನ್ನು ಸುಧಾರಿಸಿ।"
            }
            return weather_responses.get(language, weather_responses['english'])
        
        return lang_responses['default']
    
    def translate_text(self, text, target_language):
        """Translate text to target language"""
        try:
            if target_language == 'english' or not TRANSLATOR_AVAILABLE:
                return text
            
            lang_code = LANGUAGE_CODES.get(target_language, 'hi')
            translated = translator.translate(text, dest=lang_code)
            return translated.text
        except:
            return text
    
    def text_to_speech(self, text, language='english'):
        """Convert text to speech using Google TTS"""
        if not GOOGLE_CLOUD_AVAILABLE:
            print("Google Cloud TTS not available")
            return None
            
        try:
            client = texttospeech.TextToSpeechClient()
            
            lang_code = LANGUAGE_CODES.get(language, 'en')
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=f"{lang_code}-IN" if lang_code != 'en' else 'en-US',
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return base64.b64encode(response.audio_content).decode()
        
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
    
    def save_conversation(self, user_id, question, answer, language):
        """Save conversation to database"""
        conn = sqlite3.connect('krishi_ai.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (user_id, question, answer, language)
            VALUES (?, ?, ?, ?)
        ''', (user_id, question, answer, language))
        
        conn.commit()
        conn.close()

# Initialize KrishiAI
krishi_ai = KrishiAI()

# Authentication helper functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_by_id(user_id):
    conn = sqlite3.connect('krishi_ai.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = sqlite3.connect('krishi_ai.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, email, password, full_name, phone, location, farm_size, crops):
    conn = sqlite3.connect('krishi_ai.db')
    cursor = conn.cursor()
    
    password_hash = generate_password_hash(password)
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, phone, location, farm_size, crops)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, phone, location, farm_size, crops))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/main')
@login_required
def main():
    user = get_user_by_id(session['user_id'])
    return render_template('main.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user_by_username(username)
        
        if user and check_password_hash(user[3], password):  # user[3] is password_hash
            session['user_id'] = user[0]  # user[0] is id
            session['username'] = user[1]  # user[1] is username
            
            # Update last login
            conn = sqlite3.connect('krishi_ai.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user[0],))
            conn.commit()
            conn.close()
            
            flash('Login successful!', 'success')
            return redirect(url_for('main'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        phone = request.form.get('phone', '')
        location = request.form.get('location', '')
        farm_size = request.form.get('farm_size', '')
        crops = request.form.get('crops', '')
        
        # Check if user already exists
        if get_user_by_username(username):
            flash('Username already exists!', 'error')
            return render_template('signup.html')
        
        # Create new user
        user_id = create_user(username, email, password, full_name, phone, location, farm_size, crops)
        
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            flash('Account created successfully!', 'success')
            return redirect(url_for('main'))
        else:
            flash('Error creating account. Email might already exist.', 'error')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    user = get_user_by_id(session['user_id'])
    
    # Get user's conversation history
    conn = sqlite3.connect('krishi_ai.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get conversations
    cursor.execute('''
        SELECT question, answer, language, timestamp 
        FROM conversations 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 20
    ''', (session['user_id'],))
    conversations = [dict(row) for row in cursor.fetchall()]
    
    # Get user's farms
    cursor.execute('SELECT * FROM user_farms WHERE user_id = ?', (session['user_id'],))
    user_farms = [dict(row) for row in cursor.fetchall()]
    
    # Get upcoming crop calendar entries
    cursor.execute('''
        SELECT * FROM crop_calendar 
        WHERE user_id = ? AND (status = 'Planned' OR status = 'Growing')
        ORDER BY planting_date ASC
        LIMIT 5
    ''', (session['user_id'],))
    crop_calendar = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('profile.html', 
                         user=user, 
                         conversations=conversations,
                         user_farms=user_farms,
                         crop_calendar=crop_calendar)

# ====================
# API Endpoints
# ====================

# Crop Guidance API Endpoints
@app.route('/api/crop-guidance', methods=['GET'])
@login_required
def get_crop_guidance():
    """Get crop guidance information"""
    crop_name = request.args.get('crop')
    season = request.args.get('season')
    location = request.args.get('location')
    
    guidance = krishi_ai.get_crop_guidance(crop_name, season, location)
    return jsonify(guidance)

@app.route('/api/crop-guidance', methods=['POST'])
@login_required
def add_crop_guidance():
    """Add or update crop guidance (admin only)"""
    if not current_user.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    required_fields = ['crop_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        krishi_ai.add_crop_guidance(
            crop_name=data['crop_name'],
            season=data.get('season'),
            location=data.get('location'),
            soil_type=data.get('soil_type'),
            planting_time=data.get('planting_time'),
            harvesting_time=data.get('harvesting_time'),
            water_requirements=data.get('water_requirements'),
            fertilizer_needs=data.get('fertilizer_needs'),
            common_varieties=data.get('common_varieties'),
            special_notes=data.get('special_notes')
        )
        return jsonify({'message': 'Crop guidance added/updated successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Pest Control API Endpoints
@app.route('/api/pests', methods=['GET'])
@login_required
def get_pests():
    """Get pest information"""
    pest_name = request.args.get('pest')
    crop_name = request.args.get('crop')
    severity = request.args.get('severity')
    
    pests = krishi_ai.get_pest_info(pest_name, crop_name, severity)
    return jsonify(pests)

@app.route('/api/pests', methods=['POST'])
@login_required
def add_pest():
    """Add or update pest information (admin only)"""
    if not current_user.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    if 'pest_name' not in data:
        return jsonify({'error': 'Pest name is required'}), 400
    
    try:
        krishi_ai.add_pest_info(
            pest_name=data['pest_name'],
            affected_crops=data.get('affected_crops'),
            symptoms=data.get('symptoms'),
            organic_control=data.get('organic_control'),
            chemical_control=data.get('chemical_control'),
            prevention=data.get('prevention'),
            image_url=data.get('image_url'),
            severity=data.get('severity')
        )
        return jsonify({'message': 'Pest information added/updated successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Weather Tips API Endpoints
@app.route('/api/weather-tips', methods=['GET'])
@login_required
def get_weather_tips():
    """Get weather-based farming tips"""
    weather_condition = request.args.get('condition')
    tips = krishi_ai.get_weather_tips(weather_condition)
    return jsonify(tips)

@app.route('/api/weather-tips', methods=['POST'])
@login_required
def add_weather_tip():
    """Add or update weather tip (admin only)"""
    if not current_user.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    if 'weather_condition' not in data:
        return jsonify({'error': 'Weather condition is required'}), 400
    
    try:
        krishi_ai.add_weather_tip(
            weather_condition=data['weather_condition'],
            crop_impact=data.get('crop_impact'),
            recommended_actions=data.get('recommended_actions'),
            protection_measures=data.get('protection_measures'),
            timing_considerations=data.get('timing_considerations')
        )
        return jsonify({'message': 'Weather tip added/updated successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Farm Management Endpoints
@app.route('/api/farms', methods=['GET'])
@login_required
def get_my_farms():
    """Get current user's farms"""
    farms = krishi_ai.get_user_farms(session['user_id'])
    return jsonify(farms)

@app.route('/api/farms', methods=['POST'])
@login_required
def add_farm():
    """Add or update a farm for the current user"""
    data = request.get_json()
    if 'farm_name' not in data:
        return jsonify({'error': 'Farm name is required'}), 400
    
    try:
        krishi_ai.add_user_farm(
            user_id=session['user_id'],
            farm_name=data['farm_name'],
            location=data.get('location'),
            size=data.get('size'),
            soil_type=data.get('soil_type'),
            current_crops=data.get('current_crops'),
            irrigation_type=data.get('irrigation_type')
        )
        return jsonify({'message': 'Farm added/updated successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Crop Calendar Endpoints
@app.route('/api/crop-calendar', methods=['GET'])
@login_required
def get_my_crop_calendar():
    """Get current user's crop calendar"""
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    calendar = krishi_ai.get_crop_calendar(
        user_id=session['user_id'],
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    return jsonify(calendar)

@app.route('/api/crop-calendar', methods=['POST'])
@login_required
def add_crop_calendar_entry():
    """Add a new crop calendar entry"""
    data = request.get_json()
    required_fields = ['crop_name', 'planting_date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Crop name and planting date are required'}), 400
    
    try:
        krishi_ai.add_crop_calendar_entry(
            user_id=session['user_id'],
            crop_name=data['crop_name'],
            planting_date=data['planting_date'],
            expected_harvest_date=data.get('expected_harvest_date'),
            notes=data.get('notes'),
            status=data.get('status', 'Planned')
        )
        return jsonify({'message': 'Crop calendar entry added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crop-calendar/<int:entry_id>', methods=['PUT'])
@login_required
def update_crop_calendar_entry(entry_id):
    """Update a crop calendar entry"""
    data = request.get_json()
    
    try:
        # Verify the entry belongs to the user
        conn = sqlite3.connect('krishi_ai.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM crop_calendar WHERE id = ?', (entry_id,))
        entry = cursor.fetchone()
        conn.close()
        
        if not entry:
            return jsonify({'error': 'Entry not found'}), 404
            
        if entry[0] != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Update the entry
        krishi_ai.update_crop_calendar_entry(
            entry_id=entry_id,
            actual_harvest_date=data.get('actual_harvest_date'),
            notes=data.get('notes'),
            status=data.get('status')
        )
        return jsonify({'message': 'Crop calendar entry updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/current', methods=['GET'])
@login_required
def get_current_weather():
    """Get current weather data and recommendations"""
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    
    if not lat or not lon:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
    
    try:
        # Get current weather data
        weather_data = krishi_ai.get_weather_data(lat, lon)
        if not weather_data:
            return jsonify({'error': 'Weather data not available'}), 503
            
        # Get farming recommendations
        recommendations = krishi_ai.get_weather_recommendations(weather_data)
        
        # Format response
        response = {
            'temperature': weather_data['main']['temp'],
            'humidity': weather_data['main']['humidity'],
            'condition': weather_data['weather'][0]['main'],
            'description': weather_data['weather'][0]['description'],
            'wind_speed': weather_data['wind']['speed'],
            'recommendations': recommendations
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error getting weather: {e}")
        return jsonify({'error': 'Failed to fetch weather data'}), 500

@app.route('/api/weather/forecast', methods=['GET'])
@login_required
def get_weather_forecast():
    """Get weather forecast for the next 5 days"""
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    
    if not lat or not lon:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
    
    try:
        forecast_data = krishi_ai.get_weather_forecast(lat, lon)
        if not forecast_data:
            return jsonify({'error': 'Forecast data not available'}), 503
            
        # Process forecast data
        daily_forecast = {}
        for item in forecast_data.get('list', []):
            date = item['dt_txt'].split()[0]  # Extract date part
            if date not in daily_forecast:
                daily_forecast[date] = {
                    'date': date,
                    'temp_min': item['main']['temp_min'],
                    'temp_max': item['main']['temp_max'],
                    'humidity': item['main']['humidity'],
                    'conditions': {},
                    'rain': item.get('rain', {}).get('3h', 0)
                }
            # Update min/max temps
            daily_forecast[date]['temp_min'] = min(daily_forecast[date]['temp_min'], item['main']['temp_min'])
            daily_forecast[date]['temp_max'] = max(daily_forecast[date]['temp_max'], item['main']['temp_max'])
            # Track conditions
            condition = item['weather'][0]['main']
            daily_forecast[date]['conditions'][condition] = daily_forecast[date]['conditions'].get(condition, 0) + 1
        
        # Convert to list and sort by date
        forecast_list = sorted(daily_forecast.values(), key=lambda x: x['date'])
        
        return jsonify({'forecast': forecast_list})
        
    except Exception as e:
        print(f"Error getting forecast: {e}")
        return jsonify({'error': 'Failed to fetch forecast data'}), 500

@app.route('/api/ask', methods=['POST'])
@login_required
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '')
        language = data.get('language', 'english')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Get AI response
        answer = krishi_ai.get_ai_response(question, language)
        
        # Save conversation with logged-in user's ID
        user_id = session['user_id']
        krishi_ai.save_conversation(user_id, question, answer, language)
        
        # Convert to speech
        audio_data = krishi_ai.text_to_speech(answer, language)
        
        
        return jsonify({
            'answer': answer,
            'audio': audio_data,
            'language': language,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sms', methods=['POST'])
def handle_sms():
    """Handle SMS queries for offline access with multi-language support"""
    if not TWILIO_AVAILABLE:
        return jsonify({'error': 'SMS service not available'}), 503
        
    # Get the incoming message data from Twilio
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    
    # Detect language from the first word (if language code is provided)
    language = 'en'  # Default to English
    if ' ' in incoming_msg:
        lang_code = incoming_msg.split(' ')[0].lower()
        if lang_code in ['hi', 'kn', 'ta', 'te', 'mr']:
            language = lang_code
            incoming_msg = ' '.join(incoming_msg.split(' ')[1:])  # Remove language code
    
    if not incoming_msg:
        return str(MessagingResponse())
    
    # Simple command parsing
    if incoming_msg.lower() in ['help', 'h', 'menu']:
        response = MessagingResponse()
        help_text = {
            'en': """🌱 KrishiAI SMS Help\n\n"
                 "Send any farming question or use:\n"
                 "- [crop] [name] - Crop guidance\n"
                 "- [pest] [name] - Pest control\n"
                 "- [weather] - Weather tips\n"
                 "- [lang XX] - Change language\n"
                 "- [help] - Show help""",
            'hi': """🌿 कृषि एआई सहायता\n\n"
                 "कृषि प्रश्न भेजें या उपयोग करें:\n"
                 "- [crop] [नाम] - फसल मार्गदर्शन\n"
                 "- [pest] [नाम] - कीट नियंत्रण\n"
                 "- [weather] - मौसम सुझाव\n"
                 "- [lang hi] - भाषा बदलें\n"
                 "- [help] - मदद दिखाएं""",
            'kn': """🌾 ಕೃಷಿ ಏಐ ಸಹಾಯ\n\n"
                 "ಯಾವುದೇ ಕೃಷಿ ಪ್ರಶ್ನೆಯನ್ನು ಕಳುಹಿಸಿ ಅಥವಾ ಬಳಸಿ:\n"
                 "- [crop] [ಹೆಸರು] - ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ\n"
                 "- [pest] [ಹೆಸರು] - ಕೀಟ ನಿಯಂತ್ರಣ\n"
                 "- [weather] - ಹವಾಮಾನ ಸಲಹೆಗಳು\n"
                 "- [lang kn] - ಭಾಷೆ ಬದಲಿಸಿ\n"
                 "- [help] - ಸಹಾಯ ತೋರಿಸಿ"""
        }
        msg = help_text.get(language, help_text['en'])
        response.message(msg)
        return str(response)
    
    # Handle language change
    if incoming_msg.lower().startswith('lang '):
        lang_code = incoming_msg.lower().split(' ')[1]
        if lang_code in ['en', 'hi', 'kn', 'ta', 'te', 'mr']:
            response = MessagingResponse()
            lang_names = {
                'en': 'English',
                'hi': 'हिंदी',
                'kn': 'ಕನ್ನಡ',
                'ta': 'தமிழ்',
                'te': 'తెలుగు',
                'mr': 'मराठी'
            }
            response.message(f"🌐 Language set to {lang_names.get(lang_code, lang_code)}. Now send your question.")
            return str(response)
    
    try:
        # Get AI response with language support
        response_text = krishi_ai.get_ai_response(incoming_msg, language=language)
        
        # Truncate response if too long for SMS (1600 chars max for Twilio)
        if len(response_text) > 1500:
            response_text = response_text[:1497] + '...'
        
        # Add language-specific footer
        footers = {
            'en': "\n\nReply 'help' for menu.",
            'hi': "\n\nमेनू के लिए 'help' भेजें।",
            'kn': "\n\nಮೆನುವಿಗಾಗಿ 'help' ಕಳುಹಿಸಿ।",
            'ta': "\n\nபட்டியலுக்கு 'help' அனுப்பவும்.",
            'te': "\n\nమెనూ కోసం 'help' పంపండి.",
            'mr': "\n\nमेनूसाठी 'help' पाठवा."
        }
        response_text += footers.get(language, footers['en'])
        
        # Create TwiML response
        twiml = MessagingResponse()
        twiml.message(response_text)
        return str(twiml)
        
    except Exception as e:
        error_msgs = {
            'en': "Sorry, I couldn't process your request. Please try again later.",
            'hi': "क्षमा करें, मैं आपका अनुरोध संसाधित नहीं कर सका। कृपया बाद में पुनः प्रयास करें।",
            'kn': "ಕ್ಷಮಿಸಿ, ನಿಮ್ಮ ವಿನಂತಿಯನ್ನು ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
            'ta': "மன்னிக்கவும், உங்கள் கோரிக்கையை செயல்படுத்த முடியவில்லை. தயவுசெய்து பின்னர் மீண்டும் முயற்சிக்கவும்.",
            'te': "క్షమించండి, మీ అభ్యర్థనను ప్రాసెస్ చేయడంలో విఫలమయ్యాను. దయచేసి తర్వాత మళ్లీ ప్రయత్నించండి.",
            'mr': "क्षमस्व, मी तुमची विनंती प्रक्रिया करू शकलो नाही. कृपया नंतर पुन्हा प्रयत्न करा."
        }
        twiml = MessagingResponse()
        twiml.message(error_msgs.get(language, error_msgs['en']))
        return str(twiml)

@app.route('/api/languages')
def get_languages():
    """Get supported languages"""
    return jsonify({
        'languages': list(LANGUAGE_CODES.keys())
    })

@app.route('/api/history/<user_id>')
def get_conversation_history(user_id):
    """Get conversation history for a user"""
    try:
        conn = sqlite3.connect('krishi_ai.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT question, answer, language, timestamp
            FROM conversations
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (user_id,))
        
        conversations = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'conversations': [
                {
                    'question': conv[0],
                    'answer': conv[1],
                    'language': conv[2],
                    'timestamp': conv[3]
                }
                for conv in conversations
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
