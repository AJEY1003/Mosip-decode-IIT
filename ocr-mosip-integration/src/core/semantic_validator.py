import json
import logging
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticValidator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the SemanticValidator with a sentence-transformer model.
        The default model 'all-MiniLM-L6-v2' is lightweight and effective for semantic similarity.
        """
        logger.info(f"Loading Semantic Validation model: {model_name}...")
        try:
            self.model = SentenceTransformer(model_name)
            logger.info("✅ Semantic Validation model loaded successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to load Semantic Validation model: {e}")
            self.model = None

    def validate(self, pdf_text, qr_data):
        """
        Compare extracted PDF text with QR code data using semantic similarity.
        
        Args:
            pdf_text (str): The text extracted from the uploaded document.
            qr_data (str or dict): The data decoded from the QR code.
            
        Returns:
            dict: Validation results including score (0-100) and status.
        """
        if not self.model:
            return {
                "score": 0,
                "status": "error",
                "message": "Model not authenticated or loaded"
            }
            
        try:
            # Preprocess inputs
            text1 = self._preprocess(pdf_text)
            text2 = self._preprocess(qr_data)
            
            logger.info(f"Comparing PDF Text (len={len(text1)}) with QR Data (len={len(text2)})")
            logger.debug(f"PDF Embed Input: {text1[:100]}...")
            logger.debug(f"QR Embed Input: {text2}")
            
            if not text1 or not text2:
                 return {
                    "score": 0,
                    "status": "failed",
                    "message": "Empty content provided for comparison"
                }

            # Generate embeddings
            embeddings1 = self.model.encode([text1])
            embeddings2 = self.model.encode([text2])
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(embeddings1, embeddings2)
            score = float(similarity_matrix[0][0]) * 100
            
            # Round score
            score = round(score, 2)
            
            # Determine match status (Adjusted threshold for Doc vs Summary comparison)
            is_match = score >= 70
            
            match_label = "High Match" if score >= 85 else "Medium Match" if score >= 70 else "Low Match"
            
            return {
                "score": score,
                "status": "success",
                "is_match": is_match,
                "match_label": match_label
            }
            
        except Exception as e:
            logger.error(f"Error during semantic validation: {e}")
            return {
                "score": 0,
                "status": "error",
                "message": str(e)
            }

    def _preprocess(self, data):
        """
        Convert input data to a string and perform basic cleaning.
        """
        if isinstance(data, dict):
            # Convert dict to Key: Value format to provide more semantic context matches
            # e.g. "Name: John Doe Age: 30"
            return ", ".join([f"{k}: {v}" for k, v in data.items() if v])
        
        if isinstance(data, str):
            # Basic whitespace cleanup
            return " ".join(data.split())
            
        return str(data)

# Singleton instance for easy import
# validator = SemanticValidator() 
