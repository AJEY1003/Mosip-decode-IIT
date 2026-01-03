#!/usr/bin/env python3
"""
Install Tesseract OCR on Windows with Hindi Language Support
Downloads and installs Tesseract OCR automatically
"""

import os
import requests
import subprocess
import sys
from pathlib import Path

def download_file(url, filename):
    """Download file with progress"""
    print(f"📥 Downloading {filename}...")
    
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r📊 Progress: {percent:.1f}%", end='', flush=True)
    
    print(f"\n✅ Downloaded: {filename}")

def install_tesseract_windows():
    """Install Tesseract OCR on Windows"""
    print("🔧 Installing Tesseract OCR for Windows")
    print("=" * 50)
    
    # Tesseract installer URL (latest version)
    tesseract_url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
    installer_name = "tesseract-installer.exe"
    
    try:
        # Download Tesseract installer
        download_file(tesseract_url, installer_name)
        
        print("\n🚀 Running Tesseract installer...")
        print("⚠️  Please follow the installer prompts:")
        print("   1. Accept the license")
        print("   2. Choose installation directory (default is fine)")
        print("   3. IMPORTANT: Select 'Additional language data' and check 'Hindi'")
        print("   4. Complete the installation")
        
        # Run installer
        subprocess.run([installer_name], check=True)
        
        print("✅ Tesseract installation completed!")
        
        # Clean up
        os.remove(installer_name)
        print("🧹 Cleaned up installer file")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {str(e)}")
        return False

def install_python_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    
    packages = [
        'pytesseract',
        'pdf2image', 
        'pillow',
        'opencv-python'
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

def verify_installation():
    """Verify Tesseract installation"""
    print("\n🧪 Verifying Tesseract installation...")
    
    try:
        # Try to import and use pytesseract
        import pytesseract
        from PIL import Image
        
        # Common Windows paths for Tesseract
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        ]
        
        tesseract_found = False
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                tesseract_found = True
                print(f"✅ Tesseract found at: {path}")
                break
        
        if not tesseract_found:
            print("⚠️  Tesseract not found in common locations")
            return False
        
        # Check available languages
        try:
            languages = pytesseract.get_languages()
            print(f"📋 Available languages: {', '.join(languages)}")
            
            if 'hin' in languages:
                print("✅ Hindi language support available!")
            else:
                print("⚠️  Hindi language not found. Please reinstall with Hindi language pack.")
            
            if 'eng' in languages:
                print("✅ English language support available!")
            
            return True
            
        except Exception as lang_error:
            print(f"❌ Could not check languages: {str(lang_error)}")
            return False
            
    except ImportError as import_error:
        print(f"❌ Python packages not available: {str(import_error)}")
        return False

def create_test_script():
    """Create a test script for Hindi OCR"""
    test_script = '''
# Test Hindi OCR
from hindi_ocr_processor import HindiOCRProcessor

# Initialize processor
processor = HindiOCRProcessor()

# Check status
status = processor.check_tesseract_languages()
print("Tesseract Status:", status)

# Test with an image (replace with your image path)
# result = processor.process_document("test_hindi_image.jpg", "hindi_english")
# print("OCR Result:", result['raw_text'])
'''
    
    with open("test_hindi_ocr.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("📝 Created test_hindi_ocr.py for testing")

def main():
    """Main installation function"""
    print("🚀 Tesseract OCR Installation for Windows")
    print("=" * 60)
    
    print("This script will:")
    print("1. Download and install Tesseract OCR")
    print("2. Install required Python packages")
    print("3. Verify the installation")
    print("4. Create test scripts")
    
    proceed = input("\n❓ Do you want to proceed? (y/n): ").lower().strip()
    
    if proceed != 'y':
        print("❌ Installation cancelled")
        return
    
    # Step 1: Install Tesseract
    if install_tesseract_windows():
        print("✅ Tesseract installation completed")
    else:
        print("❌ Tesseract installation failed")
        return
    
    # Step 2: Install Python dependencies
    install_python_dependencies()
    
    # Step 3: Verify installation
    if verify_installation():
        print("✅ Installation verification successful")
    else:
        print("⚠️  Installation verification had issues")
    
    # Step 4: Create test script
    create_test_script()
    
    print("\n🎉 Installation Complete!")
    print("=" * 60)
    print("📋 Next Steps:")
    print("1. Restart your command prompt/IDE")
    print("2. Test Hindi OCR: py test_hindi_ocr.py")
    print("3. Use Hindi OCR in your Flask app")
    
    print("\n💡 Usage in your Flask app:")
    print("from hindi_ocr_processor import HindiOCRProcessor")
    print("processor = HindiOCRProcessor()")
    print("result = processor.process_document('hindi_document.pdf')")

if __name__ == "__main__":
    main()