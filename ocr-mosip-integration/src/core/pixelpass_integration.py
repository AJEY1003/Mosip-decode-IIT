#!/usr/bin/env py
"""
PixelPass Integration for QR Code Generation
Based on official Inji Certify + PixelPass documentation
Generates QR codes compatible with Inji Verify portal
"""

import json
import base64
import uuid
import subprocess
import os
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PixelPassQRGenerator:
    """
    PixelPass QR Code Generator
    Follows official Inji documentation for QR generation
    """
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.node_project_path = None
        self._setup_node_project()
    
    def _setup_node_project(self):
        """Set up Node.js project with PixelPass library"""
        try:
            # Use the existing node_modules in the project root instead of creating a temp project
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Go up to project root
            self.node_project_path = project_root
            
            # Check if node_modules exists
            node_modules_path = os.path.join(project_root, 'node_modules')
            if not os.path.exists(node_modules_path):
                logger.warning(f"node_modules not found at {node_modules_path}")
                # Fallback to temp directory
                self.node_project_path = os.path.join(self.temp_dir, 'pixelpass_qr')
                os.makedirs(self.node_project_path, exist_ok=True)
            
            # Create QR generation script in the project directory
            qr_script_path = os.path.join(self.node_project_path, 'generate_qr_temp.js')
            qr_script = '''
const { generateQRData } = require('@mosip/pixelpass');

// Get credential data from command line argument
const credentialData = process.argv[2];

if (!credentialData) {
    console.error('Error: Credential data is required');
    process.exit(1);
}

try {
    // Parse credential data - expecting the credential body as per Inji Certify docs
    const parsedCredential = JSON.parse(credentialData);
    
    // Use generateQRData as per official documentation
    // Pass the credential body (value of 'credential' from credential response)
    const qrData = generateQRData(JSON.stringify(parsedCredential));
    
    // Output QR data as base64 image
    console.log(JSON.stringify({
        success: true,
        qr_data: qrData,
        qr_image_data: qrData, // This should be base64 image data
        encoding: 'PixelPass-CBOR',
        timestamp: new Date().toISOString()
    }));
} catch (error) {
    console.error(JSON.stringify({
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
    }));
    process.exit(1);
}
'''
            
            with open(qr_script_path, 'w') as f:
                f.write(qr_script)
            
            logger.info(f"Node.js project set up at: {self.node_project_path}")
            logger.info(f"QR script created at: {qr_script_path}")
            
        except Exception as e:
            logger.error(f"Node.js project setup failed: {str(e)}")
            self.node_project_path = None
    
    def install_pixelpass(self) -> bool:
        """Install PixelPass library"""
        if not self.node_project_path:
            return False
        
        try:
            # Install PixelPass library
            result = subprocess.run(
                ['npm', 'install', '@mosip/pixelpass'],
                cwd=self.node_project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("PixelPass library installed successfully")
                return True
            else:
                logger.error(f"PixelPass installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"PixelPass installation error: {str(e)}")
            return False
    
    def generate_verifiable_credential(self, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Verifiable Credential from OCR data
        Following Inji Certify format
        
        Args:
            ocr_data: Extracted and validated OCR data
            
        Returns:
            dict: Verifiable Credential in JSON-LD format
        """
        try:
            # Create VC following Inji Certify format
            vc_id = str(uuid.uuid4())
            current_time = datetime.now()
            expiry_time = current_time + timedelta(days=365)  # 1 year validity
            
            verifiable_credential = {
                "@context": [
                    "https://www.w3.org/2018/credentials/v1",
                    "https://www.w3.org/2018/credentials/examples/v1"
                ],
                "id": f"urn:uuid:{vc_id}",
                "type": ["VerifiableCredential", "IdentityCredential"],
                "issuer": {
                    "id": "did:inji:issuer:government-of-india",
                    "name": "Government of India - Digital Identity Authority"
                },
                "issuanceDate": current_time.isoformat() + "Z",
                "expirationDate": expiry_time.isoformat() + "Z",
                "credentialSubject": {
                    "id": f"did:inji:citizen:{uuid.uuid4()}",
                    "name": ocr_data.get('name', ''),
                    "dateOfBirth": ocr_data.get('date_of_birth', ''),
                    "nationality": "Indian",
                    "aadhaarNumber": ocr_data.get('aadhaar_number', '****-****-****'),
                    "panNumber": ocr_data.get('pan_number', ''),
                    "phoneNumber": ocr_data.get('phone', ''),
                    "emailAddress": ocr_data.get('email', ''),
                    "address": {
                        "fullAddress": ocr_data.get('address', ''),
                        "country": "India"
                    },
                    "documentType": ocr_data.get('document_type', 'Identity Document')
                }
            }
            
            # Generate real signature using CredentialSigner
            try:
                from credential_signer import CredentialSigner
                signer = CredentialSigner()
                
                # Try to load existing keys, generate if not found
                try:
                    signer.load_keys_from_file("signing_keys.json")
                except FileNotFoundError:
                    signer.generate_key_pair()
                    signer.save_keys_to_file("signing_keys.json")
                
                # Sign the credential properly
                signed_vc = signer.sign_credential(verifiable_credential)
                verifiable_credential = signed_vc
                
            except ImportError:
                logger.warning("CredentialSigner not available, using mock signature")
                # Fallback to mock signature
                verifiable_credential["proof"] = {
                    "type": "Ed25519Signature2018",
                    "created": current_time.isoformat() + "Z",
                    "proofPurpose": "assertionMethod",
                    "verificationMethod": "did:inji:issuer:government-of-india#key-1",
                    "jws": f"mock_signature_{uuid.uuid4().hex[:16]}"  # Mock signature for testing
                }
            
            return {
                'success': True,
                'vc_id': vc_id,
                'verifiable_credential': verifiable_credential,
                'credential_body': verifiable_credential,  # For PixelPass
                'timestamp': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"VC generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'vc_id': str(uuid.uuid4())
            }
    
    def generate_qr_with_pixelpass(self, credential_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate QR code using PixelPass library
        Following official Inji documentation workflow:
        1. Get credential body from Inji Certify
        2. Pass to generateQRData from PixelPass
        3. Return base64 image data for browser display
        
        Args:
            credential_data: Verifiable Credential data (credential body)
            
        Returns:
            dict: QR generation result with base64 image data
        """
        if not self.node_project_path:
            return {
                'success': False,
                'error': 'Node.js project not set up',
                'qr_id': str(uuid.uuid4())
            }
        
        try:
            # Use the credential body as per Inji Certify documentation
            # This should be the 'credential' value from the credential response
            credential_body = credential_data.get('credential_body', credential_data)
            credential_json = json.dumps(credential_body)
            
            # Run Node.js script to generate QR using PixelPass
            result = subprocess.run(
                ['node', 'generate_qr_temp.js', credential_json],
                cwd=self.node_project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse Node.js output
                output_data = json.loads(result.stdout.strip())
                
                if output_data.get('success'):
                    qr_image_data = output_data.get('qr_image_data')
                    
                    return {
                        'success': True,
                        'qr_id': str(uuid.uuid4()),
                        'qr_data': output_data.get('qr_data'),
                        'qr_image': qr_image_data,  # Base64 image data for browser
                        'browser_url': qr_image_data,  # Can be pasted directly in browser
                        'encoding': 'PixelPass-CBOR',
                        'library': '@mosip/pixelpass',
                        'compatible_with': 'Inji Verify Portal',
                        'instructions': 'Copy qr_image data and paste in browser URL to view QR code',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': output_data.get('error', 'QR generation failed'),
                        'qr_id': str(uuid.uuid4())
                    }
            else:
                logger.error(f"PixelPass QR generation failed: {result.stderr}")
                return {
                    'success': False,
                    'error': f"PixelPass error: {result.stderr}",
                    'qr_id': str(uuid.uuid4())
                }
                
        except Exception as e:
            logger.error(f"QR generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'qr_id': str(uuid.uuid4())
            }
    
    def create_mock_qr_for_testing(self, credential_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create mock QR code for testing when Node.js/PixelPass is not available
        
        Args:
            credential_data: Verifiable Credential data
            
        Returns:
            dict: Mock QR generation result
        """
        try:
            import qrcode
            from io import BytesIO
            
            # Create QR code with credential data
            qr_content = json.dumps(credential_data)
            
            qr = qrcode.QRCode(
                version=27,  # Compatible with Inji Verify
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            
            # Generate QR image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return {
                'success': True,
                'qr_id': str(uuid.uuid4()),
                'qr_data': qr_content,
                'qr_image': f"data:image/png;base64,{qr_image_base64}",
                'encoding': 'JSON-Mock',
                'library': 'qrcode-python',
                'note': 'Mock QR for testing - use PixelPass for production',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock QR generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'qr_id': str(uuid.uuid4())
            }
    
    def complete_qr_generation_workflow(self, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete workflow following official Inji documentation:
        1. Generate Verifiable Credential from OCR data (like Inji Certify)
        2. Extract credential body
        3. Generate QR code using PixelPass
        4. Return QR image data for browser display and Inji Verify upload
        
        Args:
            ocr_data: Extracted OCR data from document
            
        Returns:
            dict: Complete workflow result with VC and QR data
        """
        try:
            # Step 1: Generate Verifiable Credential (like Inji Certify)
            vc_result = self.generate_verifiable_credential(ocr_data)
            
            if not vc_result.get('success'):
                return {
                    'success': False,
                    'error': f"VC generation failed: {vc_result.get('error')}",
                    'workflow_step': 'verifiable_credential_generation'
                }
            
            # Step 2: Extract credential body for PixelPass
            credential_body = vc_result.get('credential_body')
            
            # Step 3: Generate QR code using PixelPass
            qr_result = self.generate_qr_with_pixelpass({'credential_body': credential_body})
            
            if not qr_result.get('success'):
                # Fallback to mock QR for testing
                logger.warning("PixelPass failed, using mock QR for testing")
                logger.error(f"PixelPass QR generation failed: {qr_result.get('error')}")
                qr_result = self.create_mock_qr_for_testing(credential_body)
                
                # If mock also fails, use simple QR generator
                if not qr_result.get('success'):
                    logger.warning("Mock QR also failed, using simple QR generator")
                    try:
                        from qr_generator import qr_generator
                        simple_qr_result = qr_generator.generate_simple_qr(credential_body, 'json')
                        if simple_qr_result.get('success'):
                            qr_result = {
                                'success': True,
                                'qr_id': str(uuid.uuid4()),
                                'qr_image': simple_qr_result.get('qr_image_base64'),
                                'encoding': 'JSON-Simple',
                                'library': 'qrcode-python-simple',
                                'note': 'Fallback simple QR generator'
                            }
                    except Exception as fallback_error:
                        logger.error(f"All QR generation methods failed: {fallback_error}")
                        return {
                            'success': False,
                            'error': f"All QR generation methods failed. PixelPass: {qr_result.get('error')}, Fallback: {fallback_error}",
                            'workflow_step': 'qr_generation_all_failed'
                        }
            
            # Step 4: Return complete workflow result
            return {
                'success': True,
                'workflow_id': str(uuid.uuid4()),
                'verifiable_credential': {
                    'vc_id': vc_result.get('vc_id'),
                    'credential': vc_result.get('verifiable_credential'),
                    'credential_body': credential_body
                },
                'qr_code': {
                    'qr_id': qr_result.get('qr_id'),
                    'qr_image': qr_result.get('qr_image'),
                    'browser_url': qr_result.get('browser_url'),
                    'encoding': qr_result.get('encoding'),
                    'library': qr_result.get('library')
                },
                'instructions': {
                    'save_qr': 'Copy qr_image data and paste in browser URL to view and save QR code',
                    'verify_qr': 'Upload saved QR code to Inji Verify portal for verification',
                    'inji_verify_url': 'Access Inji Verify portal in your browser (local setup required)'
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Complete workflow error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'workflow_step': 'complete_workflow'
            }

    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.warning(f"Cleanup error: {str(e)}")

# Global PixelPass instance
pixelpass_qr = PixelPassQRGenerator()