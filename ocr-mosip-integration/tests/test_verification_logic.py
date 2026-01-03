#!/usr/bin/env python3
"""
Test Verification Logic - Understanding How Inji Verify Validates Credentials
Shows exactly how credentials are validated and why they might be marked as invalid

Usage:
    py -m test_verification_logic
"""

import json
import base64
import uuid
from datetime import datetime, timedelta
import requests
import os

def analyze_verification_process():
    """Analyze how Inji Verify determines credential validity"""
    print("🔍 Understanding Inji Verify Credential Validation")
    print("=" * 70)
    
    print("\n📋 How Inji Verify Validates Credentials:")
    print("1. 🔓 QR Code Decoding - Extract CBOR/JSON data from QR")
    print("2. 📝 Schema Validation - Check if VC follows W3C standard")
    print("3. 🔐 Signature Verification - Verify cryptographic signature")
    print("4. 👤 Issuer Trust - Check if issuer is in trusted registry")
    print("5. ⏰ Expiry Check - Verify credential hasn't expired")
    print("6. 🚫 Revocation Check - Check if credential is revoked")
    print("7. 📊 Data Integrity - Validate all required fields")

def test_credential_validation_scenarios():
    """Test different credential validation scenarios"""
    print("\n🧪 Testing Different Credential Scenarios")
    print("=" * 70)
    
    # Scenario 1: Valid Credential
    valid_credential = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://www.w3.org/2018/credentials/examples/v1"
        ],
        "id": f"urn:uuid:{uuid.uuid4()}",
        "type": ["VerifiableCredential", "IdentityCredential"],
        "issuer": {
            "id": "did:inji:issuer:government-of-india",
            "name": "Government of India - Digital Identity Authority"
        },
        "issuanceDate": datetime.now().isoformat() + "Z",
        "expirationDate": (datetime.now() + timedelta(days=365)).isoformat() + "Z",
        "credentialSubject": {
            "id": f"did:inji:citizen:{uuid.uuid4()}",
            "name": "John Smith",
            "dateOfBirth": "1988-12-25",
            "nationality": "Indian",
            "aadhaarNumber": "1234-5678-9012"
        },
        "proof": {
            "type": "Ed25519Signature2018",
            "created": datetime.now().isoformat() + "Z",
            "proofPurpose": "assertionMethod",
            "verificationMethod": "did:inji:issuer:government-of-india#key-1",
            "jws": f"mock_signature_{uuid.uuid4().hex[:16]}"
        }
    }
    
    # Scenario 2: Expired Credential
    expired_credential = valid_credential.copy()
    expired_credential["expirationDate"] = (datetime.now() - timedelta(days=30)).isoformat() + "Z"
    expired_credential["id"] = f"urn:uuid:{uuid.uuid4()}"
    
    # Scenario 3: Invalid Issuer
    invalid_issuer_credential = valid_credential.copy()
    invalid_issuer_credential["issuer"] = {
        "id": "did:fake:issuer:untrusted",
        "name": "Fake Issuer"
    }
    invalid_issuer_credential["id"] = f"urn:uuid:{uuid.uuid4()}"
    
    # Scenario 4: Missing Required Fields
    incomplete_credential = valid_credential.copy()
    del incomplete_credential["credentialSubject"]["name"]
    del incomplete_credential["proof"]
    incomplete_credential["id"] = f"urn:uuid:{uuid.uuid4()}"
    
    scenarios = [
        ("✅ Valid Credential", valid_credential, True),
        ("⏰ Expired Credential", expired_credential, False),
        ("🚫 Untrusted Issuer", invalid_issuer_credential, False),
        ("📝 Incomplete Data", incomplete_credential, False)
    ]
    
    for scenario_name, credential, expected_valid in scenarios:
        print(f"\n{scenario_name}:")
        validation_result = validate_credential_mock(credential)
        
        print(f"  Expected Valid: {expected_valid}")
        print(f"  Actual Valid: {validation_result['credential_valid']}")
        print(f"  Issues Found: {len(validation_result['validation_issues'])}")
        
        if validation_result['validation_issues']:
            for issue in validation_result['validation_issues']:
                print(f"    ❌ {issue}")
        
        if validation_result['credential_valid'] == expected_valid:
            print("  ✅ Validation result matches expectation")
        else:
            print("  ❌ Validation result differs from expectation")

def validate_credential_mock(credential):
    """
    Mock credential validation logic similar to Inji Verify
    Shows exactly how credentials are validated
    """
    validation_issues = []
    
    # 1. Schema Validation
    required_fields = ["@context", "type", "issuer", "credentialSubject"]
    for field in required_fields:
        if field not in credential:
            validation_issues.append(f"Missing required field: {field}")
    
    # 2. Expiry Check
    if "expirationDate" in credential:
        try:
            expiry_date = datetime.fromisoformat(credential["expirationDate"].replace('Z', '+00:00'))
            if datetime.now(expiry_date.tzinfo) > expiry_date:
                validation_issues.append("Credential has expired")
        except:
            validation_issues.append("Invalid expiration date format")
    
    # 3. Issuer Trust Check
    trusted_issuers = [
        "did:inji:issuer:government-of-india",
        "did:mosip:issuer:official",
        "did:inji:issuer:trusted-authority"
    ]
    
    issuer_id = credential.get("issuer", {})
    if isinstance(issuer_id, dict):
        issuer_id = issuer_id.get("id", "")
    
    if issuer_id not in trusted_issuers:
        validation_issues.append(f"Untrusted issuer: {issuer_id}")
    
    # 4. Signature Verification (mock)
    if "proof" not in credential:
        validation_issues.append("Missing cryptographic proof")
    else:
        proof = credential["proof"]
        if "jws" not in proof or not proof["jws"]:
            validation_issues.append("Missing or invalid signature")
    
    # 5. Subject Data Validation
    subject = credential.get("credentialSubject", {})
    required_subject_fields = ["name", "dateOfBirth"]
    
    for field in required_subject_fields:
        if field not in subject or not subject[field]:
            validation_issues.append(f"Missing required subject field: {field}")
    
    # 6. Data Format Validation
    if "dateOfBirth" in subject:
        dob = subject["dateOfBirth"]
        # Check if date format is valid
        try:
            datetime.fromisoformat(dob.replace('/', '-'))
        except:
            validation_issues.append("Invalid date of birth format")
    
    # Check expiry for not_expired field
    not_expired = True
    if "expirationDate" in credential:
        try:
            expiry_date = datetime.fromisoformat(credential["expirationDate"].replace('Z', '+00:00'))
            current_time = datetime.now(expiry_date.tzinfo)
            not_expired = current_time < expiry_date
        except:
            not_expired = False
    
    return {
        "credential_valid": len(validation_issues) == 0,
        "validation_issues": validation_issues,
        "issuer_trusted": issuer_id in trusted_issuers,
        "signature_valid": "proof" in credential and "jws" in credential.get("proof", {}),
        "not_expired": not_expired,
        "schema_valid": all(field in credential for field in required_fields)
    }

def test_your_flask_verify_endpoint():
    """Test your Flask app's /api/inji/verify-qr endpoint"""
    print("\n🌐 Testing Your Flask App Verification Endpoint")
    print("=" * 70)
    
    # Check if Flask app is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running")
        else:
            print("❌ Flask app not responding correctly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Flask app not running. Start with: py app.py")
        return
    except Exception as e:
        print(f"❌ Error connecting to Flask app: {str(e)}")
        return
    
    # Test with a QR image (base64)
    print("\n📱 Testing QR Verification Endpoint...")
    
    # Find a QR image file to test with
    qr_files = [f for f in os.listdir('.') if 'qr' in f.lower() and f.endswith('.png')]
    
    if not qr_files:
        print("❌ No QR image files found for testing")
        return
    
    test_file = qr_files[0]
    print(f"🔍 Testing with: {test_file}")
    
    try:
        # Read and encode image as base64
        with open(test_file, 'rb') as f:
            image_data = f.read()
        
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Test your verification endpoint
        test_payload = {
            "qr_image": f"data:image/png;base64,{image_base64}",
            "verification_method": "opencv"
        }
        
        response = requests.post(
            "http://localhost:5000/api/inji/verify-qr",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Verification Successful!")
            print(f"  Method Used: {result.get('method', 'unknown')}")
            print(f"  QR Scan Success: {result.get('qr_scan_result', {}).get('success', False)}")
            
            if 'official_verification' in result:
                official = result['official_verification']
                print(f"  Official API Used: {official.get('api_used', 'unknown')}")
                print(f"  Verified: {official.get('verified', False)}")
            
        else:
            print(f"❌ Verification Failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"  Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")

def explain_why_credentials_fail():
    """Explain common reasons why credentials are marked as invalid"""
    print("\n❓ Why Your Credentials Might Be Marked as Invalid")
    print("=" * 70)
    
    reasons = [
        {
            "reason": "🔐 Mock Signatures",
            "explanation": "Your credentials use mock signatures (mock_signature_abc123) instead of real cryptographic signatures",
            "solution": "Use real signing keys or configure Inji Verify to accept test signatures"
        },
        {
            "reason": "👤 Untrusted Issuer",
            "explanation": "The issuer DID (did:inji:issuer:government-of-india) might not be in Inji Verify's trusted issuer registry",
            "solution": "Register your issuer DID or use a pre-registered test issuer"
        },
        {
            "reason": "📝 Schema Mismatch",
            "explanation": "The credential structure might not match expected W3C VC schema",
            "solution": "Ensure @context, type, and other fields match W3C standards exactly"
        },
        {
            "reason": "⏰ Time Issues",
            "explanation": "Issuance/expiry dates might be in wrong format or timezone",
            "solution": "Use ISO 8601 format with proper timezone (Z suffix)"
        },
        {
            "reason": "🔗 Network Issues",
            "explanation": "Inji Verify can't reach issuer's DID document or revocation registry",
            "solution": "Ensure issuer DID resolves and revocation endpoints are accessible"
        },
        {
            "reason": "📊 Data Validation",
            "explanation": "Required fields missing or in wrong format (dates, IDs, etc.)",
            "solution": "Validate all required fields are present and properly formatted"
        }
    ]
    
    for i, reason_info in enumerate(reasons, 1):
        print(f"\n{i}. {reason_info['reason']}")
        print(f"   Problem: {reason_info['explanation']}")
        print(f"   Solution: {reason_info['solution']}")

def main():
    """Main function to run all verification tests"""
    print("🔍 Credential Verification Analysis Tool")
    print("=" * 70)
    
    analyze_verification_process()
    test_credential_validation_scenarios()
    explain_why_credentials_fail()
    test_your_flask_verify_endpoint()
    
    print("\n🎯 Summary:")
    print("• Inji Verify checks signatures, issuers, expiry, and schema")
    print("• Your credentials likely fail due to mock signatures or untrusted issuer")
    print("• Test with your Flask app to see exact validation results")
    print("• Use real signing keys and registered issuers for production")

if __name__ == "__main__":
    main()