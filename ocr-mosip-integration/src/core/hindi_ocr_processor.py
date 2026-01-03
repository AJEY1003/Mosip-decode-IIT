#!/usr/bin/env python3
"""
Hindi OCR Processor - Based on your Google Colab implementation
Supports Hindi text extraction from PDFs and images using Tesseract
"""

import pytesseract
import cv2
import numpy as np
from PIL import Image
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logging.warning("pdf2image not available - PDF processing disabled")

logger = logging.getLogger(__name__)

class HindiOCRProcessor:
    """
    Hindi OCR Processor using Tesseract with Hindi language support
    Based on your Google Colab implementation
    """
    
    def __init__(self, tesseract_path=None):
        """
        Initialize Hindi OCR Processor
        
        Args:
            tesseract_path: Path to tesseract executable (Windows)
        """
        self.tesseract_path = tesseract_path
        self._setup_tesseract()
        
        # Supported languages
        self.languages = {
            'hindi': 'hin',
            'english': 'eng',
            'hindi_english': 'hin+eng'
        }
        
        logger.info("Hindi OCR Processor initialized")
    
    def _setup_tesseract(self):
        """Setup Tesseract path for Windows"""
        if self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        else:
            # Common Windows paths for Tesseract
            common_paths = [
                r'D:\Tesseract\tesseract.exe',  # Your custom path
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
                'tesseract'  # If in PATH
            ]
            
            for path in common_paths:
                if os.path.exists(path) or path == 'tesseract':
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Tesseract found at: {path}")
                    break
            else:
                logger.warning("Tesseract not found. Please install Tesseract OCR")
    
    def preprocess_image(self, pil_img: Image.Image) -> np.ndarray:
        """
        Preprocess image for better Hindi OCR results
        Based on your Colab implementation
        """
        # Convert PIL to numpy array
        img = np.array(pil_img)
        
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
        
        # Apply Gaussian blur to reduce noise
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold using Otsu's method
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        return thresh
    
    def extract_text_from_image(self, image_path: str, language: str = 'hindi_english') -> Dict[str, Any]:
        """
        Extract Hindi text from image using Tesseract
        
        Args:
            image_path: Path to image file
            language: Language for OCR ('hindi', 'english', 'hindi_english')
            
        Returns:
            dict: OCR result with text and metadata
        """
        processing_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Load image
            pil_img = Image.open(image_path)
            
            # Preprocess image
            processed_img = self.preprocess_image(pil_img)
            
            # Convert back to PIL Image
            processed_pil = Image.fromarray(processed_img)
            
            # Get language code
            lang_code = self.languages.get(language, 'hin+eng')
            
            # OCR configuration for Hindi
            config = "--oem 3 --psm 6"  # Use LSTM OCR Engine Mode, assume uniform block of text
            
            # Extract text
            text = pytesseract.image_to_string(
                processed_pil,
                lang=lang_code,
                config=config
            )
            
            # Get confidence scores
            try:
                data = pytesseract.image_to_data(
                    processed_pil,
                    lang=lang_code,
                    config=config,
                    output_type=pytesseract.Output.DICT
                )
                
                # Calculate average confidence
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
            except Exception as conf_error:
                logger.warning(f"Could not get confidence scores: {str(conf_error)}")
                avg_confidence = 0.75  # Default confidence
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'processing_id': processing_id,
                'text': text.strip(),
                'language': language,
                'language_code': lang_code,
                'confidence': avg_confidence / 100 if avg_confidence > 1 else avg_confidence,
                'processing_time': processing_time,
                'image_path': image_path,
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Hindi OCR processing failed: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'processing_id': processing_id,
                'text': '',
                'language': language,
                'confidence': 0.0,
                'processing_time': processing_time,
                'image_path': image_path,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def extract_text_from_pdf(self, pdf_path: str, language: str = 'hindi_english', dpi: int = 300) -> Dict[str, Any]:
        """
        Extract Hindi text from PDF using your Colab implementation
        
        Args:
            pdf_path: Path to PDF file
            language: Language for OCR
            dpi: DPI for PDF to image conversion
            
        Returns:
            dict: OCR result with text from all pages
        """
        if not PDF_SUPPORT:
            return {
                'success': False,
                'error': 'PDF support not available. Install pdf2image: pip install pdf2image',
                'processing_id': str(uuid.uuid4())
            }
        
        processing_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Convert PDF to images (high DPI for better OCR)
            logger.info(f"Converting PDF to images at {dpi} DPI...")
            images = convert_from_path(pdf_path, dpi=dpi)
            
            logger.info(f"Total pages: {len(images)}")
            
            full_text = ""
            page_results = []
            total_confidence = 0
            
            # Process each page
            for i, page in enumerate(images):
                logger.info(f"Processing page {i+1}/{len(images)}")
                
                # Preprocess page
                processed_img = self.preprocess_image(page)
                processed_pil = Image.fromarray(processed_img)
                
                # Get language code
                lang_code = self.languages.get(language, 'hin+eng')
                
                # OCR configuration
                config = "--oem 3 --psm 6"
                
                # Extract text from page
                page_text = pytesseract.image_to_string(
                    processed_pil,
                    lang=lang_code,
                    config=config
                )
                
                # Get confidence for this page
                try:
                    data = pytesseract.image_to_data(
                        processed_pil,
                        lang=lang_code,
                        config=config,
                        output_type=pytesseract.Output.DICT
                    )
                    
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                    page_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                except Exception:
                    page_confidence = 75  # Default confidence
                
                # Store page result
                page_results.append({
                    'page_number': i + 1,
                    'text': page_text.strip(),
                    'confidence': page_confidence / 100 if page_confidence > 1 else page_confidence,
                    'character_count': len(page_text.strip())
                })
                
                full_text += page_text + "\n"
                total_confidence += page_confidence
            
            # Calculate overall metrics
            avg_confidence = total_confidence / len(images) if images else 0
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'processing_id': processing_id,
                'text': full_text.strip(),
                'language': language,
                'language_code': lang_code,
                'confidence': avg_confidence / 100 if avg_confidence > 1 else avg_confidence,
                'processing_time': processing_time,
                'pdf_path': pdf_path,
                'total_pages': len(images),
                'page_results': page_results,
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Hindi PDF OCR processing failed: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'processing_id': processing_id,
                'text': '',
                'language': language,
                'confidence': 0.0,
                'processing_time': processing_time,
                'pdf_path': pdf_path,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_tesseract_languages(self) -> Dict[str, Any]:
        """Check available Tesseract languages"""
        try:
            available_langs = pytesseract.get_languages(config='')
            
            hindi_available = 'hin' in available_langs
            english_available = 'eng' in available_langs
            
            return {
                'tesseract_available': True,
                'hindi_support': hindi_available,
                'english_support': english_available,
                'available_languages': available_langs,
                'recommended_install': [] if hindi_available else ['tesseract-ocr-hin'],
                'status': 'ready' if hindi_available else 'hindi_language_pack_needed'
            }
            
        except Exception as e:
            return {
                'tesseract_available': False,
                'hindi_support': False,
                'english_support': False,
                'error': str(e),
                'status': 'tesseract_not_installed'
            }
    
    def process_document(self, file_path: str, language: str = 'hindi_english') -> Dict[str, Any]:
        """
        Process document (image or PDF) with Hindi OCR
        
        Args:
            file_path: Path to document file
            language: Language for OCR
            
        Returns:
            dict: OCR result in standard format
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            result = self.extract_text_from_pdf(file_path, language)
        else:
            result = self.extract_text_from_image(file_path, language)
        
        # Convert to standard format for compatibility
        return {
            'raw_text': result.get('text', ''),
            'structured_data': {
                'language': result.get('language'),
                'language_code': result.get('language_code'),
                'total_pages': result.get('total_pages', 1),
                'processing_id': result.get('processing_id')
            },
            'confidence': result.get('confidence', 0.0),
            'processing_time': result.get('processing_time', 0.0),
            'success': result.get('success', False),
            'error': result.get('error'),
            'processing_details': result
        }

# Example usage and testing
if __name__ == "__main__":
    # Test Hindi OCR processor
    processor = HindiOCRProcessor()
    
    print("🔍 Hindi OCR Processor Status:")
    status = processor.check_tesseract_languages()
    print(f"Tesseract Available: {status['tesseract_available']}")
    print(f"Hindi Support: {status['hindi_support']}")
    print(f"Status: {status['status']}")
    
    if status['recommended_install']:
        print(f"Recommended Install: {', '.join(status['recommended_install'])}")
    
    # Test with sample text (if available)
    # result = processor.process_document("sample_hindi_document.pdf", "hindi_english")
    # print(f"Processing Result: {result['success']}")
    # print(f"Extracted Text: {result['raw_text'][:100]}...")