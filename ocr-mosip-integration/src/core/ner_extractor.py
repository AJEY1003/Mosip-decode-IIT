"""
NER-based Field Extractor for ITR Documents
Extracts structured data from OCR text using pattern matching and NER techniques
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)

class ITRNERExtractor:
    """
    Named Entity Recognition extractor specifically designed for ITR documents
    """
    
    def __init__(self):
        # ITR-specific field patterns with multiple variations
        self.patterns = {
            # Personal Information
            'name': [
                # Most specific patterns first - exact "Name:" label match
                r'Name\s*:\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})(?=\s*\n|\s*$|\s*PAN|\s*Aadhaar)',  # "Name: Rajesh Kumar Sharma" followed by newline/PAN/Aadhaar
                r'name\s*:\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})(?=\s*\n|\s*$|\s*PAN|\s*Aadhaar)',  # Case insensitive
                r'Full\s*Name\s*:\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})(?=\s*\n|\s*$)',  # "Full Name: ..."
                r'Applicant\s*Name\s*:\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})(?=\s*\n|\s*$)',  # "Applicant Name: ..."
                r'Taxpayer\s*Name\s*:\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})(?=\s*\n|\s*$)',  # "Taxpayer Name: ..."
                # Avoid document titles by requiring proper name format and context
                r'(?:Mr\.?\s+|Ms\.?\s+|Mrs\.?\s+)?([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)(?=\s*,\s*solemnly\s*declare)',  # From declaration section
                # Last resort - proper name format only (3 words minimum to avoid titles)
                r'([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)(?=\s*\n\s*PAN|\s*\n\s*Aadhaar)'  # 3-word names followed by PAN/Aadhaar
            ],
            
            'pan': [
                r'pan[:\s]*([A-Z]{5}[0-9]{4}[A-Z]{1})',
                r'permanent\s*account\s*number[:\s]*([A-Z]{5}[0-9]{4}[A-Z]{1})',
                r'\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b'
            ],
            
            'aadhaar': [
                r'aadhaar[:\s]*(\d{4}\s*\d{4}\s*\d{4})',
                r'aadhar[:\s]*(\d{4}\s*\d{4}\s*\d{4})',
                r'uid[:\s]*(\d{4}\s*\d{4}\s*\d{4})',
                r'\b(\d{4}\s*\d{4}\s*\d{4})\b'
            ],
            
            'date_of_birth': [
                r'date\s*of\s*birth[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
                r'dob[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
                r'birth\s*date[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
                r'born[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
                # Additional date formats
                r'date\s*of\s*birth[:\s]*(\d{1,2}\s+\w+\s+\d{4})',  # 15 March 1990
                r'dob[:\s]*(\d{1,2}\s+\w+\s+\d{4})',
                r'birth\s*date[:\s]*(\d{1,2}\s+\w+\s+\d{4})',
                r'date\s*of\s*birth[:\s]*(\w+\s+\d{1,2},?\s+\d{4})',  # March 15, 1990
                r'dob[:\s]*(\w+\s+\d{1,2},?\s+\d{4})',
                r'birth\s*date[:\s]*(\w+\s+\d{1,2},?\s+\d{4})',
                # Indian format variations
                r'date\s*of\s*birth[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2})',  # DD/MM/YY
                r'dob[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2})',
                # Flexible date patterns
                r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',  # Generic date pattern
                r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4})',  # 15 Jan 1990
                r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2},?\s+\d{4})'  # Jan 15, 1990
            ],
            
            # Financial Information
            'gross_salary': [
                r'gross\s*salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'total\s*salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'annual\s*salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'gross\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                # Enhanced patterns for different formats
                r'gross\s+salary\s+₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # "Gross Salary ₹ 8,50,000"
                r'gross\s+income:\s*(\d+(?:,\d+)*(?:\.\d{2})?)',      # "Gross Income: 850,000"
                r'total\s+income\s+₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # "Total Income ₹ 8,50,000"
                r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s+₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s+₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)'  # Table format
            ],
            
            'basic_salary': [
                r'basic\s*salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'basic\s*pay[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'basic[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                # Enhanced patterns for Form-16 format
                r'basic\s+salary\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # "Basic Salary 6,00,000"
                r'basic\s+salary\s+(\d+(?:,\d+)*(?:\.\d{2})?)',       # "Basic Salary 600000"
                r'basic\s+pay\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',    # "Basic Pay ₹ 6,00,000"
            ],
            
            'hra_received': [
                r'hra\s*received[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'house\s*rent\s*allowance[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'hra[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                # Enhanced patterns for Form-16 format
                r'hra\s+received\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # "HRA Received 2,40,000"
                r'hra\s+received\s+(\d+(?:,\d+)*(?:\.\d{2})?)',       # "HRA Received 240000"
                r'house\s+rent\s+allowance\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # "House Rent Allowance ₹ 2,40,000"
            ],
            
            'other_allowances': [
                r'other\s*allowances[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'other\s*allowance[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'allowances[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'miscellaneous\s*allowances[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                # Enhanced patterns for Form-16 format
                r'other\s+allowances\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # "Other Allowances 1,10,000"
                r'other\s+allowances\s+(\d+(?:,\d+)*(?:\.\d{2})?)',       # "Other Allowances 110000"
                r'miscellaneous\s+allowances\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # "Miscellaneous Allowances ₹ 1,10,000"
            ],
            
            'professional_tax': [
                r'professional\s*tax[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'prof\s*tax[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'pt[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                # Enhanced patterns for Form-16 format
                r'professional\s+tax\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # "Professional Tax 2,400"
                r'professional\s+tax\s+(\d+(?:,\d+)*(?:\.\d{2})?)',       # "Professional Tax 2400"
            ],
            
            'tds_deducted': [
                # Most specific patterns first - these should get higher confidence
                r'tds\s+deducted:\s*रे\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # "TDS Deducted: रे 75,000"
                r'tds\s+deducted:\s*₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # "TDS Deducted: ₹ 75,000"
                # Avoid multiline matches by being more restrictive
                r'tds\s*deducted[ \t]*:[ \t]*₹?[ \t]*(\d+(?:,\d+)*(?:\.\d{2})?)',  # Same line only
                r'tax\s*deducted[ \t]*:[ \t]*₹?[ \t]*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'deducted\s*tax[ \t]*:[ \t]*₹?[ \t]*(\d+(?:,\d+)*(?:\.\d{2})?)',
            ],
            
            'total_income': [
                r'total\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'gross\s*total\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'annual\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'taxable\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                # Enhanced patterns
                r'total\s+income\s+₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)',   # "Total Income ₹ 8,50,000"
                r'net\s+income:\s*&\s*(\d+(?:,\d+)*(?:\.\d{2})?)',    # "Net Income: & 7,75,000"
                r'net\s+income:\s*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',   # "Net Income: 7,75,000"
            ],
            
            # Bank Information
            'account_number': [
                r'account\s*number[:\s]*(\d{9,18})',
                r'bank\s*account[:\s]*(\d{9,18})',
                r'a\/c\s*no[:\s]*(\d{9,18})',
                r'account[:\s]*(\d{9,18})'
            ],
            
            'ifsc': [
                r'ifsc[:\s]*([A-Z]{4}0[A-Z0-9]{6})',
                r'ifsc\s*code[:\s]*([A-Z]{4}0[A-Z0-9]{6})',
                r'swift[:\s]*([A-Z]{4}0[A-Z0-9]{6})',
                r'\b([A-Z]{4}0[A-Z0-9]{6})\b'
            ],
            
            'bank_name': [
                r'bank\s*name[:\s]*([A-Za-z\s&\.]+?)(?:\n|$|ifsc)',
                r'bank[:\s]*([A-Za-z\s&\.]+?)(?:\n|$|ifsc)',
                r'(state bank of india|sbi|hdfc|icici|axis|pnb|canara|union bank)',
            ],
            
            # Employer Information
            'employer': [
                # Most specific patterns first - exclude the label itself
                r'Employer\s*Name\s*:\s*([A-Za-z\s&\.\-]+?)(?=\s*\n|\s*TAN|\s*Employer\s*TAN|\s*$)',  # "Employer Name: XYZ Private Limited"
                r'Employer\s*:\s*([A-Za-z\s&\.\-]+?)(?=\s*\n|\s*TAN|\s*Employer\s*TAN|\s*$)',  # "Employer: XYZ Private Limited"
                r'employer\s*name\s*:\s*([A-Za-z\s&\.\-]+?)(?=\s*\n|\s*TAN|\s*$)',  # Case insensitive
                r'employer\s*:\s*([A-Za-z\s&\.\-]+?)(?=\s*\n|\s*TAN|\s*$)',  # Case insensitive
                r'Company\s*Name\s*:\s*([A-Za-z\s&\.\-]+?)(?=\s*\n|\s*TAN|\s*$)',  # "Company Name: ..."
                r'Company\s*:\s*([A-Za-z\s&\.\-]+?)(?=\s*\n|\s*TAN|\s*$)',  # "Company: ..."
                r'Organization\s*:\s*([A-Za-z\s&\.\-]+?)(?=\s*\n|\s*TAN|\s*$)',  # "Organization: ..."
                r'Firm\s*:\s*([A-Za-z\s&\.\-]+?)(?=\s*\n|\s*TAN|\s*$)',  # "Firm: ..."
                r'Deductor\s*:\s*([A-Za-z\s&\.\-]+?)(?=\s*\n|\s*TAN|\s*$)',  # "Deductor: ..."
                # Generic patterns with better boundaries - avoid capturing labels
                r'(?:Employer\s+Name\s+|Company\s+Name\s+)?([A-Z][A-Za-z\s&\.\-]+(?:Private\s+Limited|Pvt\.?\s+Ltd\.?|Limited|Ltd\.?|Corporation|Corp\.?|Company|Co\.?))(?=\s*\n|\s*TAN|\s*$)'  # Company name patterns
            ],
            
            # Address Information
            'address': [
                r'address[:\s]*([A-Za-z0-9\s,\-\.]+?)(?:\n\n|\d{6})',
                r'residential\s*address[:\s]*([A-Za-z0-9\s,\-\.]+?)(?:\n\n|\d{6})',
                r'permanent\s*address[:\s]*([A-Za-z0-9\s,\-\.]+?)(?:\n\n|\d{6})',
                r'correspondence\s*address[:\s]*([A-Za-z0-9\s,\-\.]+?)(?:\n\n|\d{6})'
            ],
            
            'pincode': [
                r'pin\s*code[:\s]*(\d{6})',
                r'pincode[:\s]*(\d{6})',
                r'postal\s*code[:\s]*(\d{6})',
                r'\b(\d{6})\b'
            ],
            
            # Contact Information
            'mobile': [
                r'mobile[:\s]*(\+?91\s*\d{10})',
                r'phone[:\s]*(\+?91\s*\d{10})',
                r'contact[:\s]*(\+?91\s*\d{10})',
                r'tel[:\s]*(\+?91\s*\d{10})',
                r'\b(\+?91\s*\d{10})\b'
            ],
            
            'email': [
                r'email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'e-mail[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
            ],
            
            # Assessment Year
            'assessment_year': [
                r'assessment\s*year[:\s]*(\d{4}-\d{2})',
                r'ay[:\s]*(\d{4}-\d{2})',
                r'a\.y[:\s]*(\d{4}-\d{2})',
                r'(\d{4}-\d{2})'
            ],
            
            'financial_year': [
                r'financial\s*year[:\s]*(\d{4}-\d{2})',
                r'fy[:\s]*(\d{4}-\d{2})',
                r'f\.y[:\s]*(\d{4}-\d{2})'
            ],
            
            # Form 16 specific fields
            'tan': [
                r'tan[:\s]*([A-Z]{4}[0-9]{5}[A-Z]{1})',
                r'tax\s*deduction\s*account\s*number[:\s]*([A-Z]{4}[0-9]{5}[A-Z]{1})',
                r'\b([A-Z]{4}[0-9]{5}[A-Z]{1})\b'
            ],
            
            'cin': [
                r'cin[:\s]*([A-Z]{1}[0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6})',
                r'corporate\s*identification\s*number[:\s]*([A-Z]{1}[0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6})'
            ]
        }
        
        # Field confidence weights
        self.confidence_weights = {
            'exact_match': 1.0,
            'pattern_match': 0.8,
            'context_match': 0.6,
            'fuzzy_match': 0.4
        }
        
        # Field validation rules
        self.validation_rules = {
            'pan': r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',
            'aadhaar': r'^\d{4}\s\d{4}\s\d{4}$',
            'ifsc': r'^[A-Z]{4}0[A-Z0-9]{6}$',
            'email': r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
            'mobile': r'^\+?91\s*\d{10}$',
            'pincode': r'^\d{6}$',
            'account_number': r'^\d{9,18}$',
            'tan': r'^[A-Z]{4}[0-9]{5}[A-Z]{1}$',
            'cin': r'^[A-Z]{1}[0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$',
            'date_of_birth': r'^\d{4}-\d{2}-\d{2}$|^\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4}$|^\d{1,2}\s+\w+\s+\d{4}$'
        }
    
    def extract_structured_data(self, text: str, document_type: str = 'ITR') -> Dict[str, Any]:
        """
        Extract structured data from OCR text using NER patterns
        
        Args:
            text: Raw OCR text
            document_type: Type of document (ITR, Form16, etc.)
            
        Returns:
            Dictionary containing extracted fields with confidence scores
        """
        if not text or not isinstance(text, str):
            return {
                'extracted_fields': {},
                'confidence_scores': {},
                'overall_confidence': 0.0,
                'metadata': {
                    'error': 'Invalid input text',
                    'document_type': document_type,
                    'extraction_timestamp': datetime.now().isoformat()
                }
            }
        
        logger.info(f"🔍 Starting NER extraction for {document_type} document")
        logger.info(f"📄 Text length: {len(text)} characters")
        
        # Clean and normalize text
        clean_text = self._clean_text(text)
        
        # Extract fields
        extracted_fields = {}
        confidence_scores = {}
        extraction_metadata = []
        
        for field_name, patterns in self.patterns.items():
            result = self._extract_field(clean_text, field_name, patterns)
            if result['value']:
                # Apply date normalization for date_of_birth field
                if field_name == 'date_of_birth':
                    normalized_date = self._normalize_date(result['value'])
                    extracted_fields[field_name] = normalized_date
                    logger.info(f"📅 Date normalized: '{result['value']}' -> '{normalized_date}'")
                else:
                    extracted_fields[field_name] = result['value']
                
                confidence_scores[field_name] = result['confidence']
                extraction_metadata.append({
                    'field': field_name,
                    'pattern_used': result['pattern_used'],
                    'confidence': result['confidence'],
                    'raw_match': result['raw_match']
                })
                logger.info(f"✅ Extracted {field_name}: {result['value']} (confidence: {result['confidence']:.2f})")
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(confidence_scores)
        
        # Validate and clean fields
        validated_fields = self._validate_fields(extracted_fields)
        
        # Create metadata
        metadata = {
            'document_type': document_type,
            'text_length': len(text),
            'extraction_timestamp': datetime.now().isoformat(),
            'fields_extracted': len(validated_fields),
            'total_patterns_tried': sum(len(patterns) for patterns in self.patterns.values()),
            'successful_extractions': extraction_metadata
        }
        
        logger.info(f"🎯 NER Extraction Complete:")
        logger.info(f"   📊 Fields extracted: {len(validated_fields)}")
        logger.info(f"   🎯 Overall confidence: {overall_confidence:.2f}")
        logger.info(f"   ✅ Validated fields: {list(validated_fields.keys())}")
        
        return {
            'extracted_fields': validated_fields,
            'confidence_scores': confidence_scores,
            'overall_confidence': overall_confidence,
            'metadata': metadata
        }
    
    def _extract_field(self, text: str, field_name: str, patterns: List[str]) -> Dict[str, Any]:
        """Extract a specific field using multiple patterns"""
        best_match = None
        highest_confidence = 0.0
        pattern_used = None
        raw_match = None
        
        for pattern in patterns:
            try:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    value = match.group(1) if match.groups() else match.group(0)
                    confidence = self._calculate_field_confidence(field_name, value, pattern)
                    
                    if confidence > highest_confidence:
                        best_match = value
                        highest_confidence = confidence
                        pattern_used = pattern
                        raw_match = match.group(0)
                        
            except re.error as e:
                logger.warning(f"Invalid regex pattern for {field_name}: {pattern} - {e}")
                continue
        
        # Clean the best match
        cleaned_value = self._clean_field_value(field_name, best_match) if best_match else None
        
        return {
            'value': cleaned_value,
            'confidence': highest_confidence,
            'pattern_used': pattern_used,
            'raw_match': raw_match
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better pattern matching"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s@.\-\/₹,():]+', ' ', text)
        return text.strip()
    
    def _clean_field_value(self, field_name: str, value: str) -> Optional[str]:
        """Clean and format field values"""
        if not value:
            return None
            
        value = value.strip()
        
        if field_name in ['name', 'employer', 'bank_name']:
            # Clean name fields
            value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
            
            # Remove common contamination patterns
            if field_name == 'name':
                # Remove common name contamination
                value = re.sub(r'\s*PAN\s*[A-Z0-9]*\s*$', '', value, flags=re.IGNORECASE)  # Remove "PAN ABCDEF"
                value = re.sub(r'\s*Aadhaar\s*[0-9\s]*\s*$', '', value, flags=re.IGNORECASE)  # Remove "Aadhaar 1234"
                value = re.sub(r'\s*Income\s*Tax\s*Return.*$', '', value, flags=re.IGNORECASE)  # Remove "Income Tax Return"
                
            elif field_name == 'employer':
                # Remove common employer contamination
                value = re.sub(r'^Employer\s*Name\s*', '', value, flags=re.IGNORECASE)  # Remove "Employer Name" prefix
                value = re.sub(r'^Employer\s*', '', value, flags=re.IGNORECASE)  # Remove "Employer" prefix
                value = re.sub(r'^Company\s*Name\s*', '', value, flags=re.IGNORECASE)  # Remove "Company Name" prefix
                value = re.sub(r'\s*TAN\s*[A-Z0-9]*\s*$', '', value, flags=re.IGNORECASE)  # Remove "TAN ABCD"
                value = re.sub(r'\s*Employer\s*TAN\s*[A-Z0-9]*\s*$', '', value, flags=re.IGNORECASE)  # Remove "Employer TAN"
                value = re.sub(r'\s*Designation.*$', '', value, flags=re.IGNORECASE)  # Remove "Designation ..."
                
            # Remove special characters except allowed ones
            value = re.sub(r'[^\w\s&\.\-]', '', value)
            value = re.sub(r'\s+', ' ', value).strip()  # Final whitespace cleanup
            
            return value.title() if value else None
            
        elif field_name == 'pan':
            value = value.upper().replace(' ', '')
            return value if re.match(self.validation_rules['pan'], value) else None
            
        elif field_name == 'aadhaar':
            value = re.sub(r'\D', '', value)
            if len(value) == 12:
                return f"{value[:4]} {value[4:8]} {value[8:]}"
            return None
            
        elif field_name == 'ifsc':
            value = value.upper().replace(' ', '')
            return value if re.match(self.validation_rules['ifsc'], value) else None
            
        elif field_name == 'mobile':
            value = re.sub(r'\D', '', value)
            if value.startswith('91') and len(value) == 12:
                return f"+91 {value[2:]}"
            elif len(value) == 10:
                return f"+91 {value}"
            return None
            
        elif field_name == 'email':
            value = value.lower()
            return value if re.match(self.validation_rules['email'], value) else None
            
        elif field_name in ['gross_salary', 'tds_deducted', 'total_income']:
            # Clean monetary values
            value = re.sub(r'[₹,\s]', '', value)
            return value if value.isdigit() else None
            
        elif field_name == 'account_number':
            value = re.sub(r'\D', '', value)
            return value if re.match(self.validation_rules['account_number'], value) else None
            
        elif field_name == 'pincode':
            value = re.sub(r'\D', '', value)
            return value if re.match(self.validation_rules['pincode'], value) else None
            
        elif field_name in ['tan', 'cin']:
            value = value.upper().replace(' ', '')
            validation_rule = self.validation_rules.get(field_name)
            return value if validation_rule and re.match(validation_rule, value) else None
            
        else:
            return value if len(value) > 0 and len(value) < 200 else None
    
    def _calculate_field_confidence(self, field_name: str, value: str, pattern: str) -> float:
        """Calculate confidence score for a field match"""
        base_confidence = self.confidence_weights['pattern_match']
        
        # Boost confidence for well-formatted values
        if field_name == 'pan' and re.match(self.validation_rules['pan'], value.upper().replace(' ', '')):
            return 0.95
        elif field_name == 'aadhaar' and re.match(r'^\d{4}\s*\d{4}\s*\d{4}$', value):
            return 0.90
        elif field_name == 'ifsc' and re.match(self.validation_rules['ifsc'], value.upper().replace(' ', '')):
            return 0.90
        elif field_name == 'email' and re.match(self.validation_rules['email'], value):
            return 0.90
        elif field_name == 'mobile' and re.match(r'^\+?91\s*\d{10}$', value):
            return 0.90
        elif field_name == 'pincode' and re.match(self.validation_rules['pincode'], value):
            return 0.90
        
        # Context-based confidence adjustments
        if 'exact' in pattern.lower() or field_name in pattern.lower():
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _calculate_overall_confidence(self, confidence_scores: Dict[str, float]) -> float:
        """Calculate overall extraction confidence"""
        if not confidence_scores:
            return 0.0
        
        scores = list(confidence_scores.values())
        average_confidence = sum(scores) / len(scores)
        
        # Boost confidence based on number of fields extracted
        field_count_boost = min(len(scores) / 15, 0.2)  # Max 20% boost for 15+ fields
        
        overall_confidence = min(average_confidence + field_count_boost, 1.0)
        return round(overall_confidence, 3)
    
    def _validate_fields(self, fields: Dict[str, str]) -> Dict[str, str]:
        """Validate extracted fields against business rules"""
        validated = {}
        
        for field_name, value in fields.items():
            if self._is_valid_field(field_name, value):
                validated[field_name] = value
            else:
                logger.warning(f"❌ Field validation failed for {field_name}: {value}")
        
        return validated
    
    def _is_valid_field(self, field_name: str, value: str) -> bool:
        """Validate individual field values"""
        if not value or not isinstance(value, str):
            return False
        
        # Check against validation rules
        if field_name in self.validation_rules:
            return bool(re.match(self.validation_rules[field_name], value))
        
        # General validation for other fields
        return 0 < len(value) < 200
    
    def _normalize_date(self, date_str: str) -> str:
        """
        Normalize various date formats to YYYY-MM-DD format
        Handles multiple input formats commonly found in Indian documents
        """
        if not date_str:
            return date_str
        
        # Clean the date string
        date_str = date_str.strip()
        
        # Month name mappings
        month_names = {
            'jan': '01', 'january': '01',
            'feb': '02', 'february': '02',
            'mar': '03', 'march': '03',
            'apr': '04', 'april': '04',
            'may': '05',
            'jun': '06', 'june': '06',
            'jul': '07', 'july': '07',
            'aug': '08', 'august': '08',
            'sep': '09', 'september': '09',
            'oct': '10', 'october': '10',
            'nov': '11', 'november': '11',
            'dec': '12', 'december': '12'
        }
        
        try:
            # Pattern 1: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
            if re.match(r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4}', date_str):
                parts = re.split(r'[\/\-\.]', date_str)
                day, month, year = parts[0].zfill(2), parts[1].zfill(2), parts[2]
                return f"{year}-{month}-{day}"
            
            # Pattern 2: DD/MM/YY (assuming 20YY for YY < 50, 19YY otherwise)
            elif re.match(r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2}', date_str):
                parts = re.split(r'[\/\-\.]', date_str)
                day, month, year = parts[0].zfill(2), parts[1].zfill(2), parts[2]
                # Convert 2-digit year to 4-digit
                year_int = int(year)
                if year_int < 50:
                    year = f"20{year}"
                else:
                    year = f"19{year}"
                return f"{year}-{month}-{day}"
            
            # Pattern 3: DD Month YYYY (15 March 1990)
            elif re.match(r'\d{1,2}\s+\w+\s+\d{4}', date_str):
                parts = date_str.split()
                day = parts[0].zfill(2)
                month_name = parts[1].lower()
                year = parts[2]
                
                # Convert month name to number
                for name, num in month_names.items():
                    if month_name.startswith(name):
                        month = num
                        break
                else:
                    return date_str  # Return original if month not found
                
                return f"{year}-{month}-{day}"
            
            # Pattern 4: Month DD, YYYY (March 15, 1990)
            elif re.match(r'\w+\s+\d{1,2},?\s+\d{4}', date_str):
                # Remove comma if present
                date_str = date_str.replace(',', '')
                parts = date_str.split()
                month_name = parts[0].lower()
                day = parts[1].zfill(2)
                year = parts[2]
                
                # Convert month name to number
                for name, num in month_names.items():
                    if month_name.startswith(name):
                        month = num
                        break
                else:
                    return date_str  # Return original if month not found
                
                return f"{year}-{month}-{day}"
            
            # Pattern 5: DD Mon YYYY (15 Jan 1990)
            elif re.match(r'\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}', date_str.lower()):
                parts = date_str.split()
                day = parts[0].zfill(2)
                month_name = parts[1].lower()
                year = parts[2]
                
                # Convert month name to number
                for name, num in month_names.items():
                    if month_name.startswith(name):
                        month = num
                        break
                else:
                    return date_str  # Return original if month not found
                
                return f"{year}-{month}-{day}"
            
            # If no pattern matches, return original
            return date_str
            
        except (ValueError, IndexError) as e:
            logger.warning(f"Date normalization failed for '{date_str}': {e}")
            return date_str
    
    def get_field_mapping_for_form(self, form_type: str) -> List[str]:
        """Get relevant fields for different form types"""
        mappings = {
            'pre-registration': ['name', 'pan', 'date_of_birth', 'aadhaar', 'mobile', 'email', 'address', 'pincode'],
            'bank-details': ['account_number', 'ifsc', 'bank_name'],
            'form16': ['employer', 'gross_salary', 'tds_deducted', 'assessment_year', 'financial_year', 'tan'],
            'income-details': ['total_income', 'gross_salary', 'tds_deducted'],
            'contact-info': ['mobile', 'email', 'address', 'pincode']
        }
        
        return mappings.get(form_type, list(self.patterns.keys()))


class NERExtractor:
    """
    Enhanced NER Extractor for multi-document processing
    Supports combining data from multiple document types
    """
    
    def __init__(self):
        self.itr_extractor = ITRNERExtractor()
        
        # Document type specific field priorities
        self.document_field_priorities = {
            'aadhaar': ['name', 'aadhaar', 'date_of_birth', 'address', 'pincode', 'mobile'],
            'form16': ['name', 'pan', 'employer', 'gross_salary', 'tds_deducted', 'financial_year', 'assessment_year', 'tan'],
            'preregistration': ['name', 'pan', 'email', 'mobile', 'assessment_year'],
            'bankSlip': ['account_number', 'ifsc', 'bank_name', 'gross_salary'],
            'incomeDetails': ['total_income', 'gross_salary', 'tds_deducted', 'other_income']
        }
    
    def extract_entities(self, text: str, field_types: List[str] = None) -> Dict[str, Any]:
        """
        Extract entities from combined text using NER patterns
        
        Args:
            text: Combined text from multiple documents
            field_types: Specific field types to extract
            
        Returns:
            Dictionary with entities, field mapping, and processing details
        """
        logger.info(f"🧠 Multi-document NER extraction starting")
        logger.info(f"📄 Text length: {len(text)} characters")
        logger.info(f"🎯 Target fields: {field_types or 'all'}")
        
        # Use ITR extractor for the heavy lifting
        extraction_result = self.itr_extractor.extract_structured_data(text, 'Multi-Document')
        
        extracted_fields = extraction_result.get('extracted_fields', {})
        confidence_scores = extraction_result.get('confidence_scores', {})
        
        # Filter by requested field types if specified
        if field_types:
            extracted_fields = {k: v for k, v in extracted_fields.items() if k in field_types}
            confidence_scores = {k: v for k, v in confidence_scores.items() if k in field_types}
        
        # Convert to entities format expected by the API
        entities = []
        for field, value in extracted_fields.items():
            entities.append({
                'field': field,
                'value': value,
                'confidence': confidence_scores.get(field, 0.8),
                'start': 0,  # Would need more complex logic to find exact positions
                'end': len(value),
                'source': 'ner_pattern'
            })
        
        # Create field mapping
        field_mapping = extracted_fields.copy()
        
        # Processing details
        processing_details = {
            'method': 'enhanced_ner',
            'extractor_used': 'ITRNERExtractor',
            'total_patterns_tried': extraction_result.get('metadata', {}).get('total_patterns_tried', 0),
            'fields_extracted': len(extracted_fields),
            'overall_confidence': extraction_result.get('overall_confidence', 0.0),
            'extraction_timestamp': extraction_result.get('metadata', {}).get('extraction_timestamp')
        }
        
        logger.info(f"✅ Multi-document NER extraction completed")
        logger.info(f"   📊 Entities found: {len(entities)}")
        logger.info(f"   🎯 Field mapping: {len(field_mapping)} fields")
        logger.info(f"   📈 Overall confidence: {processing_details['overall_confidence']:.2f}")
        
        return {
            'entities': entities,
            'field_mapping': field_mapping,
            'processing_details': processing_details
        }
    
    def extract_from_document_type(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Extract entities optimized for specific document type
        
        Args:
            text: Text from specific document
            document_type: Type of document (aadhaar, form16, etc.)
            
        Returns:
            Extraction results optimized for document type
        """
        # Get priority fields for this document type
        priority_fields = self.document_field_priorities.get(document_type, [])
        
        # Extract using standard method
        result = self.extract_entities(text, priority_fields)
        
        # Add document type context
        result['processing_details']['document_type'] = document_type
        result['processing_details']['priority_fields'] = priority_fields
        
        return result
    
    def combine_extractions(self, document_extractions: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Combine extractions from multiple documents with intelligent merging
        
        Args:
            document_extractions: Dict with document type as key and extraction results as value
            
        Returns:
            Combined extraction results
        """
        logger.info(f"🔗 Combining extractions from {len(document_extractions)} documents")
        
        combined_entities = []
        combined_field_mapping = {}
        merge_details = {}
        conflicts = []
        
        # Priority order for different fields
        field_priorities = {
            'name': ['aadhaar', 'form16', 'preregistration', 'bankSlip', 'incomeDetails'],
            'pan': ['form16', 'preregistration', 'aadhaar'],
            'aadhaar': ['aadhaar'],
            'email': ['preregistration', 'form16'],
            'mobile': ['preregistration', 'aadhaar'],
            'gross_salary': ['form16', 'bankSlip'],
            'account_number': ['bankSlip'],
            'bank_name': ['bankSlip'],
            'ifsc': ['bankSlip'],
            'employer': ['form16'],
            'tds_deducted': ['form16'],
            'total_income': ['incomeDetails', 'form16'],
            'address': ['aadhaar', 'preregistration'],
            'pincode': ['aadhaar', 'preregistration'],
            'date_of_birth': ['aadhaar', 'preregistration']
        }
        
        # Collect all unique fields
        all_fields = set()
        for doc_type, extraction in document_extractions.items():
            if 'field_mapping' in extraction:
                all_fields.update(extraction['field_mapping'].keys())
        
        # Process each field with priority-based selection
        for field in all_fields:
            field_candidates = {}
            
            # Collect candidates from all documents
            for doc_type, extraction in document_extractions.items():
                field_mapping = extraction.get('field_mapping', {})
                if field in field_mapping:
                    # Find corresponding entity for confidence score
                    confidence = 0.8  # Default
                    for entity in extraction.get('entities', []):
                        if entity['field'] == field:
                            confidence = entity['confidence']
                            break
                    
                    field_candidates[doc_type] = {
                        'value': field_mapping[field],
                        'confidence': confidence
                    }
            
            if field_candidates:
                # Select best candidate based on priority
                selected_doc = None
                selected_value = None
                
                # Use priority order if defined
                if field in field_priorities:
                    for priority_doc in field_priorities[field]:
                        if priority_doc in field_candidates:
                            selected_doc = priority_doc
                            selected_value = field_candidates[priority_doc]['value']
                            break
                
                # Fallback to highest confidence
                if not selected_value:
                    selected_doc = max(field_candidates.keys(), 
                                     key=lambda x: field_candidates[x]['confidence'])
                    selected_value = field_candidates[selected_doc]['value']
                
                # Add to combined results
                combined_field_mapping[field] = selected_value
                combined_entities.append({
                    'field': field,
                    'value': selected_value,
                    'confidence': field_candidates[selected_doc]['confidence'],
                    'start': 0,
                    'end': len(selected_value),
                    'source': f'combined_from_{selected_doc}'
                })
                
                merge_details[field] = {
                    'selected_from': selected_doc,
                    'available_in': list(field_candidates.keys()),
                    'confidence': field_candidates[selected_doc]['confidence']
                }
                
                # Check for conflicts
                unique_values = set(candidate['value'] for candidate in field_candidates.values())
                if len(unique_values) > 1:
                    conflicts.append({
                        'field': field,
                        'values': field_candidates,
                        'selected': selected_value,
                        'selected_from': selected_doc
                    })
        
        # Calculate overall confidence
        confidences = [entity['confidence'] for entity in combined_entities]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        processing_details = {
            'method': 'multi_document_combination',
            'documents_processed': len(document_extractions),
            'total_fields_combined': len(combined_field_mapping),
            'conflicts_found': len(conflicts),
            'overall_confidence': overall_confidence,
            'merge_strategy': 'priority_based',
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Document combination completed")
        logger.info(f"   📊 Fields combined: {len(combined_field_mapping)}")
        logger.info(f"   ⚠️  Conflicts found: {len(conflicts)}")
        logger.info(f"   📈 Overall confidence: {overall_confidence:.2f}")
        
        return {
            'entities': combined_entities,
            'field_mapping': combined_field_mapping,
            'processing_details': processing_details,
            'merge_details': merge_details,
            'conflicts': conflicts
        }