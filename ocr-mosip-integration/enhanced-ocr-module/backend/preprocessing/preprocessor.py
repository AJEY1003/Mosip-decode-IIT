import cv2
import numpy as np
from PIL import Image
import io
from typing import Union
import os


class ImagePreprocessor:
    """
    Image preprocessing module for OCR enhancement
    """
    
    def __init__(self):
        pass
    
    def preprocess(self, image_path: str, output_path: str = None) -> str:
        """
        Complete preprocessing pipeline for OCR optimization
        """
        # Load image
        img = cv2.imread(image_path)
        
        # Apply preprocessing steps
        processed_img = self._grayscale_conversion(img)
        processed_img = self._noise_reduction(processed_img)
        processed_img = self._skew_correction(processed_img)
        processed_img = self._contrast_normalization(processed_img)
        processed_img = self._resize_to_optimal_dpi(processed_img)
        
        # Save processed image
        if output_path:
            cv2.imwrite(output_path, processed_img)
            return output_path
        else:
            # Create a temporary file
            temp_path = f"temp_processed_{os.path.basename(image_path)}"
            cv2.imwrite(temp_path, processed_img)
            return temp_path
    
    def _grayscale_conversion(self, img: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale
        """
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        return gray
    
    def _noise_reduction(self, img: np.ndarray) -> np.ndarray:
        """
        Apply noise reduction using non-local means denoising
        """
        # Apply fast non-local means denoising
        denoised = cv2.fastNlMeansDenoising(img)
        return denoised
    
    def _skew_correction(self, img: np.ndarray) -> np.ndarray:
        """
        Correct image skew using contour detection
        """
        coords = np.column_stack(np.where(img > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        return rotated
    
    def _contrast_normalization(self, img: np.ndarray) -> np.ndarray:
        """
        Normalize image contrast using histogram equalization
        """
        # Apply histogram equalization
        normalized = cv2.equalizeHist(img)
        return normalized
    
    def _resize_to_optimal_dpi(self, img: np.ndarray, target_dpi: int = 300) -> np.ndarray:
        """
        Resize image to optimal DPI (default 300 DPI for OCR)
        """
        # Calculate current DPI based on image dimensions and physical size
        # For now, we'll assume standard screen DPI (72) and scale to target DPI
        height, width = img.shape
        scale_factor = target_dpi / 72  # Assuming original was 72 DPI
        
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Resize image using cubic interpolation for better quality
        resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        return resized
    
    def enhance_text_regions(self, img: np.ndarray) -> np.ndarray:
        """
        Enhance text regions using morphological operations
        """
        # Create a rectangular kernel for morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        
        # Apply morphological operations to enhance text
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        
        return img
    
    def adjust_brightness_contrast(self, img: np.ndarray, brightness: int = 0, contrast: int = 0) -> np.ndarray:
        """
        Adjust brightness and contrast of the image
        """
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow) / 255
            gamma_b = shadow
            
            img = cv2.addWeighted(img, alpha_b, img, 0, gamma_b)
        
        if contrast != 0:
            f = 131 * (contrast + 127) / (127 * (131 - contrast))
            alpha_c = f
            gamma_c = 127 * (1 - f)
            
            img = cv2.addWeighted(img, alpha_c, img, 0, gamma_c)
        
        return img


class DocumentPreprocessor(ImagePreprocessor):
    """
    Specialized preprocessor for document images
    """
    
    def __init__(self):
        super().__init__()
    
    def preprocess_document(self, image_path: str, output_path: str = None) -> str:
        """
        Preprocess document-specific image with additional document optimizations
        """
        img = cv2.imread(image_path)
        
        # Apply base preprocessing
        processed_img = self._grayscale_conversion(img)
        processed_img = self._noise_reduction(processed_img)
        processed_img = self._skew_correction(processed_img)
        processed_img = self._contrast_normalization(processed_img)
        
        # Document-specific enhancements
        processed_img = self._enhance_document_text(processed_img)
        processed_img = self._remove_document_background(processed_img)
        processed_img = self._resize_to_optimal_dpi(processed_img)
        
        # Save processed image
        if output_path:
            cv2.imwrite(output_path, processed_img)
            return output_path
        else:
            temp_path = f"temp_doc_processed_{os.path.basename(image_path)}"
            cv2.imwrite(temp_path, processed_img)
            return temp_path
    
    def _enhance_document_text(self, img: np.ndarray) -> np.ndarray:
        """
        Enhance text in document images using adaptive thresholding
        """
        # Apply adaptive threshold to enhance text
        thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        return thresh
    
    def _remove_document_background(self, img: np.ndarray) -> np.ndarray:
        """
        Remove document background to improve OCR accuracy
        """
        # Apply morphological operations to clean background
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)
        
        return img


# Example usage
if __name__ == "__main__":
    preprocessor = DocumentPreprocessor()
    processed_path = preprocessor.preprocess_document("input.jpg", "output.jpg")
    print(f"Processed image saved to: {processed_path}")