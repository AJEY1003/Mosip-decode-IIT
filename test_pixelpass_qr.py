#!/usr/bin/env python3
"""
Test PixelPass QR decoding with the updated backend
"""

import requests
import json

# Test QR data in PixelPass format
test_qr_data = {
    "t": "ITR_FORM",
    "d": "2026-01-05",
    "v": "1.0",
    "p": {
        "n": "Sample User",
        "pan": "ABCDE1234F",
        "aad": "1234-5678-9012",
        "dob": "1990-01-01",
        "mob": "9876543210",
        "email": "user@example.com"
    },
    "e": {
        "emp": "ABC Technologies Pvt Ltd",
        "tan": "BLRA12345B",
        "ay": "2024-25",
        "fy": "2023-24"
    },
    "f": {
        "gs": "950000",
        "bs": "600000",
        "hra": "240000",
        "oa": "110000",
        "pt": "2400",
        "tds": "75000",
        "ti": "950000"
    },
    "b": {
        "acc": "1234567890",
        "ifsc": "SBIN0000123",
        "bank": "State Bank of India"
    },
    "ver": {
        "conf": 85,
        "enh": True,
        "mosip": True,
        "pixelpass": True,
        "cbor_encoded": True
    }
}

def test_qr_decode():
    """Test the QR decode endpoint with PixelPass data"""
    
    # Convert to JSON string (simulating QR data)
    qr_json_string = json.dumps(test_qr_data)
    
    # Prepare request
    url = "http://localhost:5000/api/qr/decode-itr"
    payload = {
        "qr_image": qr_json_string
    }
    
    print("🚀 Testing PixelPass QR decode...")
    print(f"📄 QR data length: {len(qr_json_string)} characters")
    print(f"📄 QR data preview: {qr_json_string[:200]}...")
    
    try:
        response = requests.post(url, json=payload)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ QR decode successful!")
            print(f"📋 Form sections: {json.dumps(result['form_sections'], indent=2)}")
            print(f"🎯 Confidence: {result['confidence_score']}")
            print(f"📊 Fields extracted: {sum(len(section) for section in result['form_sections'].values())}")
            
            # Check specific fields
            personal_info = result['form_sections'].get('personal_info', {})
            income_details = result['form_sections'].get('income_details', {})
            
            print("\n🔍 Key field verification:")
            print(f"  Name: {personal_info.get('name', 'MISSING')}")
            print(f"  PAN: {personal_info.get('pan', 'MISSING')}")
            print(f"  Gross Salary: {income_details.get('gross_salary', 'MISSING')}")
            print(f"  Basic Salary: {income_details.get('basic_salary', 'MISSING')}")
            print(f"  Employer: {personal_info.get('employer', 'MISSING')}")
            
        else:
            print(f"❌ QR decode failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_qr_decode()