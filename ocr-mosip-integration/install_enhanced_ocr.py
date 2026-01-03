#!/usr/bin/env python3
"""
Enhanced OCR Installation Script
Installs PaddleOCR, EasyOCR, TrOCR, and configures Tesseract
Replaces Google Vision and AWS Textract with offline alternatives
"""

import subprocess
import sys
import os
import platform
import requests
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"🔧 {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ Success")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required for enhanced OCR engines")
        return False
    
    print("✅ Python version is compatible")
    return True

def install_paddle_ocr():
    """Install PaddleOCR"""
    print("\n📦 Installing PaddleOCR...")
    
    # Check if CUDA is available
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        print(f"   CUDA available: {cuda_available}")
    except ImportError:
        cuda_available = False
        print("   CUDA check skipped (torch not installed yet)")
    
    # Install PaddlePaddle
    if cuda_available:
        paddle_cmd = "pip install paddlepaddle-gpu"
        print("   Installing PaddlePaddle with GPU support...")
    else:
        paddle_cmd = "pip install paddlepaddle"
        print("   Installing PaddlePaddle (CPU version)...")
    
    if not run_command(paddle_cmd, "Installing PaddlePaddle"):
        return False
    
    # Install PaddleOCR
    if not run_command("pip install paddleocr", "Installing PaddleOCR"):
        return False
    
    return True

def install_easy_ocr():
    """Install EasyOCR"""
    print("\n📦 Installing EasyOCR...")
    return run_command("pip install easyocr", "Installing EasyOCR")

def install_trocr():
    """Install TrOCR (Transformers + PyTorch)"""
    print("\n📦 Installing TrOCR...")
    
    # Install PyTorch
    if not run_command("pip install torch torchvision", "Installing PyTorch"):
        return False
    
    # Install Transformers
    if not run_command("pip install transformers", "Installing Transformers"):
        return False
    
    return True

def install_image_processing():
    """Install image processing libraries"""
    print("\n📦 Installing image processing libraries...")
    
    libraries = [
        ("opencv-python", "OpenCV"),
        ("Pillow", "PIL/Pillow"),
        ("numpy", "NumPy")
    ]
    
    for lib, name in libraries:
        if not run_command(f"pip install {lib}", f"Installing {name}"):
            return False
    
    return True

def configure_tesseract():
    """Configure Tesseract OCR"""
    print("\n📦 Configuring Tesseract...")
    
    system = platform.system().lower()
    
    if system == "windows":
        # Check common Tesseract installation paths
        tesseract_paths = [
            r"D:\Tesseract\tesseract.exe",
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', 'User'))
        ]
        
        tesseract_found = False
        for path in tesseract_paths:
            if os.path.exists(path):
                print(f"   ✅ Tesseract found at: {path}")
                tesseract_found = True
                break
        
        if not tesseract_found:
            print("   ⚠️  Tesseract not found in common locations")
            print("   📥 Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("   💡 Recommended installation path: D:\\Tesseract\\")
            return False
    
    elif system == "linux":
        if not run_command("sudo apt-get update", "Updating package list"):
            return False
        if not run_command("sudo apt-get install -y tesseract-ocr tesseract-ocr-hin", "Installing Tesseract"):
            return False
    
    elif system == "darwin":  # macOS
        if not run_command("brew install tesseract tesseract-lang", "Installing Tesseract via Homebrew"):
            return False
    
    # Install pytesseract
    if not run_command("pip install pytesseract", "Installing pytesseract"):
        return False
    
    return True

def test_installations():
    """Test all OCR engine installations"""
    print("\n🧪 Testing OCR engine installations...")
    
    tests = []
    
    # Test PaddleOCR
    try:
        from paddleocr import PaddleOCR
        print("   ✅ PaddleOCR import successful")
        tests.append(("PaddleOCR", True))
    except ImportError as e:
        print(f"   ❌ PaddleOCR import failed: {e}")
        tests.append(("PaddleOCR", False))
    
    # Test EasyOCR
    try:
        import easyocr
        print("   ✅ EasyOCR import successful")
        tests.append(("EasyOCR", True))
    except ImportError as e:
        print(f"   ❌ EasyOCR import failed: {e}")
        tests.append(("EasyOCR", False))
    
    # Test TrOCR
    try:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        print("   ✅ TrOCR import successful")
        tests.append(("TrOCR", True))
    except ImportError as e:
        print(f"   ❌ TrOCR import failed: {e}")
        tests.append(("TrOCR", False))
    
    # Test Tesseract
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"   ✅ Tesseract version: {version}")
        tests.append(("Tesseract", True))
    except Exception as e:
        print(f"   ❌ Tesseract test failed: {e}")
        tests.append(("Tesseract", False))
    
    # Summary
    successful = sum(1 for _, success in tests if success)
    total = len(tests)
    
    print(f"\n📊 Installation Summary: {successful}/{total} engines installed successfully")
    
    for engine, success in tests:
        status = "✅" if success else "❌"
        print(f"   {status} {engine}")
    
    return successful == total

def create_test_script():
    """Create a test script for the enhanced OCR"""
    print("\n📝 Creating test script...")
    
    test_script = '''#!/usr/bin/env python3
"""
Test script for Enhanced OCR engines
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.core.enhanced_ocr_processor import EnhancedOCRProcessor

def main():
    print("🔍 Testing Enhanced OCR Processor...")
    
    # Initialize processor
    processor = EnhancedOCRProcessor()
    
    # Get engine status
    status = processor.get_engine_status()
    
    print(f"\\n📊 Engine Status:")
    print(f"Available engines: {status['summary']['available_engines']}/{status['summary']['total_engines']}")
    
    for engine, info in status['engines'].items():
        availability = "✅" if info['available'] else "❌"
        print(f"  {availability} {engine}: {info['description']}")
    
    print(f"\\n🎯 Enhanced OCR Features:")
    print(f"  • Offline processing (no cloud dependencies)")
    print(f"  • Multi-engine accuracy")
    print(f"  • Hindi + English support")
    print(f"  • Intelligent result merging")
    
    if status['summary']['available_engines'] > 0:
        print(f"\\n✅ Enhanced OCR is ready to use!")
        print(f"   Use: processor.process_document('image_path.jpg', 'document_type')")
    else:
        print(f"\\n❌ No OCR engines available. Please run install_enhanced_ocr.py")

if __name__ == "__main__":
    main()
'''
    
    with open("test_enhanced_ocr.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("   ✅ Test script created: test_enhanced_ocr.py")

def main():
    """Main installation process"""
    print("🚀 Enhanced OCR Installation")
    print("=" * 50)
    print("Installing offline OCR engines to replace Google Vision and AWS Textract:")
    print("• PaddleOCR - High-performance multilingual OCR")
    print("• EasyOCR - Deep learning based recognition")
    print("• TrOCR - Transformer-based accuracy")
    print("• Tesseract - Traditional OCR with Hindi support")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install components
    success = True
    
    # Install image processing libraries first
    if not install_image_processing():
        print("❌ Failed to install image processing libraries")
        success = False
    
    # Install OCR engines
    if not install_paddle_ocr():
        print("❌ Failed to install PaddleOCR")
        success = False
    
    if not install_easy_ocr():
        print("❌ Failed to install EasyOCR")
        success = False
    
    if not install_trocr():
        print("❌ Failed to install TrOCR")
        success = False
    
    if not configure_tesseract():
        print("❌ Failed to configure Tesseract")
        success = False
    
    # Test installations
    if success:
        success = test_installations()
    
    # Create test script
    create_test_script()
    
    # Final summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 Enhanced OCR installation completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run: python test_enhanced_ocr.py")
        print("2. Test with: python -c \"from src.core.enhanced_ocr_processor import EnhancedOCRProcessor; print('✅ Import successful')\"")
        print("3. Use the enhanced OCR in your application")
        
        print("\n🔧 Configuration:")
        print("• All engines are offline (no API keys needed)")
        print("• Supports English and Hindi text")
        print("• Automatic engine selection based on confidence")
        print("• Intelligent result merging for better accuracy")
    else:
        print("❌ Enhanced OCR installation had some issues")
        print("Please check the error messages above and retry")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)