# MOSIP ITR Assistant - OCR Integration Project

A comprehensive solution for Income Tax Return (ITR) document processing using OCR technology integrated with MOSIP (Modular Open Source Identity Platform) services.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup (OCR Processing)
```bash
cd ocr-mosip-integration
pip install -r requirements.txt
cd src/core
python app.py
```
Backend will run on `http://localhost:5000`

### Frontend Setup (React Application)
```bash
cd mosip-itr-assistant
npm install
npm run dev
```
Frontend will run on `http://localhost:5173`

## 📸 Application Screenshots

### Dashboard Overview
![Dashboard](images/page1.png)
*Modern dashboard with animated progress rings and document processing statistics*

### Multi-Document Upload Interface
![Upload Interface](images/page2.png)
*Streamlined interface for uploading multiple document types (Aadhaar, Form 16, Bank Statements, etc.)*

### QR Code Generation
![QR Code](images/qrcode.png)
*QR code generation for secure document verification and data sharing*

## 🏗️ Architecture Overview

### System Components

1. **Frontend (React + Vite)**
   - Modern UI with Tailwind CSS
   - Multi-document upload system
   - Real-time validation results
   - Dashboard with animated charts
   - Government portal-style design

2. **Backend (Flask + Python)**
   - OCR processing with multiple engines
   - MOSIP integration for identity verification
   - NER (Named Entity Recognition) for data extraction
   - RESTful API with OpenAPI documentation

3. **OCR Engines**
   - EasyOCR for general text recognition
   - Tesseract for Hindi/multilingual support
   - Enhanced OCR with confidence scoring
   - PDF processing capabilities

## 🔄 Complete Workflow

### 1. Document Upload
- Users upload multiple document types:
  - Aadhaar Card
  - Form 16
  - Pre-registration documents
  - Bank statements
  - Income certificates

### 2. OCR Processing
- Documents processed through multiple OCR engines
- Text extraction with confidence scoring
- Structured data extraction using NER
- Multi-language support (English/Hindi)

### 3. Data Validation
- MOSIP integration for identity verification
- Field-level validation with confidence scores
- Cross-document data consistency checks
- Real-time validation feedback

### 4. Auto-Fill & Form Generation
- Intelligent form population from extracted data
- Priority-based field merging
- Conflict resolution for duplicate data
- ITR form generation with validated data

### 5. Verification & Export
- Final validation against MOSIP databases
- QR code generation for document verification
- Export capabilities for tax filing
- Audit trail maintenance

## 🛠️ Technical Implementation

### MOSIP Integration Features

1. **Identity Verification**
   - Aadhaar number validation
   - Biometric verification support
   - Real-time MOSIP API integration

2. **Document Authentication**
   - Digital signature verification
   - Document integrity checks
   - Tamper detection

3. **Data Security**
   - End-to-end encryption
   - Secure API communication
   - Privacy-compliant data handling

### OCR Processing Pipeline

1. **Image Preprocessing**
   - Image enhancement and noise reduction
   - Format standardization
   - Multi-page PDF handling

2. **Text Extraction**
   - Multiple OCR engine comparison
   - Confidence-based result selection
   - Error correction and validation

3. **Data Structuring**
   - NER-based field extraction
   - Data type validation
   - Format standardization

## 📁 Project Structure

```
├── mosip-itr-assistant/          # React Frontend
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   ├── pages/               # Application pages
│   │   ├── services/            # API integration
│   │   └── utils/               # Utility functions
│   └── package.json
│
├── ocr-mosip-integration/        # Python Backend
│   ├── src/core/                # Core processing modules
│   │   ├── app.py              # Main Flask application
│   │   ├── ocr_processor.py    # OCR processing logic
│   │   ├── ner_extractor.py    # NER data extraction
│   │   └── mosip_client.py     # MOSIP API integration
│   ├── models/                  # API schema definitions
│   └── requirements.txt
│
└── images/                      # Documentation screenshots
```

## 🔧 API Endpoints

### OCR Processing
- `POST /ocr/extract` - Extract text from documents
- `POST /api/enhanced-ocr/extract` - Enhanced OCR with multiple engines
- `POST /api/ner/extract` - Named Entity Recognition
- `POST /api/auto-fill` - Auto-fill form data

### MOSIP Integration
- `POST /api/mosip/verify` - Verify identity with MOSIP
- `POST /api/document/validate` - Document validation
- `GET /api/verification/status` - Check verification status

### Utility Endpoints
- `GET /health` - Health check
- `GET /api/docs` - API documentation
- `POST /api/qr/generate` - QR code generation

## 🎯 Key Features

### ✅ Implemented Features
- Multi-document OCR processing
- MOSIP identity verification
- NER-based data extraction
- Auto-fill functionality
- Real-time validation
- Dashboard with analytics
- QR code generation
- Multi-language support
- PDF processing
- Confidence scoring

### 🔄 Integration Points
- MOSIP API for identity verification
- Multiple OCR engines for accuracy
- RESTful API architecture
- Real-time data validation
- Secure document handling

## 🚀 Deployment

### Development
```bash
# Start backend
cd ocr-mosip-integration/src/core && python app.py

# Start frontend
cd mosip-itr-assistant && npm run dev
```

### Production
- Backend: Deploy Flask app with gunicorn
- Frontend: Build with `npm run build` and serve static files
- Database: Configure production database
- Security: Enable HTTPS and API authentication

## 📝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Acknowledgments

- MOSIP Foundation for identity platform integration
- OCR engine providers (EasyOCR, Tesseract)
- React and Flask communities
- Contributors and testers

---

**Built with ❤️ for digital India initiatives**