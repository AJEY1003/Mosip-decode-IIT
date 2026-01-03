"""
Main entry point for the Smart OCR & Verification Engine
"""
import os
import sys
from typing import Dict, Any
import tempfile
import uuid
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ocr_engine.ocr_engine import OCREngine
from backend.preprocessing.preprocessor import DocumentPreprocessor
from backend.ocr_engine.field_extractor import FieldExtractor
from backend.verification.ai_verifier import AIVerifier, RuleBasedValidator
from backend.storage.data_storage import DataStorageManager
from config.settings import Config


class SmartOCREngine:
    """
    Main class that orchestrates the entire OCR and verification process
    """
    
    def __init__(self):
        self.ocr_engine = OCREngine()
        self.preprocessor = DocumentPreprocessor()
        self.field_extractor = FieldExtractor()
        self.ai_verifier = AIVerifier()
        self.rule_validator = RuleBasedValidator()
        self.storage_manager = DataStorageManager()
    
    def process_document(self, file_path: str, confidence_threshold: float = Config.MANUAL_REVIEW_THRESHOLD) -> Dict[str, Any]:
        """
        Process a document through the entire pipeline
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Preprocess image
            print("Step 1: Preprocessing image...")
            processed_path = self.preprocessor.preprocess_document(file_path)
            
            # Step 2: Perform OCR
            print("Step 2: Performing OCR...")
            ocr_result = self.ocr_engine.process_with_multiple_engines(processed_path)
            
            if not ocr_result["success"]:
                raise Exception(f"OCR failed: {ocr_result.get('error', 'Unknown error')}")
            
            # Step 3: Extract structured fields
            print("Step 3: Extracting structured fields...")
            extracted_fields = self.field_extractor.extract_fields(ocr_result["text"])
            
            # Step 4: AI validation and correction
            print("Step 4: Validating with AI...")
            ai_result = self.ai_verifier.validate_and_correct(extracted_fields, ocr_result["text"])
            
            # Step 5: Rule-based validation
            print("Step 5: Applying rule-based validation...")
            rule_results = self.rule_validator.validate_fields(ai_result["validated_data"])
            
            # Step 6: Calculate combined confidence
            print("Step 6: Calculating confidence score...")
            combined_confidence = self.ai_verifier.calculate_combined_confidence(
                ocr_result["confidence"],
                ai_result["confidence_score"],
                rule_results
            )
            
            # Step 7: Determine document status
            if combined_confidence >= Config.AUTO_APPROVE_THRESHOLD:
                status = "auto_approved"
            elif combined_confidence >= Config.AI_REVIEW_THRESHOLD:
                status = "ai_review"
            else:
                status = "manual_review"
            
            # Step 8: Prepare document for storage
            doc_id = str(uuid.uuid4())
            document_data = {
                "_id": doc_id,
                "original_filename": os.path.basename(file_path),
                "document_type": extracted_fields.get("document_type", "unknown"),
                "extracted_fields": ai_result["validated_data"],
                "ocr_text": ocr_result["text"],
                "ocr_engine_used": ocr_result["best_engine"],
                "confidence": combined_confidence,
                "status": status,
                "ocr_confidence": ocr_result["confidence"],
                "ai_confidence": ai_result["confidence_score"],
                "rule_validation_results": rule_results,
                "issues_detected": ai_result["issues_detected"],
                "corrections_made": ai_result.get("corrections_made", {}),
                "processing_metadata": {
                    "input_file_path": file_path,
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "processed_at": start_time.isoformat()
                }
            }
            
            # Step 9: Save to storage
            print("Step 7: Saving to storage...")
            storage_result = self.storage_manager.save_document(document_data)
            
            # Clean up temporary files
            if "temp_processed" in processed_path:
                os.unlink(processed_path)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "document_id": doc_id,
                "status": status,
                "extracted_fields": ai_result["validated_data"],
                "confidence_score": combined_confidence,
                "processing_time": processing_time,
                "ocr_engine_used": ocr_result["best_engine"],
                "issues_detected": ai_result["issues_detected"],
                "corrections_made": ai_result.get("corrections_made", {})
            }
            
            print(f"Processing completed in {processing_time:.2f} seconds")
            return result
            
        except Exception as e:
            # Clean up any temporary files in case of error
            try:
                if 'processed_path' in locals() and os.path.exists(processed_path):
                    os.unlink(processed_path)
            except:
                pass  # Ignore cleanup errors
            
            raise e
    
    def validate_existing_document(self, document_id: str, manual_corrections: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Re-validate an existing document, optionally with manual corrections
        """
        # Get the existing document
        doc = self.storage_manager.get_document(document_id)
        
        if not doc:
            raise ValueError(f"Document with ID {document_id} not found")
        
        # Apply manual corrections if provided
        if manual_corrections:
            if 'full_data' in doc:
                current_fields = doc['full_data']['extracted_fields']
            else:
                current_fields = doc.get('extracted_fields', {})
            
            for field, correction in manual_corrections.items():
                current_fields[field] = correction
            
            # Update document status
            new_status = "manually_approved"
            self.storage_manager.update_document_status(document_id, new_status)
        
        return {
            "document_id": document_id,
            "validated_data": doc.get('extracted_fields', {}),
            "confidence_score": doc.get('confidence', 0.0),
            "status": doc.get('status', 'unknown'),
            "issues_detected": doc.get('issues_detected', [])
        }


def main():
    """
    Example usage of the Smart OCR Engine
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py <image_path>")
        return
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: File {image_path} does not exist")
        return
    
    # Initialize the OCR engine
    ocr_engine = SmartOCREngine()
    
    try:
        print(f"Processing document: {image_path}")
        result = ocr_engine.process_document(image_path)
        
        print("\nOCR Processing Result:")
        print(f"Document ID: {result['document_id']}")
        print(f"Status: {result['status']}")
        print(f"Confidence Score: {result['confidence_score']:.2f}")
        print(f"Processing Time: {result['processing_time']:.2f} seconds")
        print(f"OCR Engine Used: {result['ocr_engine_used']}")
        print(f"Extracted Fields: {result['extracted_fields']}")
        
        if result['issues_detected']:
            print(f"Issues Detected: {result['issues_detected']}")
        
        if result['corrections_made']:
            print(f"Corrections Made: {result['corrections_made']}")
            
    except Exception as e:
        print(f"Error processing document: {str(e)}")


if __name__ == "__main__":
    main()