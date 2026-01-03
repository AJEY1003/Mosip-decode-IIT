# MOSIP ITR Assistant - Frontend

A modern React application for Income Tax Return (ITR) document processing with MOSIP integration.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation & Setup
```bash
# Navigate to the frontend directory
cd mosip-itr-assistant

# Install dependencies
npm install

# Start the development server
npm run dev
```

The application will start on `http://localhost:5173`

## 🎯 Features

### ✅ Core Features
- **Modern Dashboard**: Animated progress rings and statistics
- **Multi-Document Upload**: Support for Aadhaar, Form 16, Bank statements, etc.
- **Real-time OCR Processing**: Integration with backend OCR services
- **Auto-Fill Forms**: Intelligent form population from extracted data
- **MOSIP Validation**: Real-time identity verification
- **QR Code Generation**: Secure document verification codes
- **Responsive Design**: Government portal-style UI

### 🎨 UI Components
- Beautiful gradient backgrounds
- Animated charts and progress indicators
- Professional form layouts
- File upload with drag-and-drop
- Real-time validation feedback
- Mobile-responsive design

## 📁 Project Structure

```
mosip-itr-assistant/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # Base UI components (buttons, inputs)
│   │   ├── FileUpload.jsx  # File upload component
│   │   ├── Hero.jsx        # Landing page hero
│   │   └── ...
│   ├── pages/              # Application pages
│   │   ├── Home.jsx        # Landing page
│   │   ├── ITRDashboard.jsx # Main dashboard
│   │   ├── Upload.jsx      # Document upload
│   │   ├── Forms.jsx       # ITR form filling
│   │   └── ValidationResult.jsx # Validation results
│   ├── services/           # API integration
│   │   └── api.js          # Backend API calls
│   ├── utils/              # Utility functions
│   │   └── nerExtractor.js # NER data processing
│   └── styles/             # CSS and styling
├── public/                 # Static assets
└── package.json           # Dependencies and scripts
```

## 🔧 Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint issues
```

## 🌐 API Integration

The frontend integrates with the backend OCR service:

### Backend Connection
- **Base URL**: `http://localhost:5000`
- **OCR Endpoint**: `/ocr/extract`
- **Enhanced OCR**: `/api/enhanced-ocr/extract`
- **NER Extraction**: `/api/ner/extract`
- **Auto-Fill**: `/api/auto-fill`

### Data Flow
1. **Upload**: Documents uploaded through FileUpload component
2. **Processing**: Sent to backend OCR service
3. **Extraction**: Text and structured data extracted
4. **Validation**: MOSIP validation for identity verification
5. **Auto-Fill**: Forms populated with extracted data
6. **Results**: Validation results displayed with confidence scores

## 🎨 Styling & Design

### Technology Stack
- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Custom CSS**: Additional styling for animations

### Design System
- **Colors**: Government portal green theme
- **Typography**: Clean, professional fonts
- **Animations**: Smooth transitions and loading states
- **Layout**: Responsive grid system
- **Components**: Reusable UI component library

## 🔄 State Management

### Data Flow
- **Local State**: React useState for component state
- **API State**: Service layer for backend communication
- **Form State**: Controlled components for form handling
- **Upload State**: File upload progress and status

### Key State Objects
```javascript
// Document upload state
const [uploadedDocuments, setUploadedDocuments] = useState({
  aadhaar: null,
  form16: null,
  bankStatement: null,
  // ...
});

// Validation results
const [validationResults, setValidationResults] = useState({
  confidence: 0,
  fields: {},
  status: 'pending'
});
```

## 🚀 Deployment

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm run preview
```

### Environment Variables
Create `.env` file:
```env
VITE_API_BASE_URL=http://localhost:5000
VITE_APP_TITLE=MOSIP ITR Assistant
```

## 🧪 Testing

### Manual Testing
1. Start backend server (`cd ocr-mosip-integration/src/core && python app.py`)
2. Start frontend (`npm run dev`)
3. Upload test documents
4. Verify OCR extraction
5. Check form auto-fill
6. Validate MOSIP integration

### Test Documents
Use documents from `../ocr-mosip-integration/test_documents/`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📚 Documentation

- [Component Documentation](src/components/README.md)
- [API Integration Guide](src/services/README.md)
- [Styling Guide](src/styles/README.md)

## 🆘 Troubleshooting

### Common Issues

**Build Errors**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API Connection Issues**
- Ensure backend is running on `http://localhost:5000`
- Check CORS configuration
- Verify API endpoints

**Styling Issues**
- Ensure Tailwind CSS is properly configured
- Check for conflicting CSS classes
- Verify responsive breakpoints

## 📄 License

This project is licensed under the MIT License.

---

**Built with React + Vite for modern web development**
