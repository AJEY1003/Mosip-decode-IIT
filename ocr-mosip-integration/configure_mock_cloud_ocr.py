#!/usr/bin/env python3
"""
Configure Mock Cloud OCR for Testing
Sets up mock Google Vision and AWS Textract for demonstration
"""

import os
from dotenv import set_key

def setup_mock_configuration():
    """Setup mock configuration for testing"""
    print("🔧 Setting up Mock Cloud OCR Configuration")
    print("=" * 50)
    
    # Create .env file if it doesn't exist
    env_file = ".env"
    if not os.path.exists(env_file):
        # Copy from example
        with open("config/.env.example", "r") as f:
            content = f.read()
        with open(env_file, "w") as f:
            f.write(content)
        print("📁 Created .env file from template")
    
    # Set mock values for testing
    mock_configs = {
        "GOOGLE_VISION_API_KEY": "mock_google_vision_api_key_for_testing",
        "AWS_ACCESS_KEY_ID": "mock_aws_access_key_for_testing", 
        "AWS_SECRET_ACCESS_KEY": "mock_aws_secret_key_for_testing",
        "AWS_REGION": "us-east-1"
    }
    
    for key, value in mock_configs.items():
        set_key(env_file, key, value)
        print(f"✅ Set {key}")
    
    print("\n🎯 Mock Configuration Complete!")
    print("=" * 50)
    print("⚠️  Note: These are MOCK values for testing only")
    print("📋 To use real cloud OCR:")
    print("1. Run: py setup_cloud_ocr.py")
    print("2. Enter your real API keys")
    print("3. Restart the backend")
    
    print("\n🧪 Testing Mock Configuration...")
    test_mock_config()

def test_mock_config():
    """Test the mock configuration"""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        print(f"Google Vision API Key: {os.getenv('GOOGLE_VISION_API_KEY', 'Not set')[:20]}...")
        print(f"AWS Access Key: {os.getenv('AWS_ACCESS_KEY_ID', 'Not set')[:20]}...")
        print(f"AWS Region: {os.getenv('AWS_REGION', 'Not set')}")
        
        print("\n✅ Mock configuration loaded successfully!")
        print("🔄 Please restart your Flask backend to apply changes")
        
    except Exception as e:
        print(f"❌ Error testing configuration: {str(e)}")

if __name__ == "__main__":
    setup_mock_configuration()