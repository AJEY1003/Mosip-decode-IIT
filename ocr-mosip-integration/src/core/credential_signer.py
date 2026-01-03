#!/usr/bin/env python3
"""
Credential Signer - Generate Real Cryptographic Signatures for Verifiable Credentials
Creates proper Ed25519 signatures that Inji Verify can validate

Usage:
    py -m credential_signer
"""

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    print("❌ cryptography library not found. Install with: pip install cryptography")
    CRYPTO_AVAILABLE = False

import json
import base64
import uuid
from datetime import datetime, timedelta
import hashlib
import os

class CredentialSigner:
    """Generate real cryptographic signatures for Verifiable Credentials"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.did_document = None
        self.key_id = None
    
    def generate_key_pair(self):
        """Generate Ed25519 key pair for signing"""
        if not CRYPTO_AVAILABLE:
            raise ImportError("cryptography library required for real signatures")
        
        # Generate Ed25519 private key
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        
        # Generate key ID
        self.key_id = f"key-{uuid.uuid4().hex[:8]}"
        
        print("✅ Generated Ed25519 key pair")
        print(f"🔑 Key ID: {self.key_id}")
        
        return {
            "private_key": self.private_key,
            "public_key": self.public_key,
            "key_id": self.key_id
        }
    
    def save_keys_to_file(self, filename="signing_keys.json"):
        """Save keys to file for reuse"""
        if not self.private_key:
            raise ValueError("No keys generated. Call generate_key_pair() first")
        
        # Serialize private key
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize public key
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Create DID document
        did_id = f"did:inji:issuer:local-{uuid.uuid4().hex[:8]}"
        
        key_data = {
            "did": did_id,
            "key_id": self.key_id,
            "private_key_pem": private_pem.decode('utf-8'),
            "public_key_pem": public_pem.decode('utf-8'),
            "created": datetime.now().isoformat(),
            "algorithm": "Ed25519",
            "purpose": "Verifiable Credential Signing"
        }
        
        with open(filename, 'w') as f:
            json.dump(key_data, f, indent=2)
        
        print(f"💾 Keys saved to: {filename}")
        print(f"🆔 DID: {did_id}")
        
        return key_data
    
    def load_keys_from_file(self, filename="signing_keys.json"):
        """Load keys from file"""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Key file not found: {filename}")
        
        with open(filename, 'r') as f:
            key_data = json.load(f)
        
        # Load private key
        private_pem = key_data["private_key_pem"].encode('utf-8')
        self.private_key = serialization.load_pem_private_key(
            private_pem, 
            password=None, 
            backend=default_backend()
        )
        
        # Load public key
        public_pem = key_data["public_key_pem"].encode('utf-8')
        self.public_key = serialization.load_pem_public_key(
            public_pem, 
            backend=default_backend()
        )
        
        self.key_id = key_data["key_id"]
        
        print(f"✅ Keys loaded from: {filename}")
        print(f"🆔 DID: {key_data['did']}")
        print(f"🔑 Key ID: {self.key_id}")
        
        return key_data
    
    def create_canonical_json(self, data):
        """Create canonical JSON for signing (deterministic)"""
        # Remove proof field if present
        data_copy = data.copy()
        if 'proof' in data_copy:
            del data_copy['proof']
        
        # Create canonical JSON (sorted keys, no spaces)
        canonical = json.dumps(data_copy, sort_keys=True, separators=(',', ':'))
        return canonical
    
    def sign_credential(self, credential_data, issuer_did=None):
        """
        Sign a Verifiable Credential with Ed25519 signature
        
        Args:
            credential_data: The credential to sign
            issuer_did: Optional issuer DID (will generate if not provided)
            
        Returns:
            dict: Signed credential with proof
        """
        if not self.private_key:
            raise ValueError("No private key available. Generate or load keys first")
        
        # Set issuer DID if not provided
        if issuer_did:
            credential_data["issuer"] = {
                "id": issuer_did,
                "name": "Local Test Issuer"
            }
        
        # Create canonical representation for signing
        canonical_json = self.create_canonical_json(credential_data)
        
        # Create message to sign (hash of canonical JSON)
        message_hash = hashlib.sha256(canonical_json.encode('utf-8')).digest()
        
        # Sign with Ed25519
        signature = self.private_key.sign(message_hash)
        
        # Create JWS header
        jws_header = {
            "alg": "EdDSA",
            "typ": "JWT",
            "kid": self.key_id
        }
        
        # Encode header and signature
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(jws_header, separators=(',', ':')).encode('utf-8')
        ).decode('utf-8').rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            canonical_json.encode('utf-8')
        ).decode('utf-8').rstrip('=')
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
        
        # Create JWS (JSON Web Signature)
        jws = f"{header_b64}.{payload_b64}.{signature_b64}"
        
        # Add proof to credential
        proof = {
            "type": "Ed25519Signature2018",
            "created": datetime.now().isoformat() + "Z",
            "proofPurpose": "assertionMethod",
            "verificationMethod": f"{credential_data.get('issuer', {}).get('id', 'did:unknown')}#{self.key_id}",
            "jws": jws
        }
        
        # Create signed credential
        signed_credential = credential_data.copy()
        signed_credential["proof"] = proof
        
        print("✅ Credential signed successfully")
        print(f"🔐 Signature algorithm: Ed25519")
        print(f"📝 JWS length: {len(jws)} characters")
        
        return signed_credential
    
    def verify_signature(self, signed_credential):
        """
        Verify the signature of a signed credential
        
        Args:
            signed_credential: Credential with proof
            
        Returns:
            dict: Verification result
        """
        try:
            if not self.public_key:
                return {"valid": False, "error": "No public key available"}
            
            proof = signed_credential.get("proof", {})
            jws = proof.get("jws", "")
            
            if not jws:
                return {"valid": False, "error": "No JWS signature found"}
            
            # Parse JWS
            parts = jws.split('.')
            if len(parts) != 3:
                return {"valid": False, "error": "Invalid JWS format"}
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Decode signature
            # Add padding if needed
            signature_b64 += '=' * (4 - len(signature_b64) % 4)
            signature = base64.urlsafe_b64decode(signature_b64)
            
            # Decode payload
            payload_b64 += '=' * (4 - len(payload_b64) % 4)
            canonical_json = base64.urlsafe_b64decode(payload_b64).decode('utf-8')
            
            # Hash the canonical JSON
            message_hash = hashlib.sha256(canonical_json.encode('utf-8')).digest()
            
            # Verify signature
            self.public_key.verify(signature, message_hash)
            
            return {
                "valid": True,
                "algorithm": "Ed25519",
                "verification_method": proof.get("verificationMethod"),
                "created": proof.get("created")
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}

def create_sample_signed_credential():
    """Create a sample signed credential for testing"""
    print("🔧 Creating Sample Signed Credential")
    print("=" * 50)
    
    # Initialize signer
    signer = CredentialSigner()
    
    # Generate or load keys
    key_file = "signing_keys.json"
    if os.path.exists(key_file):
        print("📂 Loading existing keys...")
        key_data = signer.load_keys_from_file(key_file)
        issuer_did = key_data["did"]
    else:
        print("🔑 Generating new keys...")
        signer.generate_key_pair()
        key_data = signer.save_keys_to_file(key_file)
        issuer_did = key_data["did"]
    
    # Create sample credential
    sample_credential = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://www.w3.org/2018/credentials/examples/v1"
        ],
        "id": f"urn:uuid:{uuid.uuid4()}",
        "type": ["VerifiableCredential", "IdentityCredential"],
        "issuer": {
            "id": issuer_did,
            "name": "Local Test Issuer"
        },
        "issuanceDate": datetime.now().isoformat() + "Z",
        "expirationDate": (datetime.now() + timedelta(days=365)).isoformat() + "Z",
        "credentialSubject": {
            "id": f"did:inji:citizen:{uuid.uuid4()}",
            "name": "John Smith",
            "dateOfBirth": "1988-12-25",
            "nationality": "Indian",
            "aadhaarNumber": "1234-5678-9012",
            "panNumber": "ABCDE1234F",
            "phone": "+91-9876543210",
            "email": "john.smith@example.com",
            "address": "123 Test Street, Mumbai, India"
        }
    }
    
    # Sign the credential
    print("\n🔐 Signing credential...")
    signed_credential = signer.sign_credential(sample_credential, issuer_did)
    
    # Verify the signature
    print("\n✅ Verifying signature...")
    verification_result = signer.verify_signature(signed_credential)
    
    if verification_result["valid"]:
        print("✅ Signature verification successful!")
        print(f"🔐 Algorithm: {verification_result['algorithm']}")
    else:
        print(f"❌ Signature verification failed: {verification_result['error']}")
    
    # Save signed credential
    output_file = "signed_credential.json"
    with open(output_file, 'w') as f:
        json.dump(signed_credential, f, indent=2)
    
    print(f"\n💾 Signed credential saved to: {output_file}")
    
    # Show the real signature
    jws = signed_credential["proof"]["jws"]
    print(f"\n🔑 Real Ed25519 Signature (JWS):")
    print(f"Length: {len(jws)} characters")
    print(f"Preview: {jws[:50]}...{jws[-20:]}")
    
    return signed_credential

def integrate_with_pixelpass():
    """Show how to integrate real signatures with PixelPass"""
    print("\n🔗 Integrating Real Signatures with PixelPass")
    print("=" * 50)
    
    print("📝 To use real signatures in your PixelPass integration:")
    print("1. Replace mock signature generation in pixelpass_integration.py")
    print("2. Use CredentialSigner.sign_credential() instead of mock signatures")
    print("3. Update your Flask endpoints to use real signing")
    
    print("\n💡 Code Example:")
    print("""
# In pixelpass_integration.py, replace:
"jws": f"mock_signature_{uuid.uuid4().hex[:16]}"

# With:
from credential_signer import CredentialSigner
signer = CredentialSigner()
signer.load_keys_from_file("signing_keys.json")
signed_vc = signer.sign_credential(verifiable_credential)
""")

def main():
    """Main function to demonstrate credential signing"""
    print("🔐 Credential Signer - Real Ed25519 Signatures")
    print("=" * 60)
    
    if not CRYPTO_AVAILABLE:
        print("❌ cryptography library required")
        print("📦 Install with: pip install cryptography")
        return
    
    # Create sample signed credential
    signed_credential = create_sample_signed_credential()
    
    # Show integration instructions
    integrate_with_pixelpass()
    
    print("\n🎯 Next Steps:")
    print("1. Use the generated signing_keys.json for your issuer")
    print("2. Replace mock signatures in your PixelPass integration")
    print("3. Test with Inji Verify using the signed credential")
    print("4. Register your issuer DID with Inji Verify for production")

if __name__ == "__main__":
    main()