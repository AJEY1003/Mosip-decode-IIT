# Smart OCR & Verification Engine

A modular OCR + AI verification system that integrates seamlessly into AI agent UIs, enabling high-accuracy document text extraction, validation, and structured storage with near-100% confidence.

## 🚀 Features

- **Multi-Engine OCR Pipeline**: Google Vision API, AWS Textract, and Tesseract with automatic fallback
- **Image Preprocessing**: Grayscale conversion, noise reduction, skew correction, contrast normalization
- **Field-Level Extraction**: Structured field extraction with keyword anchoring and regex
- **AI Verification Layer**: LLM-based validation and correction of extracted fields
- **Rule-Based Validation**: Deterministic checks with regex patterns
- **Confidence Scoring**: Combined scoring from OCR, AI, and rule validation
- **Dual Storage**: MongoDB for flexible storage and PostgreSQL for structured reporting
- **Real-time UI**: React-based interface with drag-and-drop upload and real-time status updates

## 🛠️ Tech Stack

- **Backend**: Python (FastAPI)
- **OCR**: Google Vision, AWS Textract, Tesseract
- **AI**: OpenAI GPT for validation
- **DB**: MongoDB + PostgreSQL
- **Image Processing**: OpenCV
- **Frontend**: React with Vite

## 📋 Requirements

### Backend
- Python 3.8+
- pip

### Frontend
- Node.js 16+
- npm or yarn

## 🚀 Quick Start

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Create a .env file with your API keys
GOOGLE_VISION_API_KEY=your_google_vision_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
OPENAI_API_KEY=your_openai_key
MONGODB_URI=mongodb://localhost:27017/ocr_db
POSTGRES_URI=postgresql://user:password@localhost:5432/ocr_db
```

3. Start the backend server:
```bash
cd backend
python -m api.main
```

### Frontend Setup

1. Install Node dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The UI will be available at `http://localhost:3000`.

## 🏗️ Project Structure

```
ocr-verification-engine/
├── backend/
│   ├── ocr_engine/          # OCR processing and field extraction
│   ├── preprocessing/       # Image preprocessing modules
│   ├── verification/        # AI and rule-based validation
│   ├── storage/            # Data storage modules
│   ├── api/                # FastAPI endpoints
│   └── main.py             # Main entry point
├── frontend/               # React UI components
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   └── utils/          # Utility functions
│   └── public/             # Public assets
├── config/                 # Configuration files
├── requirements.txt        # Python dependencies
└── README.md
```

## 📡 API Endpoints

- `POST /ocr/process` - Upload and process a document
- `GET /ocr/status/{id}` - Get processing status
- `POST /ocr/validate` - Validate document with manual corrections
- `GET /ocr/result/{id}` - Get OCR results
- `GET /health` - Health check

## 🎯 Usage

1. Upload a document using the UI or API
2. The system will preprocess the image and run it through multiple OCR engines
3. Extracted fields will be validated by AI and rule-based systems
4. Results will be stored in both MongoDB and PostgreSQL
5. View results in the UI with confidence scores and manual correction options

## 🔒 Security & Privacy

- Temporary file storage with auto-delete
- Encryption of sensitive fields
- PII masking in logs
- Secure API key management

## 📊 Success Criteria

- ≥99% accuracy on structured documents
- <5s processing time per document
- Fully modular and extendable
- Production-ready code

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.