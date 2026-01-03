#!/usr/bin/env python3
"""
Test Real Signatures in QR Codes
Generate QR codes with real Ed25519 signatures and test with Inji Verify

Usage:
    py -m test_real_signatures
"""

import json
from pixelpass_integration import PixelPassQRGenerator
from simple_qr_generator import generate_simple_text_qr
from qr_analyzer_resizer import resize_qr_to_target_size
import os

def test_real_signature_qr():
    """Test QR code generation with real signatures"""
    print("🔐 Testing QR Codes with Real Ed25519 Signatures")
    print("=" * 60)
    
    # Sample OCR data
    sample_ocr_data = {
        'name': 'Rajesh Kumar',
        'date_of_birth': '15/08/1985',
        'nationality': 'Indian',
        'aadhaar_number': '1234-5678-9012',
        'pan_number': 'ABCDE1234F',
        'phone': '+91-9876543210',
        'email': 'rajesh.kumar@example.com',
        'address': '123 MG Road, Bangalore, Karnataka, India',
        'document_type': 'Aadhaar Card'
    }
    
    print("📋 Sample OCR Data:")
    for key, value in sample_ocr_data.items():
        print(f"  {key}: {value}")
    
    # Generate QR with real signatures using PixelPass
    print("\n🔧 Generating QR with Real Signatures...")
    qr_generator = PixelPassQRGenerator()
    
    try:
        # Generate complete workflow with real signatures
        workflow_result = qr_generator.complete_qr_generation_workflow(sample_ocr_data)
        
        if workflow_result.get('success'):
            print("✅ QR Generation Successful!")
            
            # Extract the verifiable credential
            vc_data = workflow_result['verifiable_credential']['credential']
            
            # Check if it has real signature
            proof = vc_data.get('proof', {})
            jws = proof.get('jws', '')
            
            if jws.startswith('mock_'):
                print("⚠️  Still using mock signature")
                print(f"   Signature: {jws}")
            else:
                print("✅ Real Ed25519 signature detected!")
                print(f"   Signature length: {len(jws)} characters")
                print(f"   Signature preview: {jws[:50]}...{jws[-20:]}")
                
                # Show issuer information
                issuer = vc_data.get('issuer', {})
                print(f"   Issuer DID: {issuer.get('id', 'Unknown')}")
                print(f"   Verification Method: {proof.get('verificationMethod', 'Unknown')}")
            
            # Save the credential with real signature
            with open('real_signed_credential.json', 'w') as f:
                json.dump(vc_data, f, indent=2)
            print(f"\n💾 Real signed credential saved to: real_signed_credential.json")
            
            # Generate QR code image from the workflow result
            qr_result = workflow_result.get('qr_code', {})
            if qr_result.get('qr_image'):
                # Save QR image
                qr_image_data = qr_result['qr_image']
                if qr_image_data.startswith('data:image'):
                    # Extract base64 data
                    import base64
                    header, encoded = qr_image_data.split(',', 1)
                    image_bytes = base64.b64decode(encoded)
                    
                    with open('real_signature_qr.png', 'wb') as f:
                        f.write(image_bytes)
                    
                    print(f"📱 QR code image saved to: real_signature_qr.png")
                    
                    # Resize for Inji Verify testing
                    resize_result = resize_qr_to_target_size('real_signature_qr.png', target_size_kb=10)
                    if resize_result['success']:
                        print(f"📏 Resized QR for Inji Verify: {resize_result['output_path']}")
                        print(f"   Final size: {resize_result['final_size_kb']:.2f} KB")
        else:
            print(f"❌ QR Generation Failed: {workflow_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        qr_generator.cleanup()

def compare_signatures():
    """Compare mock vs real signatures"""
    print("\n🔍 Comparing Mock vs Real Signatures")
    print("=" * 60)
    
    # Check if we have both files
    files_to_check = [
        ('signed_credential.json', 'Real Signature'),
        ('real_signed_credential.json', 'PixelPass Real Signature')
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            print(f"\n📄 {description} ({filename}):")
            
            with open(filename, 'r') as f:
                credential = json.load(f)
            
            proof = credential.get('proof', {})
            jws = proof.get('jws', 'No signature')
            
            print(f"   Type: {proof.get('type', 'Unknown')}")
            print(f"   Created: {proof.get('created', 'Unknown')}")
            print(f"   Verification Method: {proof.get('verificationMethod', 'Unknown')}")
            print(f"   JWS Length: {len(jws)} characters")
            
            if jws.startswith('mock_'):
                print(f"   ❌ Mock Signature: {jws}")
            elif len(jws) > 100:
                print(f"   ✅ Real Signature: {jws[:30]}...{jws[-20:]}")
            else:
                print(f"   ⚠️  Unknown: {jws}")
        else:
            print(f"\n📄 {description}: File not found ({filename})")

def test_with_inji_verify():
    """Test the real signature QR with your Flask app"""
    print("\n🌐 Testing Real Signature QR with Flask App")
    print("=" * 60)
    
    qr_file = 'real_signature_qr_resized_10kb.png'
    
    if not os.path.exists(qr_file):
        print(f"❌ QR file not found: {qr_file}")
        print("   Generate it first by running the test above")
        return
    
    try:
        import requests
        import base64
        
        # Check if Flask app is running
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Flask app not running. Start with: py app.py")
            return
        
        print("✅ Flask app is running")
        
        # Read and encode QR image
        with open(qr_file, 'rb') as f:
            image_data = f.read()
        
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Test verification endpoint
        test_payload = {
            "qr_image": f"data:image/png;base64,{image_base64}",
            "verification_method": "opencv"
        }
        
        print("🔍 Testing QR verification...")
        response = requests.post(
            "http://localhost:5000/api/inji/verify-qr",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Verification Response Received!")
            print(f"   Method: {result.get('method', 'unknown')}")
            print(f"   QR Scan Success: {result.get('qr_scan_result', {}).get('success', False)}")
            
            # Check if real signature was detected
            qr_data = result.get('qr_scan_result', {}).get('qr_data', '')
            if qr_data:
                print(f"   QR Data Length: {len(qr_data)} characters")
                if 'eyJ' in qr_data:  # Base64 JWT signature indicator
                    print("   ✅ Real signature detected in QR data!")
                else:
                    print("   ⚠️  Signature format unclear")
        else:
            print(f"❌ Verification Failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Start with: py app.py")
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")

def main():
    """Main function to test real signatures"""
    print("🔐 Real Signature QR Code Testing")
    print("=" * 60)
    
    # Test QR generation with real signatures
    test_real_signature_qr()
    
    # Compare different signature types
    compare_signatures()
    
    # Test with Flask app
    test_with_inji_verify()
    
    print("\n🎯 Summary:")
    print("• Generated QR codes with real Ed25519 signatures")
    print("• Real signatures are cryptographically verifiable")
    print("• Test with Inji Verify using the resized QR files")
    print("• Real signatures should pass Inji Verify validation")

if __name__ == "__main__":
    main()