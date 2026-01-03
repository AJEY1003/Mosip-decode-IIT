import unittest
from unittest.mock import Mock, patch
import tempfile
import os
from backend.ocr_engine.ocr_engine import OCREngine
from backend.preprocessing.preprocessor import DocumentPreprocessor
from backend.verification.ai_verifier import AIVerifier, RuleBasedValidator
from backend.storage.data_storage import DataStorageManager


class TestOCREngine(unittest.TestCase):
    def setUp(self):
        self.ocr_engine = OCREngine()
    
    @patch.object(OCREngine, 'tesseract_ocr')
    def test_process_with_multiple_engines(self, mock_tesseract):
        # Mock the tesseract OCR to return a known result
        mock_tesseract.return_value = {
            "text": "Sample text from image",
            "confidence": 0.85,
            "success": True
        }
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = self.ocr_engine.process_with_multiple_engines(temp_path)
            
            # Verify the result structure
            self.assertIn('text', result)
            self.assertIn('confidence', result)
            self.assertIn('best_engine', result)
            self.assertIn('all_results', result)
            self.assertTrue(result['success'])
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestFieldExtractor(unittest.TestCase):
    def setUp(self):
        from backend.ocr_engine.field_extractor import FieldExtractor
        self.extractor = FieldExtractor()
    
    def test_extract_name(self):
        text = "Name: John Doe"
        result = self.extractor._extract_name(text)
        self.assertIsNotNone(result)
        self.assertIn("John", result)
        self.assertIn("Doe", result)
    
    def test_extract_date_of_birth(self):
        text = "Date of Birth: 1990-01-01"
        result = self.extractor._extract_date_of_birth(text)
        self.assertEqual(result, "1990-01-01")
    
    def test_extract_id_number(self):
        text = "PAN: ABCDE1234F"
        result = self.extractor._extract_id_number(text)
        self.assertEqual(result, "ABCDE1234F")


class TestRuleBasedValidator(unittest.TestCase):
    def setUp(self):
        self.validator = RuleBasedValidator()
    
    def test_validate_pan_format(self):
        # Valid PAN
        result = self.validator._validate_id_number("ABCDE1234F")
        self.assertTrue(result)
        
        # Invalid PAN
        result = self.validator._validate_id_number("INVALID")
        self.assertFalse(result)
    
    def test_validate_date(self):
        # Valid date
        result = self.validator._validate_date("1990-01-01")
        self.assertTrue(result)
        
        # Invalid date
        result = self.validator._validate_date("9999-99-99")
        self.assertFalse(result)


class TestPreprocessor(unittest.TestCase):
    def setUp(self):
        self.preprocessor = DocumentPreprocessor()
    
    def test_grayscale_conversion(self):
        import numpy as np
        # Create a dummy RGB image
        dummy_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        result = self.preprocessor._grayscale_conversion(dummy_img)
        
        # Result should be 2D (grayscale)
        self.assertEqual(len(result.shape), 2)
    
    def test_noise_reduction(self):
        import numpy as np
        # Create a dummy image
        dummy_img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        result = self.preprocessor._noise_reduction(dummy_img)
        
        # Result should have same shape
        self.assertEqual(result.shape, dummy_img.shape)


if __name__ == '__main__':
    unittest.main()