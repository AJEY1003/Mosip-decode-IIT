import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
from typing import Dict, List, Optional, Tuple
from google.cloud import vision
import boto3
from config.settings import Config

class OCREngine:
    def __init__(self):
        self.google_vision_client = None
        self.aws_textract_client = None
        self._init_clients()
    
    def _init_clients(self):
        """Initialize OCR API clients"""
        try:
            if Config.GOOGLE_VISION_API_KEY:
                # Initialize Google Vision client
                import os
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/service-account-key.json'  # Update this path
                self.google_vision_client = vision.ImageAnnotatorClient()
        except Exception as e:
            print(f"Failed to initialize Google Vision client: {e}")
        
        try:
            if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
                self.aws_textract_client = boto3.client(
                    'textract',
                    region_name=Config.AWS_REGION,
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
                )
        except Exception as e:
            print(f"Failed to initialize AWS Textract client: {e}")
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR results
        """
        # Read image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply noise reduction
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Correct skew
        coords = np.column_stack(np.where(denoised > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        (h, w) = denoised.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(denoised, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        # Normalize contrast
        normalized = cv2.equalizeHist(rotated)
        
        # Resize to optimal DPI (300 DPI)
        height, width = normalized.shape
        scale_factor = 300 / 72  # Assuming original was 72 DPI
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        resized = cv2.resize(normalized, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        return resized
    
    def google_vision_ocr(self, image_path: str) -> Dict[str, any]:
        """
        Perform OCR using Google Vision API
        """
        if not self.google_vision_client:
            return {"text": "", "confidence": 0.0, "success": False, "error": "Google Vision client not initialized"}
        
        try:
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = self.google_vision_client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                text = texts[0].description
                confidence = texts[0].confidence if texts[0].bounding_poly else 0.0
                return {"text": text, "confidence": confidence, "success": True}
            else:
                return {"text": "", "confidence": 0.0, "success": False, "error": "No text detected"}
                
        except Exception as e:
            return {"text": "", "confidence": 0.0, "success": False, "error": str(e)}
    
    def aws_textract_ocr(self, image_path: str) -> Dict[str, any]:
        """
        Perform OCR using AWS Textract
        """
        if not self.aws_textract_client:
            return {"text": "", "confidence": 0.0, "success": False, "error": "AWS Textract client not initialized"}
        
        try:
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
            
            response = self.aws_textract_client.detect_document_text(
                Document={'Bytes': image_bytes}
            )
            
            text_blocks = []
            total_confidence = 0
            block_count = 0
            
            for item in response['Blocks']:
                if item['BlockType'] == 'LINE':
                    text_blocks.append(item['Text'])
                    total_confidence += item['Confidence']
                    block_count += 1
            
            avg_confidence = total_confidence / block_count if block_count > 0 else 0.0
            full_text = ' '.join(text_blocks)
            
            return {
                "text": full_text,
                "confidence": avg_confidence / 100,  # AWS returns confidence as percentage
                "success": True
            }
            
        except Exception as e:
            return {"text": "", "confidence": 0.0, "success": False, "error": str(e)}
    
    def tesseract_ocr(self, image_path: str) -> Dict[str, any]:
        """
        Perform OCR using Tesseract (offline)
        """
        try:
            # Preprocess image for better results
            processed_img = self.preprocess_image(image_path)
            
            # Convert to PIL Image for pytesseract
            pil_img = Image.fromarray(processed_img)
            
            # Extract text with confidence scores
            data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
            
            text_parts = []
            confidences = []
            
            for i, text in enumerate(data['text']):
                if int(data['conf'][i]) > 0:  # Only include text with confidence > 0
                    text_parts.append(text)
                    confidences.append(int(data['conf'][i]))
            
            full_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                "text": full_text,
                "confidence": avg_confidence / 100,  # Convert to 0-1 scale
                "success": True
            }
            
        except Exception as e:
            return {"text": "", "confidence": 0.0, "success": False, "error": str(e)}
    
    def process_with_multiple_engines(self, image_path: str) -> Dict[str, any]:
        """
        Process image using multiple OCR engines with fallback strategy
        """
        results = []
        
        # Try Google Vision first
        if self.google_vision_client:
            result = self.google_vision_ocr(image_path)
            result['engine'] = 'google_vision'
            results.append(result)
        
        # Try AWS Textract if Google Vision fails or is not available
        if self.aws_textract_client:
            result = self.aws_textract_ocr(image_path)
            result['engine'] = 'aws_textract'
            results.append(result)
        
        # Always try Tesseract as fallback
        result = self.tesseract_ocr(image_path)
        result['engine'] = 'tesseract'
        results.append(result)
        
        # Select the best result based on confidence
        successful_results = [r for r in results if r['success']]
        
        if not successful_results:
            return {
                "text": "",
                "confidence": 0.0,
                "best_engine": "none",
                "all_results": results,
                "success": False
            }
        
        # Find result with highest confidence
        best_result = max(successful_results, key=lambda x: x['confidence'])
        
        # Merge results if multiple engines succeed (for improved accuracy)
        merged_text = self._merge_results(successful_results)
        
        return {
            "text": merged_text,
            "confidence": best_result['confidence'],
            "best_engine": best_result['engine'],
            "all_results": results,
            "success": True
        }
    
    def _merge_results(self, results: List[Dict]) -> str:
        """
        Merge OCR results from multiple engines to improve accuracy
        """
        # For now, return the text from the highest confidence result
        # In a more advanced implementation, we could implement text comparison
        # and voting mechanisms to merge results
        best_result = max(results, key=lambda x: x['confidence'])
        return best_result['text']


# Example usage
if __name__ == "__main__":
    ocr = OCREngine()
    result = ocr.process_with_multiple_engines("sample_document.jpg")
    print(f"OCR Result: {result}")