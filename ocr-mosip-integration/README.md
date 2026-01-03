# OCR-MOSIP Integration

OCR-driven solution for text extraction and data verification with MOSIP integration, featuring real Ed25519 cryptographic signatures and QR code generation.

## 🚀 Features

- **OCR Processing**: Extract text from documents using EasyOCR
- **Real Cryptographic Signatures**: Ed25519 signatures for Verifiable Credentials
- **QR Code Generation**: Multiple formats (human-readable, JSON, CBOR)
- **MOSIP Integration**: Connect with MOSIP identity platform
- **Inji Verify Support**: Generate QR codes compatible with Inji Verify
- **Flask REST API**: Complete API endpoints for integration

## 📁 Project Structure

```
ocr-mosip-integration/
├── src/
│   ├── core/                 # Core application modules
│   │   ├── app.py           # Flask application
│   │   ├── ocr_processor.py # OCR processing
│   │   ├── credential_signer.py # Ed25519 signature generation
│   │   └── pixelpass_integration.py # PixelPass QR generation
│   ├── clients/             # External service clients
│   │   ├── mosip_client.py  # MOSIP platform client
│   │   ├── injinet_client.py # InjINet client
│   │   └── inji_verify_client.py # Inji Verify client
│   └── utils/               # Utility modules
│       ├── simple_qr_generator.py # Human-readable QR codes
│       ├── qr_analyzer_resizer.py # QR analysis and resizing
│       └── render_qr_image.py # QR image rendering
├── tests/                   # Test modules
├── scripts/                 # JavaScript utilities
├── docs/                    # Documentation
├── config/                  # Configuration files
├── examples/                # Example credentials and outputs
├── output/                  # Generated QR codes and images
├── requirements.txt         # Python dependencies
└── package.json            # Node.js dependencies
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- pip and npm

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ocr-mosip-integration
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

4. **Configure environment**
   ```bash
   cp config/.env.example .env
   # Edit .env with your configuration
   ```

## 🚀 Quick Start

### 1. Start the Backend Server
```bash
# Navigate to the backend directory
cd ocr-mosip-integration

# Install dependencies
pip install -r requirements.txt

# Navigate to the core directory and start the Flask application
cd src/core
python app.py
```

**Important**: Always navigate to `src/core/` directory and run `python app.py` to start the backend server. This is the main Flask application entry point.

The server will start on `http://localhost:5000` by default.

### 2. Generate QR Code with Real Signatures
```bash
curl -X POST http://localhost:5000/api/pixelpass/generate-qr \
  -H "Content-Type: application/json" \
  -d '{
    "ocr_data": {
      "name": "John Doe",
      "date_of_birth": "01/01/1990",
      "aadhaar_number": "1234-5678-9012"
    }
  }'
```

### 3. Generate Human-Readable QR Code
```bash
curl -X POST http://localhost:5000/api/simple-qr/generate \
  -H "Content-Type: application/json" \
  -d '{
    "ocr_data": {
      "name": "John Doe",
      "phone": "+1234567890"
    },
    "format": "text"
  }'
```

## 🔐 Cryptographic Signatures

This project uses **real Ed25519 cryptographic signatures** instead of mock signatures:

- **Algorithm**: Ed25519Signature2018
- **Key Generation**: Automatic key pair generation and storage
- **JWS Format**: Proper JSON Web Signature format
- **Verification**: Cryptographically verifiable signatures

## 📱 QR Code Formats

### 1. Human-Readable QR Codes
- Perfect for Google scanner and basic QR readers
- Contains plain text information
- Generated via `/api/simple-qr/generate`

### 2. JSON QR Codes
- Structured data in JSON format
- For applications that can parse JSON
- Clean, organized data structure

### 3. Verifiable Credential QR Codes
- W3C Verifiable Credential format
- Real Ed25519 signatures
- Compatible with Inji Verify
- CBOR encoding for efficiency

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/
```

### Test Individual Components
```bash
# Test real signatures
python tests/test_real_signatures.py

# Test verification logic
python tests/test_verification_logic.py

# Analyze QR codes
python src/utils/qr_analyzer_resizer.py
```

## 📊 API Endpoints

### OCR Processing
- `POST /ocr/extract` - Extract text from documents
- `POST /ocr/verify` - Verify extracted data

### QR Code Generation
- `POST /api/pixelpass/generate-qr` - Generate VC QR with real signatures
- `POST /api/simple-qr/generate` - Generate human-readable QR codes

### Verification
- `POST /api/inji/verify-qr` - Verify QR codes with Inji Verify

### MOSIP Integration
- `POST /api/mosip/preregister` - Submit pre-registration
- `GET /api/mosip/status/<id>` - Check registration status

## 🔧 Configuration

### Environment Variables
```bash
# MOSIP Configuration
MOSIP_BASE_URL=https://api.mosip.net
MOSIP_CLIENT_ID=your_client_id
MOSIP_CLIENT_SECRET=your_client_secret

# InjINet Configuration
INJINET_BASE_URL=https://injinet.collab.mosip.net
INJINET_API_KEY=your_api_key

# Inji Verify Configuration
INJI_VERIFY_BASE_URL=https://verify.inji.io
INJI_VERIFY_API_KEY=your_api_key
```

## 📚 Documentation

- [Complete Integration Guide](docs/COMPLETE_INTEGRATION_GUIDE.md)
- [API Documentation](http://localhost:5000/api/docs)
- [Testing Guide](tests/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the [documentation](docs/)
- Review [test examples](tests/)
- Open an issue on GitHub

## 🎯 Key Features Summary

- ✅ Real Ed25519 cryptographic signatures
- ✅ Multiple QR code formats (text, JSON, VC)
- ✅ MOSIP platform integration
- ✅ Inji Verify compatibility
- ✅ OCR text extraction
- ✅ Flask REST API
- ✅ Comprehensive testing
- ✅ Production-ready structure