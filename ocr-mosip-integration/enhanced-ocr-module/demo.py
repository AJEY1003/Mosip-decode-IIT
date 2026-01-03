"""
Demo script for the Smart OCR & Verification Engine
"""
import sys
import os
import time
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import SmartOCREngine


def demo_processing():
    """
    Demonstrate the OCR processing pipeline
    """
    print("🔍 Smart OCR & Verification Engine Demo")
    print("=" * 50)
    
    # Initialize the OCR engine
    ocr_engine = SmartOCREngine()
    
    print("\n🔧 Engine initialized successfully")
    print(f"   OCR Engine: Multi-engine (Google Vision, AWS Textract, Tesseract)")
    print(f"   Preprocessor: Document optimization pipeline")
    print(f"   AI Verifier: GPT-based validation")
    print(f"   Storage: MongoDB + PostgreSQL")
    
    # Simulate a document processing
    print("\n📄 Simulating document processing...")
    
    # Create a mock document data structure
    mock_result = {
        "document_id": "demo_doc_12345",
        "status": "auto_approved",
        "extracted_fields": {
            "name": "RAMESH KUMAR",
            "dob": "1999-04-12",
            "id_number": "ABCDE1234F",
            "address": "123 Main Street, City, State",
            "document_type": "PAN Card"
        },
        "confidence_score": 0.98,
        "processing_time": 3.2,
        "ocr_engine_used": "google_vision",
        "issues_detected": ["Name capitalization"],
        "corrections_made": {
            "name": "RAMESH -> RAMESH KUMAR"
        }
    }
    
    print(f"\n✅ Processing completed in {mock_result['processing_time']} seconds")
    print(f"   Document ID: {mock_result['document_id']}")
    print(f"   Status: {mock_result['status']}")
    print(f"   Confidence: {mock_result['confidence_score'] * 100:.1f}%")
    print(f"   OCR Engine: {mock_result['ocr_engine_used']}")
    
    print(f"\n📝 Extracted Fields:")
    for field, value in mock_result['extracted_fields'].items():
        print(f"   {field.upper()}: {value}")
    
    if mock_result['issues_detected']:
        print(f"\n⚠️ Issues Detected: {', '.join(mock_result['issues_detected'])}")
    
    if mock_result['corrections_made']:
        print(f"\n🔧 Corrections Made: {mock_result['corrections_made']}")
    
    print(f"\n💾 Data stored in both MongoDB (flexible) and PostgreSQL (structured)")
    
    # Show confidence-based routing
    confidence = mock_result['confidence_score']
    if confidence >= 0.99:
        print("\n✅ Auto-approved (Confidence ≥ 99%)")
    elif confidence >= 0.95:
        print("\n🔍 AI review required (95% ≤ Confidence < 99%)")
    else:
        print("\n👤 Manual review required (Confidence < 95%)")
    
    print("\n" + "=" * 50)
    print("🎯 System Capabilities:")
    print("   • Multi-engine OCR with fallback")
    print("   • Image preprocessing for quality enhancement")
    print("   • Field-level extraction with keyword anchoring")
    print("   • AI-based validation and correction")
    print("   • Rule-based validation checks")
    print("   • Confidence scoring and routing")
    print("   • Dual storage (MongoDB + PostgreSQL)")
    print("   • Web UI with real-time feedback")


def demo_api_endpoints():
    """
    Show the available API endpoints
    """
    print("\n📡 Available API Endpoints:")
    print("   POST /ocr/process          - Upload and process document")
    print("   GET  /ocr/status/{id}      - Get processing status")
    print("   POST /ocr/validate         - Validate with manual corrections")
    print("   GET  /ocr/result/{id}      - Get OCR results")
    print("   GET  /health               - Health check")


def main():
    """
    Main demo function
    """
    demo_processing()
    demo_api_endpoints()
    
    print(f"\n🚀 To run the full system:")
    print(f"   1. Backend: cd backend && python -m api.main")
    print(f"   2. Frontend: cd frontend && npm run dev")
    print(f"   3. Access UI at http://localhost:3000")


if __name__ == "__main__":
    main()