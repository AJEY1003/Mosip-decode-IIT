#!/usr/bin/env python3
"""
Enhanced OCR Processor - Integration of Multiple OCR Engines
Combines PaddleOCR, EasyOCR, TrOCR, and Tesseract for maximum accuracy
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import OCR engines
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logging.warning("EasyOCR not available")

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    logging.warning("PaddleOCR not available")

try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    import torch
    TROCR_AVAILABLE = True
except ImportError:
    TROCR_AVAILABLE = False
    logging.warning("TrOCR not available")

# PDF processing
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    try:
        import pdf2image
        from pdf2image import convert_from_path
        PDF_AVAILABLE = True
        PDF_METHOD = 'pdf2image'
    except ImportError:
        PDF_AVAILABLE = False
        logging.warning("PDF processing not available - install PyMuPDF or pdf2image")

# Import original OCR processor
try:
    from ocr_processor import OCRProcessor
    ORIGINAL_OCR_AVAILABLE = True
except ImportError:
    ORIGINAL_OCR_AVAILABLE = False
    logging.warning("Original OCR processor not available")

logger = logging.getLogger(__name__)

class EnhancedOCRProcessor:
    """
    Enhanced OCR Processor that combines multiple OCR engines for maximum accuracy
    Uses PaddleOCR, EasyOCR, TrOCR, and Tesseract
    """
    
    def __init__(self, languages=['en', 'hi']):
        """
        Initialize Enhanced OCR Processor
        
        Args:
            languages: List of languages to support (default: ['en', 'hi'])
        """
        self.languages = languages
        self.engines = {}
        
        # Initialize Tesseract
        self.engines['tesseract'] = self._init_tesseract()
        
        # Initialize EasyOCR
        if EASYOCR_AVAILABLE:
            try:
                self.engines['easyocr'] = easyocr.Reader(languages)
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.warning(f"EasyOCR initialization failed: {str(e)}")
                self.engines['easyocr'] = None
        
        # Initialize PaddleOCR
        if PADDLEOCR_AVAILABLE:
            try:
                # Initialize for English and Hindi
                self.engines['paddleocr'] = PaddleOCR(
                    use_angle_cls=True, 
                    lang='en',  # Primary language
                    use_gpu=torch.cuda.is_available() if 'torch' in globals() else False,
                    show_log=False
                )
                logger.info("PaddleOCR initialized successfully")
            except Exception as e:
                logger.warning(f"PaddleOCR initialization failed: {str(e)}")
                self.engines['paddleocr'] = None
        
        # Initialize TrOCR
        if TROCR_AVAILABLE:
            try:
                self.engines['trocr_processor'] = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
                self.engines['trocr_model'] = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')
                logger.info("TrOCR initialized successfully")
            except Exception as e:
                logger.warning(f"TrOCR initialization failed: {str(e)}")
                self.engines['trocr_processor'] = None
                self.engines['trocr_model'] = None
        
        # Initialize original OCR processor as fallback
        if ORIGINAL_OCR_AVAILABLE:
            try:
                self.original_ocr = OCRProcessor(engine='easyocr', language='en')
                logger.info("Original OCR processor initialized as fallback")
            except Exception as e:
                logger.warning(f"Original OCR processor initialization failed: {str(e)}")
                self.original_ocr = None
        
        # Log available engines
        available_engines = [name for name, engine in self.engines.items() if engine is not None]
        logger.info(f"Enhanced OCR Processor initialized with engines: {available_engines}")
    
    def _init_tesseract(self):
        """Initialize Tesseract OCR"""
        try:
            # Set Tesseract path for Windows
            tesseract_paths = [
                r'D:\Tesseract\tesseract.exe',
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', 'User'))
            ]
            
            for path in tesseract_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Tesseract found at: {path}")
                    break
            
            # Test Tesseract
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
            return True
            
        except Exception as e:
            logger.warning(f"Tesseract initialization failed: {str(e)}")
            return None
    
    def process_document(self, image_path: str, document_type: str = 'Unknown') -> Dict[str, Any]:
        """
        Process document using multiple OCR engines with intelligent fallback
        
        Args:
            image_path: Path to the image file
            document_type: Type of document being processed
            
        Returns:
            dict: Comprehensive OCR results with structured data
        """
        processing_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        logger.info(f"Processing document {processing_id}: {image_path}")
        
        results = {
            'processing_id': processing_id,
            'document_type': document_type,
            'image_path': image_path,
            'timestamp': start_time.isoformat(),
            'engines_used': [],
            'raw_results': {},
            'merged_result': {},
            'structured_data': {},
            'confidence_scores': {},
            'processing_time': 0,
            'success': False
        }
        
        try:
            # Load and preprocess image
            image = self._load_and_preprocess_image(image_path)
            
            # Method 1: PaddleOCR
            if self.engines.get('paddleocr'):
                paddleocr_result = self._process_with_paddleocr(image, image_path)
                results['raw_results']['paddleocr'] = paddleocr_result
                if paddleocr_result.get('success'):
                    results['engines_used'].append('paddleocr')
            
            # Method 2: EasyOCR
            if self.engines.get('easyocr'):
                easyocr_result = self._process_with_easyocr(image, image_path)
                results['raw_results']['easyocr'] = easyocr_result
                if easyocr_result.get('success'):
                    results['engines_used'].append('easyocr')
            
            # Method 3: TrOCR
            if self.engines.get('trocr_processor') and self.engines.get('trocr_model'):
                trocr_result = self._process_with_trocr(image, image_path)
                results['raw_results']['trocr'] = trocr_result
                if trocr_result.get('success'):
                    results['engines_used'].append('trocr')
            
            # Method 4: Tesseract
            if self.engines.get('tesseract'):
                tesseract_result = self._process_with_tesseract(image, image_path)
                results['raw_results']['tesseract'] = tesseract_result
                if tesseract_result.get('success'):
                    results['engines_used'].append('tesseract')
            
            # Method 5: Fallback to original OCR
            if not results['engines_used'] and self.original_ocr:
                fallback_result = self._process_with_fallback(image_path)
                results['raw_results']['fallback'] = fallback_result
                if fallback_result.get('success'):
                    results['engines_used'].append('fallback')
            
            # Method 6: Merge and validate results
            merged_result = self._merge_ocr_results(results['raw_results'])
            results['merged_result'] = merged_result
            
            # Method 7: Extract structured data using NER
            from .ner_extractor import ITRNERExtractor
            ner_extractor = ITRNERExtractor()
            ner_result = ner_extractor.extract_structured_data(
                merged_result.get('text', ''), 
                document_type
            )
            results['structured_data'] = ner_result['extracted_fields']
            results['ner_confidence_scores'] = ner_result['confidence_scores']
            results['ner_overall_confidence'] = ner_result['overall_confidence']
            results['ner_metadata'] = ner_result['metadata']
            
            # Method 8: Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(results['raw_results'])
            results['confidence_scores'] = confidence_scores
            
            # Final processing
            processing_time = (datetime.now() - start_time).total_seconds()
            results['processing_time'] = processing_time
            results['success'] = bool(merged_result.get('text', '').strip())
            
            # DETAILED LOGGING FOR DEBUGGING
            logger.info(f"🔍 OCR PROCESSING COMPLETE - {processing_id}")
            logger.info(f"📄 Document: {image_path} ({document_type})")
            logger.info(f"⏱️  Processing Time: {processing_time:.2f}s")
            logger.info(f"🔧 Engines Used: {results['engines_used']}")
            logger.info(f"📊 Overall Confidence: {confidence_scores.get('overall_confidence', 0.0):.3f}")
            
            # Log individual engine results
            for engine, result in results['raw_results'].items():
                if result.get('success'):
                    text_preview = result.get('text', '')[:100] + '...' if len(result.get('text', '')) > 100 else result.get('text', '')
                    logger.info(f"✅ {engine.upper()}: {result.get('confidence', 0):.3f} confidence - '{text_preview}'")
                else:
                    logger.warning(f"❌ {engine.upper()}: Failed - {result.get('error', 'Unknown error')}")
            
            # Log final merged result
            final_text = merged_result.get('text', '')
            if final_text:
                text_preview = final_text[:200] + '...' if len(final_text) > 200 else final_text
                logger.info(f"🎯 FINAL RESULT ({merged_result.get('selected_engine', 'unknown')}): '{text_preview}'")
                logger.info(f"📝 Full Text Length: {len(final_text)} characters")
                
                # Add page information if available
                if image and isinstance(image, dict):
                    pages_processed = image.get('pages_processed')
                    total_pages = image.get('total_pages')
                    if pages_processed and total_pages:
                        logger.info(f"📄 PDF Pages Processed: {pages_processed}/{total_pages}")
            else:
                logger.warning(f"⚠️  NO TEXT EXTRACTED from any engine!")
            
            logger.info(f"🏁 Processing completed: {processing_id} ({'SUCCESS' if results['success'] else 'FAILED'})")
            logger.info("=" * 80)
            
            logger.info(f"Document processing completed: {processing_id} ({processing_time:.2f}s)")
            logger.info(f"Engines used: {results['engines_used']}")
            logger.info(f"Overall confidence: {confidence_scores.get('overall_confidence', 0.0):.2f}")
            
            return self._format_final_result(results)
            
        except Exception as e:
            logger.error(f"Document processing failed: {processing_id} - {str(e)}")
            results['error'] = str(e)
            results['processing_time'] = (datetime.now() - start_time).total_seconds()
            return self._format_final_result(results)
    
    def _load_and_preprocess_image(self, image_path: str) -> np.ndarray:
        """Load and preprocess image for OCR"""
        try:
            # Check if it's a PDF file
            if image_path.lower().endswith('.pdf'):
                return self._process_pdf_file(image_path)
            
            # Load regular image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert to RGB for some engines
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Basic preprocessing
            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            return {
                'original': image,
                'rgb': image_rgb,
                'gray': gray,
                'processed': thresh
            }
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            # Return None if preprocessing fails
            return None
    
    def _process_pdf_file(self, pdf_path: str, max_pages: int = 10) -> Dict[str, np.ndarray]:
        """Process PDF file and convert all pages to images, then combine them"""
        try:
            if not PDF_AVAILABLE:
                raise ValueError("PDF processing not available. Install PyMuPDF: pip install PyMuPDF")
            
            logger.info(f"Processing PDF file: {pdf_path}")
            
            # Try PyMuPDF first
            try:
                import fitz
                doc = fitz.open(pdf_path)
                
                total_pages = len(doc)
                pages_to_process = min(total_pages, max_pages)
                
                logger.info(f"PDF has {total_pages} pages, processing first {pages_to_process} pages")
                
                # Process multiple pages and combine them
                combined_images = []
                
                for page_num in range(pages_to_process):
                    logger.info(f"Processing PDF page {page_num + 1}/{pages_to_process}")
                    
                    page = doc[page_num]
                    
                    # Convert to image
                    mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("ppm")
                    
                    # Convert to PIL Image
                    pil_image = Image.open(io.BytesIO(img_data))
                    
                    # Convert to numpy array
                    image_rgb = np.array(pil_image)
                    combined_images.append(image_rgb)
                
                doc.close()
                
                # Combine all pages vertically
                if len(combined_images) == 1:
                    final_image_rgb = combined_images[0]
                else:
                    # Add spacing between pages
                    spacing_height = 50
                    spacing = np.ones((spacing_height, combined_images[0].shape[1], 3), dtype=np.uint8) * 255
                    
                    # Combine images with spacing
                    images_with_spacing = []
                    for i, img in enumerate(combined_images):
                        images_with_spacing.append(img)
                        if i < len(combined_images) - 1:  # Don't add spacing after last image
                            images_with_spacing.append(spacing)
                    
                    final_image_rgb = np.vstack(images_with_spacing)
                
                logger.info(f"Combined {pages_to_process} pages into single image: {final_image_rgb.shape}")
                
            except ImportError:
                # Fallback to pdf2image
                from pdf2image import convert_from_path
                
                # Get total pages first
                pages = convert_from_path(pdf_path, dpi=200)
                total_pages = len(pages)
                pages_to_process = min(total_pages, max_pages)
                
                logger.info(f"PDF has {total_pages} pages, processing first {pages_to_process} pages")
                
                if not pages:
                    raise ValueError("Could not convert PDF to image")
                
                # Convert pages to numpy arrays
                combined_images = []
                for page_num in range(pages_to_process):
                    logger.info(f"Processing PDF page {page_num + 1}/{pages_to_process}")
                    
                    pil_image = pages[page_num]
                    image_rgb = np.array(pil_image)
                    combined_images.append(image_rgb)
                
                # Combine all pages vertically
                if len(combined_images) == 1:
                    final_image_rgb = combined_images[0]
                else:
                    # Add spacing between pages
                    spacing_height = 50
                    spacing = np.ones((spacing_height, combined_images[0].shape[1], 3), dtype=np.uint8) * 255
                    
                    # Combine images with spacing
                    images_with_spacing = []
                    for i, img in enumerate(combined_images):
                        images_with_spacing.append(img)
                        if i < len(combined_images) - 1:
                            images_with_spacing.append(spacing)
                    
                    final_image_rgb = np.vstack(images_with_spacing)
                
                logger.info(f"Combined {pages_to_process} pages into single image: {final_image_rgb.shape}")
            
            # Convert final combined image to BGR for OpenCV
            final_image_bgr = cv2.cvtColor(final_image_rgb, cv2.COLOR_RGB2BGR)
            
            # Apply preprocessing to the combined image
            gray = cv2.cvtColor(final_image_bgr, cv2.COLOR_BGR2GRAY)
            denoised = cv2.fastNlMeansDenoising(gray)
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            logger.info(f"Successfully processed multi-page PDF: {final_image_rgb.shape}")
            
            return {
                'original': final_image_bgr,
                'rgb': final_image_rgb,
                'gray': gray,
                'processed': thresh,
                'pages_processed': pages_to_process,
                'total_pages': total_pages if 'total_pages' in locals() else pages_to_process
            }
            
        except Exception as e:
            logger.error(f"Multi-page PDF processing failed: {str(e)}")
            return None
    
    def _process_with_paddleocr(self, image: Dict[str, np.ndarray], image_path: str) -> Dict[str, Any]:
        """Process with PaddleOCR"""
        try:
            ocr_engine = self.engines['paddleocr']
            
            if image is None:
                return {'text': '', 'confidence': 0.0, 'success': False, 'error': 'No valid image data'}
            
            # Use processed image for better results
            img_to_use = image.get('processed', image.get('original'))
            if img_to_use is None:
                return {'text': '', 'confidence': 0.0, 'success': False, 'error': 'No valid image array'}
            
            # Run PaddleOCR
            result = ocr_engine.ocr(img_to_use, cls=True)
            
            if not result or not result[0]:
                return {'text': '', 'confidence': 0.0, 'success': False, 'error': 'No text detected'}
            
            # Extract text and confidence
            texts = []
            confidences = []
            
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0] if isinstance(line[1], (list, tuple)) else str(line[1])
                    confidence = line[1][1] if isinstance(line[1], (list, tuple)) and len(line[1]) > 1 else 0.8
                    
                    texts.append(text)
                    confidences.append(confidence)
            
            combined_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                'text': combined_text,
                'confidence': avg_confidence,
                'success': True,
                'engine': 'paddleocr',
                'details': {
                    'lines_detected': len(texts),
                    'individual_confidences': confidences
                }
            }
            
        except Exception as e:
            logger.error(f"PaddleOCR processing failed: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'success': False,
                'error': str(e),
                'engine': 'paddleocr'
            }
    
    def _process_with_easyocr(self, image: Dict[str, np.ndarray], image_path: str) -> Dict[str, Any]:
        """Process with EasyOCR"""
        try:
            ocr_engine = self.engines['easyocr']
            
            if image is None:
                return {'text': '', 'confidence': 0.0, 'success': False, 'error': 'No valid image data'}
            
            # Use RGB image for EasyOCR
            img_to_use = image.get('rgb', image.get('original'))
            if img_to_use is None:
                return {'text': '', 'confidence': 0.0, 'success': False, 'error': 'No valid image array'}
            
            # Run EasyOCR
            result = ocr_engine.readtext(img_to_use)
            
            if not result:
                return {'text': '', 'confidence': 0.0, 'success': False, 'error': 'No text detected'}
            
            # Extract text and confidence
            texts = []
            confidences = []
            
            for detection in result:
                if len(detection) >= 3:
                    text = detection[1]
                    confidence = detection[2]
                    
                    texts.append(text)
                    confidences.append(confidence)
            
            combined_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                'text': combined_text,
                'confidence': avg_confidence,
                'success': True,
                'engine': 'easyocr',
                'details': {
                    'detections': len(texts),
                    'individual_confidences': confidences
                }
            }
            
        except Exception as e:
            logger.error(f"EasyOCR processing failed: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'success': False,
                'error': str(e),
                'engine': 'easyocr'
            }
    
    def _process_with_trocr(self, image: Dict[str, np.ndarray], image_path: str) -> Dict[str, Any]:
        """Process with TrOCR (Transformer-based OCR)"""
        try:
            processor = self.engines['trocr_processor']
            model = self.engines['trocr_model']
            
            if image is None:
                return {'text': '', 'confidence': 0.0, 'success': False, 'error': 'No valid image data'}
            
            # Convert to PIL Image
            img_array = image.get('rgb', image.get('original'))
            if img_array is None:
                return {'text': '', 'confidence': 0.0, 'success': False, 'error': 'No valid image array'}
            
            pil_image = Image.fromarray(img_array)
            
            # Process with TrOCR
            pixel_values = processor(images=pil_image, return_tensors="pt").pixel_values
            generated_ids = model.generate(pixel_values)
            generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # TrOCR doesn't provide confidence scores directly, so we estimate based on text quality
            confidence = self._estimate_trocr_confidence(generated_text)
            
            return {
                'text': generated_text,
                'confidence': confidence,
                'success': True,
                'engine': 'trocr',
                'details': {
                    'model': 'microsoft/trocr-base-printed',
                    'estimated_confidence': True
                }
            }
            
        except Exception as e:
            logger.error(f"TrOCR processing failed: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'success': False,
                'error': str(e),
                'engine': 'trocr'
            }
    
    def _process_with_tesseract(self, image: Dict[str, np.ndarray], image_path: str) -> Dict[str, Any]:
        """Process with Tesseract OCR"""
        try:
            if image is None:
                return {'text': '', 'confidence': 0.0, 'success': False, 'error': 'No valid image data'}
            
            # Use processed image for better results
            img_to_use = image.get('processed', image.get('gray', image.get('original')))
            if img_to_use is None:
                return {'text': '', 'confidence': 0.0, 'success': False, 'error': 'No valid image array'}
            
            # Configure Tesseract
            config = '--oem 3 --psm 6'  # Use LSTM OCR Engine Mode with uniform text block
            
            # Extract text
            text = pytesseract.image_to_string(img_to_use, config=config, lang='eng+hin')
            
            # Get confidence data
            try:
                data = pytesseract.image_to_data(img_to_use, config=config, lang='eng+hin', output_type=pytesseract.Output.DICT)
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
            except:
                avg_confidence = 0.7  # Default confidence if data extraction fails
            
            return {
                'text': text.strip(),
                'confidence': avg_confidence,
                'success': bool(text.strip()),
                'engine': 'tesseract',
                'details': {
                    'config': config,
                    'languages': 'eng+hin'
                }
            }
            
        except Exception as e:
            logger.error(f"Tesseract processing failed: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'success': False,
                'error': str(e),
                'engine': 'tesseract'
            }
    
    def _process_with_fallback(self, image_path: str) -> Dict[str, Any]:
        """Process with fallback original OCR processor"""
        try:
            result = self.original_ocr.process_document(image_path)
            return {
                'text': result.get('raw_text', ''),
                'confidence': result.get('confidence', 0.0),
                'success': True,
                'engine': 'fallback_original',
                'structured_data': result.get('structured_data', {})
            }
        except Exception as e:
            logger.error(f"Fallback OCR processing failed: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'success': False,
                'error': str(e),
                'engine': 'fallback_original'
            }
    
    def _estimate_trocr_confidence(self, text: str) -> float:
        """Estimate confidence for TrOCR based on text characteristics"""
        if not text or not text.strip():
            return 0.0
        
        # Simple heuristics for confidence estimation
        confidence = 0.7  # Base confidence
        
        # Boost confidence for longer text
        if len(text) > 50:
            confidence += 0.1
        
        # Boost confidence for text with proper capitalization
        if any(c.isupper() for c in text) and any(c.islower() for c in text):
            confidence += 0.1
        
        # Reduce confidence for text with many special characters
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        if special_char_ratio > 0.3:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _process_with_enhanced_engines(self, image_path: str) -> Dict[str, Any]:
        """Process with enhanced OCR engines (PaddleOCR + EasyOCR + TrOCR + Tesseract)"""
        try:
            # This method is now handled by the main process_document method
            # Keeping for compatibility
            return {
                'text': 'Enhanced processing handled by main method',
                'confidence': 0.0,
                'engines_used': [],
                'success': False,
                'note': 'Use process_document method directly'
            }
        except Exception as e:
            logger.error(f"Enhanced OCR processing failed: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'engines_used': [],
                'success': False,
                'error': str(e)
            }
    
    def _process_with_easyocr_legacy(self, image_path: str) -> Dict[str, Any]:
        """Legacy EasyOCR processing method for compatibility"""
        try:
            if self.original_ocr:
                result = self.original_ocr.process_document(image_path)
                return {
                    'text': result.get('raw_text', ''),
                    'confidence': result.get('confidence', 0.0),
                    'structured_data': result.get('structured_data', {}),
                    'success': True
                }
            else:
                return {
                    'text': '',
                    'confidence': 0.0,
                    'success': False,
                    'error': 'Original OCR processor not available'
                }
        except Exception as e:
            logger.error(f"Legacy EasyOCR processing failed: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'success': False,
                'error': str(e)
            }
    
    def _merge_ocr_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge results from multiple OCR engines using confidence-based selection and voting
        """
        valid_results = []
        
        # Collect valid results
        for engine_name, result in raw_results.items():
            if result.get('success') and result.get('text', '').strip():
                valid_results.append({
                    'engine': engine_name,
                    'text': result['text'].strip(),
                    'confidence': result.get('confidence', 0.0),
                    'length': len(result['text'].strip()),
                    'word_count': len(result['text'].strip().split())
                })
        
        if not valid_results:
            return {'text': '', 'confidence': 0.0, 'selected_engine': 'none'}
        
        # Sort by confidence and text quality
        valid_results.sort(key=lambda x: (x['confidence'], x['word_count'], x['length']), reverse=True)
        
        # Use the best result as primary
        best_result = valid_results[0]
        
        # For improved accuracy, we could implement text comparison and voting
        # For now, we'll use confidence-weighted selection with fallback
        
        # If multiple results have similar confidence, prefer longer text
        similar_confidence_results = [
            r for r in valid_results 
            if abs(r['confidence'] - best_result['confidence']) < 0.1
        ]
        
        if len(similar_confidence_results) > 1:
            # Choose the one with most words
            best_result = max(similar_confidence_results, key=lambda x: x['word_count'])
        
        return {
            'text': best_result['text'],
            'confidence': best_result['confidence'],
            'selected_engine': best_result['engine'],
            'all_candidates': valid_results,
            'selection_reason': 'confidence_and_quality_based'
        }
    
    def _extract_structured_data(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Extract structured data using enhanced field extraction
        """
        structured_data = {}
        
        try:
            # Use basic extraction as primary method
            basic_fields = self._extract_basic_fields(text, document_type)
            structured_data.update(basic_fields)
            
            # Add document type
            structured_data['document_type'] = document_type
            
            # Add text analysis
            structured_data['text_analysis'] = {
                'total_characters': len(text),
                'total_words': len(text.split()),
                'has_numbers': bool(re.search(r'\d', text)),
                'has_uppercase': bool(re.search(r'[A-Z]', text)),
                'has_lowercase': bool(re.search(r'[a-z]', text)),
                'language_detected': self._detect_language(text)
            }
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Structured data extraction failed: {str(e)}")
            return {'document_type': document_type, 'extraction_error': str(e)}
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection based on character patterns"""
        if not text:
            return 'unknown'
        
        # Count different script characters
        latin_chars = sum(1 for c in text if c.isalpha() and ord(c) < 256)
        devanagari_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        
        total_alpha = sum(1 for c in text if c.isalpha())
        
        if total_alpha == 0:
            return 'unknown'
        
        devanagari_ratio = devanagari_chars / total_alpha
        
        if devanagari_ratio > 0.3:
            return 'hindi'
        elif latin_chars / total_alpha > 0.7:
            return 'english'
        else:
            return 'mixed'
    
    def _extract_basic_fields(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Basic field extraction using regex patterns (fallback method)
        """
        fields = {}
        
        # Extract name
        name_patterns = [
            r'(?:name|full name)[:\s]+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['name'] = match.group(1).strip().title()
                break
        
        # Extract date of birth
        dob_patterns = [
            r'(?:date of birth|dob|birth)[:\s]+(\d{2}[\/\-]\d{2}[\/\-]\d{4})',
            r'(\d{2}[\/\-]\d{2}[\/\-]\d{4})'
        ]
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['date_of_birth'] = match.group(1)
                break
        
        # Extract ID numbers
        id_patterns = {
            'pan_number': r'[A-Z]{5}[0-9]{4}[A-Z]',
            'aadhaar_number': r'\d{4}\s?\d{4}\s?\d{4}',
            'passport_number': r'[A-Z]{1}[0-9]{7}'
        }
        
        for field_name, pattern in id_patterns.items():
            match = re.search(pattern, text)
            if match:
                fields[field_name] = match.group(0)
        
        return fields
    
    def _calculate_confidence_scores(self, raw_results: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate comprehensive confidence scores
        """
        scores = {}
        
        # Individual engine confidences
        for engine_name, result in raw_results.items():
            if result.get('success'):
                scores[f'{engine_name}_confidence'] = result.get('confidence', 0.0)
        
        # Overall confidence (weighted average)
        valid_confidences = [
            result.get('confidence', 0.0) 
            for result in raw_results.values() 
            if result.get('success')
        ]
        
        if valid_confidences:
            scores['overall_confidence'] = sum(valid_confidences) / len(valid_confidences)
            scores['max_confidence'] = max(valid_confidences)
            scores['min_confidence'] = min(valid_confidences)
        else:
            scores['overall_confidence'] = 0.0
            scores['max_confidence'] = 0.0
            scores['min_confidence'] = 0.0
        
        return scores
    
    def _format_final_result(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format final result in the expected format for compatibility
        """
        return {
            'raw_text': results['merged_result'].get('text', ''),
            'structured_data': results.get('structured_data', {}),
            'confidence': results['confidence_scores'].get('overall_confidence', 0.0),
            'processing_time': results.get('processing_time', 0.0),
            'engines_used': results.get('engines_used', []),
            'processing_details': {
                'processing_id': results.get('processing_id'),
                'timestamp': results.get('timestamp'),
                'selected_engine': results['merged_result'].get('selected_engine'),
                'confidence_breakdown': results.get('confidence_scores', {}),
                'raw_results_summary': {
                    engine: {
                        'success': result.get('success', False),
                        'confidence': result.get('confidence', 0.0),
                        'text_length': len(result.get('text', ''))
                    }
                    for engine, result in results.get('raw_results', {}).items()
                }
            },
            'success': results.get('success', False),
            'error': results.get('error')
        }
    
    def get_engine_status(self) -> Dict[str, Any]:
        """
        Get status of all available OCR engines
        """
        status = {
            'enhanced_ocr_available': True,
            'engines': {}
        }
        
        # Check Tesseract
        if self.engines.get('tesseract'):
            status['engines']['tesseract'] = {
                'available': True,
                'type': 'offline',
                'description': 'Tesseract - Traditional OCR engine with Hindi support'
            }
        else:
            status['engines']['tesseract'] = {
                'available': False,
                'type': 'offline',
                'description': 'Tesseract - Not available'
            }
        
        # Check EasyOCR
        if self.engines.get('easyocr'):
            status['engines']['easyocr'] = {
                'available': True,
                'type': 'offline',
                'description': 'EasyOCR - Deep learning based OCR'
            }
        else:
            status['engines']['easyocr'] = {
                'available': False,
                'type': 'offline',
                'description': 'EasyOCR - Not available'
            }
        
        # Check PaddleOCR
        if self.engines.get('paddleocr'):
            status['engines']['paddleocr'] = {
                'available': True,
                'type': 'offline',
                'description': 'PaddleOCR - High-performance OCR with multilingual support'
            }
        else:
            status['engines']['paddleocr'] = {
                'available': False,
                'type': 'offline',
                'description': 'PaddleOCR - Not available (install: pip install paddlepaddle paddleocr)'
            }
        
        # Check TrOCR
        if self.engines.get('trocr_processor') and self.engines.get('trocr_model'):
            status['engines']['trocr'] = {
                'available': True,
                'type': 'offline',
                'description': 'TrOCR - Transformer-based OCR for high accuracy'
            }
        else:
            status['engines']['trocr'] = {
                'available': False,
                'type': 'offline',
                'description': 'TrOCR - Not available (install: pip install transformers torch)'
            }
        
        # Check fallback
        if self.original_ocr:
            status['engines']['fallback'] = {
                'available': True,
                'type': 'offline',
                'description': 'Original OCR processor - Fallback option'
            }
        
        # Count available engines
        available_count = sum(1 for engine in status['engines'].values() if engine['available'])
        status['summary'] = {
            'total_engines': len(status['engines']),
            'available_engines': available_count,
            'offline_engines': available_count,  # All our engines are offline now
            'cloud_engines': 0  # No cloud engines
        }
        
        return status

# Example usage and testing
if __name__ == "__main__":
    # Test the enhanced OCR processor
    processor = EnhancedOCRProcessor()
    
    print("🔍 Enhanced OCR Processor Status:")
    status = processor.get_engine_status()
    print(f"Enhanced OCR Available: {status.get('enhanced_ocr_available', False)}")
    print(f"Summary: {status['summary']['available_engines']}/{status['summary']['total_engines']} engines available")
    print("\nAvailable Engines:")
    for engine, info in status['engines'].items():
        availability = "✅" if info['available'] else "❌"
        print(f"  {availability} {engine}: {info['description']}")
    
    print(f"\n🎯 OCR Engine Combination:")
    print(f"  • PaddleOCR → High-performance multilingual OCR")
    print(f"  • EasyOCR → Deep learning based recognition") 
    print(f"  • TrOCR → Transformer-based accuracy")
    print(f"  • Tesseract → Traditional OCR with Hindi support")
    print(f"  • Intelligent merging → Best result selection")
    
    # Test with a sample image (if available)
    # result = processor.process_document("sample_document.jpg", "Passport")
    # print(f"Processing Result: {result}")
    
    print(f"\n📋 Installation Commands (if engines missing):")
    print(f"  pip install paddlepaddle paddleocr")
    print(f"  pip install easyocr")
    print(f"  pip install transformers torch")
    print(f"  # Tesseract: Download from https://github.com/tesseract-ocr/tesseract")