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
                'confidence': confidence,
                'bbox': bbox
            })
        
        extracted_data['raw_text'] = '\n'.join(all_text)
        extracted_data['confidence'] = total_confidence / len(results) if results else 0
        
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
            'confidence': np.mean([int(c) for c in data['conf'] if int(c) > 0]) / 100,
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
            'address': None,
            'father_name': None,
            'issue_date': None,
            'expiry_date': None,
            'phone': None,
            'email': None
        }
        
        lines = raw_text.split('\n')
        text_lower = raw_text.lower()
        
        # Attempt to extract phone number
        phone_pattern = r'\b(?:\+91|0)?[6-9]\d{9}\b'
        phone_match = re.search(phone_pattern, raw_text)
        if phone_match:
            extracted_fields['phone'] = phone_match.group()
        
        # Attempt to extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, raw_text)
        if email_match:
            extracted_fields['email'] = email_match.group()
        
        # Attempt to extract dates (DD/MM/YYYY format)
        date_pattern = r'\b(0[1-9]|[12][0-9]|3[01])[/-](0[1-9]|1[012])[/-](19|20)\d\d\b'
        date_matches = re.findall(date_pattern, raw_text)
        if date_matches:
            extracted_fields['date_of_birth'] = '/'.join(date_matches[0])
        
        # Extract gender if mentioned
        if 'male' in text_lower:
            extracted_fields['gender'] = 'M'
        elif 'female' in text_lower:
            extracted_fields['gender'] = 'F'
        
        # Try to extract name from lines with "name" label
        name_pattern = r'(?:full\s*name|name):\s*([A-Za-z\s\.]+?)(?:\n|$)'
        name_match = re.search(name_pattern, raw_text, re.IGNORECASE)
        if name_match:
            name_value = name_match.group(1).strip()
            # Clean up - remove any partial words or labels that might have been captured
            name_value = name_value.split('\n')[0].strip()
            # Only keep alphabetic characters and spaces
            name_value = ''.join(c for c in name_value if c.isalpha() or c.isspace()).strip()
            if name_value:
                extracted_fields['name'] = name_value
        else:
            # Fallback: try to extract name from first few lines
            for line in lines[:5]:
                cleaned_line = line.strip()
                # Remove common labels like "Full Name:", "Name:", etc.
                if ':' in cleaned_line:
                    cleaned_line = cleaned_line.split(':', 1)[1].strip()
                
                # Check if it looks like a name (mostly letters with possible spaces)
                if len(cleaned_line) > 3 and all(c.isalpha() or c.isspace() for c in cleaned_line):
                    extracted_fields['name'] = cleaned_line
                    break
        
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
