"""
Simple QR Code Generator for ITR Documents
Uses qrcode library to generate QR codes with structured data
"""

import qrcode
import json
import base64
import io
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class ITRQRGenerator:
    """
    QR Code generator for ITR documents with MOSIP-compatible format
    """
    
    def __init__(self):
        self.qr_settings = {
            'version': 1,
            'error_correction': qrcode.constants.ERROR_CORRECT_M,
            'box_size': 10,
            'border': 4,
        }
    
    def generate_simple_qr(self, data: Dict[str, Any], format_type: str = 'json') -> Dict[str, Any]:
        """
        Generate a simple QR code with structured data
        
        Args:
            data: Dictionary containing the structured data
            format_type: Format for QR data ('json', 'text', 'url')
            
        Returns:
            Dictionary with QR generation results
        """
        try:
            logger.info(f"🔲 Generating simple QR code with {len(data)} fields")
            
            # Prepare QR data based on format
            if format_type == 'json':
                qr_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            elif format_type == 'text':
                qr_data = self._format_as_text(data)
            elif format_type == 'url':
                qr_data = self._format_as_url(data)
            else:
                qr_data = json.dumps(data)
            
            # Generate QR code
            qr = qrcode.QRCode(**self.qr_settings)
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            img_buffer = io.BytesIO()
            qr_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            qr_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            qr_data_url = f"data:image/png;base64,{qr_base64}"
            
            logger.info(f"✅ Simple QR code generated successfully")
            
            return {
                'success': True,
                'qr_image_base64': qr_data_url,
                'qr_data': qr_data,
                'format': format_type,
                'data_length': len(qr_data),
                'generation_timestamp': datetime.now().isoformat(),
                'qr_version': qr.version,
                'error_correction': 'M'
            }
            
        except Exception as e:
            logger.error(f"❌ Simple QR generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'qr_image_base64': None,
                'generation_timestamp': datetime.now().isoformat()
            }
    
    def generate_signed_qr(self, data: Dict[str, Any], signature_type: str = 'mock') -> Dict[str, Any]:
        """
        Generate a signed QR code for MOSIP compatibility
        
        Args:
            data: Dictionary containing the structured data
            signature_type: Type of signature ('mock', 'ed25519', 'rsa')
            
        Returns:
            Dictionary with signed QR generation results
        """
        try:
            logger.info(f"🔐 Generating signed QR code with {signature_type} signature")
            
            # Create workflow ID
            workflow_id = f"itr-workflow-{uuid.uuid4().hex[:8]}"
            
            # Prepare credential data
            credential_data = {
                'id': f"urn:uuid:{uuid.uuid4()}",
                'type': ['VerifiableCredential', 'ITRCredential'],
                'issuer': 'did:mosip:itr-system',
                'issuanceDate': datetime.now().isoformat(),
                'credentialSubject': {
                    'id': f"did:mosip:user:{data.get('pan', 'unknown')}",
                    **data
                },
                'proof': self._generate_mock_proof(data, signature_type)
            }
            
            # Generate QR with credential
            qr_result = self.generate_simple_qr(credential_data, 'json')
            
            if qr_result['success']:
                logger.info(f"✅ Signed QR code generated successfully")
                
                return {
                    'success': True,
                    'workflow_id': workflow_id,
                    'qr_code': {
                        'qr_image': qr_result['qr_image_base64'],
                        'encoding': 'JSON',
                        'signature_type': signature_type,
                        'data_length': qr_result['data_length']
                    },
                    'credential': credential_data,
                    'generation_timestamp': datetime.now().isoformat(),
                    'compatible_with': ['Inji Verify Portal', 'MOSIP Ecosystem']
                }
            else:
                raise Exception(f"QR generation failed: {qr_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Signed QR generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'workflow_id': None,
                'generation_timestamp': datetime.now().isoformat()
            }
    
    def _format_as_text(self, data: Dict[str, Any]) -> str:
        """Format data as human-readable text"""
        lines = []
        lines.append("=== ITR CREDENTIAL ===")
        
        for key, value in data.items():
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"{formatted_key}: {value}")
        
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return '\n'.join(lines)
    
    def _format_as_url(self, data: Dict[str, Any]) -> str:
        """Format data as URL with query parameters"""
        base_url = "https://verify.inji.io/verify"
        params = []
        
        for key, value in data.items():
            if value:
                params.append(f"{key}={str(value)}")
        
        return f"{base_url}?{'&'.join(params)}"
    
    def _generate_mock_proof(self, data: Dict[str, Any], signature_type: str) -> Dict[str, Any]:
        """Generate mock cryptographic proof"""
        proof_data = {
            'type': 'Ed25519Signature2018' if signature_type == 'ed25519' else 'RsaSignature2018',
            'created': datetime.now().isoformat(),
            'verificationMethod': f'did:mosip:itr-system#key-{signature_type}',
            'proofPurpose': 'assertionMethod'
        }
        
        # Generate mock signature based on data
        data_string = json.dumps(data, sort_keys=True)
        mock_signature = base64.b64encode(
            f"mock-signature-{hash(data_string) % 1000000}".encode()
        ).decode()
        
        proof_data['proofValue'] = mock_signature
        
        return proof_data
    
    def validate_qr_data(self, qr_data: str) -> Dict[str, Any]:
        """
        Validate QR code data
        
        Args:
            qr_data: QR code data string
            
        Returns:
            Validation results
        """
        try:
            # Try to parse as JSON
            parsed_data = json.loads(qr_data)
            
            validation_result = {
                'valid': True,
                'format': 'json',
                'data_type': type(parsed_data).__name__,
                'field_count': len(parsed_data) if isinstance(parsed_data, dict) else 0,
                'has_credential_structure': self._check_credential_structure(parsed_data),
                'validation_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ QR data validation successful")
            return validation_result
            
        except json.JSONDecodeError:
            # Not JSON, treat as text
            return {
                'valid': True,
                'format': 'text',
                'data_type': 'string',
                'character_count': len(qr_data),
                'has_credential_structure': False,
                'validation_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ QR data validation failed: {str(e)}")
            return {
                'valid': False,
                'error': str(e),
                'validation_timestamp': datetime.now().isoformat()
            }
    
    def _check_credential_structure(self, data: Any) -> bool:
        """Check if data has verifiable credential structure"""
        if not isinstance(data, dict):
            return False
        
        required_fields = ['type', 'credentialSubject']
        return all(field in data for field in required_fields)

# Global instance
qr_generator = ITRQRGenerator()