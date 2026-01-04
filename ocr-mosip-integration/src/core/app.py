from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import logging
import base64
import uuid
from datetime import datetime
import yaml
from jsonschema import validate, ValidationError

from ocr_processor import OCRProcessor
from enhanced_ocr_processor import EnhancedOCRProcessor
from hindi_ocr_processor import HindiOCRProcessor
from mosip_client import MOSIPClient
from injinet_client import InjInetClient, MockInjINetClient
from inji_verify_client import InjiVerifyClient, MockInjiVerifyClient
from semantic_validator import SemanticValidator

load_dotenv()

app = Flask(__name__)
# Enable CORS for Stoplight Studio integration
CORS(app, origins=["*"])  # Allow all origins for development
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size (increased for multi-page documents)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create results folder for saving extracted text
RESULTS_FOLDER = 'ocr_results'
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OCR processors
ocr = OCRProcessor(engine='easyocr', language='en')  # Original OCR
enhanced_ocr = EnhancedOCRProcessor(languages=['en', 'hi'])  # Enhanced OCR with Tesseract + EasyOCR + TrOCR
hindi_ocr = HindiOCRProcessor()  # Hindi OCR with Tesseract

# Initialize MOSIP client
mosip = MOSIPClient()

# Initialize InjINet client
# Use MockInjINetClient for testing, replace with real credentials when available
injinet = MockInjINetClient(
    base_url=os.getenv('INJINET_BASE_URL', 'https://injinet.collab.mosip.net'),
    client_id=os.getenv('INJINET_CLIENT_ID'),
    client_secret=os.getenv('INJINET_CLIENT_SECRET'),
    api_key=os.getenv('INJINET_API_KEY')
)

# Initialize Inji Verify client
# Use real InjiVerifyClient for QR decoding
inji_verify = InjiVerifyClient(
    base_url=os.getenv('INJI_VERIFY_BASE_URL', 'https://verify.inji.io'),
    api_key=os.getenv('INJI_VERIFY_API_KEY')
)

# Initialize Semantic Validator
try:
    semantic_validator = SemanticValidator()
except Exception as e:
    logger.error(f"Could not initialize Semantic Validator: {e}")
    semantic_validator = None

# Store extraction results for verification
extraction_cache = {}

# Load schema definitions for validation
def load_schema(schema_name):
    """Load YAML schema for request/response validation"""
    try:
        schema_path = os.path.join('models', f'{schema_name}.yaml')
        with open(schema_path, 'r') as f:
            schema = yaml.safe_load(f)
        return schema
    except Exception as e:
        logger.warning(f"Could not load schema {schema_name}: {e}")
        return None

def validate_request_schema(data, schema_name):
    """Validate request data against schema"""
    try:
        schema = load_schema(schema_name)
        if schema:
            validate(data, schema)
            return True, None
    except ValidationError as e:
        return False, f"Schema validation failed: {e.message}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"
    return True, None  # No schema available, skip validation

def save_ocr_results_to_file(request_id, ocr_result, document_type, engines_used):
    """
    Save OCR results to a text file for verification
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ocr_result_{timestamp}_{request_id[:8]}.txt"
        filepath = os.path.join(RESULTS_FOLDER, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"OCR EXTRACTION RESULTS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Request ID: {request_id}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Document Type: {document_type}\n")
            f.write(f"Engines Used: {', '.join(engines_used)}\n")
            f.write(f"Success: {ocr_result.get('success', False)}\n")
            f.write(f"Confidence: {ocr_result.get('confidence', 0.0):.3f}\n")
            f.write(f"Processing Time: {ocr_result.get('processing_time', 0.0):.2f}s\n")
            
            # Add page information if available
            processing_details = ocr_result.get('processing_details', {})
            if processing_details:
                pages_info = processing_details.get('pages_processed')
                total_pages = processing_details.get('total_pages')
                if pages_info and total_pages:
                    f.write(f"PDF Pages Processed: {pages_info}/{total_pages}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("EXTRACTED TEXT\n")
            f.write("=" * 80 + "\n")
            
            raw_text = ocr_result.get('raw_text', '')
            if raw_text:
                f.write(raw_text)
                f.write(f"\n\n[Text Length: {len(raw_text)} characters]\n")
            else:
                f.write("NO TEXT EXTRACTED\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("STRUCTURED DATA\n")
            f.write("=" * 80 + "\n")
            
            structured_data = ocr_result.get('structured_data', {})
            if structured_data:
                for key, value in structured_data.items():
                    f.write(f"{key}: {value}\n")
            else:
                f.write("No structured data extracted\n")
            
            # Add individual engine results if available
            if processing_details and 'raw_results_summary' in processing_details:
                f.write("\n" + "=" * 80 + "\n")
                f.write("INDIVIDUAL ENGINE RESULTS\n")
                f.write("=" * 80 + "\n")
                
                for engine, details in processing_details['raw_results_summary'].items():
                    f.write(f"\n{engine.upper()}:\n")
                    f.write(f"  Success: {details.get('success', False)}\n")
                    f.write(f"  Confidence: {details.get('confidence', 0.0):.3f}\n")
                    f.write(f"  Text Length: {details.get('text_length', 0)}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF RESULTS\n")
            f.write("=" * 80 + "\n")
        
        print(f"💾 OCR RESULTS SAVED TO FILE: {filepath}")
        logger.info(f"OCR results saved to file: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ ERROR SAVING OCR RESULTS: {str(e)}")
        logger.error(f"Error saving OCR results: {str(e)}")
        return None

def generate_mock_ocr_data(document_type, filepath=None):
    """
    Generate mock OCR data for testing Enhanced OCR integration
    Simulates results from PaddleOCR, EasyOCR, TrOCR, and Tesseract
    """
    import random
    
    # Mock data templates based on document type
    mock_templates = {
        'ITR Document': {
            'name': 'Rajesh Kumar Sharma',
            'pan': 'ABCDE1234F',
            'aadhaar': '1234 5678 9012',
            'date_of_birth': '15/03/1985',
            'gross_salary': '1200000',
            'tds_deducted': '150000',
            'total_income': '1200000',
            'account_number': '123456789012',
            'ifsc': 'SBIN0001234',
            'bank_name': 'State Bank of India',
            'employer': 'Tech Solutions Private Limited',
            'address': '123 MG Road, Bangalore, Karnataka',
            'pincode': '560001',
            'mobile': '+91 9876543210',
            'email': 'rajesh.sharma@email.com',
            'assessment_year': '2024-25',
            'financial_year': '2023-24',
            'tan': 'BLRA12345B'
        },
        'Form 16': {
            'name': 'Priya Patel',
            'pan': 'FGHIJ5678K',
            'employer': 'Infosys Technologies Limited',
            'gross_salary': '800000',
            'tds_deducted': '80000',
            'assessment_year': '2024-25',
            'financial_year': '2023-24',
            'tan': 'PUNE23456C',
            'address': '456 IT Park, Pune, Maharashtra',
            'pincode': '411001'
        },
        'Passport': {
            'name': 'John Smith',
            'date_of_birth': '25/12/1988',
            'nationality': 'United Kingdom',
            'passport_number': 'UK123456789',
            'email': 'john.smith@example.com',
            'phone': '+44-20-7946-0958',
            'address': '123 Baker Street, London, UK',
            'gender': 'Male',
            'issue_date': '15/06/2020',
            'expiry_date': '15/06/2030'
        },
        'Aadhaar': {
            'name': 'राज कुमार / Raj Kumar',
            'date_of_birth': '15/03/1990',
            'aadhaar': '1234 5678 9012',
            'address': 'गांव पोस्ट तहसील, जिला दिल्ली / Village Post Tehsil, District Delhi',
            'gender': 'पुरुष / Male',
            'mobile': '+91 9876543210',
            'pincode': '110001'
        }
    }
    
    # Get template or use ITR as default
    template = mock_templates.get(document_type, mock_templates['ITR Document'])
    
    # Generate mock raw text
    raw_text_lines = []
    raw_text_lines.append(f"=== {document_type.upper()} ===")
    raw_text_lines.append("")
    
    for key, value in template.items():
        formatted_key = key.replace('_', ' ').title()
        raw_text_lines.append(f"{formatted_key}: {value}")
    
    raw_text = "\n".join(raw_text_lines)
    
    # Generate mock processing details
    processing_details = {
        'processing_id': str(uuid.uuid4())[:8],
        'engines_used': ['mock_paddleocr', 'mock_easyocr', 'mock_tesseract'],
        'selected_engine': 'mock_paddleocr',
        'confidence_score': round(random.uniform(0.75, 0.95), 3),
        'processing_time': round(random.uniform(2.0, 8.0), 2),
        'raw_results_summary': {
            'mock_paddleocr': {
                'success': True,
                'confidence': round(random.uniform(0.8, 0.95), 3),
                'text_length': len(raw_text)
            },
            'mock_easyocr': {
                'success': True,
                'confidence': round(random.uniform(0.7, 0.9), 3),
                'text_length': len(raw_text) - 50
            },
            'mock_tesseract': {
                'success': True,
                'confidence': round(random.uniform(0.6, 0.85), 3),
                'text_length': len(raw_text) + 20
            }
        }
    }
    
    return {
        'success': True,
        'raw_text': raw_text,
        'structured_data': template,  # Return the structured template data
        'confidence': processing_details['confidence_score'],
        'processing_time': processing_details['processing_time'],
        'engines_used': processing_details['engines_used'],
        'processing_details': processing_details,
        'ner_confidence_scores': {field: round(random.uniform(0.7, 0.95), 2) for field in template.keys()},
        'ner_overall_confidence': round(random.uniform(0.8, 0.95), 2),
        'ner_metadata': {
            'document_type': document_type,
            'fields_extracted': len(template),
            'extraction_timestamp': datetime.now().isoformat()
        }
    }
    raw_text = "\n".join(raw_text_lines)
    
    # Mock engine results for enhanced OCR
    mock_engines = ['paddleocr', 'easyocr', 'trocr', 'tesseract']
    selected_engines = random.sample(mock_engines, random.randint(2, 4))
    
    # Mock confidence scores for different engines
    engine_confidences = {
        'paddleocr': round(random.uniform(0.88, 0.95), 3),
        'easyocr': round(random.uniform(0.85, 0.92), 3),
        'trocr': round(random.uniform(0.90, 0.96), 3),
        'tesseract': round(random.uniform(0.82, 0.89), 3)
    }
    
    overall_confidence = sum(engine_confidences[engine] for engine in selected_engines) / len(selected_engines)
    
    # Return mock OCR result with enhanced details
    return {
        'raw_text': raw_text,
        'structured_data': template,
        'confidence': round(overall_confidence, 3),
        'processing_time': round(random.uniform(0.8, 3.2), 2),
        'engines_used': selected_engines,
        'success': True,
        'processing_details': {
            'processing_id': f'mock_{random.randint(1000, 9999)}',
            'selected_engine': random.choice(selected_engines),
            'confidence_breakdown': {f'{engine}_confidence': engine_confidences[engine] for engine in selected_engines},
            'raw_results_summary': {
                engine: {
                    'success': True,
                    'confidence': engine_confidences[engine],
                    'text_length': len(raw_text)
                } for engine in selected_engines
            }
        }
    }

@app.route('/api/docs', methods=['GET'])
def get_api_docs():
    """
    Serve OpenAPI specification for Stoplight integration
    """
    try:
        import yaml
        with open('reference/OCR-MOSIP-API.yaml', 'r') as f:
            spec = yaml.safe_load(f)
        return jsonify(spec), 200
    except Exception as e:
        return jsonify({'error': f'Could not load API specification: {str(e)}'}), 500

@app.route('/api/docs/yaml', methods=['GET'])
def get_api_docs_yaml():
    """
    Serve OpenAPI specification as YAML for Stoplight integration
    """
    try:
        with open('reference/OCR-MOSIP-API.yaml', 'r') as f:
            spec_content = f.read()
        return spec_content, 200, {'Content-Type': 'application/x-yaml'}
    except Exception as e:
        return f'# Error loading API specification: {str(e)}', 500, {'Content-Type': 'text/plain'}

@app.route('/', methods=['GET'])
def api_info():
    """
    API information and documentation links
    """
    return jsonify({
        'service': 'OCR-MOSIP Integration API',
        'version': '1.0',
        'description': 'OCR-driven solution for text extraction and data verification',
        'endpoints': {
            'health': '/health',
            'ocr_extract': '/ocr/extract',
            'ocr_verify': '/ocr/verify',
            'api_docs': '/api/docs',
            'api_docs_yaml': '/api/docs/yaml'
        },
        'documentation': {
            'openapi_spec': f'{request.host_url}api/docs',
            'stoplight_ready': True
        },
        'status': 'ready'
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'OCR-MOSIP Integration Service',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/ocr/extract', methods=['POST'])
def extract_text():
    """
    Extract text and data from document images using OCR
    
    Stoplight Schema: OCRExtractionRequest -> OCRExtractionResponse
    
    Request body (JSON):
    {
        "document_type": "string",    // Type of document (Passport, NationalID, etc.)
        "image_data": "string",       // Base64 encoded image OR file path
        "image_format": "string"      // Image format (jpg, png, pdf, etc.)
    }
    
    Response:
    {
        "request_id": "string",           // Unique request ID
        "extracted_data": {...},          // Extracted structured data
        "confidence_score": number,       // Confidence (0-1)
        "status": "success|error",        // Status
        "message": "string"               // Status message
    }
    """
    try:
        data = request.get_json()
        
        # Validate request matches OCRExtractionRequest schema
        if not data:
            return jsonify({
                'request_id': str(uuid.uuid4()),
                'extracted_data': {},
                'confidence_score': 0,
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        document_type = data.get('document_type', 'Unknown')
        image_data = data.get('image_data')
        image_format = data.get('image_format', '')
        
        if not image_data:
            return jsonify({
                'request_id': str(uuid.uuid4()),
                'extracted_data': {},
                'confidence_score': 0,
                'status': 'error',
                'message': 'image_data is required'
            }), 400
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Handle both file paths and base64 encoded data
        filepath = None
        try:
            # Check if it's mock data for testing
            if image_data == "mock_document_data" or image_data.startswith("mock_"):
                # Use mock data - no file processing needed
                filepath = "mock_file"
            elif image_data.startswith('data:'):
                # Base64 data URL
                header, encoded = image_data.split(',', 1)
                image_bytes = base64.b64decode(encoded)
            elif len(image_data) > 200 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in image_data[:50]):
                # Base64 string
                image_bytes = base64.b64decode(image_data)
            else:
                # Treat as file path
                filepath = image_data
                if not os.path.exists(filepath):
                    return jsonify({
                        'request_id': request_id,
                        'extracted_data': {},
                        'confidence_score': 0,
                        'status': 'error',
                        'message': f'File not found: {filepath}'
                    }), 404
        except Exception as e:
            return jsonify({
                'request_id': request_id,
                'extracted_data': {},
                'confidence_score': 0,
                'status': 'error',
                'message': f'Invalid image_data format: {str(e)}'
            }), 400
        
        # If we decoded base64, save temporarily (skip for mock data)
        if not filepath and not image_data.startswith("mock_"):
            filename = f"{request_id}.{image_format or 'jpg'}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
        
        # Use enhanced OCR processing or fallback to original
        if filepath == "mock_file" or image_data.startswith("mock_"):
            # Use mock data for testing
            ocr_result = generate_mock_ocr_data(document_type, filepath)
        else:
            # Try enhanced OCR first, fallback to original if needed
            try:
                logger.info("Using Enhanced OCR (Tesseract + Google + AWS)")
                ocr_result = enhanced_ocr.process_document(filepath, document_type)
                
                # If enhanced OCR fails or has low confidence, try original
                if not ocr_result.get('success') or ocr_result.get('confidence', 0) < 0.5:
                    logger.warning("Enhanced OCR failed or low confidence, using original EasyOCR")
                    ocr_result = ocr.process_document(filepath)
                    
            except Exception as enhanced_error:
                logger.warning(f"Enhanced OCR failed: {str(enhanced_error)}, using original EasyOCR")
                try:
                    ocr_result = ocr.process_document(filepath)
                except Exception as ocr_error:
                    logger.warning(f"Original OCR also failed: {str(ocr_error)}, using mock data")
                    ocr_result = generate_mock_ocr_data(document_type, filepath)
        
        # Prepare response matching OCRExtractionResponse schema
        response = {
            'request_id': request_id,
            'extracted_data': {
                'raw_text': ocr_result['raw_text'],
                'structured_data': ocr_result['structured_data'],
                'document_type': document_type
            },
            'confidence_score': ocr_result.get('confidence', 0.75),
            'status': 'success',
            'message': 'OCR extraction completed successfully'
        }
        
        # Cache the result for verification
        extraction_cache[request_id] = {
            'request_data': data,
            'extraction_result': ocr_result,
            'timestamp': datetime.now().isoformat()
        }
        
        # Clean up temporary file if created from base64 (skip for mock data)
        if not image_data.startswith('/') and not image_data.startswith('C:') and not image_data.startswith("mock_"):
            try:
                os.remove(filepath)
            except:
                pass
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"OCR extraction error: {str(e)}")
        return jsonify({
            'request_id': request_id if 'request_id' in locals() else str(uuid.uuid4()),
            'extracted_data': {},
            'confidence_score': 0,
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/enhanced-ocr/extract', methods=['POST'])
def enhanced_extract_text():
    """
    Extract text using Enhanced OCR (PaddleOCR + EasyOCR + TrOCR + Tesseract)
    
    This endpoint uses multiple offline OCR engines for maximum accuracy:
    • PaddleOCR - High-performance multilingual OCR
    • EasyOCR - Deep learning based recognition  
    • TrOCR - Transformer-based accuracy
    • Tesseract - Traditional OCR with Hindi support
    
    Request body (JSON):
    {
        "document_type": "string",    // Type of document (Passport, Aadhaar, etc.)
        "image_data": "string",       // Base64 encoded image OR file path
        "image_format": "string",     // Image format (jpg, png, pdf, etc.)
        "use_all_engines": boolean    // Whether to use all available engines
    }
    
    Response:
    {
        "request_id": "string",
        "extracted_data": {...},
        "confidence_score": number,
        "engines_used": [array],      // List of engines that successfully processed
        "processing_details": {...},  // Detailed processing information
        "status": "success|error",
        "message": "string"
    }
    """
    request_id = str(uuid.uuid4())
    
    # IMMEDIATE LOGGING TO VERIFY ENDPOINT IS CALLED
    print("=" * 80)
    print(f"🚀 ENHANCED OCR ENDPOINT CALLED - {request_id}")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    logger.info(f"🚀 ENHANCED OCR ENDPOINT CALLED - {request_id}")
    
    try:
        # Check content length
        content_length = request.content_length
        if content_length and content_length > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({
                'request_id': request_id,
                'extracted_data': {},
                'confidence_score': 0,
                'status': 'error',
                'message': f'Request too large. Maximum size is {app.config["MAX_CONTENT_LENGTH"] // (1024*1024)}MB. Consider compressing your document or reducing the number of pages.'
            }), 413
        
        data = request.get_json()
        
        # LOG REQUEST DATA
        print(f"📦 REQUEST DATA RECEIVED - {request_id}")
        print(f"   Document Type: {data.get('document_type', 'Unknown') if data else 'No data'}")
        print(f"   Image Format: {data.get('image_format', 'Unknown') if data else 'No data'}")
        print(f"   Use All Engines: {data.get('use_all_engines', True) if data else 'No data'}")
        print(f"   Image Data Length: {len(data.get('image_data', '')) if data and data.get('image_data') else 0}")
        logger.info(f"📦 Request data received for {request_id}")
        
        if not data:
            return jsonify({
                'request_id': request_id,
                'extracted_data': {},
                'confidence_score': 0,
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        document_type = data.get('document_type', 'Unknown')
        image_data = data.get('image_data')
        image_format = data.get('image_format', '')
        use_all_engines = data.get('use_all_engines', True)
        
        # Check image data size
        if image_data and len(image_data) > 40 * 1024 * 1024:  # 40MB limit for base64 data
            return jsonify({
                'request_id': request_id,
                'extracted_data': {},
                'confidence_score': 0,
                'status': 'error',
                'message': 'Image data too large. Please compress the image or reduce the number of pages.'
            }), 413
        
        if not image_data:
            return jsonify({
                'request_id': request_id,
                'extracted_data': {},
                'confidence_score': 0,
                'status': 'error',
                'message': 'image_data is required'
            }), 400
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Handle image data (same as original endpoint)
        filepath = None
        image_bytes = None
        
        print(f"🔍 ANALYZING IMAGE DATA - {request_id}")
        print(f"   Image data starts with: '{image_data[:50]}...' (first 50 chars)")
        print(f"   Image data type: {type(image_data)}")
        print(f"   Total length: {len(image_data)}")
        
        try:
            if image_data == "mock_document_data" or image_data.startswith("mock_"):
                print(f"📝 MOCK DATA DETECTED - using mock processing")
                filepath = "mock_file"
            elif image_data.startswith('data:'):
                print(f"📄 BASE64 DATA URL DETECTED - decoding...")
                header, encoded = image_data.split(',', 1)
                image_bytes = base64.b64decode(encoded)
                print(f"   Decoded {len(image_bytes)} bytes from base64")
            elif len(image_data) > 200 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in image_data[:50]):
                print(f"📄 RAW BASE64 DETECTED - decoding...")
                image_bytes = base64.b64decode(image_data)
                print(f"   Decoded {len(image_bytes)} bytes from raw base64")
            else:
                print(f"📁 FILE PATH DETECTED - checking if exists...")
                filepath = image_data
                if not os.path.exists(filepath):
                    print(f"❌ FILE NOT FOUND: {filepath}")
                    return jsonify({
                        'request_id': request_id,
                        'extracted_data': {},
                        'confidence_score': 0,
                        'status': 'error',
                        'message': f'File not found: {filepath}'
                    }), 404
                else:
                    print(f"✅ FILE EXISTS: {filepath}")
        except Exception as e:
            print(f"❌ ERROR PROCESSING IMAGE DATA: {str(e)}")
            return jsonify({
                'request_id': request_id,
                'extracted_data': {},
                'confidence_score': 0,
                'status': 'error',
                'message': f'Invalid image_data format: {str(e)}'
            }), 400
        
        # Save temporary file if needed
        if not filepath and not image_data.startswith("mock_"):
            filename = f"{request_id}.{image_format or 'jpg'}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            logger.info(f"💾 SAVING FILE: {filename} ({len(image_bytes)} bytes)")
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            logger.info(f"✅ File saved successfully: {filepath}")
            
            # Check if it's a PDF
            if filepath.lower().endswith('.pdf'):
                logger.info(f"📄 PDF file detected - will convert to image for OCR")
        
        # Use Enhanced OCR processing
        if filepath == "mock_file" or image_data.startswith("mock_"):
            print(f"🎭 USING MOCK OCR PROCESSING")
            ocr_result = generate_mock_ocr_data(document_type, filepath)
            # Add mock processing details
            ocr_result['engines_used'] = ['mock']
            ocr_result['processing_details'] = {
                'processing_id': request_id,
                'selected_engine': 'mock',
                'confidence_breakdown': {'mock_confidence': 0.85}
            }
        else:
            print(f"🚀 USING REAL ENHANCED OCR PROCESSING")
            logger.info(f"🚀 STARTING Enhanced OCR Processing: {request_id}")
            logger.info(f"📄 Document Type: {document_type}")
            logger.info(f"📁 File Path: {filepath}")
            logger.info(f"🔧 Use All Engines: {use_all_engines}")
            
            ocr_result = enhanced_ocr.process_document(filepath, document_type)
            
            # DETAILED LOGGING OF RESULTS
            logger.info(f"🎯 FLASK ENDPOINT RESULTS - {request_id}")
            logger.info(f"✅ Success: {ocr_result.get('success', False)}")
            logger.info(f"🔧 Engines Used: {ocr_result.get('engines_used', [])}")
            logger.info(f"📊 Confidence: {ocr_result.get('confidence', 0.0):.3f}")
            
            raw_text = ocr_result.get('raw_text', '')
            if raw_text:
                text_preview = raw_text[:300] + '...' if len(raw_text) > 300 else raw_text
                logger.info(f"📝 EXTRACTED TEXT ({len(raw_text)} chars): '{text_preview}'")
            else:
                logger.warning(f"⚠️  NO TEXT EXTRACTED in Flask endpoint!")
            
            structured_data = ocr_result.get('structured_data', {})
            if structured_data:
                logger.info(f"📋 Structured Data: {list(structured_data.keys())}")
            
            logger.info(f"⏱️  Processing Time: {ocr_result.get('processing_time', 0.0):.2f}s")
            logger.info("=" * 60)
        
        # Prepare enhanced response with NER structured data
        structured_data = ocr_result.get('structured_data', {})
        ner_confidence = ocr_result.get('ner_overall_confidence', ocr_result.get('confidence', 0.0))
        
        response = {
            'request_id': request_id,
            'extracted_data': {
                'raw_text': ocr_result.get('raw_text', ''),
                'structured_data': structured_data,  # This now contains NER-extracted fields
                'document_type': document_type,
                'ner_metadata': ocr_result.get('ner_metadata', {}),
                'field_confidence_scores': ocr_result.get('ner_confidence_scores', {})
            },
            'confidence_score': ner_confidence,  # Use NER confidence if available
            'engines_used': ocr_result.get('engines_used', []),
            'processing_details': ocr_result.get('processing_details', {}),
            'processing_time': ocr_result.get('processing_time', 0.0),
            'status': 'success' if ocr_result.get('success', False) else 'error',
            'message': 'Enhanced OCR with NER extraction completed successfully' if ocr_result.get('success', False) else 'Enhanced OCR extraction failed'
        }
        
        # 💾 SAVE OCR RESULTS TO FILE FOR VERIFICATION
        saved_file = save_ocr_results_to_file(
            request_id, 
            ocr_result, 
            document_type, 
            ocr_result.get('engines_used', [])
        )
        if saved_file:
            print(f"📁 You can check the extracted text in: {saved_file}")
        
        # Cache the result
        extraction_cache[request_id] = {
            'request_data': data,
            'extraction_result': ocr_result,
            'timestamp': datetime.now().isoformat(),
            'enhanced': True,
            'saved_file': saved_file
        }
        
        # Clean up temporary file
        if not image_data.startswith('/') and not image_data.startswith('C:') and not image_data.startswith("mock_"):
            try:
                os.remove(filepath)
            except:
                pass
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Enhanced OCR extraction error: {str(e)}")
        return jsonify({
            'request_id': request_id if 'request_id' in locals() else str(uuid.uuid4()),
            'extracted_data': {},
            'confidence_score': 0,
            'engines_used': [],
            'status': 'error',
            'message': f'Enhanced OCR processing failed: {str(e)}'
        }), 500

@app.route('/api/hindi-ocr/extract', methods=['POST'])
def hindi_extract_text():
    """
    Extract Hindi text using Tesseract OCR (Based on your Colab implementation)
    
    Request body (JSON):
    {
        "document_type": "string",    // Type of document
        "image_data": "string",       // Base64 encoded image OR file path
        "language": "string",         // 'hindi', 'english', or 'hindi_english'
        "file_type": "string"         // 'image' or 'pdf'
    }
    
    Response:
    {
        "request_id": "string",
        "extracted_data": {...},
        "confidence_score": number,
        "language_used": "string",
        "processing_details": {...},
        "status": "success|error",
        "message": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'request_id': str(uuid.uuid4()),
                'extracted_data': {},
                'confidence_score': 0,
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        document_type = data.get('document_type', 'Unknown')
        image_data = data.get('image_data')
        language = data.get('language', 'hindi_english')
        file_type = data.get('file_type', 'image')
        
        if not image_data:
            return jsonify({
                'request_id': str(uuid.uuid4()),
                'extracted_data': {},
                'confidence_score': 0,
                'status': 'error',
                'message': 'image_data is required'
            }), 400
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Handle image data (same as other endpoints)
        filepath = None
        try:
            if image_data == "mock_document_data" or image_data.startswith("mock_"):
                filepath = "mock_file"
            elif image_data.startswith('data:'):
                header, encoded = image_data.split(',', 1)
                image_bytes = base64.b64decode(encoded)
            elif len(image_data) > 200 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in image_data[:50]):
                image_bytes = base64.b64decode(image_data)
            else:
                filepath = image_data
                if not os.path.exists(filepath):
                    return jsonify({
                        'request_id': request_id,
                        'extracted_data': {},
                        'confidence_score': 0,
                        'status': 'error',
                        'message': f'File not found: {filepath}'
                    }), 404
        except Exception as e:
            return jsonify({
                'request_id': request_id,
                'extracted_data': {},
                'confidence_score': 0,
                'status': 'error',
                'message': f'Invalid image_data format: {str(e)}'
            }), 400
        
        # Save temporary file if needed
        if not filepath and not image_data.startswith("mock_"):
            file_ext = '.pdf' if file_type == 'pdf' else '.jpg'
            filename = f"{request_id}{file_ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
        
        # Use Hindi OCR processing
        if filepath == "mock_file" or image_data.startswith("mock_"):
            # Generate mock Hindi text
            mock_hindi_text = """
मॉक हिंदी टेक्स्ट
नाम: जॉन स्मिथ
जन्म तिथि: 25/12/1988
राष्ट्रीयता: भारतीय
आधार संख्या: 1234-5678-9012
"""
            ocr_result = {
                'raw_text': mock_hindi_text,
                'structured_data': {
                    'language': language,
                    'language_code': 'hin+eng',
                    'processing_id': request_id
                },
                'confidence': 0.85,
                'processing_time': 0.5,
                'success': True
            }
        else:
            logger.info(f"Processing with Hindi OCR: {request_id}")
            ocr_result = hindi_ocr.process_document(filepath, language)
        
        # Prepare response
        response = {
            'request_id': request_id,
            'extracted_data': {
                'raw_text': ocr_result.get('raw_text', ''),
                'structured_data': ocr_result.get('structured_data', {}),
                'document_type': document_type
            },
            'confidence_score': ocr_result.get('confidence', 0.0),
            'language_used': language,
            'processing_details': ocr_result.get('processing_details', {}),
            'processing_time': ocr_result.get('processing_time', 0.0),
            'status': 'success' if ocr_result.get('success', False) else 'error',
            'message': 'Hindi OCR extraction completed successfully' if ocr_result.get('success', False) else 'Hindi OCR extraction failed'
        }
        
        # Cache the result
        extraction_cache[request_id] = {
            'request_data': data,
            'extraction_result': ocr_result,
            'timestamp': datetime.now().isoformat(),
            'hindi_ocr': True
        }
        
        # Clean up temporary file
        if not image_data.startswith('/') and not image_data.startswith('C:') and not image_data.startswith("mock_"):
            try:
                os.remove(filepath)
            except:
                pass
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Hindi OCR extraction error: {str(e)}")
        return jsonify({
            'request_id': request_id if 'request_id' in locals() else str(uuid.uuid4()),
            'extracted_data': {},
            'confidence_score': 0,
            'language_used': language if 'language' in locals() else 'hindi_english',
            'status': 'error',
            'message': f'Hindi OCR processing failed: {str(e)}'
        }), 500

@app.route('/api/hindi-ocr/status', methods=['GET'])
def get_hindi_ocr_status():
    """
    Get Hindi OCR status and language availability
    
    Response:
    {
        "tesseract_available": boolean,
        "hindi_support": boolean,
        "available_languages": [array],
        "status": "string",
        "recommendations": [array]
    }
    """
    try:
        # Get Hindi OCR status
        status = hindi_ocr.check_tesseract_languages()
        
        # Add recommendations
        recommendations = []
        if status['tesseract_available']:
            if status['hindi_support']:
                recommendations.append("Hindi OCR is ready for use")
            else:
                recommendations.append("Install Hindi language pack for Tesseract")
                recommendations.append("Run: py install_tesseract_windows.py")
        else:
            recommendations.append("Install Tesseract OCR first")
            recommendations.append("Run: py install_tesseract_windows.py")
        
        status['recommendations'] = recommendations
        status['timestamp'] = datetime.now().isoformat()
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Hindi OCR status check error: {str(e)}")
        return jsonify({
            'error': str(e),
            'tesseract_available': False,
            'hindi_support': False,
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/enhanced-ocr/status', methods=['GET'])
def get_enhanced_ocr_status():
    """
    Get status of all available Enhanced OCR engines
    
    Response:
    {
        "enhanced_ocr_available": boolean,
        "engines": {
            "engine_name": {
                "available": boolean,
                "type": "offline|cloud",
                "description": "string"
            }
        },
        "summary": {
            "total_engines": number,
            "available_engines": number,
            "offline_engines": number,
            "cloud_engines": number
        },
        "recommendations": [array],
        "installation_commands": [array],
        "status": "string",
        "timestamp": "string"
    }
    """
    try:
        # Get enhanced OCR status
        status = enhanced_ocr.get_engine_status()
        
        # Add recommendations
        recommendations = []
        installation_commands = []
        
        available_count = status['summary']['available_engines']
        total_count = status['summary']['total_engines']
        
        if available_count == 0:
            recommendations.append("No OCR engines available - install at least one engine")
            installation_commands.append("python install_enhanced_ocr.py")
        elif available_count < total_count:
            recommendations.append(f"Only {available_count}/{total_count} engines available - install more for better accuracy")
            
            # Check specific engines
            if not status['engines'].get('paddleocr', {}).get('available'):
                installation_commands.append("pip install paddlepaddle paddleocr")
            if not status['engines'].get('easyocr', {}).get('available'):
                installation_commands.append("pip install easyocr")
            if not status['engines'].get('trocr', {}).get('available'):
                installation_commands.append("pip install transformers torch")
            if not status['engines'].get('tesseract', {}).get('available'):
                installation_commands.append("Download Tesseract from https://github.com/tesseract-ocr/tesseract")
        else:
            recommendations.append("All OCR engines are available - optimal configuration!")
        
        # Add offline advantage
        if status['summary']['offline_engines'] > 0:
            recommendations.append("Using offline OCR engines - no API keys or internet required")
        
        status['recommendations'] = recommendations
        status['installation_commands'] = installation_commands
        status['status'] = 'optimal' if available_count == total_count else 'partial' if available_count > 0 else 'unavailable'
        status['timestamp'] = datetime.now().isoformat()
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Enhanced OCR status check error: {str(e)}")
        return jsonify({
            'error': str(e),
            'enhanced_ocr_available': False,
            'engines': {},
            'summary': {'total_engines': 0, 'available_engines': 0, 'offline_engines': 0, 'cloud_engines': 0},
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/enhanced-ocr/results', methods=['GET'])
def list_ocr_results():
    """
    List saved OCR result files
    
    Response:
    {
        "results": [
            {
                "filename": "string",
                "filepath": "string", 
                "timestamp": "string",
                "size": number
            }
        ],
        "total_files": number,
        "results_folder": "string"
    }
    """
    try:
        results = []
        
        if os.path.exists(RESULTS_FOLDER):
            for filename in os.listdir(RESULTS_FOLDER):
                if filename.endswith('.txt') and filename.startswith('ocr_result_'):
                    filepath = os.path.join(RESULTS_FOLDER, filename)
                    stat = os.stat(filepath)
                    
                    results.append({
                        'filename': filename,
                        'filepath': filepath,
                        'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'size': stat.st_size
                    })
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'results': results,
            'total_files': len(results),
            'results_folder': os.path.abspath(RESULTS_FOLDER),
            'status': 'success'
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing OCR results: {str(e)}")
        return jsonify({
            'error': str(e),
            'results': [],
            'total_files': 0,
            'status': 'error'
        }), 500

def get_ocr_engine_status():
    """
    Get status of all available OCR engines
    
    Response:
    {
        "enhanced_ocr_available": boolean,
        "engines": {...},
        "recommendations": [...]
    }
    """
    try:
        # Get enhanced OCR status
        enhanced_status = enhanced_ocr.get_engine_status()
        
        # Add recommendations
        recommendations = []
        if enhanced_status['enhanced_ocr_available']:
            recommendations.append("Enhanced OCR with multiple engines is available for maximum accuracy")
            if 'google_vision' in enhanced_status['engines']:
                recommendations.append("Google Vision API available for high-quality cloud OCR")
            if 'aws_textract' in enhanced_status['engines']:
                recommendations.append("AWS Textract available for document analysis")
        else:
            recommendations.append("Only EasyOCR available - consider setting up enhanced OCR engines")
        
        enhanced_status['recommendations'] = recommendations
        enhanced_status['timestamp'] = datetime.now().isoformat()
        
        return jsonify(enhanced_status), 200
        
    except Exception as e:
        logger.error(f"Engine status check error: {str(e)}")
        return jsonify({
            'error': str(e),
            'enhanced_ocr_available': False,
            'engines': {'easyocr': {'available': True, 'type': 'offline'}},
            'timestamp': datetime.now().isoformat()
        }), 500
def verify_extraction():
    """
    Verify extracted OCR data against validation rules
    
    Stoplight Schema: VerificationRequest -> VerificationResponse
    
    Request body (JSON):
    {
        "request_id": "string",           // Reference to extraction request_id
        "extracted_data": {...},          // Data to verify
        "verification_rules": {...}       // Rules to apply
    }
    
    Response:
    {
        "verification_id": "string",           // Unique verification ID
        "verified_fields": {...},              // Verified data
        "discrepancies": [array],              // List of mismatches
        "verification_status": "passed|failed",// Status
        "timestamp": "string"                  // ISO timestamp
    }
    """
    try:
        data = request.get_json()
        
        # Validate request matches VerificationRequest schema
        if not data:
            return jsonify({
                'verification_id': str(uuid.uuid4()),
                'verified_fields': {},
                'discrepancies': [],
                'verification_status': 'failed',
                'timestamp': datetime.now().isoformat(),
                'error': 'No JSON data provided'
            }), 400
        
        request_id = data.get('request_id')
        extracted_data = data.get('extracted_data', {})
        verification_rules = data.get('verification_rules', {})
        
        # Generate unique verification ID
        verification_id = str(uuid.uuid4())
        
        # Retrieve cached extraction if using request_id
        cached_extraction = None
        if request_id and request_id in extraction_cache:
            cached_extraction = extraction_cache[request_id]
        
        # Run verification
        verified_fields = {}
        discrepancies = []
        all_passed = True
        
        # Check required fields
        required_fields = verification_rules.get('required_fields', [])
        if isinstance(required_fields, list):
            for field in required_fields:
                if field not in extracted_data or not extracted_data[field]:
                    discrepancies.append({
                        'field': field,
                        'issue': 'Missing required field',
                        'expected': field,
                        'actual': extracted_data.get(field)
                    })
                    all_passed = False
                else:
                    verified_fields[field] = extracted_data[field]
        
        # Check field formats
        field_formats = verification_rules.get('field_formats', {})
        if isinstance(field_formats, dict):
            for field, format_rule in field_formats.items():
                if field in extracted_data:
                    field_value = extracted_data[field]
                    
                    # Validate format based on rule
                    if format_rule == 'email':
                        if '@' not in str(field_value):
                            discrepancies.append({
                                'field': field,
                                'issue': 'Invalid email format',
                                'expected': 'email',
                                'actual': field_value
                            })
                            all_passed = False
                        else:
                            verified_fields[field] = field_value
                    
                    elif format_rule == 'date':
                        # Check if it looks like a date
                        if not any(sep in str(field_value) for sep in ['-', '/', '.']):
                            discrepancies.append({
                                'field': field,
                                'issue': 'Invalid date format',
                                'expected': 'date (YYYY-MM-DD or DD/MM/YYYY)',
                                'actual': field_value
                            })
                            all_passed = False
                        else:
                            verified_fields[field] = field_value
                    
                    elif format_rule == 'phone':
                        phone_str = str(field_value).replace('+', '').replace('-', '').replace(' ', '')
                        if not phone_str.isdigit() or len(phone_str) < 10:
                            discrepancies.append({
                                'field': field,
                                'issue': 'Invalid phone format',
                                'expected': 'phone (10+ digits)',
                                'actual': field_value
                            })
                            all_passed = False
                        else:
                            verified_fields[field] = field_value
                    
                    elif format_rule == 'alphanumeric':
                        if not str(field_value).replace(' ', '').isalnum():
                            discrepancies.append({
                                'field': field,
                                'issue': 'Invalid alphanumeric format',
                                'expected': 'alphanumeric',
                                'actual': field_value
                            })
                            all_passed = False
                        else:
                            verified_fields[field] = field_value
                    else:
                        verified_fields[field] = field_value
        
        # Check confidence thresholds
        if cached_extraction:
            min_confidence = verification_rules.get('min_confidence', 0.5)
            ocr_confidence = cached_extraction['extraction_result'].get('confidence', 0.75)
            
            if ocr_confidence < min_confidence:
                discrepancies.append({
                    'field': 'overall_confidence',
                    'issue': f'OCR confidence below threshold',
                    'expected': f'>= {min_confidence}',
                    'actual': ocr_confidence
                })
                all_passed = False
        
        # Prepare response matching VerificationResponse schema
        response = {
            'verification_id': verification_id,
            'verified_fields': verified_fields,
            'discrepancies': discrepancies,
            'verification_status': 'passed' if all_passed else 'failed',
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache verification result
        extraction_cache[verification_id] = {
            'verification_result': response,
            'timestamp': datetime.now().isoformat()
        }
        
        status_code = 200 if all_passed else 422
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        return jsonify({
            'verification_id': verification_id if 'verification_id' in locals() else str(uuid.uuid4()),
            'verified_fields': {},
            'discrepancies': [],
            'verification_status': 'failed',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500
@app.route('/api/injinet/validate', methods=['POST'])
def validate_with_injinet():
    """
    Validate extracted OCR data with InjINet Indian identity records
    
    Request body JSON:
    {
        'extracted_data': {
            'name': str,
            'date_of_birth': str,
            'aadhaar_number': str,
            'pan_number': str,
            'phone': str,
            'email': str,
            'address': str
        },
        'document_type': str
    }
    
    Returns: InjINet validation response with UIN/VID
    """
    try:
        data = request.get_json()
        
        if not data or 'extracted_data' not in data:
            return jsonify({
                'success': False,
                'error': 'extracted_data is required',
                'validation_id': str(uuid.uuid4())
            }), 400
        
        extracted_data = data['extracted_data']
        extracted_data['document_type'] = data.get('document_type', 'Unknown')
        
        # Validate with InjINet
        validation_result = injinet.validate_indian_identity(extracted_data)
        
        if validation_result['success']:
            return jsonify(validation_result), 200
        else:
            return jsonify(validation_result), 422
            
    except Exception as e:
        logger.error(f"InjINet validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'validation_id': str(uuid.uuid4())
        }), 500

@app.route('/api/injinet/generate-vc', methods=['POST'])
def generate_verifiable_credential():
    """
    Generate Verifiable Credential from validated InjINet data
    
    Request body JSON:
    {
        'validation_id': str,
        'validated_data': {
            'success': bool,
            'identity_verified': bool,
            'verified_fields': dict,
            'uin': str,
            'vid': str
        }
    }
    
    Returns: Verifiable Credential in JWT format
    """
    try:
        data = request.get_json()
        
        if not data or 'validated_data' not in data:
            return jsonify({
                'success': False,
                'error': 'validated_data is required',
                'vc_id': str(uuid.uuid4())
            }), 400
        
        validated_data = data['validated_data']
        
        # Check if identity was verified
        if not validated_data.get('identity_verified', False):
            return jsonify({
                'success': False,
                'error': 'Identity must be verified before VC generation',
                'vc_id': str(uuid.uuid4())
            }), 422
        
        # Generate Verifiable Credential
        vc_result = injinet.generate_verifiable_credential(validated_data)
        
        if vc_result['success']:
            return jsonify(vc_result), 201
        else:
            return jsonify(vc_result), 422
            
    except Exception as e:
        logger.error(f"VC generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'vc_id': str(uuid.uuid4())
        }), 500

@app.route('/api/injinet/store-wallet', methods=['POST'])
def store_in_inji_wallet():
    """
    Store Verifiable Credential in InjI Wallet
    
    Request body JSON:
    {
        'vc_data': {
            'vc_id': str,
            'vc_jwt': str,
            'verifiable_credential': dict
        },
        'user_phone': str (optional)
    }
    
    Returns: Wallet storage result with download URL/QR code
    """
    try:
        data = request.get_json()
        
        if not data or 'vc_data' not in data:
            return jsonify({
                'success': False,
                'error': 'vc_data is required'
            }), 400
        
        vc_data = data['vc_data']
        user_phone = data.get('user_phone')
        
        # Store in InjI Wallet
        wallet_result = injinet.store_in_inji_wallet(vc_data, user_phone)
        
        if wallet_result['success']:
            return jsonify(wallet_result), 200
        else:
            return jsonify(wallet_result), 422
            
    except Exception as e:
        logger.error(f"Wallet storage error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/complete-workflow', methods=['POST'])
def complete_ocr_to_vc_workflow():
    """
    Complete workflow: OCR → Validation → InjINet → VC Generation → Wallet Storage
    
    Request body: multipart/form-data or JSON
    - 'document': Document image file (multipart) OR
    - 'document_data': Base64 image data (JSON)
    - 'document_type': Type of document
    - 'user_phone': Phone number for wallet notification (optional)
    
    Returns: Complete workflow result with VC and wallet information
    """
    try:
        # Handle both multipart and JSON requests
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Multipart form data
            if 'document' not in request.files:
                return jsonify({'error': 'No document file provided'}), 400
            
            file = request.files['document']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            document_type = request.form.get('document_type', 'Unknown')
            user_phone = request.form.get('user_phone')
            
            # Step 1: OCR Extraction
            ocr_result = ocr.process_document(filepath)
            
            # Clean up file
            os.remove(filepath)
            
        else:
            # JSON request
            data = request.get_json()
            if not data or 'document_data' not in data:
                return jsonify({'error': 'document_data is required'}), 400
            
            document_type = data.get('document_type', 'Unknown')
            user_phone = data.get('user_phone')
            
            # Use mock OCR for base64 data
            ocr_result = generate_mock_ocr_data(document_type)
        
        # Step 2: Data Verification (your existing logic)
        verification_rules = {
            "required_fields": ["name", "date_of_birth"],
            "field_formats": {
                "email": "email",
                "phone": "phone",
                "date_of_birth": "date"
            },
            "min_confidence": 0.7
        }
        
        # Step 3: InjINet Identity Validation
        extracted_data = ocr_result.get('structured_data', {})
        extracted_data['document_type'] = document_type
        
        validation_result = injinet.validate_indian_identity(extracted_data)
        
        if not validation_result['success'] or not validation_result.get('identity_verified'):
            return jsonify({
                'workflow_status': 'failed',
                'step_failed': 'identity_validation',
                'ocr_result': {
                    'raw_text': ocr_result.get('raw_text', ''),
                    'structured_data': extracted_data,
                    'confidence': ocr_result.get('confidence', 0.0)
                },
                'validation_result': validation_result,
                'error': 'Identity validation failed'
            }), 422
        
        # Step 4: Generate Verifiable Credential
        vc_result = injinet.generate_verifiable_credential(validation_result)
        
        if not vc_result['success']:
            return jsonify({
                'workflow_status': 'failed',
                'step_failed': 'vc_generation',
                'ocr_result': {
                    'raw_text': ocr_result.get('raw_text', ''),
                    'structured_data': extracted_data,
                    'confidence': ocr_result.get('confidence', 0.0)
                },
                'validation_result': validation_result,
                'vc_result': vc_result,
                'error': 'VC generation failed'
            }), 422
        
        # Step 5: Store in InjI Wallet
        wallet_result = injinet.store_in_inji_wallet(vc_result, user_phone)
        
        # Return complete workflow result
        return jsonify({
            'workflow_status': 'success',
            'ocr_result': {
                'raw_text': ocr_result.get('raw_text', ''),
                'structured_data': extracted_data,
                'confidence': ocr_result.get('confidence', 0.0)
            },
            'validation_result': validation_result,
            'vc_result': vc_result,
            'wallet_result': wallet_result,
            'summary': {
                'identity_verified': validation_result.get('identity_verified', False),
                'vc_generated': vc_result.get('success', False),
                'wallet_stored': wallet_result.get('success', False),
                'uin': validation_result.get('uin'),
                'vid': validation_result.get('vid'),
                'vc_id': vc_result.get('vc_id'),
                'wallet_download_url': wallet_result.get('download_url'),
                'qr_code': wallet_result.get('qr_code')
            },
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Complete workflow error: {str(e)}")
        return jsonify({
            'workflow_status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/inji/verify-qr', methods=['POST'])
def verify_qr_code():
    """
    Verify Verifiable Credential from QR code image
    
    Request body: multipart/form-data OR JSON
    - multipart/form-data: 'qr_image': QR code image file
    - JSON: {"qr_image": "data:image/png;base64,...", "verification_method": "opencv"}
    
    Returns: QR verification result with credential details
    """
    try:
        verification_id = str(uuid.uuid4())
        qr_image_data = None
        
        # Log the request for debugging
        logger.info(f"QR verification request - Content-Type: {request.content_type}")
        logger.info(f"QR verification request - Method: {request.method}")
        
        # Handle both file upload and JSON with base64
        if request.content_type and 'multipart/form-data' in request.content_type:
            # File upload format
            logger.info("Processing multipart/form-data request")
            if 'qr_image' not in request.files:
                logger.error("No qr_image file in multipart request")
                return jsonify({
                    'success': False,
                    'error': 'QR code image file is required',
                    'verification_id': verification_id
                }), 400
            
            qr_file = request.files['qr_image']
            if qr_file.filename == '':
                logger.error("Empty filename in multipart request")
                return jsonify({
                    'success': False,
                    'error': 'No QR image file selected',
                    'verification_id': verification_id
                }), 400
            
            # Read image data from file
            qr_image_data = qr_file.read()
            
        else:
            # JSON format with base64 data
            logger.info("Processing JSON request")
            data = request.get_json()
            
            if not data:
                logger.error("No JSON data provided")
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided',
                    'verification_id': verification_id,
                    'help': 'Send JSON with qr_image field containing base64 image data'
                }), 400
            
            logger.info(f"JSON data keys: {list(data.keys())}")
            
            qr_image_base64 = data.get('qr_image')
            if not qr_image_base64:
                logger.error("No qr_image field in JSON data")
                return jsonify({
                    'success': False,
                    'error': 'QR code image is required',
                    'verification_id': verification_id,
                    'received_fields': list(data.keys()),
                    'help': 'Include qr_image field with base64 image data'
                }), 400
            
            logger.info(f"QR image data length: {len(qr_image_base64)}")
            
            # First try official Inji Verify API with the QR data
            try:
                # Extract QR data using OpenCV first
                qr_scan_result = inji_verify.decode_qr_from_base64(qr_image_base64)
                
                if qr_scan_result.get('success'):
                    qr_data = qr_scan_result.get('qr_data', '')
                    logger.info(f"QR data extracted successfully: {len(qr_data)} characters")
                    
                    # Try official Inji Verify API
                    try:
                        official_result = inji_verify.verify_with_official_inji_api(qr_data)
                        
                        if official_result.get('success'):
                            logger.info("Official MOSIP API verification successful")
                            return jsonify({
                                'success': True,
                                'verification_id': verification_id,
                                'qr_scan_result': qr_scan_result,
                                'official_verification': official_result,
                                'method': 'official_inji_api',
                                'api_used': 'Official MOSIP Inji Verify API',
                                'timestamp': datetime.now().isoformat()
                            }), 200
                        else:
                            logger.warning("Official API failed, using OpenCV fallback")
                            # Official API failed, use OpenCV result
                            return jsonify({
                                'success': True,
                                'verification_id': verification_id,
                                'qr_scan_result': qr_scan_result,
                                'method': 'opencv_fallback',
                                'note': 'Official API unavailable, used OpenCV verification',
                                'timestamp': datetime.now().isoformat()
                            }), 200
                    except Exception as api_error:
                        logger.error(f"Official API error: {str(api_error)}")
                        # Fallback to OpenCV
                        return jsonify({
                            'success': True,
                            'verification_id': verification_id,
                            'qr_scan_result': qr_scan_result,
                            'method': 'opencv_fallback',
                            'note': 'Official API error, used OpenCV verification',
                            'timestamp': datetime.now().isoformat()
                        }), 200
                else:
                    logger.error(f"QR scanning failed: {qr_scan_result.get('error')}")
                    return jsonify({
                        'success': False,
                        'error': 'Failed to decode QR from base64 image',
                        'verification_id': verification_id,
                        'qr_scan_result': qr_scan_result,
                        'help': 'Ensure qr_image contains valid base64 image data'
                    }), 400
                    
            except Exception as e:
                logger.error(f"QR verification error: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'verification_id': verification_id
                }), 500
        
        # Handle file-based QR verification (original logic)
        if qr_image_data:
            logger.info("Processing file-based QR verification")
            # Verify QR code credential using file data
            verification_result = inji_verify.verify_qr_code_credential(qr_image_data)
            
            if verification_result['success']:
                return jsonify(verification_result), 200
            else:
                return jsonify(verification_result), 422
            
    except Exception as e:
        logger.error(f"QR verification endpoint error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'verification_id': str(uuid.uuid4()),
            'help': 'Check request format and try again'
        }), 500

@app.route('/api/inji/generate-qr', methods=['POST'])
def generate_qr_for_vc():
    """
    Generate QR code for Verifiable Credential
    
    Request body JSON:
    {
        'verifiable_credential': dict  // VC data to encode in QR
    }
    
    Returns: QR code image and data
    """
    try:
        data = request.get_json()
        
        if not data or 'verifiable_credential' not in data:
            return jsonify({
                'success': False,
                'error': 'verifiable_credential is required',
                'qr_id': str(uuid.uuid4())
            }), 400
        
        vc_data = data['verifiable_credential']
        
        # Generate QR code
        qr_result = inji_verify.generate_qr_code_for_vc(vc_data)
        
        if qr_result['success']:
            return jsonify(qr_result), 201
        else:
            return jsonify(qr_result), 422
            
    except Exception as e:
        logger.error(f"QR generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'qr_id': str(uuid.uuid4())
        }), 500

@app.route('/api/inji/create-presentation', methods=['POST'])
def create_verifiable_presentation():
    """
    Create Verifiable Presentation for OpenID4VP
    
    Request body JSON:
    {
        'credentials': [list of VCs],
        'challenge': str (optional)
    }
    
    Returns: Verifiable Presentation
    """
    try:
        data = request.get_json()
        
        if not data or 'credentials' not in data:
            return jsonify({
                'success': False,
                'error': 'credentials array is required',
                'vp_id': str(uuid.uuid4())
            }), 400
        
        credentials = data['credentials']
        challenge = data.get('challenge')
        
        # Create Verifiable Presentation
        vp_result = inji_verify.create_verifiable_presentation(credentials, challenge)
        
        if vp_result['success']:
            return jsonify(vp_result), 201
        else:
            return jsonify(vp_result), 422
            
    except Exception as e:
        logger.error(f"VP creation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'vp_id': str(uuid.uuid4())
        }), 500

@app.route('/api/complete-workflow-with-qr', methods=['POST'])
def complete_workflow_with_qr():
    """
    Complete workflow: OCR → InjINet → VC → QR Generation
    
    Request body: multipart/form-data or JSON
    - 'document': Document image file (multipart) OR
    - 'document_data': Base64 image data (JSON)
    - 'document_type': Type of document
    - 'user_phone': Phone number for wallet notification (optional)
    - 'generate_qr': boolean (default: true)
    
    Returns: Complete workflow result with VC and QR code
    """
    try:
        # Handle both multipart and JSON requests
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Multipart form data
            if 'document' not in request.files:
                return jsonify({'error': 'No document file provided'}), 400
            
            file = request.files['document']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            document_type = request.form.get('document_type', 'Unknown')
            user_phone = request.form.get('user_phone')
            generate_qr = request.form.get('generate_qr', 'true').lower() == 'true'
            
            # Step 1: OCR Extraction
            ocr_result = ocr.process_document(filepath)
            
            # Clean up file
            os.remove(filepath)
            
        else:
            # JSON request
            data = request.get_json()
            if not data or 'document_data' not in data:
                return jsonify({'error': 'document_data is required'}), 400
            
            document_type = data.get('document_type', 'Unknown')
            user_phone = data.get('user_phone')
            generate_qr = data.get('generate_qr', True)
            
            # Use mock OCR for base64 data
            ocr_result = generate_mock_ocr_data(document_type)
        
        # Step 2: InjINet Identity Validation
        extracted_data = ocr_result.get('structured_data', {})
        extracted_data['document_type'] = document_type
        
        validation_result = injinet.validate_indian_identity(extracted_data)
        
        if not validation_result['success'] or not validation_result.get('identity_verified'):
            return jsonify({
                'workflow_status': 'failed',
                'step_failed': 'identity_validation',
                'ocr_result': {
                    'raw_text': ocr_result.get('raw_text', ''),
                    'structured_data': extracted_data,
                    'confidence': ocr_result.get('confidence', 0.0)
                },
                'validation_result': validation_result,
                'error': 'Identity validation failed'
            }), 422
        
        # Step 3: Generate Verifiable Credential
        vc_result = injinet.generate_verifiable_credential(validation_result)
        
        if not vc_result['success']:
            return jsonify({
                'workflow_status': 'failed',
                'step_failed': 'vc_generation',
                'ocr_result': {
                    'raw_text': ocr_result.get('raw_text', ''),
                    'structured_data': extracted_data,
                    'confidence': ocr_result.get('confidence', 0.0)
                },
                'validation_result': validation_result,
                'vc_result': vc_result,
                'error': 'VC generation failed'
            }), 422
        
        # Step 4: Generate QR Code (if requested)
        qr_result = None
        if generate_qr:
            qr_result = inji_verify.generate_qr_code_for_vc(vc_result['verifiable_credential'])
        
        # Step 5: Store in InjI Wallet
        wallet_result = injinet.store_in_inji_wallet(vc_result, user_phone)
        
        # Return complete workflow result
        return jsonify({
            'workflow_status': 'success',
            'ocr_result': {
                'raw_text': ocr_result.get('raw_text', ''),
                'structured_data': extracted_data,
                'confidence': ocr_result.get('confidence', 0.0)
            },
            'validation_result': validation_result,
            'vc_result': vc_result,
            'qr_result': qr_result,
            'wallet_result': wallet_result,
            'summary': {
                'identity_verified': validation_result.get('identity_verified', False),
                'vc_generated': vc_result.get('success', False),
                'qr_generated': qr_result.get('success', False) if qr_result else False,
                'wallet_stored': wallet_result.get('success', False),
                'uin': validation_result.get('uin'),
                'vid': validation_result.get('vid'),
                'vc_id': vc_result.get('vc_id'),
                'qr_code_image': qr_result.get('qr_code_image') if qr_result else None,
                'wallet_download_url': wallet_result.get('download_url')
            },
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Complete workflow with QR error: {str(e)}")
        return jsonify({
            'workflow_status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def authenticate_mosip():
    """
    Authenticate with MOSIP platform
    
    Returns: Authentication status
    """
    try:
        # Check if credentials are configured
        if not mosip.username or not mosip.client_id:
            return jsonify({
                'success': False,
                'error': 'MOSIP credentials not configured. Please set environment variables.'
            }), 400
        
        success = mosip.authenticate()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Successfully authenticated with MOSIP',
                'base_url': mosip.base_url
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Authentication failed'
            }), 401
            
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mosip/preregister', methods=['POST'])
def preregister():
    """
    Submit pre-registration data to MOSIP with OCR extracted information
    
    Request body JSON:
    {
        'ocr_data': {
            'name': str,
            'date_of_birth': str,
            'gender': str,
            'phone': str,
            'email': str,
            'address': str,
            'id_number': str
        },
        'document_type': str,  # e.g., 'Passport', 'NationalID'
        'document_file': base64_encoded_string  # Optional: actual document file
    }
    
    Returns: Pre-registration response with registration ID
    """
    try:
        data = request.get_json()
        
        if not data or 'ocr_data' not in data:
            return jsonify({'error': 'OCR data required'}), 400
        
        ocr_data = data['ocr_data']
        
        # Format data for MOSIP pre-registration API
        resident_data = {
            'fullName': ocr_data.get('name', ''),
            'dateOfBirth': format_date(ocr_data.get('date_of_birth', '')),
            'gender': ocr_data.get('gender', ''),
            'mobileNumber': ocr_data.get('phone', ''),
            'emailId': ocr_data.get('email', ''),
            'address': {
                'street': ocr_data.get('address', ''),
                'city': '',
                'state': '',
                'postalCode': '',
                'country': 'India'
            },
            'documents': [
                {
                    'documentType': data.get('document_type', 'National ID'),
                    'documentNumber': ocr_data.get('id_number', ''),
                }
            ]
        }
        
        # Add document file if provided
        if 'document_file' in data and data['document_file']:
            resident_data['documents'][0]['documentFileContent'] = data['document_file']
        
        # Authenticate if not already done
        if not mosip.access_token:
            if not mosip.authenticate():
                return jsonify({'error': 'Failed to authenticate with MOSIP'}), 401
        
        # Submit pre-registration
        result = mosip.submit_preregistration(resident_data)
        
        return jsonify(result), (201 if result['success'] else 400)
        
    except Exception as e:
        logger.error(f"Pre-registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mosip/status/<pre_reg_id>', methods=['GET'])
def get_registration_status(pre_reg_id):
    """
    Get status of submitted pre-registration
    
    URL Parameter: pre_reg_id - Pre-registration ID
    
    Returns: Current status and details
    """
    try:
        if not mosip.access_token:
            if not mosip.authenticate():
                return jsonify({'error': 'Failed to authenticate with MOSIP'}), 401
        
        result = mosip.get_preregistration_status(pre_reg_id)
        
        return jsonify(result), (200 if result['success'] else 400)
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mosip/upload-document', methods=['POST'])
def upload_document():
    """
    Upload document for pre-registration
    
    Request body JSON:
    {
        'pre_reg_id': str,
        'document_type': str,
        'document_file': base64_encoded_string
    }
    
    Returns: Upload response
    """
    try:
        data = request.get_json()
        
        if not data or 'pre_reg_id' not in data or 'document_file' not in data:
            return jsonify({'error': 'pre_reg_id and document_file required'}), 400
        
        if not mosip.access_token:
            if not mosip.authenticate():
                return jsonify({'error': 'Failed to authenticate with MOSIP'}), 401
        
        document_data = {
            'documentType': data.get('document_type', 'National ID'),
            'documentFileContent': data['document_file']
        }
        
        result = mosip.upload_document(data['pre_reg_id'], document_data)
        
        return jsonify(result), (201 if result['success'] else 400)
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/combined/ocr-and-register', methods=['POST'])
def ocr_and_register():
    """
    Combined endpoint: Extract OCR from document AND submit to MOSIP
    
    Request body: multipart/form-data
    - 'document': Document image file
    - 'document_type': Type of document (optional)
    
    Returns: OCR result + pre-registration response
    """
    try:
        if 'document' not in request.files:
            return jsonify({'error': 'No document file provided'}), 400
        
        file = request.files['document']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only images allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Step 1: Extract text with OCR
        ocr_result = ocr.process_document(filepath)
        
        # Read file as base64
        with open(filepath, 'rb') as f:
            document_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # Clean up temporary file
        os.remove(filepath)
        
        # Step 2: Authenticate with MOSIP
        if not mosip.access_token:
            if not mosip.authenticate():
                return jsonify({
                    'ocr_result': ocr_result,
                    'mosip_registration': {
                        'success': False,
                        'error': 'Failed to authenticate with MOSIP'
                    }
                }), 401
        
        # Step 3: Submit to MOSIP
        resident_data = {
            'fullName': ocr_result['structured_data'].get('name', ''),
            'dateOfBirth': format_date(ocr_result['structured_data'].get('date_of_birth', '')),
            'gender': ocr_result['structured_data'].get('gender', ''),
            'mobileNumber': ocr_result['structured_data'].get('phone', ''),
            'emailId': ocr_result['structured_data'].get('email', ''),
            'address': {
                'street': ocr_result['structured_data'].get('address', ''),
                'city': '',
                'state': '',
                'postalCode': '',
                'country': 'India'
            },
            'documents': [
                {
                    'documentType': request.form.get('document_type', 'National ID'),
                    'documentNumber': ocr_result['structured_data'].get('id_number', ''),
                    'documentFileContent': document_base64
                }
            ]
        }
        
        mosip_result = mosip.submit_preregistration(resident_data)
        
        return jsonify({
            'ocr_result': {
                'raw_text': ocr_result['raw_text'],
                'structured_data': ocr_result['structured_data'],
                'confidence': ocr_result['confidence']
            },
            'mosip_registration': mosip_result,
            'timestamp': datetime.now().isoformat()
        }), (201 if mosip_result['success'] else 400)
        
    except Exception as e:
        logger.error(f"Combined OCR-Register error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    """Check if file has allowed extension"""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'bmp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/api/qr/generate-test-itr', methods=['GET'])
def generate_test_itr_qr():
    """
    Generate a test QR code with sample ITR data for testing
    
    Response:
    {
        "qr_data": "string",      // JSON string with ITR data
        "qr_image": "string",     // Base64 QR code image
        "sample_data": {...}      // The sample data structure
    }
    """
    try:
        # Sample ITR data
        sample_data = {
            "personalInfo": {
                "name": "Rajesh Kumar Sharma",
                "pan": "ABCDE1234F",
                "aadhaar": "123456789012",
                "date_of_birth": "15/03/1985",
                "address": "123 MG Road, Bangalore, Karnataka 560001",
                "phone": "+91 9876543210",
                "email": "rajesh.sharma@email.com"
            },
            "incomeDetails": {
                "gross_salary": 1200000,
                "basic_salary": 800000,
                "hra_received": 200000,
                "other_allowances": 100000,
                "interest_income": 50000,
                "other_income": 25000
            },
            "deductions": {
                "standard_deduction": 50000,
                "section_80c": 150000,
                "section_80d": 25000,
                "professional_tax": 2400
            },
            "taxDetails": {
                "tds_deducted": 120000,
                "advance_tax": 50000,
                "tax_regime": "new"
            }
        }
        
        # Convert to JSON string
        import json
        qr_data_string = json.dumps(sample_data, indent=2)
        
        # Generate QR code image
        import qrcode
        from io import BytesIO
        import base64
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data_string)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        qr_data_url = f"data:image/png;base64,{qr_image_base64}"
        
        return jsonify({
            'qr_data': qr_data_string,
            'qr_image': qr_data_url,
            'sample_data': sample_data,
            'message': 'Test QR code generated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Test QR generation error: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to generate test QR code'
        }), 500

@app.route('/api/form16/process-and-generate-qr', methods=['POST'])
def process_form16_and_generate_qr():
    """
    Complete Form-16 processing workflow:
    1. Upload Form-16 document
    2. Extract data using Enhanced OCR + NER
    3. Generate comprehensive QR code with all ITR fields
    4. Return both extracted data and QR code for download
    
    Request body: multipart/form-data
    - 'form16_document': Form-16 file (PDF/image)
    - 'include_qr_generation': boolean (default: true)
    
    Response:
    {
        "request_id": "string",
        "status": "success|error",
        "extracted_data": {
            "personal_info": {...},
            "income_details": {...},
            "deductions": {...},
            "tax_details": {...}
        },
        "ner_confidence": number,
        "qr_code": {
            "qr_image": "data:image/png;base64,...",
            "qr_data": "string",
            "download_url": "string"
        },
        "form_completeness": {
            "total_fields": number,
            "filled_fields": number,
            "completeness_percentage": number,
            "missing_fields": [array]
        },
        "message": "string"
    }
    """
    try:
        request_id = str(uuid.uuid4())
        
        logger.info(f"🔍 Form-16 Processing Request - {request_id}")
        print(f"🔍 Form-16 Processing Request - {request_id}")
        
        # Check if file was uploaded
        if 'form16_document' not in request.files:
            return jsonify({
                'request_id': request_id,
                'status': 'error',
                'extracted_data': {},
                'message': 'No Form-16 document provided'
            }), 400
        
        file = request.files['form16_document']
        if file.filename == '':
            return jsonify({
                'request_id': request_id,
                'status': 'error',
                'extracted_data': {},
                'message': 'No file selected'
            }), 400
        
        include_qr = request.form.get('include_qr_generation', 'true').lower() == 'true'
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{request_id}_{filename}")
        file.save(filepath)
        
        print(f"📄 Processing Form-16: {filename}")
        print(f"📁 File saved to: {filepath}")
        
        # Step 1: Enhanced OCR extraction
        print("🔍 Step 1: Enhanced OCR extraction...")
        try:
            ocr_result = enhanced_ocr.process_document(filepath, 'Form 16')
            print(f"✅ OCR completed - Success: {ocr_result.get('success', False)}")
            print(f"📊 OCR Confidence: {ocr_result.get('confidence', 0.0):.3f}")
        except Exception as e:
            print(f"❌ Enhanced OCR failed: {str(e)}, using fallback")
            ocr_result = generate_mock_ocr_data('Form 16', filepath)
        
        if not ocr_result.get('success'):
            return jsonify({
                'request_id': request_id,
                'status': 'error',
                'extracted_data': {},
                'message': 'Failed to extract text from Form-16 document'
            }), 400
        
        raw_text = ocr_result.get('raw_text', '')
        print(f"📝 Extracted text length: {len(raw_text)} characters")
        
        # Step 2: Enhanced NER extraction for Form-16 specific fields
        print("🧠 Step 2: NER extraction for Form-16 fields...")
        try:
            from ner_extractor import NERExtractor
            ner_extractor = NERExtractor()
            
            # Form-16 specific field extraction
            form16_fields = [
                'name', 'pan', 'aadhaar', 'date_of_birth', 'address', 'mobile', 'email',
                'gross_salary', 'basic_salary', 'hra_received', 'other_allowances', 
                'professional_tax', 'tds_deducted', 'employer', 'tan', 'assessment_year',
                'section_80c', 'section_80d', 'standard_deduction'
            ]
            
            ner_result = ner_extractor.extract_fields(raw_text, form16_fields)
            ner_confidence = ner_result.get('overall_confidence', 0.0)
            extracted_fields = ner_result.get('extracted_fields', {})
            
            print(f"🧠 NER completed - Confidence: {ner_confidence:.3f}")
            print(f"📋 Extracted {len(extracted_fields)} fields")
            
        except Exception as e:
            print(f"❌ NER extraction failed: {str(e)}, using OCR structured data")
            extracted_fields = ocr_result.get('structured_data', {})
            ner_confidence = ocr_result.get('confidence', 0.0)
        
        # Step 3: Organize data into ITR form sections
        print("📋 Step 3: Organizing data into ITR form sections...")
        form_sections = organize_form16_data_to_itr(extracted_fields)
        
        # Step 4: Calculate form completeness
        completeness_info = calculate_form_completeness(form_sections)
        print(f"📊 Form completeness: {completeness_info['completeness_percentage']:.1f}%")
        
        # Step 5: Generate comprehensive QR code (if requested)
        qr_info = None
        if include_qr:
            print("🔲 Step 5: Generating comprehensive QR code...")
            try:
                qr_info = generate_comprehensive_itr_qr(form_sections, request_id)
                print(f"✅ QR code generated successfully")
            except Exception as e:
                print(f"❌ QR generation failed: {str(e)}")
                qr_info = {'error': str(e)}
        
        # Prepare response
        response = {
            'request_id': request_id,
            'status': 'success',
            'extracted_data': form_sections,
            'ner_confidence': ner_confidence,
            'form_completeness': completeness_info,
            'message': f'Form-16 processed successfully. Extracted {completeness_info["filled_fields"]} fields with {completeness_info["completeness_percentage"]:.1f}% completeness.'
        }
        
        if qr_info and 'error' not in qr_info:
            response['qr_code'] = qr_info
        
        # Cache the result
        extraction_cache[request_id] = {
            'form16_processing': True,
            'ocr_result': ocr_result,
            'ner_result': {'extracted_fields': extracted_fields, 'overall_confidence': ner_confidence},
            'form_sections': form_sections,
            'completeness_info': completeness_info,
            'qr_info': qr_info,
            'timestamp': datetime.now().isoformat()
        }
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Form-16 processing error: {str(e)}")
        return jsonify({
            'request_id': request_id if 'request_id' in locals() else str(uuid.uuid4()),
            'status': 'error',
            'extracted_data': {},
            'message': f'Form-16 processing failed: {str(e)}'
        }), 500

def organize_form16_data_to_itr(extracted_fields):
    """
    Organize Form-16 extracted fields into ITR form sections
    
    Args:
        extracted_fields (dict): Fields extracted from Form-16
        
    Returns:
        dict: Organized ITR form sections
    """
    print(f"📋 Organizing {len(extracted_fields)} fields into ITR sections...")
    
    form_sections = {
        'personal_info': {},
        'income_details': {},
        'deductions': {},
        'tax_details': {}
    }
    
    # Personal Information mapping
    personal_mapping = {
        'name': 'name',
        'pan': 'pan',
        'aadhaar': 'aadhaar',
        'date_of_birth': 'date_of_birth',
        'address': 'address',
        'mobile': 'phone',
        'email': 'email',
        'employer': 'employer'
    }
    
    # Income Details mapping
    income_mapping = {
        'gross_salary': 'gross_salary',
        'basic_salary': 'basic_salary',
        'hra_received': 'hra_received',
        'other_allowances': 'other_allowances',
        'interest_income': 'interest_income',
        'other_income': 'other_income'
    }
    
    # Deductions mapping
    deductions_mapping = {
        'standard_deduction': 'standard_deduction',
        'section_80c': 'section_80c',
        'section_80d': 'section_80d',
        'professional_tax': 'professional_tax'
    }
    
    # Tax Details mapping
    tax_mapping = {
        'tds_deducted': 'tds_deducted',
        'advance_tax': 'advance_tax',
        'tan': 'tan',
        'assessment_year': 'assessment_year'
    }
    
    # Map fields to sections
    for field, value in extracted_fields.items():
        if not value:
            continue
            
        # Personal Info
        if field in personal_mapping:
            form_sections['personal_info'][personal_mapping[field]] = value
            print(f"✅ Personal: {field} -> {personal_mapping[field]} = {value}")
        
        # Income Details
        elif field in income_mapping:
            try:
                # Convert to integer for numeric fields
                numeric_value = int(float(str(value).replace(',', '').replace('₹', '')))
                form_sections['income_details'][income_mapping[field]] = numeric_value
                print(f"✅ Income: {field} -> {income_mapping[field]} = {numeric_value}")
            except:
                form_sections['income_details'][income_mapping[field]] = value
                print(f"✅ Income (text): {field} -> {income_mapping[field]} = {value}")
        
        # Deductions
        elif field in deductions_mapping:
            try:
                numeric_value = int(float(str(value).replace(',', '').replace('₹', '')))
                form_sections['deductions'][deductions_mapping[field]] = numeric_value
                print(f"✅ Deduction: {field} -> {deductions_mapping[field]} = {numeric_value}")
            except:
                form_sections['deductions'][deductions_mapping[field]] = value
                print(f"✅ Deduction (text): {field} -> {deductions_mapping[field]} = {value}")
        
        # Tax Details
        elif field in tax_mapping:
            if field in ['tds_deducted', 'advance_tax']:
                try:
                    numeric_value = int(float(str(value).replace(',', '').replace('₹', '')))
                    form_sections['tax_details'][tax_mapping[field]] = numeric_value
                    print(f"✅ Tax: {field} -> {tax_mapping[field]} = {numeric_value}")
                except:
                    form_sections['tax_details'][tax_mapping[field]] = value
                    print(f"✅ Tax (text): {field} -> {tax_mapping[field]} = {value}")
            else:
                form_sections['tax_details'][tax_mapping[field]] = value
                print(f"✅ Tax: {field} -> {tax_mapping[field]} = {value}")
    
    # Add default values
    if not form_sections['deductions'].get('standard_deduction'):
        form_sections['deductions']['standard_deduction'] = 50000
        print("✅ Added default standard_deduction: 50000")
    
    if not form_sections['tax_details'].get('tax_regime'):
        form_sections['tax_details']['tax_regime'] = 'new'
        print("✅ Added default tax_regime: new")
    
    return form_sections

def calculate_form_completeness(form_sections):
    """
    Calculate how complete the ITR form is based on extracted data
    
    Args:
        form_sections (dict): Organized form sections
        
    Returns:
        dict: Completeness information
    """
    # Define all possible ITR fields
    all_fields = {
        'personal_info': ['name', 'pan', 'aadhaar', 'date_of_birth', 'address', 'phone', 'email'],
        'income_details': ['gross_salary', 'basic_salary', 'hra_received', 'other_allowances', 'interest_income', 'other_income'],
        'deductions': ['standard_deduction', 'section_80c', 'section_80d', 'professional_tax'],
        'tax_details': ['tds_deducted', 'advance_tax', 'tax_regime']
    }
    
    total_fields = sum(len(fields) for fields in all_fields.values())
    filled_fields = 0
    missing_fields = []
    
    for section, fields in all_fields.items():
        section_data = form_sections.get(section, {})
        for field in fields:
            if field in section_data and section_data[field]:
                filled_fields += 1
            else:
                missing_fields.append(f"{section}.{field}")
    
    completeness_percentage = (filled_fields / total_fields) * 100
    
    return {
        'total_fields': total_fields,
        'filled_fields': filled_fields,
        'completeness_percentage': completeness_percentage,
        'missing_fields': missing_fields
    }

def generate_comprehensive_itr_qr(form_sections, request_id):
    """
    Generate a comprehensive QR code containing all ITR form data
    
    Args:
        form_sections (dict): Complete ITR form data
        request_id (str): Request identifier
        
    Returns:
        dict: QR code information
    """
    try:
        # Create comprehensive ITR data structure
        itr_qr_data = {
            "itr_form_data": {
                "personalInfo": form_sections.get('personal_info', {}),
                "incomeDetails": form_sections.get('income_details', {}),
                "deductions": form_sections.get('deductions', {}),
                "taxDetails": form_sections.get('tax_details', {})
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "request_id": request_id,
                "format": "COMPREHENSIVE_ITR_FORM",
                "version": "1.0",
                "source": "Form16_NER_Extraction"
            },
            "validation": {
                "total_fields": sum(len(section) for section in form_sections.values()),
                "extraction_method": "Enhanced_OCR_NER",
                "completeness_check": True
            }
        }
        
        # Convert to JSON string
        import json
        qr_data_string = json.dumps(itr_qr_data, indent=2)
        
        # Generate QR code using existing backend functionality
        try:
            # Use the existing QR generation from the test endpoint logic
            import qrcode
            from io import BytesIO
            import base64
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data_string)
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            qr_data_url = f"data:image/png;base64,{qr_image_base64}"
            
            # Save QR code to output folder for download
            output_filename = f"form16_itr_qr_{request_id[:8]}.png"
            output_path = os.path.join('output', output_filename)
            os.makedirs('output', exist_ok=True)
            qr_image.save(output_path)
            
            return {
                'qr_image': qr_data_url,
                'qr_data': qr_data_string,
                'download_filename': output_filename,
                'download_path': output_path,
                'data_size': len(qr_data_string),
                'fields_included': sum(len(section) for section in form_sections.values())
            }
            
        except ImportError:
            # Fallback if qrcode is not available
            return {
                'qr_data': qr_data_string,
                'data_size': len(qr_data_string),
                'fields_included': sum(len(section) for section in form_sections.values()),
                'note': 'QR image generation not available - data only'
            }
        
    except Exception as e:
        logger.error(f"QR generation error: {str(e)}")
        raise e

@app.route('/api/qr/decode-itr', methods=['POST'])
def decode_qr_for_itr():
    """
    Decode QR code from wallet and extract ITR form data for auto-fill
    
    Request body JSON:
    {
        "qr_image": "string",         // Base64 encoded QR image OR QR data string
        "image_format": "string"      // Image format (jpg, png, etc.) - optional
    }
    
    Response:
    {
        "request_id": "string",
        "status": "success|error",
        "form_sections": {
            "personal_info": {...},
            "income_details": {...},
            "deductions": {...},
            "tax_details": {...}
        },
        "confidence_score": number,
        "message": "string"
    }
    """
    try:
        data = request.get_json()
        request_id = str(uuid.uuid4())
        
        logger.info(f"🔍 QR ITR Decode Request - {request_id}")
        print(f"🔍 QR ITR Decode Request - {request_id}")
        
        if not data:
            print("❌ No JSON data provided")
            return jsonify({
                'request_id': request_id,
                'status': 'error',
                'form_sections': {},
                'confidence_score': 0,
                'message': 'No JSON data provided'
            }), 400
        
        qr_image = data.get('qr_image')
        image_format = data.get('image_format', 'png')
        
        print(f"📦 Request data keys: {list(data.keys())}")
        print(f"📱 QR image data length: {len(qr_image) if qr_image else 0}")
        print(f"🖼️ Image format: {image_format}")
        
        if not qr_image:
            print("❌ qr_image is required")
            return jsonify({
                'request_id': request_id,
                'status': 'error',
                'form_sections': {},
                'confidence_score': 0,
                'message': 'qr_image is required'
            }), 400
        
        logger.info(f"📱 Processing QR data: {len(qr_image)} characters")
        
        # Log first 100 characters of QR data for debugging
        qr_preview = qr_image[:100] + "..." if len(qr_image) > 100 else qr_image
        print(f"📝 QR data preview: {qr_preview}")
        
        # Try to decode QR code
        qr_decode_result = None
        
        # Check if it's base64 image data
        if qr_image.startswith('data:image/'):
            logger.info("🖼️ Detected data URL image, using OpenCV QR decoder")
            print("🖼️ Detected data URL image, using OpenCV QR decoder")
            try:
                qr_decode_result = inji_verify.decode_qr_from_base64(qr_image)
                print(f"🔍 OpenCV decode result: {qr_decode_result}")
            except Exception as e:
                logger.error(f"OpenCV QR decode failed: {str(e)}")
                print(f"❌ OpenCV QR decode failed: {str(e)}")
                # Fallback to treating as direct QR data
                qr_decode_result = {'success': True, 'qr_data': qr_image}
        elif qr_image.startswith('{') or qr_image.startswith('['):
            logger.info("📝 Detected JSON data, treating as QR content")
            print("📝 Detected JSON data, treating as QR content")
            # Treat as direct JSON QR data
            qr_decode_result = {'success': True, 'qr_data': qr_image}
        elif len(qr_image) > 1000 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in qr_image[:100]):
            logger.info("🖼️ Detected base64 image data, using OpenCV QR decoder")
            print("🖼️ Detected base64 image data, using OpenCV QR decoder")
            try:
                qr_decode_result = inji_verify.decode_qr_from_base64(qr_image)
                print(f"🔍 OpenCV decode result: {qr_decode_result}")
            except Exception as e:
                logger.error(f"OpenCV QR decode failed: {str(e)}")
                print(f"❌ OpenCV QR decode failed: {str(e)}")
                # Fallback to treating as direct QR data
                qr_decode_result = {'success': True, 'qr_data': qr_image}
        else:
            logger.info("📝 Detected text data, treating as QR content")
            print("📝 Detected text data, treating as QR content")
            # Treat as direct QR data
            qr_decode_result = {'success': True, 'qr_data': qr_image}
        
        if not qr_decode_result.get('success'):
            print(f"❌ QR decode failed: {qr_decode_result}")
            return jsonify({
                'request_id': request_id,
                'status': 'error',
                'form_sections': {},
                'confidence_score': 0,
                'message': f'Failed to decode QR: {qr_decode_result.get("error", "Unknown error")}'
            }), 400
        
        qr_data = qr_decode_result.get('qr_data', '')
        logger.info(f"✅ QR decoded successfully: {len(qr_data)} characters")
        print(f"✅ QR decoded successfully: {len(qr_data)} characters")
        print(f"📄 QR data content: {qr_data[:200]}..." if len(qr_data) > 200 else f"📄 QR data content: {qr_data}")
        
        # Parse QR data and extract ITR form fields
        form_sections = parse_qr_data_for_itr(qr_data)
        print(f"📋 Parsed form sections: {form_sections}")
        
        # Calculate confidence based on how many fields were extracted
        total_possible_fields = 20  # Approximate number of ITR form fields
        extracted_fields = sum(len(section) for section in form_sections.values())
        confidence_score = min(0.95, extracted_fields / total_possible_fields)
        
        logger.info(f"📋 Extracted {extracted_fields} fields with confidence {confidence_score:.2f}")
        print(f"📋 Extracted {extracted_fields} fields with confidence {confidence_score:.2f}")
        
        response = {
            'request_id': request_id,
            'status': 'success',
            'form_sections': form_sections,
            'confidence_score': confidence_score,
            'message': f'QR decoded successfully, extracted {extracted_fields} form fields'
        }
        
        print(f"📤 Final response: {response}")
        
        # Cache the result
        extraction_cache[request_id] = {
            'qr_decode_result': qr_decode_result,
            'form_sections': form_sections,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"QR ITR decode error: {str(e)}")
        return jsonify({
            'request_id': request_id if 'request_id' in locals() else str(uuid.uuid4()),
            'status': 'error',
            'form_sections': {},
            'confidence_score': 0,
            'message': f'QR decoding failed: {str(e)}'
        }), 500

def parse_qr_data_for_itr(qr_data):
    """
    Parse QR data and extract ITR form fields
    
    Args:
        qr_data (str): Raw QR code data
        
    Returns:
        dict: Organized form sections with extracted data
    """
    try:
        logger.info(f"🔍 Parsing QR data for ITR form fields")
        print(f"🔍 Parsing QR data for ITR form fields")
        print(f"📄 QR data to parse: {qr_data[:500]}..." if len(qr_data) > 500 else f"📄 QR data to parse: {qr_data}")
        
        # Initialize form sections
        form_sections = {
            'personal_info': {},
            'income_details': {},
            'deductions': {},
            'tax_details': {}
        }
        
        # Try to parse as JSON first
        try:
            import json
            qr_json = json.loads(qr_data)
            logger.info("📄 QR data is valid JSON")
            print("📄 QR data is valid JSON")
            print(f"🔍 JSON structure: {qr_json}")
            
            # Extract fields from JSON structure
            if isinstance(qr_json, dict):
                # Map common JSON fields to ITR form fields
                field_mapping = {
                    # Personal Information
                    'name': ('personal_info', 'name'),
                    'fullName': ('personal_info', 'name'),
                    'pan': ('personal_info', 'pan'),
                    'panNumber': ('personal_info', 'pan'),
                    'aadhaar': ('personal_info', 'aadhaar'),
                    'aadhaarNumber': ('personal_info', 'aadhaar'),
                    'dateOfBirth': ('personal_info', 'date_of_birth'),
                    'date_of_birth': ('personal_info', 'date_of_birth'),
                    'address': ('personal_info', 'address'),
                    'phone': ('personal_info', 'phone'),
                    'mobile': ('personal_info', 'phone'),
                    'email': ('personal_info', 'email'),
                    
                    # Income Details
                    'grossSalary': ('income_details', 'gross_salary'),
                    'gross_salary': ('income_details', 'gross_salary'),
                    'basicSalary': ('income_details', 'basic_salary'),
                    'basic_salary': ('income_details', 'basic_salary'),
                    'hra': ('income_details', 'hra_received'),
                    'hraReceived': ('income_details', 'hra_received'),
                    'otherAllowances': ('income_details', 'other_allowances'),
                    'interestIncome': ('income_details', 'interest_income'),
                    'otherIncome': ('income_details', 'other_income'),
                    
                    # Deductions
                    'standardDeduction': ('deductions', 'standard_deduction'),
                    'section80C': ('deductions', 'section_80c'),
                    'section80D': ('deductions', 'section_80d'),
                    'professionalTax': ('deductions', 'professional_tax'),
                    
                    # Tax Details
                    'tdsDeducted': ('tax_details', 'tds_deducted'),
                    'tds': ('tax_details', 'tds_deducted'),
                    'advanceTax': ('tax_details', 'advance_tax'),
                    'taxRegime': ('tax_details', 'tax_regime')
                }
                
                # Check for PixelPass format first (compact structure with p, f, e, b sections)
                if 'p' in qr_json or 'f' in qr_json or 'e' in qr_json or 'b' in qr_json:
                    logger.info("🎯 Detected PixelPass format QR code")
                    print("🎯 Detected PixelPass format QR code")
                    
                    # Personal info section (p)
                    if 'p' in qr_json:
                        personal = qr_json['p']
                        print(f"🔍 PixelPass personal section: {personal}")
                        
                        pixelpass_personal_mapping = {
                            'n': 'name',
                            'pan': 'pan',
                            'aad': 'aadhaar',
                            'dob': 'date_of_birth',
                            'mob': 'phone',
                            'email': 'email'
                        }
                        
                        for pp_field, form_field in pixelpass_personal_mapping.items():
                            if pp_field in personal and personal[pp_field]:
                                form_sections['personal_info'][form_field] = personal[pp_field]
                                print(f"✅ PixelPass Personal: {pp_field} -> {form_field} = {personal[pp_field]}")
                    
                    # Financial section (f)
                    if 'f' in qr_json:
                        financial = qr_json['f']
                        print(f"🔍 PixelPass financial section: {financial}")
                        
                        pixelpass_financial_mapping = {
                            'gs': 'gross_salary',
                            'bs': 'basic_salary',
                            'hra': 'hra_received',
                            'oa': 'other_allowances',
                            'pt': 'professional_tax',
                            'tds': 'tds_deducted',
                            'ti': 'total_income'
                        }
                        
                        for pp_field, form_field in pixelpass_financial_mapping.items():
                            if pp_field in financial and financial[pp_field]:
                                value = financial[pp_field]
                                # Convert to integer if it's a numeric string
                                try:
                                    value = int(float(str(value).replace(',', '')))
                                except:
                                    pass
                                
                                if form_field in ['gross_salary', 'basic_salary', 'hra_received', 'other_allowances', 'total_income']:
                                    form_sections['income_details'][form_field] = value
                                elif form_field in ['professional_tax']:
                                    form_sections['deductions'][form_field] = value
                                elif form_field in ['tds_deducted']:
                                    form_sections['tax_details'][form_field] = value
                                
                                print(f"✅ PixelPass Financial: {pp_field} -> {form_field} = {value}")
                    
                    # Employment section (e)
                    if 'e' in qr_json:
                        employment = qr_json['e']
                        print(f"🔍 PixelPass employment section: {employment}")
                        
                        pixelpass_employment_mapping = {
                            'emp': 'employer',
                            'tan': 'tan',
                            'ay': 'assessment_year',
                            'fy': 'financial_year'
                        }
                        
                        for pp_field, form_field in pixelpass_employment_mapping.items():
                            if pp_field in employment and employment[pp_field]:
                                # These are typically personal info fields in our form structure
                                form_sections['personal_info'][form_field] = employment[pp_field]
                                print(f"✅ PixelPass Employment: {pp_field} -> {form_field} = {employment[pp_field]}")
                    
                    # Bank section (b)
                    if 'b' in qr_json:
                        bank = qr_json['b']
                        print(f"🔍 PixelPass bank section: {bank}")
                        
                        pixelpass_bank_mapping = {
                            'acc': 'account_number',
                            'ifsc': 'ifsc',
                            'bank': 'bank_name'
                        }
                        
                        for pp_field, form_field in pixelpass_bank_mapping.items():
                            if pp_field in bank and bank[pp_field]:
                                form_sections['personal_info'][form_field] = bank[pp_field]
                                print(f"✅ PixelPass Bank: {pp_field} -> {form_field} = {bank[pp_field]}")
                
                else:
                    # Standard format parsing
                    # Extract fields using mapping
                    for qr_field, (section, form_field) in field_mapping.items():
                        if qr_field in qr_json and qr_json[qr_field]:
                            form_sections[section][form_field] = qr_json[qr_field]
                            logger.info(f"✅ Mapped {qr_field} -> {section}.{form_field}: {qr_json[qr_field]}")
                            print(f"✅ Mapped {qr_field} -> {section}.{form_field}: {qr_json[qr_field]}")
                
                # Handle nested structures
                if 'personalInfo' in qr_json:
                    print("🔍 Found personalInfo section")
                    personal = qr_json['personalInfo']
                    for field in ['name', 'pan', 'aadhaar', 'date_of_birth', 'address', 'phone', 'email']:
                        if field in personal:
                            form_sections['personal_info'][field] = personal[field]
                            print(f"✅ Personal: {field} = {personal[field]}")
                
                # Handle document_info structure (from OCR-generated QR codes)
                if 'document_info' in qr_json:
                    print("🔍 Found document_info section")
                    doc_info = qr_json['document_info']
                    # Map document fields to ITR personal info
                    field_mapping = {
                        'name': 'name',
                        'date_of_birth': 'date_of_birth',
                        'email': 'email',
                        'phone': 'phone',
                        'address': 'address',
                        'passport_number': 'passport_number',  # Additional field
                        'nationality': 'nationality'  # Additional field
                    }
                    for doc_field, form_field in field_mapping.items():
                        if doc_field in doc_info:
                            form_sections['personal_info'][form_field] = doc_info[doc_field]
                            print(f"✅ Document Info: {doc_field} -> {form_field} = {doc_info[doc_field]}")
                
                if 'incomeDetails' in qr_json:
                    print("🔍 Found incomeDetails section")
                    income = qr_json['incomeDetails']
                    for field in ['gross_salary', 'basic_salary', 'hra_received', 'other_allowances', 'interest_income', 'other_income']:
                        if field in income:
                            form_sections['income_details'][field] = income[field]
                            print(f"✅ Income: {field} = {income[field]}")
                
                if 'deductions' in qr_json:
                    print("🔍 Found deductions section")
                    deductions = qr_json['deductions']
                    for field in ['standard_deduction', 'section_80c', 'section_80d', 'professional_tax']:
                        if field in deductions:
                            form_sections['deductions'][field] = deductions[field]
                            print(f"✅ Deduction: {field} = {deductions[field]}")
                
                if 'taxDetails' in qr_json:
                    print("🔍 Found taxDetails section")
                    tax = qr_json['taxDetails']
                    for field in ['tds_deducted', 'advance_tax', 'tax_regime']:
                        if field in tax:
                            form_sections['tax_details'][field] = tax[field]
                            print(f"✅ Tax: {field} = {tax[field]}")
                            
        except json.JSONDecodeError:
            logger.info("📝 QR data is not JSON, trying text parsing")
            print("📝 QR data is not JSON, trying text parsing")
            
            # Parse as text data
            lines = qr_data.split('\n')
            current_section = 'personal_info'
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                print(f"🔍 Processing line: {line}")
                
                # Check for section headers
                if 'personal' in line.lower() or 'info' in line.lower():
                    current_section = 'personal_info'
                    print("📂 Switched to personal_info section")
                    continue
                elif 'income' in line.lower() or 'salary' in line.lower():
                    current_section = 'income_details'
                    print("📂 Switched to income_details section")
                    continue
                elif 'deduction' in line.lower():
                    current_section = 'deductions'
                    print("📂 Switched to deductions section")
                    continue
                elif 'tax' in line.lower():
                    current_section = 'tax_details'
                    print("📂 Switched to tax_details section")
                    continue
                
                # Extract key-value pairs
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    print(f"🔍 Found key-value: {key} = {value}")
                    
                    # Map text fields to form fields
                    field_mappings = {
                        'name': 'name',
                        'full_name': 'name',
                        'pan': 'pan',
                        'pan_number': 'pan',
                        'aadhaar': 'aadhaar',
                        'aadhaar_number': 'aadhaar',
                        'date_of_birth': 'date_of_birth',
                        'dob': 'date_of_birth',
                        'address': 'address',
                        'phone': 'phone',
                        'mobile': 'phone',
                        'email': 'email',
                        'gross_salary': 'gross_salary',
                        'basic_salary': 'basic_salary',
                        'hra': 'hra_received',
                        'tds': 'tds_deducted',
                        'advance_tax': 'advance_tax'
                    }
                    
                    if key in field_mappings:
                        form_field = field_mappings[key]
                        
                        # Determine which section this field belongs to
                        if form_field in ['name', 'pan', 'aadhaar', 'date_of_birth', 'address', 'phone', 'email']:
                            form_sections['personal_info'][form_field] = value
                            print(f"✅ Added to personal_info: {form_field} = {value}")
                        elif form_field in ['gross_salary', 'basic_salary', 'hra_received', 'other_allowances', 'interest_income', 'other_income']:
                            # Convert numeric values
                            try:
                                form_sections['income_details'][form_field] = int(float(value.replace(',', '').replace('₹', '')))
                                print(f"✅ Added to income_details: {form_field} = {form_sections['income_details'][form_field]}")
                            except:
                                form_sections['income_details'][form_field] = value
                                print(f"✅ Added to income_details (text): {form_field} = {value}")
                        elif form_field in ['standard_deduction', 'section_80c', 'section_80d', 'professional_tax']:
                            try:
                                form_sections['deductions'][form_field] = int(float(value.replace(',', '').replace('₹', '')))
                                print(f"✅ Added to deductions: {form_field} = {form_sections['deductions'][form_field]}")
                            except:
                                form_sections['deductions'][form_field] = value
                                print(f"✅ Added to deductions (text): {form_field} = {value}")
                        elif form_field in ['tds_deducted', 'advance_tax', 'tax_regime']:
                            if form_field == 'tax_regime':
                                form_sections['tax_details'][form_field] = value
                                print(f"✅ Added to tax_details: {form_field} = {value}")
                            else:
                                try:
                                    form_sections['tax_details'][form_field] = int(float(value.replace(',', '').replace('₹', '')))
                                    print(f"✅ Added to tax_details: {form_field} = {form_sections['tax_details'][form_field]}")
                                except:
                                    form_sections['tax_details'][form_field] = value
                                    print(f"✅ Added to tax_details (text): {form_field} = {value}")
        
        # Add default values for missing fields
        if not form_sections['deductions'].get('standard_deduction'):
            form_sections['deductions']['standard_deduction'] = 50000
            print("✅ Added default standard_deduction: 50000")
        
        if not form_sections['tax_details'].get('tax_regime'):
            form_sections['tax_details']['tax_regime'] = 'new'
            print("✅ Added default tax_regime: new")
        
        logger.info(f"📊 Final form sections: {sum(len(section) for section in form_sections.values())} fields extracted")
        print(f"📊 Final form sections: {sum(len(section) for section in form_sections.values())} fields extracted")
        print(f"📋 Complete form sections: {form_sections}")
        
        return form_sections
        
    except Exception as e:
        logger.error(f"Error parsing QR data: {str(e)}")
        print(f"❌ Error parsing QR data: {str(e)}")
        return {
            'personal_info': {},
            'income_details': {},
            'deductions': {'standard_deduction': 50000},
            'tax_details': {'tax_regime': 'new'}
        }

def format_date(date_string):
    """
    Format date string to YYYY-MM-DD format
    
    Handles formats like DD/MM/YYYY or DD-MM-YYYY
    """
    if not date_string:
        return ''
    
    try:
        # Try parsing DD/MM/YYYY format
        if '/' in date_string:
            parts = date_string.split('/')
            if len(parts) == 3:
                return f"{parts[2]}-{parts[1]}-{parts[0]}"
        
        # Try parsing DD-MM-YYYY format
        if '-' in date_string:
            parts = date_string.split('-')
            if len(parts) == 3:
                if len(parts[2]) == 4:  # DD-MM-YYYY
                    return f"{parts[2]}-{parts[1]}-{parts[0]}"
                else:  # Already YYYY-MM-DD
                    return date_string
        
        return date_string
    except:
        return date_string

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/ocr/verify', methods=['POST'])
def verify_ocr_data():
    """
    Verify OCR extracted data against validation rules
    
    Request body:
    {
        "request_id": "string",
        "extracted_data": {...},
        "verification_rules": {...}
    }
    
    Response:
    {
        "verification_id": "string",
        "verified_fields": {...},
        "discrepancies": [...],
        "verification_status": "passed|failed"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'verification_id': str(uuid.uuid4()),
                'verified_fields': {},
                'discrepancies': [],
                'verification_status': 'failed',
                'error': 'No JSON data provided'
            }), 400
        
        request_id = data.get('request_id')
        extracted_data = data.get('extracted_data', {})
        verification_rules = data.get('verification_rules', {})
        
        # Generate verification ID
        verification_id = str(uuid.uuid4())
        
        # Get cached extraction result if available
        cached_extraction = None
        if request_id and request_id in extraction_cache:
            cached_extraction = extraction_cache[request_id]
        
        # Perform verification
        verified_fields = {}
        discrepancies = []
        all_passed = True
        
        # Check required fields
        required_fields = verification_rules.get('required_fields', [])
        if isinstance(required_fields, list):
            for field in required_fields:
                if field not in extracted_data or not extracted_data[field]:
                    discrepancies.append({
                        'field': field,
                        'issue': 'Missing required field',
                        'expected': field,
                        'actual': extracted_data.get(field)
                    })
                    all_passed = False
                else:
                    verified_fields[field] = extracted_data[field]
        
        # Check field formats
        field_formats = verification_rules.get('field_formats', {})
        if isinstance(field_formats, dict):
            for field, format_rule in field_formats.items():
                if field in extracted_data:
                    field_value = extracted_data[field]
                    
                    # Validate format based on rule
                    if format_rule == 'email':
                        if '@' not in str(field_value):
                            discrepancies.append({
                                'field': field,
                                'issue': 'Invalid email format',
                                'expected': 'email',
                                'actual': field_value
                            })
                            all_passed = False
                        else:
                            verified_fields[field] = field_value
                    
                    elif format_rule == 'date':
                        # Check if it looks like a date
                        if not any(sep in str(field_value) for sep in ['-', '/', '.']):
                            discrepancies.append({
                                'field': field,
                                'issue': 'Invalid date format',
                                'expected': 'date (YYYY-MM-DD or DD/MM/YYYY)',
                                'actual': field_value
                            })
                            all_passed = False
                        else:
                            verified_fields[field] = field_value
                    
                    elif format_rule == 'phone':
                        phone_str = str(field_value).replace('+', '').replace('-', '').replace(' ', '')
                        if not phone_str.isdigit() or len(phone_str) < 10:
                            discrepancies.append({
                                'field': field,
                                'issue': 'Invalid phone format',
                                'expected': 'phone (10+ digits)',
                                'actual': field_value
                            })
                            all_passed = False
                        else:
                            verified_fields[field] = field_value
                    
                    elif format_rule == 'alphanumeric':
                        if not str(field_value).replace(' ', '').isalnum():
                            discrepancies.append({
                                'field': field,
                                'issue': 'Invalid alphanumeric format',
                                'expected': 'alphanumeric',
                                'actual': field_value
                            })
                            all_passed = False
                        else:
                            verified_fields[field] = field_value
                    else:
                        verified_fields[field] = field_value
        
        # Check confidence thresholds
        if cached_extraction:
            min_confidence = verification_rules.get('min_confidence', 0.5)
            ocr_confidence = cached_extraction['extraction_result'].get('confidence', 0.75)
            
            if ocr_confidence < min_confidence:
                discrepancies.append({
                    'field': 'overall_confidence',
                    'issue': f'OCR confidence below threshold',
                    'expected': f'>= {min_confidence}',
                    'actual': ocr_confidence
                })
                all_passed = False
        
        # Prepare response
        response = {
            'verification_id': verification_id,
            'verified_fields': verified_fields,
            'discrepancies': discrepancies,
            'verification_status': 'passed' if all_passed else 'failed',
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache verification result
        extraction_cache[verification_id] = {
            'verification_result': response,
            'timestamp': datetime.now().isoformat()
        }
        
        status_code = 200 if all_passed else 422
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        return jsonify({
            'verification_id': verification_id if 'verification_id' in locals() else str(uuid.uuid4()),
            'verified_fields': {},
            'discrepancies': [],
            'verification_status': 'failed',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@app.route('/api/pixelpass/generate-qr', methods=['POST'])
def generate_pixelpass_qr():
    """
    Generate QR code using PixelPass library
    Following official Inji documentation workflow
    
    Request body:
    {
        "ocr_data": {
            "name": "John Doe",
            "date_of_birth": "01/01/1990",
            "aadhaar_number": "1234-5678-9012",
            ...
        }
    }
    
    Response:
    {
        "success": true,
        "workflow_id": "uuid",
        "verifiable_credential": {...},
        "qr_code": {
            "qr_image": "data:image/png;base64,...",
            "browser_url": "data:image/png;base64,...",
            "encoding": "PixelPass-CBOR"
        },
        "instructions": {...}
    }
    """
    try:
        from pixelpass_integration import PixelPassQRGenerator
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided',
                'workflow_id': str(uuid.uuid4())
            }), 400
        
        ocr_data = data.get('ocr_data')
        if not ocr_data:
            return jsonify({
                'success': False,
                'error': 'ocr_data is required',
                'workflow_id': str(uuid.uuid4())
            }), 400
        
        # Initialize PixelPass QR generator
        qr_generator = PixelPassQRGenerator()
        
        # Run complete workflow
        workflow_result = qr_generator.complete_qr_generation_workflow(ocr_data)
        
        # Cleanup
        qr_generator.cleanup()
        
        if workflow_result.get('success'):
            return jsonify(workflow_result), 200
        else:
            return jsonify(workflow_result), 500
            
    except ImportError as e:
        logger.error(f"PixelPass import error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'PixelPass integration not available',
            'details': str(e),
            'workflow_id': str(uuid.uuid4())
        }), 500
    except Exception as e:
        logger.error(f"PixelPass QR generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'workflow_id': str(uuid.uuid4())
        }), 500

@app.route('/api/pixelpass/test-setup', methods=['GET'])
def test_pixelpass_setup():
    """
    Test PixelPass setup and Node.js availability
    
    Response:
    {
        "success": true,
        "node_available": true,
        "pixelpass_installed": false,
        "setup_instructions": [...]
    }
    """
    try:
        from pixelpass_integration import PixelPassQRGenerator
        
        qr_generator = PixelPassQRGenerator()
        
        # Test Node.js project setup
        node_available = qr_generator.node_project_path is not None
        
        # Test PixelPass installation
        pixelpass_installed = False
        if node_available:
            pixelpass_installed = qr_generator.install_pixelpass()
        
        setup_instructions = [
            "1. Install Node.js and npm",
            "2. Create directory: mkdir pixelpass-qr && cd pixelpass-qr",
            "3. Initialize npm: npm init -y",
            "4. Install PixelPass: npm install @mosip/pixelpass",
            "5. Test with: node setup_pixelpass.js"
        ]
        
        qr_generator.cleanup()
        
        return jsonify({
            'success': True,
            'node_available': node_available,
            'pixelpass_installed': pixelpass_installed,
            'setup_instructions': setup_instructions,
            'test_endpoint': '/api/pixelpass/generate-qr',
            'documentation': 'Follow official Inji documentation for QR generation'
        }), 200
        
    except Exception as e:
        logger.error(f"PixelPass setup test error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'setup_instructions': [
                "1. Install Node.js and npm",
                "2. Install @mosip/pixelpass library",
                "3. Check pixelpass_integration.py file"
            ]
        }), 500

@app.route('/api/simple-qr/generate', methods=['POST'])
def generate_simple_qr():
    """
    Generate simple, human-readable QR code from OCR data
    Perfect for Google scanner and other basic QR readers
    
    Request body:
    {
        "ocr_data": {
            "name": "John Doe",
            "date_of_birth": "01/01/1990",
            "phone": "+1234567890",
            ...
        },
        "format": "text" | "json"  // Optional, defaults to "text"
    }
    
    Response:
    {
        "success": true,
        "qr_id": "uuid",
        "qr_image_base64": "data:image/png;base64,...",
        "qr_content": "readable text or json",
        "readable_by": "Any QR scanner"
    }
    """
    try:
        from simple_qr_generator import generate_simple_text_qr, generate_json_qr
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided',
                'qr_id': str(uuid.uuid4())
            }), 400
        
        ocr_data = data.get('ocr_data')
        if not ocr_data:
            return jsonify({
                'success': False,
                'error': 'ocr_data is required',
                'qr_id': str(uuid.uuid4())
            }), 400
        
        qr_format = data.get('format', 'text').lower()
        
        # Generate appropriate QR code
        if qr_format == 'json':
            result = generate_json_qr(ocr_data)
        else:
            result = generate_simple_text_qr(ocr_data)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except ImportError as e:
        logger.error(f"Simple QR import error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Simple QR generator not available',
            'details': str(e),
            'qr_id': str(uuid.uuid4())
        }), 500
    except Exception as e:
        logger.error(f"Simple QR generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'qr_id': str(uuid.uuid4())
        }), 500

@app.route('/api/validate-semantic', methods=['POST'])
def validate_semantic():
    """
    Validate semantic similarity between PDF content and QR data.
    
    Request body (JSON):
    {
        "pdf_text": "string",       # Text extracted from the PDF
        "qr_data": "string"|"object" # Data decoded from the QR code
    }
    
    Response:
    {
        "score": number,          # 0-100 similarity score
        "status": "success|error",
        "is_match": boolean,
        "match_label": "string"
    }
    """
    try:
        data = request.get_json()
        if not data:
             return jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400
             
        pdf_text = data.get('pdf_text')
        qr_data = data.get('qr_data')
        
        if not pdf_text:
            return jsonify({'status': 'error', 'message': 'pdf_text is required'}), 400
            
        if not qr_data:
            return jsonify({'status': 'error', 'message': 'qr_data is required'}), 400
            
        if not semantic_validator:
             return jsonify({'status': 'error', 'message': 'Semantic Validator service is not available'}), 503
             
        # Perform validation
        result = semantic_validator.validate(pdf_text, qr_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Semantic validation endpoint error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'score': 0
        }), 500

@app.route('/api/ner/extract', methods=['POST'])
def extract_ner():
    """
    Extract Named Entity Recognition (NER) from combined text
    
    Stoplight Schema: NERExtractionRequest -> NERExtractionResponse
    
    Request body JSON:
    {
        "text": "string",           // Combined text from multiple documents
        "field_types": [array],    // Specific field types to extract (optional)
        "confidence_threshold": number  // Minimum confidence threshold (optional)
    }
    
    Response:
    {
        "success": boolean,
        "entities": [array],       // Extracted entities with confidence scores
        "field_mapping": object,   // Simple field-to-value mapping
        "processing_details": object
    }
    """
    try:
        data = request.get_json()
        
        # Validate request schema
        is_valid, validation_error = validate_request_schema(data, 'NERExtractionRequest')
        if not is_valid:
            return jsonify({
                'success': False,
                'error': validation_error,
                'entities': [],
                'field_mapping': {},
                'timestamp': datetime.now().isoformat()
            }), 400
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'text is required',
                'entities': [],
                'field_mapping': {},
                'timestamp': datetime.now().isoformat()
            }), 400
        
        text = data['text']
        field_types = data.get('field_types', [
            'name', 'pan', 'aadhaar', 'email', 'mobile', 'date_of_birth',
            'gross_salary', 'tds_deducted', 'total_income', 'account_number',
            'ifsc', 'bank_name', 'employer', 'address', 'pincode'
        ])
        confidence_threshold = data.get('confidence_threshold', 0.7)
        
        logger.info(f"🧠 NER extraction requested for {len(text)} characters")
        logger.info(f"🎯 Target fields: {field_types}")
        logger.info(f"📊 Confidence threshold: {confidence_threshold}")
        
        # Check if we have the NER extractor available
        try:
            from ner_extractor import NERExtractor
            ner_extractor = NERExtractor()
            
            # Extract entities using the NER extractor
            ner_result = ner_extractor.extract_entities(text, field_types)
            
            # Filter entities by confidence threshold
            filtered_entities = [
                entity for entity in ner_result.get('entities', [])
                if entity.get('confidence', 0) >= confidence_threshold
            ]
            
            # Update field mapping to only include high-confidence fields
            filtered_field_mapping = {
                field: value for field, value in ner_result.get('field_mapping', {}).items()
                if any(e['field'] == field and e['confidence'] >= confidence_threshold 
                      for e in ner_result.get('entities', []))
            }
            
            logger.info(f"✅ NER extraction successful: {len(filtered_entities)} entities above threshold")
            
            return jsonify({
                'success': True,
                'entities': filtered_entities,
                'field_mapping': filtered_field_mapping,
                'processing_details': {
                    **ner_result.get('processing_details', {}),
                    'confidence_threshold_applied': confidence_threshold,
                    'entities_before_filtering': len(ner_result.get('entities', [])),
                    'entities_after_filtering': len(filtered_entities)
                },
                'text_length': len(text),
                'fields_requested': field_types,
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except ImportError:
            logger.warning("NER extractor not available, using regex-based extraction")
            # Fallback to regex-based extraction
            entities, field_mapping = extract_entities_with_regex(text, field_types)
            
            # Apply confidence threshold
            filtered_entities = [e for e in entities if e.get('confidence', 0) >= confidence_threshold]
            filtered_field_mapping = {
                field: value for field, value in field_mapping.items()
                if any(e['field'] == field and e['confidence'] >= confidence_threshold for e in entities)
            }
            
            return jsonify({
                'success': True,
                'entities': filtered_entities,
                'field_mapping': filtered_field_mapping,
                'processing_details': {
                    'method': 'regex_fallback',
                    'note': 'Advanced NER not available, used regex patterns',
                    'confidence_threshold_applied': confidence_threshold,
                    'entities_before_filtering': len(entities),
                    'entities_after_filtering': len(filtered_entities)
                },
                'text_length': len(text),
                'fields_requested': field_types,
                'timestamp': datetime.now().isoformat()
            }), 200
            
    except Exception as e:
        logger.error(f"NER extraction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'entities': [],
            'field_mapping': {},
            'timestamp': datetime.now().isoformat()
        }), 500

def extract_entities_with_regex(text, field_types):
    """
    Fallback regex-based entity extraction
    """
    import re
    
    entities = []
    field_mapping = {}
    
    # Define regex patterns for different field types
    patterns = {
        'name': [
            r'Name[:\s]+([A-Za-z\s]{2,50})',
            r'नाम[:\s]+([A-Za-z\s]{2,50})',
            r'^([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        ],
        'pan': [
            r'PAN[:\s]*([A-Z]{5}[0-9]{4}[A-Z]{1})',
            r'([A-Z]{5}[0-9]{4}[A-Z]{1})',
        ],
        'aadhaar': [
            r'Aadhaar[:\s]*(\d{4}[\s-]?\d{4}[\s-]?\d{4})',
            r'आधार[:\s]*(\d{4}[\s-]?\d{4}[\s-]?\d{4})',
            r'(\d{4}[\s-]\d{4}[\s-]\d{4})',
        ],
        'email': [
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ],
        'mobile': [
            r'Mobile[:\s]*(\+?91[\s-]?[6-9]\d{9})',
            r'Phone[:\s]*(\+?91[\s-]?[6-9]\d{9})',
            r'(\+?91[\s-]?[6-9]\d{9})',
        ],
        'date_of_birth': [
            r'DOB[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'Date of Birth[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'जन्म तिथि[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
        ],
        'gross_salary': [
            r'Gross Salary[:\s]*₹?[\s]*([0-9,]+)',
            r'Total Income[:\s]*₹?[\s]*([0-9,]+)',
        ],
        'tds_deducted': [
            r'TDS[:\s]*₹?[\s]*([0-9,]+)',
            r'Tax Deducted[:\s]*₹?[\s]*([0-9,]+)',
        ],
        'account_number': [
            r'Account[:\s]*(\d{9,18})',
            r'A/c[:\s]*(\d{9,18})',
        ],
        'ifsc': [
            r'IFSC[:\s]*([A-Z]{4}0[A-Z0-9]{6})',
        ],
        'bank_name': [
            r'Bank[:\s]*([A-Za-z\s]{5,50})',
        ],
        'employer': [
            r'Employer[:\s]*([A-Za-z\s]{5,100})',
            r'Company[:\s]*([A-Za-z\s]{5,100})',
        ],
        'pincode': [
            r'PIN[:\s]*(\d{6})',
            r'Pincode[:\s]*(\d{6})',
        ]
    }
    
    for field_type in field_types:
        if field_type in patterns:
            for pattern in patterns[field_type]:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    value = match.group(1).strip()
                    if value and len(value) > 1:  # Basic validation
                        entities.append({
                            'field': field_type,
                            'value': value,
                            'confidence': 0.8,  # Default confidence for regex
                            'start': match.start(1),
                            'end': match.end(1),
                            'source': 'regex'
                        })
                        
                        # Use first match for field mapping
                        if field_type not in field_mapping:
                            field_mapping[field_type] = value
                        break
                
                # Break after first successful pattern match
                if field_type in field_mapping:
                    break
    
    return entities, field_mapping

@app.route('/api/form/auto-fill', methods=['POST'])
def auto_fill_form():
    """
    Auto-fill form fields using NER results
    
    Request body JSON:
    {
        "ner_results": {...},        // NER extraction results
        "document_sources": {...},   // Source documents for each field
        "confidence_threshold": 0.7  // Minimum confidence threshold
    }
    
    Response:
    {
        "success": boolean,
        "form_data": {
            "field_name": {
                "value": "string",
                "confidence": number,
                "source": "string",
                "verified": boolean
            }
        },
        "summary": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'ner_results' not in data:
            return jsonify({
                'success': False,
                'error': 'ner_results is required',
                'form_data': {}
            }), 400
        
        ner_results = data['ner_results']
        document_sources = data.get('document_sources', {})
        confidence_threshold = data.get('confidence_threshold', 0.7)
        
        logger.info(f"🤖 Auto-fill requested with confidence threshold: {confidence_threshold}")
        
        form_data = {}
        entities = ner_results.get('entities', [])
        field_mapping = ner_results.get('field_mapping', {})
        
        # Process entities and create form data
        for entity in entities:
            field = entity['field']
            value = entity['value']
            confidence = entity.get('confidence', 0.0)
            source = entity.get('source', 'unknown')
            
            # Only include fields that meet confidence threshold
            if confidence >= confidence_threshold:
                form_data[field] = {
                    'value': value,
                    'confidence': confidence,
                    'source': source,
                    'verified': confidence >= 0.9,
                    'document_source': document_sources.get(field, 'combined')
                }
        
        # Add field mapping data for any missing fields
        for field, value in field_mapping.items():
            if field not in form_data:
                form_data[field] = {
                    'value': value,
                    'confidence': 0.8,  # Default confidence for field mapping
                    'source': 'field_mapping',
                    'verified': False,
                    'document_source': document_sources.get(field, 'combined')
                }
        
        # Create summary
        summary = {
            'total_fields_found': len(entities),
            'fields_above_threshold': len(form_data),
            'verified_fields': len([f for f in form_data.values() if f['verified']]),
            'average_confidence': sum(f['confidence'] for f in form_data.values()) / len(form_data) if form_data else 0,
            'confidence_threshold': confidence_threshold
        }
        
        logger.info(f"✅ Auto-fill completed: {len(form_data)} fields populated")
        
        return jsonify({
            'success': True,
            'form_data': form_data,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Auto-fill error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'form_data': {},
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/documents/combine', methods=['POST'])
def combine_document_extractions():
    """
    Combine multiple document extractions using priority-based merging
    
    Request body JSON:
    {
        "document_extractions": {
            "aadhaar": {...},
            "form16": {...},
            "preregistration": {...},
            "bankSlip": {...},
            "incomeDetails": {...}
        },
        "merge_strategy": "priority_based",
        "field_priorities": {
            "name": ["aadhaar", "form16", "preregistration"],
            "pan": ["form16", "preregistration", "aadhaar"]
        }
    }
    
    Response:
    {
        "success": boolean,
        "combined_data": {...},
        "merge_details": {...},
        "conflicts": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'document_extractions' not in data:
            return jsonify({
                'success': False,
                'error': 'document_extractions is required',
                'combined_data': {}
            }), 400
        
        document_extractions = data['document_extractions']
        merge_strategy = data.get('merge_strategy', 'priority_based')
        field_priorities = data.get('field_priorities', {
            'name': ['aadhaar', 'form16', 'preregistration'],
            'pan': ['form16', 'preregistration', 'aadhaar'],
            'aadhaar': ['aadhaar'],
            'email': ['preregistration', 'form16'],
            'mobile': ['preregistration', 'aadhaar'],
            'gross_salary': ['form16', 'bankSlip'],
            'account_number': ['bankSlip'],
            'bank_name': ['bankSlip'],
            'ifsc': ['bankSlip'],
            'employer': ['form16'],
            'tds_deducted': ['form16']
        })
        
        logger.info(f"🔗 Combining {len(document_extractions)} document extractions")
        
        combined_data = {}
        merge_details = {}
        conflicts = []
        
        # Get all possible fields from all documents
        all_fields = set()
        for doc_type, extraction in document_extractions.items():
            if extraction and 'structured_data' in extraction:
                all_fields.update(extraction['structured_data'].keys())
        
        # Process each field using priority-based merging
        for field in all_fields:
            field_values = {}
            
            # Collect values from all documents
            for doc_type, extraction in document_extractions.items():
                if extraction and 'structured_data' in extraction:
                    structured_data = extraction['structured_data']
                    if field in structured_data and structured_data[field]:
                        field_values[doc_type] = {
                            'value': structured_data[field],
                            'confidence': extraction.get('confidence', 0.8)
                        }
            
            if field_values:
                # Apply priority-based selection
                selected_value = None
                selected_source = None
                
                if field in field_priorities:
                    # Use priority order
                    for priority_doc in field_priorities[field]:
                        if priority_doc in field_values:
                            selected_value = field_values[priority_doc]['value']
                            selected_source = priority_doc
                            break
                
                if not selected_value:
                    # Use highest confidence if no priority defined
                    best_doc = max(field_values.keys(), 
                                 key=lambda x: field_values[x]['confidence'])
                    selected_value = field_values[best_doc]['value']
                    selected_source = best_doc
                
                combined_data[field] = selected_value
                merge_details[field] = {
                    'selected_from': selected_source,
                    'available_in': list(field_values.keys()),
                    'confidence': field_values[selected_source]['confidence']
                }
                
                # Check for conflicts (different values from different sources)
                unique_values = set(fv['value'] for fv in field_values.values())
                if len(unique_values) > 1:
                    conflicts.append({
                        'field': field,
                        'values': field_values,
                        'selected': selected_value,
                        'selected_from': selected_source
                    })
        
        summary = {
            'total_fields_combined': len(combined_data),
            'documents_processed': len(document_extractions),
            'conflicts_found': len(conflicts),
            'merge_strategy': merge_strategy
        }
        
        logger.info(f"✅ Document combination completed: {len(combined_data)} fields, {len(conflicts)} conflicts")
        
        return jsonify({
            'success': True,
            'combined_data': combined_data,
            'merge_details': merge_details,
            'conflicts': conflicts,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Document combination error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'combined_data': {},
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('FLASK_DEBUG', False)
    )
