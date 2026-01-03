#!/usr/bin/env py
"""
Render PixelPass QR Data to Image
Converts the encoded QR data from PixelPass into a visual QR code image
"""

import qrcode
import json
from PIL import Image
import base64
from io import BytesIO

def render_qr_from_pixelpass_data():
    """Convert PixelPass QR data to visual QR code image"""
    print("🖼️  Rendering PixelPass QR Data to Image")
    print("=" * 50)
    
    # Load the PixelPass QR data
    try:
        with open('real_qr_code.json', 'r') as f:
            qr_data_json = json.load(f)
    except FileNotFoundError:
        print("❌ real_qr_code.json not found. Run: node generate_real_qr.js")
        return
    
    # Get the QR data string from PixelPass
    qr_data = qr_data_json['qr_data']
    
    print(f"📱 QR Data Info:")
    print(f"  Subject: {qr_data_json['credential_subject']}")
    print(f"  Encoding: {qr_data_json['encoding']}")
    print(f"  Library: {qr_data_json['library']}")
    print(f"  Data Length: {len(qr_data)} characters")
    
    # Create QR code image from the PixelPass data
    print(f"\n🎨 Creating QR code image...")
    
    # Configure QR code settings for better compatibility
    qr = qrcode.QRCode(
        version=None,  # Auto-determine version based on data
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Low error correction for more data
        box_size=10,   # Size of each box in pixels
        border=4,      # Border size in boxes
    )
    
    # Add the PixelPass data to QR code
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create the QR code image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save the QR code image
    qr_filename = "pixelpass_qr_code.png"
    qr_image.save(qr_filename)
    
    print(f"✅ QR code image saved as: {qr_filename}")
    print(f"📏 Image size: {qr_image.size}")
    
    # Also create a base64 version for web use
    buffer = BytesIO()
    qr_image.save(buffer, format='PNG')
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Save complete result with image data
    result = {
        "success": True,
        "qr_image_file": qr_filename,
        "qr_image_base64": f"data:image/png;base64,{qr_image_base64}",
        "qr_data": qr_data,
        "encoding": qr_data_json['encoding'],
        "library": qr_data_json['library'],
        "credential_subject": qr_data_json['credential_subject'],
        "image_size": qr_image.size,
        "instructions": {
            "view_image": f"Open {qr_filename} to see the QR code",
            "scan_with_phone": "Use any QR scanner app to read the code",
            "verify_with_inji": "Upload to Inji Verify portal for credential verification",
            "test_with_api": "Use the base64 data with /api/inji/verify-qr endpoint"
        }
    }
    
    with open('pixelpass_qr_image.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"💾 Complete result saved to: pixelpass_qr_image.json")
    
    return qr_filename, qr_image_base64

def test_qr_image_verification():
    """Test the generated QR image with our verification API"""
    print(f"\n🧪 Testing QR Image Verification...")
    
    try:
        with open('pixelpass_qr_image.json', 'r') as f:
            image_data = json.load(f)
    except FileNotFoundError:
        print("❌ pixelpass_qr_image.json not found")
        return
    
    import requests
    
    # Test with Flask API using base64 image
    test_payload = {
        "qr_image": image_data['qr_image_base64'],
        "verification_method": "opencv"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/inji/verify-qr",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ QR Image Verification Successful!")
            print(f"  Verification ID: {result.get('verification_id')}")
            print(f"  QR Scan Success: {result.get('qr_scan_result', {}).get('success')}")
            
        else:
            print(f"❌ Verification Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Flask app not running. Start with: py app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def create_high_quality_qr():
    """Create a high-quality QR code for printing/display"""
    print(f"\n🎯 Creating High-Quality QR Code...")
    
    try:
        with open('real_qr_code.json', 'r') as f:
            qr_data_json = json.load(f)
    except FileNotFoundError:
        print("❌ real_qr_code.json not found")
        return
    
    qr_data = qr_data_json['qr_data']
    
    # Create high-quality QR code
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction
        box_size=20,   # Larger boxes for better quality
        border=6,      # Larger border
    )
    
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create high-quality image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save high-quality version
    hq_filename = "pixelpass_qr_high_quality.png"
    qr_image.save(hq_filename, quality=100, optimize=False)
    
    print(f"✅ High-quality QR code saved as: {hq_filename}")
    print(f"📏 Image size: {qr_image.size}")
    
    return hq_filename

if __name__ == "__main__":
    # Render QR image from PixelPass data
    qr_file, qr_base64 = render_qr_from_pixelpass_data()
    
    # Test the generated image
    test_qr_image_verification()
    
    # Create high-quality version
    hq_file = create_high_quality_qr()
    
    print(f"\n🎉 QR Code Images Generated Successfully!")
    print(f"📁 Files created:")
    print(f"  • {qr_file} (Standard quality)")
    print(f"  • {hq_file} (High quality for printing)")
    print(f"  • pixelpass_qr_image.json (Complete data)")
    
    print(f"\n📱 Next Steps:")
    print(f"1. Open {qr_file} to see your QR code")
    print(f"2. Scan with any QR reader app")
    print(f"3. Upload to Inji Verify portal")
    print(f"4. Use {hq_file} for printing or display")