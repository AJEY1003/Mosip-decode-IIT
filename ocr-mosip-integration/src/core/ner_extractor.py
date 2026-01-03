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
                r'name[:\s]*([A-Za-z\s]+?)(?:\n|$|[0-9])',
                r'applicant[:\s]*([A-Za-z\s]+?)(?:\n|$|[0-9])',
                r'full\s*name[:\s]*([A-Za-z\s]+?)(?:\n|$|[0-9])',
                r'taxpayer[:\s]*([A-Za-z\s]+?)(?:\n|$|[0-9])',
                r'mr\.?\s*([A-Za-z\s]+?)(?:\n|$|[0-9])',
                r'ms\.?\s*([A-Za-z\s]+?)(?:\n|$|[0-9])',
                r'([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'  # Name pattern
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
                r'born[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})'
            ],
            
            # Financial Information
            'gross_salary': [
                r'gross\s*salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'total\s*salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'annual\s*salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'gross\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
            ],
            
            'tds_deducted': [
                r'tds\s*deducted[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'tax\s*deducted[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'tds[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'deducted\s*tax[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
            ],
            
            'total_income': [
                r'total\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'gross\s*total\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'annual\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'taxable\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
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
                r'employer[:\s]*([A-Za-z\s&\.]+?)(?:\n|$|address)',
                r'company[:\s]*([A-Za-z\s&\.]+?)(?:\n|$|address)',
                r'organization[:\s]*([A-Za-z\s&\.]+?)(?:\n|$|address)',
                r'firm[:\s]*([A-Za-z\s&\.]+?)(?:\n|$|address)',
                r'deductor[:\s]*([A-Za-z\s&\.]+?)(?:\n|$|address)'
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
            'cin': r'^[A-Z]{1}[0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$'
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
            value = re.sub(r'\s+', ' ', value)
            value = re.sub(r'[^\w\s&\.]', '', value)
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