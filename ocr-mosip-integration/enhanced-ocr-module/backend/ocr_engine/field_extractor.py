import re
from typing import Dict, List, Any, Optional
from config.settings import FIELD_KEYWORDS, VALIDATION_PATTERNS


class FieldExtractor:
    """
    Extract structured fields from OCR text using keyword anchoring and regex
    """
    
    def __init__(self):
        self.field_keywords = FIELD_KEYWORDS
        self.validation_patterns = VALIDATION_PATTERNS
    
    def extract_fields(self, text: str) -> Dict[str, Any]:
        """
        Extract structured fields from OCR text
        """
        extracted_fields = {}
        
        # Extract name
        extracted_fields['name'] = self._extract_name(text)
        
        # Extract date of birth
        extracted_fields['dob'] = self._extract_date_of_birth(text)
        
        # Extract ID number
        extracted_fields['id_number'] = self._extract_id_number(text)
        
        # Extract address
        extracted_fields['address'] = self._extract_address(text)
        
        # Extract document type
        extracted_fields['document_type'] = self._extract_document_type(text)
        
        # Clean up empty fields
        cleaned_fields = {k: v for k, v in extracted_fields.items() if v}
        
        return cleaned_fields
    
    def _extract_name(self, text: str) -> Optional[str]:
        """
        Extract name using keywords and pattern recognition
        """
        text_lower = text.lower()
        
        # Look for name keywords
        for keyword in self.field_keywords['name']:
            pattern = rf'{re.escape(keyword)}[.:]?\s*([A-Z][a-zA-Z\s]+)'
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Return the first match that looks like a name (not too long)
                for match in matches:
                    name = match.strip()
                    if 5 <= len(name) <= 50 and len(name.split()) >= 2:
                        return name.title()
        
        # If no keyword found, look for potential names in the text
        # Look for capitalized words that might be names
        potential_names = re.findall(r'\b([A-Z][a-z]{2,}\s+[A-Z][a-z]{2,})\b', text)
        if potential_names:
            return potential_names[0].title()
        
        return None
    
    def _extract_date_of_birth(self, text: str) -> Optional[str]:
        """
        Extract date of birth using various formats
        """
        # Common date patterns
        patterns = [
            r'(?:date of birth|birth date|dob|d\.o\.b\.?|birth)\s*[:\-]?\s*(\d{2}[\/\-\s]\d{2}[\/\-\s]\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(?:date of birth|birth date|dob|d\.o\.b\.?|birth)\s*[:\-]?\s*(\d{4}[\/\-\s]\d{2}[\/\-\s]\d{2})',  # YYYY/MM/DD
            r'(?:date of birth|birth date|dob|d\.o\.b\.?|birth)\s*[:\-]?\s*(\d{1,2}[a-z]{2}\s+[a-z]+\s+\d{4})',  # 12th Jan 1990
            r'(\d{2}[\/\-\s]\d{2}[\/\-\s]\d{4})',  # General date format
            r'(\d{4}[\/\-\s]\d{2}[\/\-\s]\d{2})',  # General date format (YYYY-MM-DD)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Validate and format the date
                for match in matches:
                    formatted_date = self._format_date(match)
                    if formatted_date:
                        return formatted_date
        
        return None
    
    def _format_date(self, date_str: str) -> Optional[str]:
        """
        Format date string to YYYY-MM-DD format
        """
        # Remove extra spaces and normalize separators
        date_str = re.sub(r'[\s]+', ' ', date_str.strip())
        date_str = re.sub(r'[\/\-\s]+', '-', date_str)
        
        # Handle different formats
        parts = date_str.split('-')
        
        if len(parts) == 3:
            day, month, year = parts[0], parts[1], parts[2]
            
            # Check if it's DD-MM-YYYY or MM-DD-YYYY format
            # Usually DOB has year as 4 digits at the end
            if len(year) == 4 and year.isdigit():
                # Format: DD-MM-YYYY or MM-DD-YYYY (assuming DD-MM-YYYY)
                day = day.zfill(2)
                month = month.zfill(2)
                year = year.zfill(4)
                return f"{year}-{month}-{day}"
            elif len(parts[0]) == 4 and parts[0].isdigit():
                # Format: YYYY-MM-DD
                year = parts[0].zfill(4)
                month = parts[1].zfill(2)
                day = parts[2].zfill(2)
                return f"{year}-{month}-{day}"
        
        return None
    
    def _extract_id_number(self, text: str) -> Optional[str]:
        """
        Extract ID number (PAN, Aadhaar, Passport, etc.)
        """
        text_upper = text.upper()
        
        # Look for ID keywords
        for keyword in self.field_keywords['id_number']:
            pattern = rf'{re.escape(keyword)}[.:]?\s*([A-Z0-9\s\-]+)'
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    id_candidate = re.sub(r'[\s\-]+', '', match.strip())
                    if self._validate_id_format(id_candidate):
                        return id_candidate
        
        # Look for potential ID numbers without keywords
        # PAN pattern
        pan_matches = re.findall(r'[A-Z]{5}[0-9]{4}[A-Z]', text_upper)
        if pan_matches:
            return pan_matches[0]
        
        # Aadhaar pattern
        aadhaar_matches = re.findall(r'\d{4}\s?\d{4}\s?\d{4}', text)
        if aadhaar_matches:
            return aadhaar_matches[0].replace(' ', '')
        
        # Passport pattern
        passport_matches = re.findall(r'[A-Z]{1}[0-9]{7}', text_upper)
        if passport_matches:
            return passport_matches[0]
        
        return None
    
    def _validate_id_format(self, id_number: str) -> bool:
        """
        Validate ID number format
        """
        id_number_clean = re.sub(r'[\s\-]+', '', id_number)
        
        # Check against known patterns
        for pattern_name, pattern in self.validation_patterns.items():
            if pattern_name in ['pan', 'aadhaar', 'passport']:
                if re.match(pattern, id_number_clean, re.IGNORECASE):
                    return True
        
        return False
    
    def _extract_address(self, text: str) -> Optional[str]:
        """
        Extract address using keywords and context
        """
        text_lower = text.lower()
        
        # Look for address keywords
        for keyword in self.field_keywords['address']:
            # Look for address after keyword
            pattern = rf'{re.escape(keyword)}[.:]?\s*([A-Za-z0-9\s,#\-\.]+?)(?:\n|$|(?=\n[A-Z]))'
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                address = matches[0].strip()
                if len(address) > 10:  # Address should be reasonably long
                    return address
        
        # If no keyword found, look for potential addresses
        # Look for patterns that might indicate addresses
        # This is a simplified approach - real implementation would need more sophisticated NLP
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 15:  # Reasonable length for address
                # Check if line contains common address indicators
                if any(indicator in line.lower() for indicator in ['street', 'road', 'lane', 'colony', 'nagar', 'marg', 'house', 'flat', 'building', 'city', 'state', 'pin', 'zip']):
                    return line
        
        return None
    
    def _extract_document_type(self, text: str) -> Optional[str]:
        """
        Extract document type
        """
        text_lower = text.lower()
        
        # Common document types
        doc_types = {
            'aadhaar': ['aadhaar', 'uidai'],
            'pan': ['pan', 'permanent account number'],
            'passport': ['passport'],
            'driving_license': ['driving license', 'dl'],
            'voter_id': ['voter id', 'epic'],
            'ration_card': ['ration card', 'pds'],
            'bank_statement': ['bank statement'],
            'income_tax': ['income tax', 'itr'],
            'salary_slip': ['salary slip', 'pay slip'],
        }
        
        for doc_type, keywords in doc_types.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return doc_type.title().replace('_', ' ')
        
        return None
    
    def extract_with_bounding_boxes(self, text: str, bounding_boxes: List[Dict]) -> Dict[str, Any]:
        """
        Extract fields using bounding box information for more accurate positioning
        """
        # This would be implemented when bounding box data is available
        # For now, we'll use the text-based extraction
        return self.extract_fields(text)


# Example usage
if __name__ == "__main__":
    extractor = FieldExtractor()
    
    sample_text = """
    Permanent Account Number (PAN) Card
    Name: RAMESH KUMAR
    Date of Birth: 12-04-1999
    PAN: ABCDE1234F
    Father's Name: SHYAM LAL
    """
    
    extracted = extractor.extract_fields(sample_text)
    print("Extracted fields:", extracted)