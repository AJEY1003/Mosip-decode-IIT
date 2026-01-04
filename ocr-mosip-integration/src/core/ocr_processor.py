import cv2
import numpy as np
from PIL import Image
import easyocr
import pytesseract
from typing import Dict, List, Tuple
import re

class OCRProcessor:
    """
    Handles document image processing and text extraction using OCR
    """
    
    def __init__(self, engine='easyocr', language='en'):
        """
        Initialize OCR processor
        
        Args:
            engine: 'easyocr' or 'tesseract'
            language: Language code (default: English)
        """
        self.engine = engine
        self.language = language
        
        if engine == 'easyocr':
            self.reader = easyocr.Reader([language])
        elif engine == 'tesseract':
            # Tesseract path configuration for Windows
            pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image_path: Path to image file
            
        Returns:
            Processed image array
        """
        # Read image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)
        
        # Thresholding
        _, thresholded = cv2.threshold(enhanced, 150, 255, cv2.THRESH_BINARY)
        
        return thresholded
    
    def extract_text_easyocr(self, image_path: str) -> Dict:
        """
        Extract text using EasyOCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted text and confidence scores
        """
        img = cv2.imread(image_path)
        results = self.reader.readtext(img)
        
        extracted_data = {
            'raw_text': '',
            'structured_data': {},
            'confidence': 0.0,
            'details': []
        }
        
        # Combine all text
        all_text = []
        total_confidence = 0
        
        for (bbox, text, confidence) in results:
            all_text.append(text)
            total_confidence += confidence
            extracted_data['details'].append({
                'text': text,
                'confidence': float(confidence),  # Convert to Python float
                'bbox': [[float(x), float(y)] for x, y in bbox]  # Convert coordinates to Python floats
            })
        
        extracted_data['raw_text'] = '\n'.join(all_text)
        extracted_data['confidence'] = float(total_confidence / len(results)) if results else 0.0
        
        return extracted_data
    
    def extract_text_tesseract(self, image_path: str) -> Dict:
        """
        Extract text using Tesseract OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted text and confidence scores
        """
        img = Image.open(image_path)
        
        # Extract text with data
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        extracted_data = {
            'raw_text': pytesseract.image_to_string(img),
            'structured_data': {},
            'confidence': float(np.mean([int(c) for c in data['conf'] if int(c) > 0]) / 100) if any(int(c) > 0 for c in data['conf']) else 0.0,
            'details': []
        }
        
        return extracted_data
    
    def extract_text(self, image_path: str) -> Dict:
        """
        Extract text from image using configured engine
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted text
        """
        if self.engine == 'easyocr':
            return self.extract_text_easyocr(image_path)
        else:
            return self.extract_text_tesseract(image_path)
    
    def extract_id_fields(self, raw_text: str) -> Dict:
        """
        Parse and extract structured ID field data from raw OCR text
        Enhanced to handle multiple document types: Aadhaar, PAN, Form 16, Bank statements, etc.
        
        Args:
            raw_text: Raw text extracted from OCR
            
        Returns:
            Dictionary with extracted fields
        """
        extracted_fields = {
            'name': None,
            'date_of_birth': None,
            'gender': None,
            'id_number': None,
            'aadhaar_number': None,
            'pan_number': None,
            'address': None,
            'father_name': None,
            'mother_name': None,
            'issue_date': None,
            'expiry_date': None,
            'phone': None,
            'email': None,
            'income': None,
            'employer': None,
            'designation': None,
            'bank_name': None,
            'account_number': None,
            'ifsc_code': None,
            'document_type': None
        }
        
        lines = raw_text.split('\n')
        text_lower = raw_text.lower()
        
        # Detect document type
        if any(keyword in text_lower for keyword in ['aadhaar', 'aadhar', 'unique identification']):
            extracted_fields['document_type'] = 'Aadhaar Card'
        elif any(keyword in text_lower for keyword in ['permanent account number', 'pan card', 'income tax']):
            extracted_fields['document_type'] = 'PAN Card'
        elif any(keyword in text_lower for keyword in ['form 16', 'tds certificate', 'salary certificate']):
            extracted_fields['document_type'] = 'Form 16'
        elif any(keyword in text_lower for keyword in ['bank statement', 'account statement', 'balance']):
            extracted_fields['document_type'] = 'Bank Statement'
        
        # Extract Aadhaar number (12 digits)
        aadhaar_patterns = [
            r'\b\d{4}\s*\d{4}\s*\d{4}\b',  # XXXX XXXX XXXX format
            r'\b\d{12}\b'  # XXXXXXXXXXXX format
        ]
        for pattern in aadhaar_patterns:
            aadhaar_match = re.search(pattern, raw_text)
            if aadhaar_match:
                aadhaar_num = re.sub(r'\s+', '', aadhaar_match.group())
                if len(aadhaar_num) == 12 and aadhaar_num.isdigit():
                    extracted_fields['aadhaar_number'] = aadhaar_num
                    extracted_fields['id_number'] = aadhaar_num
                    break
        
        # Extract PAN number (ABCDE1234F format)
        pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
        pan_match = re.search(pan_pattern, raw_text)
        if pan_match:
            extracted_fields['pan_number'] = pan_match.group()
            if not extracted_fields['id_number']:
                extracted_fields['id_number'] = pan_match.group()
        
        # Extract phone number (various formats)
        phone_patterns = [
            r'\b(?:\+91[\s-]?)?[6-9]\d{9}\b',  # Indian mobile numbers
            r'\b0\d{2,4}[\s-]?\d{6,8}\b'  # Landline numbers
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, raw_text)
            if phone_match:
                phone_num = re.sub(r'[\s-]', '', phone_match.group())
                extracted_fields['phone'] = phone_num
                break
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, raw_text)
        if email_match:
            extracted_fields['email'] = email_match.group()
        
        # Extract dates (multiple formats)
        date_patterns = [
            r'\b(0[1-9]|[12][0-9]|3[01])[/-](0[1-9]|1[012])[/-](19|20)\d\d\b',  # DD/MM/YYYY
            r'\b(19|20)\d\d[/-](0[1-9]|1[012])[/-](0[1-9]|[12][0-9]|3[01])\b',  # YYYY/MM/DD
            r'\b(0[1-9]|[12][0-9]|3[01])\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(19|20)\d\d\b'  # DD Mon YYYY
        ]
        
        for pattern in date_patterns:
            date_matches = re.findall(pattern, raw_text, re.IGNORECASE)
            if date_matches:
                if isinstance(date_matches[0], tuple):
                    if len(date_matches[0]) == 3:
                        extracted_fields['date_of_birth'] = '/'.join(date_matches[0])
                else:
                    extracted_fields['date_of_birth'] = date_matches[0]
                break
        
        # Extract gender
        gender_patterns = [
            (r'\b(?:gender|sex)[\s:]*(?:male|m)\b', 'M'),
            (r'\b(?:gender|sex)[\s:]*(?:female|f)\b', 'F'),
            (r'\bmale\b(?!\s*(?:female|f))', 'M'),
            (r'\bfemale\b', 'F')
        ]
        
        for pattern, gender_value in gender_patterns:
            if re.search(pattern, text_lower):
                extracted_fields['gender'] = gender_value
                break
        
        # Extract names (multiple strategies)
        name_patterns = [
            r'(?:name|full\s*name|holder\s*name)[\s:]+([A-Za-z\s\.]+?)(?:\n|$|[0-9])',
            r'(?:mr|ms|mrs)\.?\s+([A-Za-z\s\.]+?)(?:\n|$|[0-9])',
            r'(?:son|daughter|wife)\s+of[\s:]+([A-Za-z\s\.]+?)(?:\n|$)',
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*$'  # Capitalized words on their own line
        ]
        
        for pattern in name_patterns:
            name_matches = re.findall(pattern, raw_text, re.IGNORECASE | re.MULTILINE)
            if name_matches:
                for name_candidate in name_matches:
                    name_value = name_candidate.strip()
                    # Clean up the name
                    name_value = re.sub(r'\s+', ' ', name_value)
                    name_value = ''.join(c for c in name_value if c.isalpha() or c.isspace()).strip()
                    
                    # Validate name (should be 2-50 characters, mostly letters)
                    if 2 <= len(name_value) <= 50 and len(name_value.split()) >= 1:
                        # Avoid common false positives
                        false_positives = ['government', 'india', 'card', 'number', 'date', 'birth', 'address']
                        if not any(fp in name_value.lower() for fp in false_positives):
                            extracted_fields['name'] = name_value
                            break
            if extracted_fields['name']:
                break
        
        # Extract father's/mother's name
        parent_patterns = [
            r'(?:father|father\'s\s*name|s/o)[\s:]+([A-Za-z\s\.]+?)(?:\n|$)',
            r'(?:mother|mother\'s\s*name|d/o|w/o)[\s:]+([A-Za-z\s\.]+?)(?:\n|$)'
        ]
        
        for i, pattern in enumerate(parent_patterns):
            parent_match = re.search(pattern, raw_text, re.IGNORECASE)
            if parent_match:
                parent_name = parent_match.group(1).strip()
                parent_name = ''.join(c for c in parent_name if c.isalpha() or c.isspace()).strip()
                if len(parent_name) > 2:
                    if i == 0:
                        extracted_fields['father_name'] = parent_name
                    else:
                        extracted_fields['mother_name'] = parent_name
        
        # Extract address
        address_patterns = [
            r'(?:address|addr)[\s:]+([A-Za-z0-9\s,.-]+?)(?:\n\n|\n[A-Z]|$)',
            r'(?:house|h\.?\s*no|flat)[\s:]+([A-Za-z0-9\s,.-]+?)(?:\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in address_patterns:
            address_match = re.search(pattern, raw_text, re.IGNORECASE | re.DOTALL)
            if address_match:
                address = address_match.group(1).strip()
                if len(address) > 10:  # Reasonable address length
                    extracted_fields['address'] = address
                    break
        
        # Extract income/salary information
        income_patterns = [
            r'(?:gross\s*salary|total\s*income|annual\s*income)[\s:]*(?:rs\.?|₹)?\s*([0-9,]+)',
            r'(?:salary|income)[\s:]*(?:rs\.?|₹)?\s*([0-9,]+)',
            r'₹\s*([0-9,]+)',  # Currency symbol pattern
            r'rs\.?\s*([0-9,]+)',  # Rs. pattern
            r'([0-9]{2,3},[0-9]{2,3},[0-9]{3})'  # Indian number format like 12,00,000
        ]
        
        for pattern in income_patterns:
            income_matches = re.findall(pattern, raw_text, re.IGNORECASE)
            if income_matches:
                for match in income_matches:
                    income_value = match.replace(',', '') if isinstance(match, str) else str(match).replace(',', '')
                    if income_value.isdigit() and len(income_value) >= 4:  # Reasonable income amount
                        extracted_fields['income'] = income_value
                        break
                if extracted_fields['income']:
                    break
        
        # Extract designation/job title
        designation_patterns = [
            r'(?:designation|position|job\s*title)[\s:]+([A-Za-z\s&\.]+?)(?:\n|$)',
            r'(?:working\s*as|employed\s*as)[\s:]+([A-Za-z\s&\.]+?)(?:\n|$)',
            r'(?:senior|junior|lead|principal|chief)?\s*(?:software|data|system|network|web)?\s*(?:engineer|developer|analyst|manager|architect|consultant)'
        ]
        
        for pattern in designation_patterns:
            designation_match = re.search(pattern, raw_text, re.IGNORECASE)
            if designation_match:
                if len(designation_match.groups()) > 0:
                    designation = designation_match.group(1).strip()
                else:
                    designation = designation_match.group(0).strip()
                if len(designation) > 2 and len(designation) < 50:
                    extracted_fields['designation'] = designation
                    break
        
        # Extract employer information
        employer_patterns = [
            r'(?:employer|company|organization)[\s:]+([A-Za-z\s&\.]+?)(?:\n|$)',
            r'(?:working\s*at|employed\s*with)[\s:]+([A-Za-z\s&\.]+?)(?:\n|$)'
        ]
        
        for pattern in employer_patterns:
            employer_match = re.search(pattern, raw_text, re.IGNORECASE)
            if employer_match:
                employer = employer_match.group(1).strip()
                if len(employer) > 2:
                    extracted_fields['employer'] = employer
                    break
        
        # Extract bank details
        bank_patterns = [
            r'(?:bank\s*name|bank)[\s:]+([A-Za-z\s&\.]+?)(?:\n|$)',
            r'(?:account\s*number|a/c\s*no)[\s:]+([0-9]+)',
            r'(?:ifsc|ifsc\s*code)[\s:]+([A-Z]{4}[0-9]{7})'
        ]
        
        bank_match = re.search(bank_patterns[0], raw_text, re.IGNORECASE)
        if bank_match:
            extracted_fields['bank_name'] = bank_match.group(1).strip()
        
        account_match = re.search(bank_patterns[1], raw_text, re.IGNORECASE)
        if account_match:
            extracted_fields['account_number'] = account_match.group(1)
        
        ifsc_match = re.search(bank_patterns[2], raw_text, re.IGNORECASE)
        if ifsc_match:
            extracted_fields['ifsc_code'] = ifsc_match.group(1)
        
        return extracted_fields
    
    def process_document(self, image_path: str) -> Dict:
        """
        Complete document processing: extract text and parse fields
        
        Args:
            image_path: Path to document image
            
        Returns:
            Dictionary with extracted text and parsed fields
        """
        # Extract raw text
        result = self.extract_text(image_path)
        
        # Parse structured fields
        result['structured_data'] = self.extract_id_fields(result['raw_text'])
        
        return result
    
    def get_confidence_score(self, image_path: str) -> float:
        """
        Get confidence score for OCR extraction
        
        Args:
            image_path: Path to image file
            
        Returns:
            Average confidence score
        """
        try:
            result = self.extract_text(image_path)
            return result.get('confidence', 0.0)
        except Exception:
            return 0.0
