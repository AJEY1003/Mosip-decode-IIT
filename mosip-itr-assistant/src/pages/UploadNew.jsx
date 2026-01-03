import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
    Upload as UploadIcon, FileText, User, CreditCard, 
    Settings, BarChart3, ArrowLeft, Cloud, CheckCircle, 
    AlertCircle, Zap, Database, TrendingUp, Lock, X
} from 'lucide-react';
import apiService from '../services/api';
import './UploadNew.css';

const UploadNew = () => {
    const navigate = useNavigate();
    const [selectedOCR, setSelectedOCR] = useState('enhanced');
    const [documentsUploaded, setDocumentsUploaded] = useState(0);
    const [textsExtracted, setTextsExtracted] = useState(0);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState(null);
    const [uploadedDocuments, setUploadedDocuments] = useState({
        aadhaar: null,
        form16: null,
        preregistration: null,
        bankSlip: null,
        income: null
    });
    const [extractedTexts, setExtractedTexts] = useState({});
    const [processingDetails, setProcessingDetails] = useState({
        engines_used: [],
        processing_time: 0,
        total_pages: 0
    });

    // Document type configurations
    const documentTypes = [
        {
            id: 'aadhaar',
            title: 'Aadhaar Card',
            icon: '👤',
            fields: 'name aadhaar date of birth +2 more',
            description: 'Upload Aadhaar Card for identity verification',
            color: 'bg-blue-500'
        },
        {
            id: 'form16',
            title: 'Form 16',
            icon: '📄',
            fields: 'name PAN employer +3 more',
            description: 'Upload Form 16 from your employer',
            color: 'bg-purple-500'
        },
        {
            id: 'preregistration',
            title: 'Pre-registration Form',
            icon: '📝',
            fields: 'name PAN email +2 more',
            description: 'Upload ITR pre-registration form',
            color: 'bg-green-500'
        },
        {
            id: 'bankSlip',
            title: 'Bank Statement',
            icon: '🏦',
            fields: 'account IFSC bank name +2 more',
            description: 'Upload bank statement or salary slip',
            color: 'bg-orange-500'
        },
        {
            id: 'income',
            title: 'Income Documents',
            icon: '💰',
            fields: 'salary TDS income +2 more',
            description: 'Upload additional income documents',
            color: 'bg-red-500'
        }
    ];

    // Extract text from a single document
    const extractTextFromDocument = async (documentType, file) => {
        try {
            console.log(`🔄 Processing ${documentType}:`, file.name);
            
            const useEnhanced = selectedOCR === 'enhanced';
            const data = useEnhanced 
                ? await apiService.enhancedExtractText(file, documentType, true)
                : await apiService.extractText(file, documentType);

            console.log(`✅ ${documentType} processed:`, data);
            
            // Update processing details
            if (data.processing_details) {
                setProcessingDetails(prev => ({
                    ...prev,
                    engines_used: [...new Set([...prev.engines_used, ...(data.processing_details.engines_used || [])])],
                    processing_time: prev.processing_time + (data.processing_details.processing_time || 0),
                    total_pages: prev.total_pages + (data.processing_details.total_pages || 1)
                }));
            }

            return data;
        } catch (error) {
            console.error(`❌ Failed to process ${documentType}:`, error);
            throw error;
        }
    };

    // Handle file upload for a specific document type (without immediate processing)
    const handleUpload = async (documentType) => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.pdf,.jpg,.jpeg,.png';
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            try {
                // Just store the file, don't process it yet
                setUploadedDocuments(prev => ({
                    ...prev,
                    [documentType]: file
                }));

                // Update counters
                setDocumentsUploaded(prev => prev + 1);

                console.log(`✅ ${documentType} uploaded: ${file.name}`);
            } catch (error) {
                console.error(`❌ Failed to upload ${documentType}:`, error);
                setError(`Failed to upload ${documentType}: ${error.message}`);
            }
        };
        input.click();
    };

    // Process all documents and navigate to forms
    const handleProcessAndAutoFill = async () => {
        const uploadedFiles = Object.entries(uploadedDocuments).filter(([_, file]) => file !== null);
        
        if (uploadedFiles.length === 0) {
            setError('Please upload at least one document before processing.');
            return;
        }

        setIsProcessing(true);
        setError(null);
        setExtractedTexts({}); // Reset extracted texts
        setTextsExtracted(0); // Reset counter

        try {
            console.log('🚀 Starting batch OCR processing for all documents...');
            
            const batchExtractedTexts = {};
            let processedCount = 0;

            // Process each uploaded document
            for (const [documentType, file] of uploadedFiles) {
                try {
                    console.log(`🔄 Processing ${documentType}: ${file.name}`);
                    
                    const extractedData = await extractTextFromDocument(documentType, file);
                    batchExtractedTexts[documentType] = extractedData;
                    
                    processedCount++;
                    setTextsExtracted(processedCount);
                    
                    console.log(`✅ ${documentType} processed successfully`);
                } catch (error) {
                    console.error(`❌ Failed to process ${documentType}:`, error);
                    // Continue processing other documents even if one fails
                    setError(`Warning: Failed to process ${documentType}. Other documents will still be processed.`);
                }
            }

            // Update extracted texts state
            setExtractedTexts(batchExtractedTexts);

            console.log(`🎉 Batch processing completed: ${processedCount}/${uploadedFiles.length} documents processed`);
            
            // Navigate to forms page with multi-document data
            navigate('/forms', { 
                state: { 
                    multiDocumentData: batchExtractedTexts,
                    uploadedDocuments: uploadedDocuments,
                    processingDetails: {
                        ...processingDetails,
                        documents_processed: processedCount,
                        total_documents: uploadedFiles.length,
                        used_enhanced_ocr: selectedOCR === 'enhanced',
                        batch_processing: true
                    },
                    autoFillEnabled: true
                } 
            });
            
        } catch (error) {
            console.error('❌ Batch document processing failed:', error);
            setError(error.message || 'Batch document processing failed. Please try again.');
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="upload-documents-container">
            {/* Main Content */}
            <main className="main-content">
                <section className="upload-section">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                    >
                        <h2 className="upload-title">Upload Your Documents</h2>
                        <p className="upload-description">
                            Upload different types of documents. Our AI will automatically extract and combine
                            the necessary information to fill your ITR form.
                        </p>
                    </motion.div>

                    {/* Error Display */}
                    {error && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="error-banner"
                        >
                            <AlertCircle className="w-5 h-5" />
                            <span>{error}</span>
                            <button onClick={() => setError(null)}>
                                <X className="w-4 h-4" />
                            </button>
                        </motion.div>
                    )}

                    <div className="upload-cards">
                        {documentTypes.slice(0, 3).map((doc, index) => (
                            <motion.div
                                key={doc.id}
                                initial={{ opacity: 0, y: 30 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.6, delay: index * 0.1 }}
                                className="upload-card"
                            >
                                <div className="card-icon">{doc.icon}</div>
                                <h3>{doc.title}</h3>
                                <div className="card-fields">{doc.fields}</div>
                                <p>{doc.description}</p>
                                
                                {uploadedDocuments[doc.id] ? (
                                    <div className="uploaded-status">
                                        <CheckCircle className="w-4 h-4 text-green-600" />
                                        <span className="text-green-600 font-medium">
                                            {uploadedDocuments[doc.id].name}
                                        </span>
                                        <span className="text-xs text-gray-500 ml-2">
                                            (Ready for processing)
                                        </span>
                                    </div>
                                ) : (
                                    <button 
                                        className="upload-btn"
                                        onClick={() => handleUpload(doc.id)}
                                        disabled={isProcessing}
                                    >
                                        <Cloud className="w-4 h-4 mr-2" />
                                        Upload
                                    </button>
                                )}
                                
                                <small>PDF, JPG, PNG up to 10MB</small>
                            </motion.div>
                        ))}
                    </div>

                    {/* Additional Documents */}
                    {documentTypes.length > 3 && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.4 }}
                            className="additional-docs"
                        >
                            <h3 className="additional-title">Additional Documents (Optional)</h3>
                            <div className="upload-cards">
                                {documentTypes.slice(3).map((doc, index) => (
                                    <div key={doc.id} className="upload-card">
                                        <div className="card-icon">{doc.icon}</div>
                                        <h3>{doc.title}</h3>
                                        <div className="card-fields">{doc.fields}</div>
                                        <p>{doc.description}</p>
                                        
                                        {uploadedDocuments[doc.id] ? (
                                            <div className="uploaded-status">
                                                <CheckCircle className="w-4 h-4 text-green-600" />
                                                <span className="text-green-600 font-medium">
                                                    {uploadedDocuments[doc.id].name}
                                                </span>
                                                <span className="text-xs text-gray-500 ml-2">
                                                    (Ready for processing)
                                                </span>
                                            </div>
                                        ) : (
                                            <button 
                                                className="upload-btn"
                                                onClick={() => handleUpload(doc.id)}
                                                disabled={isProcessing}
                                            >
                                                <Cloud className="w-4 h-4 mr-2" />
                                                Upload
                                            </button>
                                        )}
                                        
                                        <small>PDF, JPG, PNG up to 10MB</small>
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </section>

                {/* Side Panels */}
                <div className="side-panels">
                    {/* Processing Settings */}
                    <motion.aside
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="processing-panel"
                    >
                        <div className="panel-icon">
                            <Settings className="w-6 h-6" />
                        </div>
                        <h3>Processing Settings</h3>
                        
                        <div className="ocr-selection">
                            <p className="setting-title">
                                <Zap className="w-4 h-4 mr-2" />
                                OCR Engine Selection
                            </p>
                            <label className="radio-label">
                                <input
                                    type="radio"
                                    value="basic"
                                    checked={selectedOCR === 'basic'}
                                    onChange={() => setSelectedOCR('basic')}
                                />
                                Basic OCR (EasyOCR)
                            </label>
                            <label className="radio-label">
                                <input
                                    type="radio"
                                    value="enhanced"
                                    checked={selectedOCR === 'enhanced'}
                                    onChange={() => setSelectedOCR('enhanced')}
                                />
                                Enhanced OCR (Multi-Engine)
                            </label>
                        </div>

                        <div className="smart-auto-fill">
                            <p className="setting-title">
                                <Database className="w-4 h-4 mr-2" />
                                Batch OCR Processing
                            </p>
                            <p>Upload all your documents first, then click "Start OCR & Auto-Fill" to process all documents together and intelligently merge the extracted data.</p>
                        </div>

                        <div className="panel-buttons">
                            <button 
                                className="back-btn"
                                onClick={() => navigate('/')}
                            >
                                <ArrowLeft className="w-4 h-4 mr-2" />
                                Back to Home
                            </button>
                            <button 
                                className="process-btn"
                                onClick={handleProcessAndAutoFill}
                                disabled={isProcessing || documentsUploaded === 0}
                            >
                                {isProcessing ? (
                                    <>
                                        <div className="spinner" />
                                        Processing OCR...
                                    </>
                                ) : (
                                    <>
                                        <Zap className="w-4 h-4 mr-2" />
                                        Start OCR & Auto-Fill ({documentsUploaded})
                                    </>
                                )}
                            </button>
                        </div>
                    </motion.aside>

                    {/* Upload Summary */}
                    <motion.aside
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.6, delay: 0.3 }}
                        className="summary-panel"
                    >
                        <div className="panel-icon">
                            <BarChart3 className="w-6 h-6" />
                        </div>
                        <h3>Upload Summary</h3>
                        
                        <div className="summary-stats">
                            <div className="stat">
                                <label>Documents Uploaded</label>
                                <span className="stat-value">{documentsUploaded}</span>
                            </div>
                            <div className="stat">
                                <label>Texts Extracted</label>
                                <span className="stat-value">{textsExtracted}</span>
                            </div>
                            {processingDetails.engines_used.length > 0 && (
                                <div className="stat">
                                    <label>OCR Engines Used</label>
                                    <span className="stat-value">{processingDetails.engines_used.length}</span>
                                </div>
                            )}
                        </div>

                        <div className="secure-processing">
                            <p className="security-title">
                                <Lock className="w-4 h-4 mr-2" />
                                Secure Batch Processing
                            </p>
                            <p>All documents are stored securely during upload. OCR processing begins only when you click "Start OCR & Auto-Fill" for better control and efficiency.</p>
                        </div>

                        <button 
                            className="process-btn"
                            onClick={handleProcessAndAutoFill}
                            disabled={isProcessing || documentsUploaded === 0}
                        >
                            {isProcessing ? (
                                <>
                                    <div className="spinner" />
                                    Processing OCR...
                                </>
                            ) : (
                                <>
                                    <Zap className="w-4 h-4 mr-2" />
                                    Start OCR & Auto-Fill ({documentsUploaded})
                                </>
                            )}
                        </button>
                    </motion.aside>
                </div>
            </main>
        </div>
    );
};

export default UploadNew;