import requests
import json
from typing import Dict, Optional
import os
from dotenv import load_dotenv
import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timezone

# Suppress SSL warnings for sandbox
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class MOSIPClient:
    """
    MOSIP Pre-Registration API client for communicating with MOSIP platform
    
    Features:
    - Create pre-registration applications with demographic data
    - Upload supporting documents
    - Book appointments at registration centers
    - Check appointment availability
    - Full workflow automation
    
    Endpoints:
    - https://prereg.collab.mosip.net/preregistration/v1/applications
    - https://prereg.collab.mosip.net/preregistration/v1/documents
    - https://prereg.collab.mosip.net/preregistration/v1/appointment
    """
    
    def __init__(self, base_url: str = None):
        """
        Initialize MOSIP Pre-Registration client
        
        Args:
            base_url: MOSIP Pre-Registration service base URL
                      Defaults to: https://prereg.collab.mosip.net
        """
        self.base_url = base_url or 'https://prereg.collab.mosip.net'
        self.username = os.getenv('MOSIP_USERNAME')
        self.password = os.getenv('MOSIP_PASSWORD')
        self.client_id = os.getenv('MOSIP_CLIENT_ID')
        self.client_secret = os.getenv('MOSIP_CLIENT_SECRET')
        self.access_token = None
        self.token_type = 'Bearer'
        
        # API version and IDs
        self.api_version = '1.0'
        self.app_create_id = 'mosip.pre.registration.application.create'
        self.app_update_id = 'mosip.pre.registration.application.update'
        self.doc_upload_id = 'mosip.pre.registration.document.upload'
        self.appointment_book_id = 'mosip.pre.registration.booking.appointment.save'
        
        # Pre-Registration API endpoints
        self.applications_endpoint = f"{self.base_url}/preregistration/v1/applications"
        self.documents_endpoint = f"{self.base_url}/preregistration/v1/documents"
        self.appointment_endpoint = f"{self.base_url}/preregistration/v1/appointment"
        
        # Legacy endpoint (kept for backward compatibility)
        self.preregistration_endpoint = self.applications_endpoint
        
    def authenticate(self) -> bool:
        """
        Authenticate with MOSIP Pre-Registration API
        
        Note: Pre-Registration API on MOSIP Sandbox may not require authentication
        or may use session-based authentication from logged-in portal.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            logger.info("Testing Pre-Registration API connectivity...")
            
            # Test endpoint access
            response = requests.get(
                self.preregistration_endpoint,
                verify=False,
                timeout=5
            )
            
            # 401 means endpoint exists but needs auth (good sign)
            # 200 means endpoint accessible without auth (sandbox behavior)
            if response.status_code in [200, 401, 403]:
                logger.info(f"Pre-Registration API accessible (Status: {response.status_code})")
                return True
            else:
                logger.error(f"Pre-Registration API not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication check error: {str(e)}")
            return False
    
    def get_headers(self) -> Dict:
        """
        Get request headers for API calls
        
        Returns:
            Dictionary of headers
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'MOSIP-OCR-Integration/1.0'
        }
        
        if self.access_token:
            headers['Authorization'] = f'{self.token_type} {self.access_token}'
        
        return headers
    
    def create_application(self, demographic_data: Dict) -> Dict:
        """
        Create a pre-registration application with demographic data
        
        This is the recommended way to submit OCR-extracted data to MOSIP
        instead of manually filling the web form.
        
        Args:
            demographic_data: Dictionary with resident demographic information
                            {
                                'fullName': str,
                                'dateOfBirth': str (YYYY-MM-DD),
                                'gender': str (M/F/O),
                                'mobileNumber': str (10 digits),
                                'emailId': str,
                                'address': {
                                    'street': str,
                                    'city': str,
                                    'state': str,
                                    'postalCode': str (6 digits),
                                    'country': str
                                }
                            }
        
        Returns:
            Dictionary with preRegistrationId and response
        """
        try:
            payload = {
                "id": self.app_create_id,
                "version": self.api_version,
                "requesttime": self._get_timestamp(),
                "request": {
                    "demographicDetails": {
                        "fullName": [
                            {
                                "value": demographic_data.get('fullName', ''),
                                "language": "eng"
                            }
                        ],
                        "dateOfBirth": demographic_data.get('dateOfBirth', ''),
                        "gender": demographic_data.get('gender', ''),
                        "mobileNumber": demographic_data.get('mobileNumber', ''),
                        "emailId": demographic_data.get('emailId', ''),
                        "addressLine1": [
                            {
                                "value": demographic_data.get('address', {}).get('street', ''),
                                "language": "eng"
                            }
                        ],
                        "addressLine2": [
                            {
                                "value": demographic_data.get('address', {}).get('city', ''),
                                "language": "eng"
                            }
                        ],
                        "city": [
                            {
                                "value": demographic_data.get('address', {}).get('city', ''),
                                "language": "eng"
                            }
                        ],
                        "region": [
                            {
                                "value": demographic_data.get('address', {}).get('state', ''),
                                "language": "eng"
                            }
                        ],
                        "postalCode": demographic_data.get('address', {}).get('postalCode', '')
                    },
                    "documentsMetadata": []
                }
            }
            
            logger.info(f"Creating application for {demographic_data.get('fullName', 'Unknown')}")
            
            headers = self.get_headers()
            
            response = requests.post(
                self.applications_endpoint,
                json=payload,
                headers=headers,
                verify=False,
                timeout=30
            )
            
            logger.info(f"Create Application Response Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                pre_reg_id = result.get('response', {}).get('preRegistrationId')
                logger.info(f"✅ Application created successfully: {pre_reg_id}")
                return {
                    'success': True,
                    'preRegistrationId': pre_reg_id,
                    'data': result,
                    'status_code': response.status_code
                }
            else:
                logger.error(f"Failed to create application: {response.text}")
                return {
                    'success': False,
                    'error': response.text,
                    'status_code': response.status_code
                }
        except Exception as e:
            logger.error(f"Error creating application: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def upload_document(self, pre_reg_id: str, file_path: str,
                       doc_type: str = "POI", doc_subtype: str = "Passport") -> Dict:
        """
        Upload document to pre-registration application
        
        Args:
            pre_reg_id: Pre-registration ID from create_application()
            file_path: Path to document file
            doc_type: Document type (POI, POA, etc.)
            doc_subtype: Document subtype (Passport, License, etc.)
        
        Returns:
            Dictionary with upload response
        """
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'error': f"File not found: {file_path}"}
            
            payload = {
                'id': self.doc_upload_id,
                'version': self.api_version,
                'requesttime': self._get_timestamp(),
                'preRegistrationId': pre_reg_id,
                'documentType': doc_type,
                'documentSubType': doc_subtype
            }
            
            with open(file_path, 'rb') as f:
                files = {'file': f}
                
                headers = {'Authorization': f'{self.token_type} {self.access_token}'} if self.access_token else {}
                
                response = requests.post(
                    self.documents_endpoint,
                    files=files,
                    data=payload,
                    headers=headers,
                    verify=False,
                    timeout=30
                )
                
                logger.info(f"Document upload status: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    logger.info(f"✅ Document uploaded for {pre_reg_id}")
                    return {'success': True, 'data': response.json()}
                else:
                    logger.error(f"Document upload failed: {response.text}")
                    return {'success': False, 'error': response.text}
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def book_appointment(self, pre_reg_id: str, center_id: str,
                        appointment_date: str, time_from: str, time_to: str) -> Dict:
        """
        Book appointment at registration center
        
        Args:
            pre_reg_id: Pre-registration ID
            center_id: Registration center ID
            appointment_date: Date in YYYY-MM-DD format
            time_from: Start time in HH:MM format
            time_to: End time in HH:MM format
        
        Returns:
            Dictionary with booking response
        """
        try:
            endpoint = f"{self.appointment_endpoint}/{pre_reg_id}"
            
            payload = {
                "id": self.appointment_book_id,
                "version": self.api_version,
                "requesttime": self._get_timestamp(),
                "request": {
                    "registration_center_id": center_id,
                    "appointment_date": appointment_date,
                    "time_slot_from": time_from,
                    "time_slot_to": time_to
                }
            }
            
            logger.info(f"Booking appointment for {pre_reg_id} on {appointment_date}")
            
            headers = self.get_headers()
            
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                verify=False,
                timeout=30
            )
            
            logger.info(f"Booking status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Appointment booked for {pre_reg_id}")
                return {'success': True, 'data': response.json()}
            else:
                logger.error(f"Appointment booking failed: {response.text}")
                return {'success': False, 'error': response.text}
        except Exception as e:
            logger.error(f"Error booking appointment: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_appointment_availability(self, center_id: str) -> Dict:
        """
        Get available appointment slots for a registration center
        
        Args:
            center_id: Registration center ID
        
        Returns:
            Dictionary with available slots
        """
        try:
            endpoint = f"{self.appointment_endpoint}/availability/{center_id}"
            
            headers = self.get_headers()
            
            response = requests.get(
                endpoint,
                headers=headers,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Availability fetched for center {center_id}")
                return {'success': True, 'data': response.json()}
            else:
                logger.error(f"Failed to get availability: {response.text}")
                return {'success': False, 'error': response.text}
        except Exception as e:
            logger.error(f"Error getting availability: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_application_status(self, pre_reg_id: str) -> Dict:
        """Get status of pre-registration application"""
        try:
            endpoint = f"{self.applications_endpoint}/{pre_reg_id}"
            
            headers = self.get_headers()
            
            response = requests.get(
                endpoint,
                headers=headers,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Application status retrieved: {pre_reg_id}")
                return {'success': True, 'data': response.json()}
            else:
                logger.error(f"Failed to get status: {response.text}")
                return {'success': False, 'error': response.text}
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_timestamp(self) -> str:
        """Get ISO 8601 timestamp for API requests"""
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        """
        Submit pre-registration data to MOSIP Pre-Registration API
        
        Args:
            resident_data: Dictionary containing resident demographic and document data
                          {
                              'fullName': str,
                              'dateOfBirth': str (YYYY-MM-DD),
                              'gender': str (M/F),
                              'mobileNumber': str,
                              'emailId': str,
                              'address': {
                                  'street': str,
                                  'city': str,
                                  'state': str,
                                  'postalCode': str,
                                  'country': str
                              },
                              'documents': [
                                  {
                                      'documentType': str (e.g., 'Passport', 'NationalID'),
                                      'documentNumber': str,
                                      'documentFileContent': base64_encoded_file
                                  }
                              ]
                          }
        
        Returns:
            Dictionary with API response
        """
        try:
            # Pre-Registration API endpoint
            endpoint = self.preregistration_endpoint
            
            logger.info(f"Submitting to MOSIP: {endpoint}")
            logger.debug(f"Data: {json.dumps(resident_data, indent=2)}")
            
            headers = self.get_headers()
            
            response = requests.post(
                endpoint,
                json=resident_data,
                headers=headers,
                verify=False,
                timeout=30
            )
            
            logger.info(f"MOSIP API Response Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"Pre-registration submitted successfully")
                return {
                    'success': True,
                    'data': result,
                    'registration_id': result.get('response', {}).get('preRegistrationId'),
                    'status_code': response.status_code
                }
            elif response.status_code == 401:
                logger.warning("Authentication required - Log in to MOSIP portal first")
                return {
                    'success': False,
                    'error': 'Authentication required. Please log in to MOSIP portal.',
                    'status_code': 401,
                    'instruction': 'Visit https://prereg.collab.mosip.net/ and log in with your credentials'
                }
            else:
                logger.error(f"Pre-registration submission failed: {response.text}")
                return {
                    'success': False,
                    'error': response.text,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Pre-registration error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_preregistration_status(self, pre_reg_id: str) -> Dict:
        """
        Get status of submitted pre-registration
        
        Args:
            pre_reg_id: Pre-registration ID returned from submission
            
        Returns:
            Dictionary with registration status
        """
        try:
            endpoint = f"{self.preregistration_endpoint}/{pre_reg_id}"
            
            headers = self.get_headers()
            
            response = requests.get(
                endpoint,
                headers=headers,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'status': result
                }
            else:
                logger.error(f"Failed to get status: {response.text}")
                return {
                    'success': False,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Status check error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_document(self, pre_reg_id: str, document_data: Dict) -> Dict:
        """
        Upload document for pre-registration
        
        Args:
            pre_reg_id: Pre-registration ID
            document_data: {
                'documentType': str,
                'documentFileContent': base64_encoded_file
            }
            
        Returns:
            Dictionary with upload response
        """
        try:
            endpoint = f"{self.base_url}/preregistration/v1/applications/{pre_reg_id}/documents"
            
            headers = self.get_headers()
            
            response = requests.post(
                endpoint,
                json=document_data,
                headers=headers,
                verify=False
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Document uploaded successfully")
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                logger.error(f"Document upload failed: {response.text}")
                return {
                    'success': False,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Document upload error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_resident(self, resident_data: Dict) -> Dict:
        """
        Verify resident data against MOSIP database
        
        Args:
            resident_data: Resident information to verify
            
        Returns:
            Verification result with match score
        """
        try:
            # This would call ID Authentication or ID Verification APIs
            endpoint = f"{self.base_url}/idauthentication/v1/verify"
            
            headers = self.get_headers()
            
            response = requests.post(
                endpoint,
                json=resident_data,
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'verification_result': result
                }
            else:
                logger.error(f"Verification failed: {response.text}")
                return {
                    'success': False,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
