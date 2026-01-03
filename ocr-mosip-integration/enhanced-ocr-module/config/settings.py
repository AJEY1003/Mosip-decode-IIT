import os
from typing import Dict, Any

# Configuration settings for OCR Verification Engine
class Config:
    # OCR API Keys
    GOOGLE_VISION_API_KEY = os.getenv('GOOGLE_VISION_API_KEY', '')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # Database Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/ocr_db')
    POSTGRES_URI = os.getenv('POSTGRES_URI', 'postgresql://user:password@localhost:5432/ocr_db')
    
    # Processing Settings
    OCR_TIMEOUT = int(os.getenv('OCR_TIMEOUT', '30'))
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10MB
    TEMP_DIR = os.getenv('TEMP_DIR', './temp')
    
    # AI Model Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    
    # Security Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'pdf'}
    
    # Confidence thresholds
    AUTO_APPROVE_THRESHOLD = float(os.getenv('AUTO_APPROVE_THRESHOLD', '0.99'))
    AI_REVIEW_THRESHOLD = float(os.getenv('AI_REVIEW_THRESHOLD', '0.95'))
    MANUAL_REVIEW_THRESHOLD = float(os.getenv('MANUAL_REVIEW_THRESHOLD', '0.95'))

# Validation patterns
VALIDATION_PATTERNS = {
    'pan': r'^[A-Z]{5}[0-9]{4}[A-Z]$',
    'aadhaar': r'^\d{4}\s?\d{4}\s?\d{4}$',
    'passport': r'^[A-Z]{1}[0-9]{7}$',
    'date': r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD format
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone': r'^\+?[1-9]\d{1,14}$'
}

# Field extraction keywords
FIELD_KEYWORDS = {
    'name': ['name', 'full name', 'surname', 'given name', 'first name', 'last name'],
    'dob': ['date of birth', 'birth date', 'dob', 'birth'],
    'id_number': ['id number', 'identification', 'id no', 'id no.', 'number'],
    'address': ['address', 'permanent address', 'present address', 'residence'],
    'document_type': ['document type', 'type', 'document']
}