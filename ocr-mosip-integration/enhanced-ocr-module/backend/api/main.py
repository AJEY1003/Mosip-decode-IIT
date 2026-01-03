from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import os
import tempfile
from datetime import datetime
import asyncio
import sys
import importlib.util

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import modules using importlib to handle path issues
ocr_engine_spec = importlib.util.spec_from_file_location(
    "OCREngine", 
    os.path.join(project_root, "backend", "ocr_engine", "ocr_engine.py")
)
OCRModule = importlib.util.module_from_spec(ocr_engine_spec)
ocr_engine_spec.loader.exec_module(OCRModule)
OCREngine = OCRModule.OCREngine

preprocessor_spec = importlib.util.spec_from_file_location(
    "DocumentPreprocessor", 
    os.path.join(project_root, "backend", "preprocessing", "preprocessor.py")
)
preprocessor_module = importlib.util.module_from_spec(preprocessor_spec)
preprocessor_spec.loader.exec_module(preprocessor_module)
DocumentPreprocessor = preprocessor_module.DocumentPreprocessor

field_extractor_spec = importlib.util.spec_from_file_location(
    "FieldExtractor", 
    os.path.join(project_root, "backend", "ocr_engine", "field_extractor.py")
)
field_extractor_module = importlib.util.module_from_spec(field_extractor_spec)
field_extractor_spec.loader.exec_module(field_extractor_module)
FieldExtractor = field_extractor_module.FieldExtractor

ai_verifier_spec = importlib.util.spec_from_file_location(
    "AIVerifier", 
    os.path.join(project_root, "backend", "verification", "ai_verifier.py")
)
ai_verifier_module = importlib.util.module_from_spec(ai_verifier_spec)
ai_verifier_spec.loader.exec_module(ai_verifier_module)
AIVerifier = ai_verifier_module.AIVerifier
RuleBasedValidator = ai_verifier_module.RuleBasedValidator

data_storage_spec = importlib.util.spec_from_file_location(
    "DataStorageManager", 
    os.path.join(project_root, "backend", "storage", "data_storage.py")
)
data_storage_module = importlib.util.module_from_spec(data_storage_spec)
data_storage_spec.loader.exec_module(data_storage_module)
DataStorageManager = data_storage_module.DataStorageManager

config_spec = importlib.util.spec_from_file_location(
    "Config", 
    os.path.join(project_root, "config", "settings.py")
)
config_module = importlib.util.module_from_spec(config_spec)
config_spec.loader.exec_module(config_module)
Config = config_module.Config

# Initialize the OCR system components
ocr_engine = OCREngine()
preprocessor = DocumentPreprocessor()
field_extractor = FieldExtractor()
ai_verifier = AIVerifier()
rule_validator = RuleBasedValidator()
storage_manager = DataStorageManager()

# Initialize FastAPI app
app = FastAPI(
    title="Smart OCR & Verification Engine API",
    description="A modular OCR + AI verification system with confidence scoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class OCRProcessRequest(BaseModel):
    file_url: Optional[str] = None
    confidence_threshold: Optional[float] = Config.MANUAL_REVIEW_THRESHOLD

class OCRResponse(BaseModel):
    id: str
    status: str
    extracted_fields: Dict[str, Any]
    confidence_score: float
    processing_time: float

class ValidationRequest(BaseModel):
    document_id: str
    manual_corrections: Optional[Dict[str, str]] = {}

class ValidationResult(BaseModel):
    document_id: str
    validated_data: Dict[str, Any]
    confidence_score: float
    issues_detected: list
    status: str

# In-memory storage for processing status (in production, use Redis or database)
processing_status = {}

@app.get("/")
async def root():
    return {"message": "Smart OCR & Verification Engine API", "status": "running"}

@app.post("/ocr/process", response_model=OCRResponse)
async def process_document(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Process a document with OCR and return extracted fields with confidence score
    """
    start_time = datetime.now()
    
    # Validate file type
    if not file.content_type or not any(ext in file.content_type for ext in ['image/', 'application/pdf']):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images and PDFs are supported.")
    
    # Generate a unique document ID
    doc_id = str(uuid.uuid4())
    
    # Store processing status
    processing_status[doc_id] = {
        "status": "processing",
        "progress": 0,
        "message": "File upload complete"
    }
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Update processing status
        processing_status[doc_id]["progress"] = 10
        processing_status[doc_id]["message"] = "Starting preprocessing"
        
        # Preprocess image
        processed_path = preprocessor.preprocess_document(temp_file_path)
        
        processing_status[doc_id]["progress"] = 30
        processing_status[doc_id]["message"] = "Preprocessing complete, starting OCR"
        
        # Perform OCR
        ocr_result = ocr_engine.process_with_multiple_engines(processed_path)
        
        processing_status[doc_id]["progress"] = 60
        processing_status[doc_id]["message"] = "OCR complete, extracting fields"
        
        # Extract structured fields
        extracted_fields = field_extractor.extract_fields(ocr_result["text"])
        
        processing_status[doc_id]["progress"] = 70
        processing_status[doc_id]["message"] = "Field extraction complete, validating with AI"
        
        # Validate and correct with AI
        ai_result = ai_verifier.validate_and_correct(extracted_fields, ocr_result["text"])
        
        processing_status[doc_id]["progress"] = 85
        processing_status[doc_id]["message"] = "AI validation complete, applying rule-based validation"
        
        # Apply rule-based validation
        rule_results = rule_validator.validate_fields(ai_result["validated_data"])
        
        # Calculate combined confidence score
        combined_confidence = ai_verifier.calculate_combined_confidence(
            ocr_result["confidence"],
            ai_result["confidence_score"],
            rule_results
        )
        
        processing_status[doc_id]["progress"] = 95
        processing_status[doc_id]["message"] = "Finalizing results"
        
        # Determine document status based on confidence
        if combined_confidence >= Config.AUTO_APPROVE_THRESHOLD:
            status = "auto_approved"
        elif combined_confidence >= Config.AI_REVIEW_THRESHOLD:
            status = "ai_review"
        else:
            status = "manual_review"
        
        # Prepare document for storage
        document_data = {
            "_id": doc_id,
            "original_filename": file.filename,
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
                "upload_time": start_time.isoformat(),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
        }
        
        # Save to storage
        storage_result = storage_manager.save_document(document_data)
        
        processing_status[doc_id]["progress"] = 100
        processing_status[doc_id]["status"] = "completed"
        processing_status[doc_id]["message"] = "Processing complete"
        
        # Clean up temporary files
        os.unlink(temp_file_path)
        if os.path.exists(processed_path) and "temp_processed" in processed_path:
            os.unlink(processed_path)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return OCRResponse(
            id=doc_id,
            status=status,
            extracted_fields=ai_result["validated_data"],
            confidence_score=combined_confidence,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_status[doc_id]["status"] = "failed"
        processing_status[doc_id]["message"] = str(e)
        
        # Clean up temporary files in case of error
        try:
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
            if 'processed_path' in locals() and os.path.exists(processed_path):
                os.unlink(processed_path)
        except:
            pass  # Ignore cleanup errors
        
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/ocr/status/{document_id}")
async def get_processing_status(document_id: str):
    """
    Get the processing status of a document
    """
    if document_id in processing_status:
        return processing_status[document_id]
    else:
        # Check if document exists in storage
        doc = storage_manager.get_document(document_id)
        if doc:
            return {
                "status": "completed",
                "progress": 100,
                "document_info": doc
            }
        else:
            raise HTTPException(status_code=404, detail="Document not found")

@app.get("/ocr/result/{document_id}", response_model=OCRResponse)
async def get_ocr_result(document_id: str):
    """
    Get the OCR result for a processed document
    """
    doc = storage_manager.get_document(document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Handle both cases where doc is from PG or combined
    if 'full_data' in doc:
        # This is a combined result
        extracted_fields = doc['full_data'].get('extracted_fields', {})
        confidence_score = doc['full_data'].get('confidence', 0.0)
    else:
        # This is a PG-only result
        extracted_fields = doc.get('extracted_fields', {})
        confidence_score = float(doc.get('confidence', 0.0)) if doc.get('confidence') is not None else 0.0
    
    return OCRResponse(
        id=document_id,
        status=doc.get('status', 'unknown'),
        extracted_fields=extracted_fields,
        confidence_score=confidence_score,
        processing_time=doc.get('processing_metadata', {}).get('processing_time', 0.0)
    )

@app.post("/ocr/validate", response_model=ValidationResult)
async def validate_document(request: ValidationRequest):
    """
    Validate and potentially update a document's extracted fields
    """
    # Get the existing document
    doc = storage_manager.get_document(request.document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Apply manual corrections if provided
    if request.manual_corrections:
        # Update the document with manual corrections
        if 'full_data' in doc:
            current_fields = doc['full_data']['extracted_fields']
        else:
            current_fields = doc.get('extracted_fields', {})
        
        for field, correction in request.manual_corrections.items():
            current_fields[field] = correction
        
        # Update the document status
        new_status = "manually_approved" if request.document_id.startswith('manual') else doc.get('status', 'processed')
        storage_manager.update_document_status(request.document_id, new_status)
    
    # Return validation result
    return ValidationResult(
        document_id=request.document_id,
        validated_data=doc.get('extracted_fields', {}) if 'extracted_fields' in doc else {},
        confidence_score=float(doc.get('confidence', 0.0)) if doc.get('confidence') is not None else 0.0,
        issues_detected=doc.get('issues_detected', []),
        status=doc.get('status', 'unknown')
    )

@app.get("/ocr/search")
async def search_documents(
    name: Optional[str] = None,
    document_type: Optional[str] = None,
    status: Optional[str] = None,
    confidence_min: Optional[float] = None,
    confidence_max: Optional[float] = None
):
    """
    Search for processed documents with various filters
    """
    filters = {}
    if name:
        filters['name'] = name
    if document_type:
        filters['document_type'] = document_type
    if status:
        filters['status'] = status
    if confidence_min is not None:
        filters['confidence_min'] = confidence_min
    if confidence_max is not None:
        filters['confidence_max'] = confidence_max
    
    results = storage_manager.search_documents(filters)
    return {"results": results, "count": len(results)}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "ocr_engine": "available",
            "preprocessor": "available",
            "ai_verifier": "available" if Config.OPENAI_API_KEY else "not configured",
            "storage": "available"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)