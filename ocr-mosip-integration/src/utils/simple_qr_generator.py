#!/usr/bin/env python3
"""
Simple QR Code Generator for Human-Readable OCR Data
Creates QR codes that show readable text when scanned with Google scanner

Usage:
    py -m simple_qr_generator
"""

try:
    import qrcode
except ImportError:
    print("❌ qrcode library not found. Install with: pip install qrcode[pil]")
    exit(1)

import json
import base64
from io import BytesIO
from datetime import datetime
import uuid
import sys
import os

def generate_simple_text_qr(ocr_data):
    """
    Generate a simple, human-readable QR code from OCR data
    
    Args:
        ocr_data: Dictionary with extracted OCR data
        
    Returns:
        dict: QR generation result with readable content
    """
    try:
        # Create simple, readable text format
        text_lines = []
        text_lines.append("=== DOCUMENT INFORMATION ===")
        text_lines.append("")
        
        # Add each field in readable format
        field_mapping = {
            'name': 'Name',
            'date_of_birth': 'Date of Birth',
            'nationality': 'Nationality',
            'passport_number': 'Passport Number',
            'id_number': 'ID Number',
            'aadhaar_number': 'Aadhaar Number',
            'pan_number': 'PAN Number',
            'phone': 'Phone',
            'email': 'Email',
            'address': 'Address',
            'gender': 'Gender',
            'document_type': 'Document Type'
        }
        
        for key, label in field_mapping.items():
            if key in ocr_data and ocr_data[key]:
                text_lines.append(f"{label}: {ocr_data[key]}")
        
        text_lines.append("")
        text_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Join all lines
        qr_text = "\n".join(text_lines)
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,  # Start with smallest version
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_text)
        qr.make(fit=True)
        
        # Generate QR image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Save as file
        filename = f"simple_qr_{uuid.uuid4().hex[:8]}.png"
        qr_image.save(filename)
        
        return {
            'success': True,
            'qr_id': str(uuid.uuid4()),
            'qr_text': qr_text,
            'qr_image_file': filename,
            'qr_image_base64': f"data:image/png;base64,{qr_image_base64}",
            'encoding': 'Plain Text',
            'readable_by': 'Any QR scanner (Google, iPhone, etc.)',
            'note': 'This QR code shows readable text when scanned',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'qr_id': str(uuid.uuid4())
        }

def generate_json_qr(ocr_data):
    """
    Generate QR code with JSON data (for apps that can parse JSON)
    
    Args:
        ocr_data: Dictionary with extracted OCR data
        
    Returns:
        dict: QR generation result with JSON content
    """
    try:
        # Create clean JSON structure
        clean_data = {
            'document_info': ocr_data,
            'generated_at': datetime.now().isoformat(),
            'format': 'OCR_EXTRACTED_DATA'
        }
        
        qr_json = json.dumps(clean_data, indent=2)
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_json)
        qr.make(fit=True)
        
        # Generate QR image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Save as file
        filename = f"json_qr_{uuid.uuid4().hex[:8]}.png"
        qr_image.save(filename)
        
        return {
            'success': True,
            'qr_id': str(uuid.uuid4()),
            'qr_data': qr_json,
            'qr_image_file': filename,
            'qr_image_base64': f"data:image/png;base64,{qr_image_base64}",
            'encoding': 'JSON',
            'readable_by': 'Apps that can parse JSON',
            'note': 'This QR code contains structured JSON data',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'qr_id': str(uuid.uuid4())
        }

def test_simple_qr():
    """Test the simple QR generation with sample data"""
    sample_data = {
        'name': 'John Smith',
        'date_of_birth': '25/12/1988',
        'nationality': 'United Kingdom',
        'passport_number': 'UK123456789',
        'email': 'john.smith@example.com',
        'phone': '+44-20-7946-0958',
        'address': '123 Baker Street, London, UK',
        'document_type': 'Passport'
    }
    
    print("🔍 Testing Simple QR Code Generation")
    print("=" * 50)
    
    # Generate simple text QR
    text_result = generate_simple_text_qr(sample_data)
    if text_result['success']:
        print("✅ Simple Text QR Generated:")
        print(f"   File: {text_result['qr_image_file']}")
        print(f"   Readable by: {text_result['readable_by']}")
        print("\n📱 QR Content Preview:")
        print(text_result['qr_text'])
    else:
        print(f"❌ Text QR Failed: {text_result['error']}")
    
    print("\n" + "=" * 50)
    
    # Generate JSON QR
    json_result = generate_json_qr(sample_data)
    if json_result['success']:
        print("✅ JSON QR Generated:")
        print(f"   File: {json_result['qr_image_file']}")
        print(f"   Readable by: {json_result['readable_by']}")
    else:
        print(f"❌ JSON QR Failed: {json_result['error']}")
    
    print("\n🎯 Recommendations:")
    print("1. Use Simple Text QR for human scanning (Google scanner)")
    print("2. Use JSON QR for app-based verification")
    print("3. Use Verifiable Credential QR for MOSIP/Inji systems")
    
    print("\n📋 Usage Instructions:")
    print("1. Run: py -m simple_qr_generator")
    print("2. Scan generated QR codes with Google scanner")
    print("3. Compare with your current PixelPass QR codes")

def main():
    """Main function for module execution"""
    print("🚀 Simple QR Generator - Python Module")
    print("=" * 50)
    
    # Check if running as module
    if __name__ == "__main__":
        print("✅ Running as Python module (py -m simple_qr_generator)")
    else:
        print("ℹ️  Imported as module")
    
    # Check dependencies
    try:
        import qrcode
        print("✅ qrcode library available")
    except ImportError:
        print("❌ qrcode library missing. Install with: pip install qrcode[pil]")
        return
    
    try:
        from PIL import Image
        print("✅ PIL (Pillow) library available")
    except ImportError:
        print("❌ PIL library missing. Install with: pip install Pillow")
        return
    
    print("\n🔧 Starting QR generation test...")
    test_simple_qr()
    
    print("\n✨ Test completed! Check the generated PNG files.")

if __name__ == "__main__":
    main()