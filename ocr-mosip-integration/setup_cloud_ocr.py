#!/usr/bin/env python3
"""
Setup Cloud OCR Configuration
Configure Google Vision API and AWS Textract for enhanced OCR
"""

import os
from dotenv import load_dotenv, set_key

def setup_google_vision():
    """Setup Google Vision API"""
    print("🔧 Setting up Google Vision API")
    print("=" * 50)
    
    print("📋 Steps to get Google Vision API key:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project or select existing")
    print("3. Enable Vision API")
    print("4. Create credentials (API Key)")
    print("5. Download service account JSON file")
    
    api_key = input("\n🔑 Enter your Google Vision API Key (or press Enter to skip): ").strip()
    
    if api_key:
        # Update .env file
        env_file = ".env"
        if not os.path.exists(env_file):
            # Copy from example
            with open("config/.env.example", "r") as f:
                content = f.read()
            with open(env_file, "w") as f:
                f.write(content)
        
        set_key(env_file, "GOOGLE_VISION_API_KEY", api_key)
        print("✅ Google Vision API key saved to .env")
        
        # Ask for service account file
        service_account = input("📁 Enter path to service account JSON file (or press Enter to skip): ").strip()
        if service_account and os.path.exists(service_account):
            set_key(env_file, "GOOGLE_APPLICATION_CREDENTIALS", service_account)
            print("✅ Service account path saved to .env")
        
        return True
    else:
        print("⏭️  Skipping Google Vision API setup")
        return False

def setup_aws_textract():
    """Setup AWS Textract"""
    print("\n🔧 Setting up AWS Textract")
    print("=" * 50)
    
    print("📋 Steps to get AWS credentials:")
    print("1. Go to: https://aws.amazon.com/console/")
    print("2. Create IAM user with Textract permissions")
    print("3. Generate access key and secret key")
    
    access_key = input("\n🔑 Enter your AWS Access Key ID (or press Enter to skip): ").strip()
    
    if access_key:
        secret_key = input("🔐 Enter your AWS Secret Access Key: ").strip()
        region = input("🌍 Enter AWS Region (default: us-east-1): ").strip() or "us-east-1"
        
        # Update .env file
        env_file = ".env"
        if not os.path.exists(env_file):
            # Copy from example
            with open("config/.env.example", "r") as f:
                content = f.read()
            with open(env_file, "w") as f:
                f.write(content)
        
        set_key(env_file, "AWS_ACCESS_KEY_ID", access_key)
        set_key(env_file, "AWS_SECRET_ACCESS_KEY", secret_key)
        set_key(env_file, "AWS_REGION", region)
        
        print("✅ AWS credentials saved to .env")
        return True
    else:
        print("⏭️  Skipping AWS Textract setup")
        return False

def test_configuration():
    """Test the OCR configuration"""
    print("\n🧪 Testing OCR Configuration")
    print("=" * 50)
    
    try:
        from enhanced_ocr_processor import EnhancedOCRProcessor
        
        processor = EnhancedOCRProcessor()
        status = processor.get_engine_status()
        
        print("📊 OCR Engine Status:")
        print(f"Enhanced OCR Available: {status['enhanced_ocr_available']}")
        
        print("\n🔍 Available Engines:")
        for engine, info in status['engines'].items():
            status_icon = "✅" if info['available'] else "❌"
            print(f"  {status_icon} {engine}: {info['description']} ({info['type']})")
        
        if status['enhanced_ocr_available']:
            print("\n🎉 Enhanced OCR is ready!")
        else:
            print("\n⚠️  Enhanced OCR not fully configured")
            
        return status
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return None

def main():
    """Main setup function"""
    print("🚀 Cloud OCR Configuration Setup")
    print("=" * 60)
    
    print("This script will help you configure cloud OCR engines:")
    print("• Google Vision API (High accuracy cloud OCR)")
    print("• AWS Textract (Document analysis)")
    print("\nNote: These are optional - Tesseract and EasyOCR work offline")
    
    # Setup Google Vision
    google_configured = setup_google_vision()
    
    # Setup AWS Textract
    aws_configured = setup_aws_textract()
    
    # Test configuration
    if google_configured or aws_configured:
        print("\n🔄 Restarting backend to load new configuration...")
        print("Please restart your Flask backend: py app.py")
    
    test_configuration()
    
    print("\n🎯 Setup Complete!")
    print("=" * 60)
    
    if google_configured:
        print("✅ Google Vision API configured")
    if aws_configured:
        print("✅ AWS Textract configured")
    
    print("\n📋 Next Steps:")
    print("1. Restart your Flask backend")
    print("2. Test enhanced OCR: POST /api/enhanced-ocr/extract")
    print("3. Check engine status: GET /api/ocr/engine-status")

if __name__ == "__main__":
    main()