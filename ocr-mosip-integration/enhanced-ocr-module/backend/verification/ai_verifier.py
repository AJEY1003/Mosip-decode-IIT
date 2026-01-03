import openai
from typing import Dict, Any, List, Optional
from config.settings import Config
import json
import re


class AIVerifier:
    """
    AI verification layer to validate and correct OCR-extracted fields
    """
    
    def __init__(self):
        if Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY
        self.model = Config.AI_MODEL
    
    def validate_and_correct(self, extracted_fields: Dict[str, Any], ocr_text: str = "") -> Dict[str, Any]:
        """
        Validate and correct extracted fields using AI
        """
        if not Config.OPENAI_API_KEY:
            return {
                "validated_data": extracted_fields,
                "confidence_score": 0.0,
                "issues_detected": ["AI verification not available - no API key configured"],
                "corrections_made": {}
            }
        
        # Create a prompt for the AI model
        prompt = self._create_validation_prompt(extracted_fields, ocr_text)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert document validation assistant. Your job is to validate extracted document fields, correct OCR errors, normalize formats, and detect inconsistencies. Respond in JSON format only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for more consistent results
                max_tokens=1000
            )
            
            response_text = response.choices[0].message['content'].strip()
            
            # Extract JSON from response (in case it's wrapped in markdown)
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no markdown, assume the whole response is JSON
                json_str = response_text
            
            # Parse the response
            result = json.loads(json_str)
            
            return result
            
        except Exception as e:
            # Fallback if AI service fails
            return {
                "validated_data": extracted_fields,
                "confidence_score": 0.5,  # Default confidence when AI fails
                "issues_detected": [f"AI verification failed: {str(e)}"],
                "corrections_made": {},
                "status": "ai_error"
            }
    
    def _create_validation_prompt(self, extracted_fields: Dict[str, Any], ocr_text: str) -> str:
        """
        Create a validation prompt for the AI model
        """
        prompt = f"""
        Please validate and correct the following OCR-extracted document fields:
        
        Extracted Fields:
        {json.dumps(extracted_fields, indent=2)}
        
        Original OCR Text:
        {ocr_text[:1000]}  # Limit to first 1000 characters
        
        Validate each field for:
        1. Format correctness (dates, ID numbers, etc.)
        2. Logical consistency (e.g., age based on DOB)
        3. Common OCR errors (numbers mistaken for letters, etc.)
        4. Data normalization (standardize formats)
        
        Return your response in the following JSON format:
        {{
            "validated_data": {{
                "name": "...",
                "dob": "...",
                "id_number": "...",
                "address": "...",
                "document_type": "..."
            }},
            "confidence_score": 0.x,
            "issues_detected": ["list", "of", "issues"],
            "corrections_made": {{
                "field_name": "original_value -> corrected_value"
            }}
        }}
        
        If a field is missing or invalid, return it as null in validated_data.
        Ensure the confidence_score is between 0 and 1, reflecting your confidence in the corrections.
        """
        
        return prompt
    
    def calculate_combined_confidence(self, ocr_confidence: float, ai_confidence: float, 
                                     validation_results: Dict[str, bool]) -> float:
        """
        Calculate combined confidence score from OCR, AI, and rule validation
        """
        # Weighted average of confidences
        # OCR confidence: 40%, AI confidence: 40%, Rule validation: 20%
        rule_confidence = sum(validation_results.values()) / len(validation_results) if validation_results else 1.0
        
        combined_confidence = (
            ocr_confidence * 0.4 + 
            ai_confidence * 0.4 + 
            rule_confidence * 0.2
        )
        
        return min(combined_confidence, 1.0)  # Cap at 1.0


class RuleBasedValidator:
    """
    Rule-based validation layer for deterministic checks
    """
    
    def __init__(self):
        self.patterns = {
            'pan': r'^[A-Z]{5}[0-9]{4}[A-Z]$',
            'aadhaar': r'^\d{12}$',
            'passport': r'^[A-Z]{1}[0-9]{7}$',
            'date': r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD format
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^\+?[1-9]\d{1,14}$'
        }
    
    def validate_fields(self, fields: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate fields using rule-based checks
        """
        results = {}
        
        for field_name, value in fields.items():
            if value is None or value == "":
                results[field_name] = True  # Empty fields are considered valid
                continue
            
            if field_name == 'id_number':
                results[field_name] = self._validate_id_number(value)
            elif field_name == 'dob':
                results[field_name] = self._validate_date(value)
            elif field_name == 'name':
                results[field_name] = self._validate_name(value)
            elif field_name == 'email':
                results[field_name] = self._validate_pattern(value, 'email')
            elif field_name == 'phone':
                results[field_name] = self._validate_pattern(value, 'phone')
            else:
                results[field_name] = True  # Default to valid for unhandled fields
        
        return results
    
    def _validate_id_number(self, id_number: str) -> bool:
        """
        Validate ID number format
        """
        id_number_clean = re.sub(r'[\s\-]+', '', str(id_number).upper())
        
        # Check against PAN format
        if re.match(self.patterns['pan'], id_number_clean):
            return True
        
        # Check against Aadhaar format
        aadhaar_clean = re.sub(r'[\s]+', '', str(id_number))
        if re.match(self.patterns['aadhaar'], aadhaar_clean):
            return True
        
        # Check against Passport format
        if re.match(self.patterns['passport'], id_number_clean):
            return True
        
        return False
    
    def _validate_date(self, date_str: str) -> bool:
        """
        Validate date format and reasonableness
        """
        import datetime
        
        if not re.match(self.patterns['date'], date_str):
            return False
        
        try:
            year, month, day = map(int, date_str.split('-'))
            date_obj = datetime.date(year, month, day)
            
            # Check if date is not in the future
            current_date = datetime.date.today()
            if date_obj > current_date:
                return False
            
            # Check if date is not too far in the past (before 1900)
            if year < 1900:
                return False
            
            return True
        except ValueError:
            return False
    
    def _validate_name(self, name: str) -> bool:
        """
        Validate name format
        """
        name_str = str(name).strip()
        
        # Basic checks: not empty, contains only letters and spaces
        if not name_str:
            return False
        
        # Allow letters, spaces, hyphens, and apostrophes
        if re.match(r"^[A-Za-z\s\'\-]+$", name_str) and len(name_str) >= 2:
            return True
        
        return False
    
    def _validate_pattern(self, value: str, pattern_name: str) -> bool:
        """
        Validate value against a specific pattern
        """
        value_str = str(value).strip()
        pattern = self.patterns.get(pattern_name)
        
        if not pattern:
            return True  # If no pattern exists, consider valid
        
        return bool(re.match(pattern, value_str))


# Example usage
if __name__ == "__main__":
    # Example usage
    verifier = AIVerifier()
    validator = RuleBasedValidator()
    
    sample_fields = {
        "name": "RAMESH KUMAR",
        "dob": "1999-04-12",
        "id_number": "ABCDE1234F",
        "address": "123 Main Street, City, State"
    }
    
    validation_results = validator.validate_fields(sample_fields)
    print("Validation results:", validation_results)
    
    # Note: This would require an OpenAI API key to work
    # ai_result = verifier.validate_and_correct(sample_fields)
    # print("AI verification result:", ai_result)