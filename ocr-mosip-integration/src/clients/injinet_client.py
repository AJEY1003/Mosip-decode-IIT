#!/usr/bin/env python3
"""
InjInet Client for Verifiable Credential Generation
Integrates with InjInet APIs for Indian identity verification and VC creation
"""

import requests
import json
import base64
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class InjInetClient:
    """Client for InjInet API integration"""
    
    def __init__(self, base_url: str = None, client_id: str = None, 
                 client_secret: str = None, api_key: str = None):
        """
        Initialize InjInet client
        
        Args:
            base_url: InjInet API base URL
            client_id: Client ID for authentication
            client_secret: Client secret for authentication
            api_key: API key if required
        """
        self.base_url = base_url or "https://injinet.collab.mosip.net"
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_key = api_key
        self.access_token = None
        self.token_expires_at = None
        
        # API endpoints
        self.endpoints = {
            'auth': '/v1/auth/token',
            'validate_identity': '/v1/identity/validate',
            'generate_vc': '/v1/credentials/generate',
            'verify_vc': '/v1/credentials/verify',
            'wallet_store': '/v1/wallet/store'
        }
    
    def authenticate(self) -> bool:
        """
        Authenticate with InjInet and get access token
        
        Returns:
            bool: True if authentication successful
        """
        if not self.client_id or not self.client_secret:
            logger.error("Client ID and Client Secret are required for authentication")
            return False
        
        try:
            auth_url = f"{self.base_url}{self.endpoints['auth']}"
            
            # Prepare authentication payload
            auth_payload = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
                "scope": "identity_verify vc_generate wallet_store"
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            response = requests.post(auth_url, json=auth_payload, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                logger.info("InjInet authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        return headers
    
    def _is_token_valid(self) -> bool:
        """Check if current token is still valid"""
        if not self.access_token or not self.token_expires_at:
            return False
        return datetime.now() < self.token_expires_at
    
    def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid authentication token"""
        if not self._is_token_valid():
            return self.authenticate()
        return True
    
    def validate_indian_identity(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted data against Indian identity records
        
        Args:
            extracted_data: Data extracted from OCR
            
        Returns:
            dict: Validation result
        """
        if not self._ensure_authenticated():
            return {
                'success': False,
                'error': 'Authentication failed',
                'validation_id': str(uuid.uuid4())
            }
        
        try:
            validate_url = f"{self.base_url}{self.endpoints['validate_identity']}"
            
            # Prepare validation payload
            validation_payload = {
                "validation_id": str(uuid.uuid4()),
                "identity_data": {
                    "name": extracted_data.get('name'),
                    "date_of_birth": self._format_date(extracted_data.get('date_of_birth')),
                    "aadhaar_number": extracted_data.get('aadhaar_number'),
                    "pan_number": extracted_data.get('pan_number'),
                    "phone": extracted_data.get('phone'),
                    "email": extracted_data.get('email'),
                    "address": extracted_data.get('address')
                },
                "document_type": extracted_data.get('document_type', 'Unknown'),
                "validation_level": "FULL"  # BASIC, STANDARD, FULL
            }
            
            response = requests.post(
                validate_url, 
                json=validation_payload, 
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                validation_result = response.json()
                return {
                    'success': True,
                    'validation_id': validation_result.get('validation_id'),
                    'identity_verified': validation_result.get('identity_verified', False),
                    'confidence_score': validation_result.get('confidence_score', 0.0),
                    'verified_fields': validation_result.get('verified_fields', {}),
                    'discrepancies': validation_result.get('discrepancies', []),
                    'uin': validation_result.get('uin'),  # Unique Identity Number
                    'vid': validation_result.get('vid'),  # Virtual ID
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"Identity validation failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Validation failed: {response.status_code}",
                    'validation_id': validation_payload['validation_id']
                }
                
        except Exception as e:
            logger.error(f"Identity validation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'validation_id': str(uuid.uuid4())
            }
    
    def generate_verifiable_credential(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Verifiable Credential from validated identity data
        
        Args:
            validated_data: Validated identity data from InjInet
            
        Returns:
            dict: VC generation result
        """
        if not self._ensure_authenticated():
            return {
                'success': False,
                'error': 'Authentication failed',
                'vc_id': str(uuid.uuid4())
            }
        
        try:
            vc_url = f"{self.base_url}{self.endpoints['generate_vc']}"
            
            # Prepare VC generation payload
            vc_payload = {
                "vc_id": str(uuid.uuid4()),
                "issuer": {
                    "id": "did:injinet:issuer:government",
                    "name": "Government of India - InjInet"
                },
                "subject": {
                    "id": f"did:injinet:citizen:{validated_data.get('uin', uuid.uuid4())}",
                    "identity_data": validated_data.get('verified_fields', {})
                },
                "credential_type": ["VerifiableCredential", "IdentityCredential"],
                "validation_reference": validated_data.get('validation_id'),
                "confidence_score": validated_data.get('confidence_score', 0.0),
                "valid_from": datetime.now().isoformat(),
                "valid_until": (datetime.now() + timedelta(days=365)).isoformat()  # 1 year validity
            }
            
            response = requests.post(
                vc_url, 
                json=vc_payload, 
                headers=self._get_headers()
            )
            
            if response.status_code == 201:
                vc_result = response.json()
                return {
                    'success': True,
                    'vc_id': vc_result.get('vc_id'),
                    'verifiable_credential': vc_result.get('verifiable_credential'),
                    'vc_jwt': vc_result.get('vc_jwt'),  # JWT format VC
                    'qr_code': vc_result.get('qr_code'),  # QR code for mobile wallet
                    'wallet_url': vc_result.get('wallet_url'),  # URL to add to InjI wallet
                    'expiry_date': vc_result.get('expiry_date'),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"VC generation failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"VC generation failed: {response.status_code}",
                    'vc_id': vc_payload['vc_id']
                }
                
        except Exception as e:
            logger.error(f"VC generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'vc_id': str(uuid.uuid4())
            }
    
    def store_in_inji_wallet(self, vc_data: Dict[str, Any], user_phone: str = None) -> Dict[str, Any]:
        """
        Store Verifiable Credential in InjI Wallet
        
        Args:
            vc_data: VC data from generation
            user_phone: User's phone number for wallet notification
            
        Returns:
            dict: Wallet storage result
        """
        if not self._ensure_authenticated():
            return {
                'success': False,
                'error': 'Authentication failed'
            }
        
        try:
            wallet_url = f"{self.base_url}{self.endpoints['wallet_store']}"
            
            wallet_payload = {
                "vc_id": vc_data.get('vc_id'),
                "vc_jwt": vc_data.get('vc_jwt'),
                "user_identifier": user_phone,
                "notification_method": "SMS" if user_phone else "QR",
                "wallet_type": "InjI_Mobile"
            }
            
            response = requests.post(
                wallet_url, 
                json=wallet_payload, 
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                wallet_result = response.json()
                return {
                    'success': True,
                    'wallet_stored': True,
                    'download_url': wallet_result.get('download_url'),
                    'qr_code': wallet_result.get('qr_code'),
                    'sms_sent': wallet_result.get('sms_sent', False),
                    'expiry_hours': wallet_result.get('expiry_hours', 24)
                }
            else:
                return {
                    'success': False,
                    'error': f"Wallet storage failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Wallet storage error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_date(self, date_string: str) -> str:
        """Format date string to ISO format"""
        if not date_string:
            return ""
        
        try:
            # Handle DD/MM/YYYY format
            if '/' in date_string:
                parts = date_string.split('/')
                if len(parts) == 3:
                    return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
            
            # Handle DD-MM-YYYY format
            if '-' in date_string and len(date_string.split('-')[0]) <= 2:
                parts = date_string.split('-')
                if len(parts) == 3:
                    return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
            
            return date_string
        except:
            return date_string

# Mock InjINet client for testing when credentials are not available
class MockInjINetClient(InjInetClient):
    """Mock InjINet client for testing purposes"""
    
    def authenticate(self) -> bool:
        """Mock authentication - always succeeds"""
        self.access_token = "mock_token_12345"
        self.token_expires_at = datetime.now() + timedelta(hours=1)
        return True
    
    def validate_indian_identity(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock identity validation"""
        return {
            'success': True,
            'validation_id': str(uuid.uuid4()),
            'identity_verified': True,
            'confidence_score': 0.95,
            'verified_fields': {
                'name': extracted_data.get('name', 'Verified Name'),
                'date_of_birth': extracted_data.get('date_of_birth', '1990-05-15'),
                'aadhaar_number': '****-****-1234',
                'phone': extracted_data.get('phone', '+91-98765-43210'),
                'email': extracted_data.get('email', 'verified@example.com')
            },
            'discrepancies': [],
            'uin': '1234567890123456',
            'vid': '9876543210987654',
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_verifiable_credential(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock VC generation"""
        vc_id = str(uuid.uuid4())
        return {
            'success': True,
            'vc_id': vc_id,
            'verifiable_credential': {
                '@context': ['https://www.w3.org/2018/credentials/v1'],
                'type': ['VerifiableCredential', 'IdentityCredential'],
                'issuer': 'did:injinet:issuer:government',
                'issuanceDate': datetime.now().isoformat(),
                'credentialSubject': validated_data.get('verified_fields', {})
            },
            'vc_jwt': f"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.mock_vc_jwt_payload.mock_signature",
            'qr_code': f"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
            'wallet_url': f"https://injinet.collab.mosip.net/wallet/add/{vc_id}",
            'expiry_date': (datetime.now() + timedelta(days=365)).isoformat(),
            'timestamp': datetime.now().isoformat()
        }
    
    def store_in_inji_wallet(self, vc_data: Dict[str, Any], user_phone: str = None) -> Dict[str, Any]:
        """Mock wallet storage"""
        return {
            'success': True,
            'wallet_stored': True,
            'download_url': f"https://injinet.collab.mosip.net/wallet/download/{vc_data.get('vc_id')}",
            'qr_code': "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
            'sms_sent': bool(user_phone),
            'expiry_hours': 24
        }