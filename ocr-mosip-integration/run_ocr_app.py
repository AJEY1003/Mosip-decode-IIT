#!/usr/bin/env python3
"""
OCR-enabled launcher for the MOSIP ITR Assistant backend
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    from werkzeug.utils import secure_filename
    import logging
    import base64
    import uuid
    from datetime import datetime
    
    # Import OCR processors
    from core.ocr_processor import OCRProcessor
    
    # Import ITR analyzer and QR generator
    from core.itr_analyzer import ITRAnalyzer
    from core.qr_generator import ITRQRGenerator
    
    app = Flask(__name__)
    CORS(app)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize processors
    ocr_processor = OCRProcessor(engine='easyocr', language='en')
    itr_analyzer = ITRAnalyzer()
    qr_generator = ITRQRGenerator()
    
    # Configure upload folder
    UPLOAD_FOLDER = 'uploads'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'message': 'MOSIP ITR Assistant Backend with OCR is running'}
    
    @app.route('/')
    def home():
        return {
            'message': 'MOSIP ITR Assistant Backend API with OCR',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'ocr_extract': '/ocr/extract',
                'enhanced_ocr': '/api/enhanced-ocr/extract',
                'itr_analyze': '/api/itr/analyze',
                'itr_process_documents': '/api/itr/process-documents',
                'itr_calculate_refund': '/api/itr/calculate-refund',
                'generate_qr': '/api/documents/generate-qr',
                'decode_qr': '/api/qr/decode'
            }
        }
    
    @app.route('/ocr/extract', methods=['POST'])
    def extract_text():
        """
        Extract text from uploaded document using OCR
        """
        try:
            file_path = None
            filename = None
            request_id = str(uuid.uuid4())
            
            # Handle both FormData and JSON requests
            if request.content_type and 'multipart/form-data' in request.content_type:
                # FormData upload
                if 'file' not in request.files:
                    return jsonify({'error': 'No file uploaded'}), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{request_id}_{filename}")
                file.save(file_path)
                
            else:
                # JSON with base64 data
                data = request.get_json()
                if not data or 'image_data' not in data:
                    return jsonify({'error': 'No image data provided'}), 400
                
                image_data = data['image_data']
                if image_data.startswith('data:'):
                    # Remove data URL prefix
                    image_data = image_data.split(',')[1]
                
                # Decode base64 and save as file
                import base64
                image_bytes = base64.b64decode(image_data)
                filename = f"document_{request_id}.jpg"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)
            
            logger.info(f"Processing file: {filename} with request ID: {request_id}")
            
            # Process with OCR
            extracted_data = ocr_processor.extract_text(file_path)
            
            # Clean up uploaded file
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            
            result = {
                'request_id': request_id,
                'filename': filename,
                'extracted_text': extracted_data.get('raw_text', ''),
                'structured_data': extracted_data.get('structured_data', {}),
                'confidence': extracted_data.get('confidence', 0.0),
                'details': extracted_data.get('details', []),
                'timestamp': datetime.now().isoformat(),
                'engine': 'easyocr',
                'status': 'success'
            }
            
            logger.info(f"OCR extraction completed for request: {request_id}")
            return jsonify(result), 200
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            # Clean up file on error
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            
            return jsonify({
                'error': 'OCR extraction failed',
                'message': str(e),
                'status': 'error'
            }), 500
    
    @app.route('/api/enhanced-ocr/extract', methods=['POST'])
    def enhanced_extract_text():
        """
        Enhanced OCR extraction with preprocessing
        """
        try:
            file_path = None
            filename = None
            request_id = str(uuid.uuid4())
            
            # Handle both FormData and JSON requests
            if request.content_type and 'multipart/form-data' in request.content_type:
                # FormData upload
                if 'file' not in request.files:
                    return jsonify({'error': 'No file uploaded'}), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{request_id}_{filename}")
                file.save(file_path)
                
            else:
                # JSON with base64 data
                data = request.get_json()
                if not data or 'image_data' not in data:
                    return jsonify({'error': 'No image data provided'}), 400
                
                image_data = data['image_data']
                if image_data.startswith('data:'):
                    # Remove data URL prefix
                    image_data = image_data.split(',')[1]
                
                # Decode base64 and save as file
                import base64
                image_bytes = base64.b64decode(image_data)
                filename = f"enhanced_document_{request_id}.jpg"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)
            
            logger.info(f"Enhanced OCR processing file: {filename} with request ID: {request_id}")
            
            # Preprocess image
            processed_image = ocr_processor.preprocess_image(file_path)
            
            # Extract text with enhanced processing
            extracted_data = ocr_processor.process_document(file_path)
            confidence_score = ocr_processor.get_confidence_score(file_path)
            
            # Clean up uploaded file
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            
            result = {
                'request_id': request_id,
                'filename': filename,
                'extracted_text': extracted_data.get('raw_text', ''),
                'structured_data': extracted_data.get('structured_data', {}),
                'confidence_score': confidence_score,
                'details': extracted_data.get('details', []),
                'timestamp': datetime.now().isoformat(),
                'engine': 'easyocr_enhanced',
                'preprocessing': 'applied',
                'status': 'success'
            }
            
            logger.info(f"Enhanced OCR extraction completed for request: {request_id}")
            return jsonify(result), 200
            
        except Exception as e:
            logger.error(f"Enhanced OCR extraction failed: {str(e)}")
            # Clean up file on error
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            
            return jsonify({
                'error': 'Enhanced OCR extraction failed',
                'message': str(e),
                'status': 'error'
            }), 500
    
    @app.route('/api/enhanced-ocr/status', methods=['GET'])
    def get_enhanced_ocr_status():
        """
        Get Enhanced OCR engine status
        """
        try:
            return jsonify({
                'status': 'active',
                'engine': 'easyocr',
                'version': '1.7.2',
                'language_support': ['en'],
                'preprocessing': 'enabled',
                'confidence_scoring': 'enabled',
                'timestamp': datetime.now().isoformat()
            }), 200
        except Exception as e:
            return jsonify({
                'error': 'Status check failed',
                'message': str(e)
            }), 500
    
    @app.route('/api/test-extraction', methods=['POST'])
    def test_field_extraction():
        """
        Test field extraction with raw text (for debugging)
        """
        try:
            data = request.get_json()
            if not data or 'raw_text' not in data:
                return jsonify({'error': 'No raw text provided'}), 400
            
            raw_text = data['raw_text']
            document_type = data.get('document_type', 'Test Document')
            
            # Extract structured fields
            structured_data = ocr_processor.extract_id_fields(raw_text)
            
            result = {
                'document_type': document_type,
                'raw_text': raw_text,
                'structured_data': structured_data,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            return jsonify(result), 200
            
        except Exception as e:
            logger.error(f"Test extraction failed: {str(e)}")
            return jsonify({
                'error': 'Test extraction failed',
                'message': str(e),
                'status': 'error'
            }), 500
    
    @app.route('/api/itr/analyze', methods=['POST'])
    def analyze_itr_documents():
        """
        Comprehensive ITR analysis with multiple documents
        """
        try:
            data = request.get_json()
            if not data or 'documents' not in data:
                return jsonify({'error': 'No documents provided'}), 400
            
            documents = data['documents']
            logger.info(f"Starting ITR analysis with {len(documents)} documents")
            
            # Perform comprehensive analysis
            analysis_result = itr_analyzer.analyze_documents(documents)
            
            result = {
                'analysis_id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                **analysis_result
            }
            
            logger.info(f"ITR analysis completed successfully")
            return jsonify(result), 200
            
        except Exception as e:
            logger.error(f"ITR analysis failed: {str(e)}")
            return jsonify({
                'error': 'ITR analysis failed',
                'message': str(e),
                'status': 'error'
            }), 500
    
    @app.route('/api/itr/process-documents', methods=['POST'])
    def process_multiple_documents():
        """
        Process multiple documents for ITR filing
        """
        try:
            if 'files' not in request.files:
                return jsonify({'error': 'No files uploaded'}), 400
            
            files = request.files.getlist('files')
            document_types = request.form.getlist('document_types')
            
            if len(files) != len(document_types):
                return jsonify({'error': 'Mismatch between files and document types'}), 400
            
            processed_documents = {}
            request_id = str(uuid.uuid4())
            
            for i, (file, doc_type) in enumerate(zip(files, document_types)):
                if file.filename == '':
                    continue
                
                # Save and process each file
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{request_id}_{i}_{filename}")
                file.save(file_path)
                
                logger.info(f"Processing {doc_type}: {filename}")
                
                # Extract data using OCR
                extracted_data = ocr_processor.process_document(file_path)
                
                processed_documents[doc_type] = {
                    'filename': filename,
                    'extracted_text': extracted_data.get('raw_text', ''),
                    'structured_data': extracted_data.get('structured_data', {}),
                    'confidence': extracted_data.get('confidence', 0.0),
                    'details': extracted_data.get('details', [])
                }
                
                # Clean up file
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Perform ITR analysis
            analysis_result = itr_analyzer.analyze_documents(processed_documents)
            
            result = {
                'request_id': request_id,
                'processed_documents': processed_documents,
                'itr_analysis': analysis_result,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            logger.info(f"Multi-document ITR processing completed for request: {request_id}")
            return jsonify(result), 200
            
        except Exception as e:
            logger.error(f"Multi-document processing failed: {str(e)}")
            return jsonify({
                'error': 'Multi-document processing failed',
                'message': str(e),
                'status': 'error'
            }), 500
    
    @app.route('/api/itr/calculate-refund', methods=['POST'])
    def calculate_tax_refund():
        """
        Calculate potential tax refund based on provided data
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Extract income and deduction details
            income_details = data.get('income_details', {})
            deductions = data.get('deductions', {})
            
            # Calculate taxes
            tax_calculations = itr_analyzer._calculate_taxes(income_details, deductions)
            refund_analysis = itr_analyzer._analyze_refund(tax_calculations, income_details)
            
            result = {
                'tax_calculations': tax_calculations,
                'refund_analysis': refund_analysis,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            return jsonify(result), 200
            
        except Exception as e:
            logger.error(f"Refund calculation failed: {str(e)}")
            return jsonify({
                'error': 'Refund calculation failed',
                'message': str(e),
                'status': 'error'
            }), 500
    
    @app.route('/api/documents/generate-qr', methods=['POST'])
    def generate_documents_qr():
        """
        Generate QR code from processed documents containing ITR data
        """
        try:
            data = request.get_json()
            if not data or 'documents' not in data:
                return jsonify({'error': 'No documents provided'}), 400
            
            documents = data['documents']
            logger.info(f"Generating QR code from {len(documents)} documents")
            
            # Perform ITR analysis first
            analysis_result = itr_analyzer.analyze_documents(documents)
            
            # Generate QR code with ITR data
            qr_result = qr_generator.generate_itr_qr(
                analysis_result, 
                analysis_result.get('document_summary', {})
            )
            
            if qr_result.get('status') == 'error':
                return jsonify(qr_result), 500
            
            result = {
                'qr_code': qr_result,
                'analysis_summary': {
                    'total_income': analysis_result.get('tax_calculations', {}).get('gross_income', 0),
                    'recommended_regime': analysis_result.get('tax_calculations', {}).get('recommended_regime', 'new'),
                    'refund_amount': analysis_result.get('refund_analysis', {}).get('refund_amount', 0),
                    'tax_payable': analysis_result.get('refund_analysis', {}).get('additional_tax_due', 0),
                    'taxpayer_name': analysis_result.get('personal_info', {}).get('name', 'N/A')
                },
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            logger.info(f"QR code generated successfully: {qr_result.get('qr_id')}")
            return jsonify(result), 200
            
        except Exception as e:
            logger.error(f"QR generation failed: {str(e)}")
            return jsonify({
                'error': 'QR generation failed',
                'message': str(e),
                'status': 'error'
            }), 500
    
    @app.route('/api/qr/decode', methods=['POST'])
    def decode_qr_data():
        """
        Decode QR code data to extract ITR form information
        """
        try:
            data = request.get_json()
            if not data or 'qr_data' not in data:
                return jsonify({'error': 'No QR data provided'}), 400
            
            qr_data = data['qr_data']
            logger.info("Decoding QR data for ITR form")
            
            # Decode QR data
            decode_result = qr_generator.decode_qr_data(qr_data)
            
            if decode_result.get('status') == 'error':
                return jsonify(decode_result), 400
            
            # Format for ITR form
            itr_form_data = decode_result['itr_data']
            metadata = decode_result['metadata']
            
            result = {
                'itr_form_data': itr_form_data,
                'metadata': metadata,
                'form_sections': {
                    'personal_info': {
                        'name': itr_form_data.get('name', ''),
                        'pan': itr_form_data.get('pan', ''),
                        'aadhaar': itr_form_data.get('aadhaar', ''),
                        'date_of_birth': itr_form_data.get('date_of_birth', ''),
                        'address': itr_form_data.get('address', ''),
                        'phone': itr_form_data.get('phone', ''),
                        'email': itr_form_data.get('email', '')
                    },
                    'income_details': {
                        'gross_salary': itr_form_data.get('gross_salary', 0),
                        'basic_salary': itr_form_data.get('basic_salary', 0),
                        'hra_received': itr_form_data.get('hra_received', 0),
                        'other_allowances': itr_form_data.get('other_allowances', 0),
                        'interest_income': itr_form_data.get('interest_income', 0),
                        'other_income': itr_form_data.get('other_income', 0)
                    },
                    'deductions': {
                        'standard_deduction': itr_form_data.get('standard_deduction', 50000),
                        'section_80c': itr_form_data.get('section_80c', 0),
                        'section_80d': itr_form_data.get('section_80d', 0),
                        'professional_tax': itr_form_data.get('professional_tax', 0)
                    },
                    'tax_details': {
                        'tds_deducted': itr_form_data.get('tds_deducted', 0),
                        'advance_tax': itr_form_data.get('advance_tax', 0),
                        'self_assessment_tax': itr_form_data.get('self_assessment_tax', 0),
                        'tax_regime': itr_form_data.get('tax_regime', 'new')
                    },
                    'computed_values': {
                        'total_income': itr_form_data.get('total_income', 0),
                        'taxable_income': itr_form_data.get('taxable_income', 0),
                        'tax_liability': itr_form_data.get('tax_liability', 0),
                        'refund_amount': itr_form_data.get('refund_amount', 0),
                        'tax_payable': itr_form_data.get('tax_payable', 0)
                    }
                },
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            logger.info("QR data decoded successfully for ITR form")
            return jsonify(result), 200
            
        except Exception as e:
            logger.error(f"QR decode failed: {str(e)}")
            return jsonify({
                'error': 'QR decode failed',
                'message': str(e),
                'status': 'error'
            }), 500
    
    if __name__ == '__main__':
        print("Starting MOSIP ITR Assistant Backend with OCR...")
        print("Backend will be available at: http://localhost:5000")
        print("OCR endpoints:")
        print("  - POST /ocr/extract")
        print("  - POST /api/enhanced-ocr/extract")
        app.run(host='0.0.0.0', port=5000, debug=True)
        
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Please install required packages:")
    print("pip install flask flask-cors easyocr pillow opencv-python")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)