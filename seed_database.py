"""
Database Seeding Script for KrishiAI

This script populates the database with initial data for:
- Crop guidance
- Pest control information
- Weather tips
- Sample user farms and crop calendar entries
"""

import sqlite3
from datetime import datetime, timedelta
import os

def connect_db():
    """Connect to the SQLite database"""
    return sqlite3.connect('krishi_ai.db')

def seed_crop_guidance():
    """Seed the crop_guidance table with sample data"""
    crops = [
        {
            'crop_name': 'Rice',
            'season': 'Kharif',
            'location': 'Punjab',
            'soil_type': 'Clay loam',
            'planting_time': 'June-July',
            'harvesting_time': 'October-November',
            'water_requirements': 'Requires standing water, 5-7 cm depth during early stages',
            'fertilizer_needs': '120:60:40 kg NPK per hectare',
            'common_varieties': 'Pusa Basmati, PR-126, PAU 201',
            'special_notes': 'Sensitive to water stress during flowering and grain filling stages'
        },
        {
            'crop_name': 'Wheat',
            'season': 'Rabi',
            'location': 'Uttar Pradesh',
            'soil_type': 'Sandy loam',
            'planting_time': 'November-December',
            'harvesting_time': 'March-April',
            'water_requirements': '4-6 irrigations, critical stages: crown root, tillering, flowering',
            'fertilizer_needs': '150:60:40 kg NPK per hectare',
            'common_varieties': 'HD 2967, PBW 550, DBW 17',
            'special_notes': 'Avoid waterlogging, requires good drainage'
        },
        {
            'crop_name': 'Cotton',
            'season': 'Kharif',
            'location': 'Maharashtra',
            'soil_type': 'Black cotton soil',
            'planting_time': 'June-July',
            'harvesting_time': 'December-March',
            'water_requirements': '6-8 irrigations, critical stages: flowering and boll formation',
            'fertilizer_needs': '100:50:50 kg NPK per hectare',
            'common_varieties': 'Bollgard II, RCH 2, Bunny',
            'special_notes': 'Requires warm climate and well-drained soil'
        }
    ]
    
    conn = connect_db()
    cursor = conn.cursor()
    
    for crop in crops:
        cursor.execute('''
            INSERT OR REPLACE INTO crop_guidance 
            (crop_name, season, location, soil_type, planting_time, harvesting_time,
             water_requirements, fertilizer_needs, common_varieties, special_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            crop['crop_name'], crop['season'], crop['location'], crop['soil_type'],
            crop['planting_time'], crop['harvesting_time'], crop['water_requirements'],
            crop['fertilizer_needs'], crop['common_varieties'], crop['special_notes']
        ))
    
    conn.commit()
    conn.close()
    print("✓ Seeded crop guidance data")

def seed_pest_control():
    """Seed the pest_control table with sample data"""
    pests = [
        {
            'pest_name': 'Brown Plant Hopper',
            'affected_crops': 'Rice',
            'symptoms': 'Yellowing and browning of leaves, hopper burn',
            'organic_control': 'Use neem oil spray, encourage natural predators like spiders',
            'chemical_control': 'Imidacloprid 17.8 SL @ 0.3 ml/l or Buprofezin 25 SC @ 1.0 ml/l',
            'prevention': 'Avoid excessive nitrogen, maintain proper water level',
            'severity': 'High',
            'image_url': 'https://example.com/bph.jpg'
        },
        {
            'pest_name': 'Bollworm',
            'affected_crops': 'Cotton',
            'symptoms': 'Holes in bolls, damaged flowers',
            'organic_control': 'Use neem seed kernel extract, pheromone traps',
            'chemical_control': 'Emamectin benzoate 5 SG @ 0.4 g/l or Spinosad 45 SC @ 0.3 ml/l',
            'prevention': 'Deep summer plowing, crop rotation',
            'severity': 'High',
            'image_url': 'https://example.com/bollworm.jpg'
        },
        {
            'pest_name': 'Aphids',
            'affected_crops': 'Wheat, Mustard, Vegetables',
            'symptoms': 'Curling of leaves, sticky honeydew on leaves',
            'organic_control': 'Spray neem oil or soap solution',
            'chemical_control': 'Imidacloprid 17.8 SL @ 0.3 ml/l or Thiamethoxam 25 WG @ 0.2 g/l',
            'prevention': 'Remove weeds, use yellow sticky traps',
            'severity': 'Medium',
            'image_url': 'https://example.com/aphids.jpg'
        }
    ]
    
    conn = connect_db()
    cursor = conn.cursor()
    
    for pest in pests:
        cursor.execute('''
            INSERT OR REPLACE INTO pest_control 
            (pest_name, affected_crops, symptoms, organic_control, 
             chemical_control, prevention, severity, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pest['pest_name'], pest['affected_crops'], pest['symptoms'],
            pest['organic_control'], pest['chemical_control'],
            pest['prevention'], pest['severity'], pest['image_url']
        ))
    
    conn.commit()
    conn.close()
    print("✓ Seeded pest control data")

def seed_weather_tips():
    """Seed the weather_tips table with sample data"""
    weather_tips = [
        {
            'weather_condition': 'Drought',
            'crop_impact': 'Reduced crop yield, wilting, stunted growth',
            'recommended_actions': 'Use drought-resistant varieties, mulching, drip irrigation',
            'protection_measures': 'Water conservation techniques, shade nets',
            'timing_considerations': 'Avoid transplanting during peak drought'
        },
        {
            'weather_condition': 'Heavy Rainfall',
            'crop_impact': 'Waterlogging, nutrient leaching, disease spread',
            'recommended_actions': 'Improve drainage, apply foliar nutrients',
            'protection_measures': 'Raised beds, proper field leveling',
            'timing_considerations': 'Delay fertilizer application until after heavy rain'
        },
        {
            'weather_condition': 'Heat Wave',
            'crop_impact': 'Flower drop, reduced pollination, sunburn',
            'recommended_actions': 'Increase irrigation frequency, use shade nets',
            'protection_measures': 'Mulching, anti-transpirants',
            'timing_considerations': 'Irrigate in early morning or late evening'
        }
    ]
    
    conn = connect_db()
    cursor = conn.cursor()
    
    for tip in weather_tips:
        cursor.execute('''
            INSERT OR REPLACE INTO weather_tips 
            (weather_condition, crop_impact, recommended_actions, 
             protection_measures, timing_considerations)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            tip['weather_condition'], tip['crop_impact'],
            tip['recommended_actions'], tip['protection_measures'],
            tip['timing_considerations']
        ))
    
    conn.commit()
    conn.close()
    print("✓ Seeded weather tips data")

def seed_sample_user_data():
    """Seed sample user farm and crop calendar data"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Add a sample user if not exists
    cursor.execute("SELECT id FROM users WHERE username = 'demo'")
    user = cursor.fetchone()
    
    if not user:
        cursor.execute('''
            INSERT INTO users 
            (username, email, password_hash, full_name, phone, location, farm_size, crops)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'demo', 'demo@example.com', 
            'pbkdf2:sha256:260000$...',  # This should be a properly hashed password in production
            'Demo User', '9876543210', 'Punjab', '5 acres', 'Wheat, Rice'
        ))
        user_id = cursor.lastrowid
    else:
        user_id = user[0]
    
    # Add sample farm
    cursor.execute('''
        INSERT OR REPLACE INTO user_farms 
        (user_id, farm_name, location, size, soil_type, current_crops, irrigation_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, 'Main Farm', 'Ludhiana', '3.0', 'Sandy loam', 'Wheat', 'Drip irrigation'
    ))
    
    # Add sample crop calendar entries
    today = datetime.now().date()
    
    cursor.execute('''
        INSERT OR REPLACE INTO crop_calendar 
        (user_id, crop_name, planting_date, expected_harvest_date, status, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        user_id, 'Wheat', 
        (today - timedelta(days=30)).isoformat(),  # Planted 30 days ago
        (today + timedelta(days=90)).isoformat(),  # Expected in 90 days
        'Growing',
        'HD 2967 variety, good growth so far'
    ))
    
    cursor.execute('''
        INSERT OR REPLACE INTO crop_calendar 
        (user_id, crop_name, planting_date, status, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        user_id, 'Rice', 
        (today + timedelta(days=30)).isoformat(),  # Planned in 30 days
        'Planned',
        'Basmati variety, prepare nursery in 2 weeks'
    ))
    
    conn.commit()
    conn.close()
    print("✓ Seeded sample user data")

def main():
    print("Starting database seeding...")
    
    # Create database tables if they don't exist
    from app import KrishiAI
    krishiai = KrishiAI()
    
    # Seed data
    seed_crop_guidance()
    seed_pest_control()
    seed_weather_tips()
    seed_sample_user_data()
    
    print("\n✓ Database seeding completed successfully!")

if __name__ == "__main__":
    main()
