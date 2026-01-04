import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
    FileText, ArrowRight, ArrowLeft, Zap, Settings, Upload, Shield, Database, 
    CheckCircle, AlertCircle, X, Cloud, Lock, CreditCard, Building, User, 
    Receipt, DollarSign, FileCheck, Sparkles, Star, TrendingUp, Activity,
    QrCode, Download, Copy
} from 'lucide-react';
import FileUpload from '../components/FileUpload';
import Button from '../components/Button';
import apiService from '../services/api';

const UploadPage = () => {
    const navigate = useNavigate();
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState(null);
    const [useEnhancedOCR, setUseEnhancedOCR] = useState(true);
    const [engineStatus, setEngineStatus] = useState(null);
    const [processingDetails, setProcessingDetails] = useState(null);
    const [extractedTexts, setExtractedTexts] = useState({});
    const [combinedData, setCombinedData] = useState(null);
    const [qrCodeData, setQrCodeData] = useState(null);
    const [showQRCode, setShowQRCode] = useState(false);
    
    // Multi-document state
    const [uploadedDocuments, setUploadedDocuments] = useState({
        aadhaar: null,
        form16: null,
        preregistration: null,
        bankSlip: null,
        incomeDetails: null
    });

    // Document type configurations
    const documentTypes = [
        {
            key: 'aadhaar',
            title: 'Aadhaar Card',
            icon: User,
            description: 'Upload your Aadhaar card for identity verification',
            color: 'blue',
            fields: ['name', 'aadhaar', 'date_of_birth', 'address', 'pincode']
        },
        {
            key: 'form16',
            title: 'Form 16',
            icon: FileText,
            description: 'Upload Form 16 from your employer',
            color: 'green',
            fields: ['name', 'pan', 'employer', 'gross_salary', 'tds_deducted', 'financial_year']
        },
        {
            key: 'preregistration',
            title: 'Pre-registration Form',
            icon: FileCheck,
            description: 'Upload your ITR pre-registration form',
            color: 'purple',
            fields: ['name', 'pan', 'email', 'mobile', 'assessment_year']
        },
        {
            key: 'bankSlip',
            title: 'Bank Statement',
            icon: CreditCard,
            description: 'Upload bank statement or salary slip',
            color: 'orange',
            fields: ['account_number', 'ifsc', 'bank_name', 'gross_salary']
        },
        {
            key: 'incomeDetails',
            title: 'Income Details',
            icon: DollarSign,
            description: 'Upload additional income documents',
            color: 'emerald',
            fields: ['total_income', 'other_income', 'deductions']
        }
    ];

    // Check enhanced OCR status on component mount
    useEffect(() => {
        checkEnhancedOCRStatus();
    }, []);

    const checkEnhancedOCRStatus = async () => {
        try {
            const status = await apiService.getEnhancedOCRStatus();
            setEngineStatus(status);
            console.log('🔧 Enhanced OCR Status:', status);
        } catch (error) {
            console.error('Failed to check enhanced OCR status:', error);
        }
    };

    // Handle individual document upload
    const handleDocumentUpload = (documentType, file) => {
        setUploadedDocuments(prev => ({
            ...prev,
            [documentType]: file
        }));
        setError(null);
        
        // Check file size and show warning
        const fileSizeMB = file.size / (1024 * 1024);
        if (fileSizeMB > 15) {
            setError(`Large file detected (${fileSizeMB.toFixed(1)}MB). Processing may take longer.`);
        }
    };

    // Remove uploaded document
    const removeDocument = (documentType) => {
        setUploadedDocuments(prev => ({
            ...prev,
            [documentType]: null
        }));
        
        // Remove extracted text for this document
        setExtractedTexts(prev => {
            const newTexts = { ...prev };
            delete newTexts[documentType];
            return newTexts;
        });
    };

    // Extract text from individual document
    const extractTextFromDocument = async (documentType, file) => {
        try {
            console.log(`🔍 Extracting text from ${documentType}...`);
            
            let data;
            if (useEnhancedOCR) {
                console.log('🚀 Using Enhanced OCR...');
                data = await apiService.enhancedExtractText(file, `${documentType} Document`, true);
            } else {
                console.log('🔧 Using Standard OCR...');
                data = await apiService.extractText(file, `${documentType} Document`);
            }
            
            // Debug the API response
            console.log(`✅ API Response from ${documentType}:`, data);
            console.log(`📋 Structured data:`, data?.extracted_data?.structured_data);
            console.log(`📝 Raw text:`, data?.extracted_data?.raw_text?.substring(0, 100) + '...');
            
            // Store extracted text
            setExtractedTexts(prev => ({
                ...prev,
                [documentType]: data
            }));
            
            console.log(`✅ Text extracted from ${documentType}:`, data);
            return data;
            
        } catch (error) {
            console.error(`❌ Failed to extract text from ${documentType}:`, error);
            throw error;
        }
    };

    // Combine all extracted texts and apply NER
    const combineAndProcessTexts = async () => {
        try {
            console.log('🔄 Combining extracted texts and applying NER...');
            
            // Combine all extracted texts
            const allTexts = Object.values(extractedTexts)
                .map(data => data.extracted_text || data.text || '')
                .join('\n\n');
            
            console.log('📝 Combined text length:', allTexts.length);
            
            // Apply NER to combined text
            const nerResults = await apiService.extractNER(allTexts);
            console.log('🎯 NER Results:', nerResults);
            
            // Create combined data structure
            const combined = {
                combined_text: allTexts,
                ner_results: nerResults,
                document_sources: Object.keys(extractedTexts),
                individual_extractions: extractedTexts,
                processing_details: {
                    total_documents: Object.keys(extractedTexts).length,
                    combined_text_length: allTexts.length,
                    ner_entities_found: nerResults?.entities?.length || 0
                }
            };
            
            setCombinedData(combined);
            return combined;
            
        } catch (error) {
            console.error('❌ Failed to combine and process texts:', error);
            throw error;
        }
    };

    // Generate QR code from extracted documents
    const generateQRCode = async () => {
        try {
            console.log('🔄 Generating QR code from extracted documents...');
            
            // Generate QR code with all document data
            const qrResult = await apiService.generateDocumentsQR(extractedTexts);
            console.log('✅ QR Code generated:', qrResult);
            
            return qrResult;
            
        } catch (error) {
            console.error('❌ Failed to generate QR code:', error);
            throw error;
        }
    };

    // Process all uploaded documents
    const handleProcessAllDocuments = async () => {
        const uploadedFiles = Object.entries(uploadedDocuments).filter(([_, file]) => file !== null);
        
        if (uploadedFiles.length === 0) {
            setError('Please upload at least one document before processing.');
            return;
        }

        setIsProcessing(true);
        setError(null);
        setExtractedTexts({});
        setCombinedData(null);
        setQrCodeData(null);

        try {
            console.log(`🚀 Processing ${uploadedFiles.length} documents...`);
            
            // Extract text from all uploaded documents
            const extractionPromises = uploadedFiles.map(async ([docType, file]) => {
                return await extractTextFromDocument(docType, file);
            });
            
            // Wait for all extractions to complete
            await Promise.all(extractionPromises);
            
            // Combine texts and apply NER
            const combinedResult = await combineAndProcessTexts();
            
            // Generate QR code with extracted data
            const qrResult = await generateQRCode();
            setQrCodeData(qrResult);
            setShowQRCode(true);
            
            console.log('✅ All processing completed successfully');
            
        } catch (error) {
            console.error('❌ Document processing failed:', error);
            setError(error.message || 'Document processing failed. Please try again.');
        } finally {
            setIsProcessing(false);
        }
    };

    // Legacy single file upload handler (for backward compatibility)
    const handleUpload = (file) => {
        // For backward compatibility, treat single upload as form16
        handleDocumentUpload('form16', file);
    };

    // Legacy process handler (for backward compatibility)
    const handleProcess = async () => {
        const form16File = uploadedDocuments.form16;
        if (!form16File) return;

        setIsProcessing(true);
        setError(null);

        try {
            const data = await extractTextFromDocument('form16', form16File);
            
            console.log('🚀 Navigating to Forms page with data:', data);
            console.log('📋 Data structure check:', {
                hasExtractedData: !!data?.extracted_data,
                hasStructuredData: !!data?.extracted_data?.structured_data,
                structuredDataKeys: data?.extracted_data?.structured_data ? Object.keys(data.extracted_data.structured_data) : [],
                hasRawText: !!data?.extracted_data?.raw_text,
                rawTextLength: data?.extracted_data?.raw_text?.length || 0
            });
            
            // Navigate to forms page with single document data
            navigate('/forms', { 
                state: { 
                    extractedData: data,
                    originalFile: form16File,
                    processingDetails: processingDetails,
                    usedEnhancedOCR: useEnhancedOCR
                } 
            });
            
        } catch (error) {
            console.error('❌ OCR processing failed:', error);
            setError(error.message || 'OCR processing failed. Please try again.');
        } finally {
            setIsProcessing(false);
        }
    };

    // Get color classes for document types
    const getColorClasses = (color) => {
        const colors = {
            blue: 'bg-blue-500/10 text-blue-600 border-blue-200',
            green: 'bg-green-500/10 text-green-600 border-green-200',
            purple: 'bg-purple-500/10 text-purple-600 border-purple-200',
            orange: 'bg-orange-500/10 text-orange-600 border-orange-200',
            emerald: 'bg-emerald-500/10 text-emerald-600 border-emerald-200'
        };
        return colors[color] || colors.blue;
    };

    // Check if any documents are uploaded
    const hasUploadedDocuments = Object.values(uploadedDocuments).some(file => file !== null);
    const uploadedCount = Object.values(uploadedDocuments).filter(file => file !== null).length;

    const features = [
        {
            icon: Shield,
            title: "Bank-Grade Security",
            description: "Your documents are encrypted with 256-bit SSL encryption"
        },
        {
            icon: Zap,
            title: "Lightning Fast",
            description: "Process documents in under 2 minutes with 99.9% accuracy"
        },
        {
            icon: Database,
            title: "Smart Extraction",
            description: "AI-powered data extraction from multiple document formats"
        }
    ];

    return (
    <div className="relative min-h-screen w-full overflow-hidden">
        {/* Dark gradient background with texture */}
        <div className="absolute inset-0 bg-gradient-to-br from-[hsl(var(--gov-navy))] via-[hsl(var(--gov-green-dark))] to-[hsl(var(--gov-green))]" />
        
        {/* Subtle grid pattern */}
        <div 
            className="absolute inset-0 opacity-[0.03]"
            style={{
                backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
                backgroundSize: '40px 40px'
            }}
        />
        
        {/* Radial glow accent */}
        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-[hsl(var(--gov-gold))] opacity-[0.08] blur-[150px] rounded-full -translate-y-1/2 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-[hsl(var(--gov-green-light))] opacity-[0.1] blur-[120px] rounded-full translate-y-1/2 -translate-x-1/3" />

        <div className="relative z-10">
            {/* Hero Section */}
            <div className="pt-24 pb-16 overflow-hidden">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="text-center mb-16"
                    >
                        <div className="inline-flex items-center gap-3 mb-6">
                            <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
                            <span className="text-sm font-semibold text-white/70">
                                Secure Document Upload
                            </span>
                            <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
                        </div>
                        
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-white">
                            Multi-Document Upload
                        </h1>
                        
                        <p className="text-xl text-white/80 leading-relaxed max-w-3xl mx-auto">
                            Upload multiple documents for automatic form filling. Our AI will extract and combine data from all your documents.
                        </p>
                    </motion.div>

                    {/* Features */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="grid md:grid-cols-3 gap-8 mb-16"
                    >
                        {features.map((feature, index) => (
                            <div key={index} className="text-center">
                                <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/20">
                                    <feature.icon className="w-8 h-8 text-[hsl(var(--gov-gold))]" />
                                </div>
                                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                                <p className="text-white/70 text-sm">{feature.description}</p>
                            </div>
                        ))}
                    </motion.div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
                {/* Document Upload Grid */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.3 }}
                    className="mb-12"
                >
                    <div className="text-center mb-8">
                        <h2 className="text-3xl font-bold text-white mb-4">Upload Your Documents</h2>
                        <p className="text-white/70 max-w-2xl mx-auto">
                            Upload different types of documents. Our AI will automatically extract and combine relevant information to fill your ITR form.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {documentTypes.map((docType, index) => (
                            <motion.div
                                key={docType.key}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                className="bg-white rounded-2xl p-6 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))] relative overflow-hidden"
                            >
                                {/* Sparkle effects */}
                                <div className="absolute inset-0 pointer-events-none">
                                    {[...Array(3)].map((_, i) => (
                                        <motion.div
                                            key={i}
                                            className="absolute"
                                            initial={{ opacity: 0, scale: 0 }}
                                            animate={{ 
                                                opacity: [0, 1, 0], 
                                                scale: [0, 1, 0],
                                                x: Math.random() * 200,
                                                y: Math.random() * 200
                                            }}
                                            transition={{ 
                                                duration: 2, 
                                                delay: i * 0.5 + index * 0.2, 
                                                repeat: Infinity, 
                                                repeatDelay: 3 
                                            }}
                                        >
                                            <Star className="w-3 h-3 text-yellow-400 fill-current" />
                                        </motion.div>
                                    ))}
                                </div>

                                <div className="relative z-10">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${getColorClasses(docType.color)}`}>
                                            <docType.icon className="w-6 h-6" />
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-bold text-[hsl(var(--foreground))]">{docType.title}</h3>
                                            <div className="flex flex-wrap gap-1 mt-1">
                                                {docType.fields.slice(0, 3).map(field => (
                                                    <span key={field} className="text-xs bg-gray-100 px-2 py-1 rounded-full text-gray-600">
                                                        {field.replace(/_/g, ' ')}
                                                    </span>
                                                ))}
                                                {docType.fields.length > 3 && (
                                                    <span className="text-xs text-gray-500">+{docType.fields.length - 3} more</span>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    <p className="text-sm text-[hsl(var(--muted-foreground))] mb-4">
                                        {docType.description}
                                    </p>

                                    {uploadedDocuments[docType.key] ? (
                                        <div className="space-y-3">
                                            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                                                <div className="flex items-center gap-3">
                                                    <CheckCircle className="w-5 h-5 text-green-600" />
                                                    <div>
                                                        <p className="font-medium text-green-800 text-sm">
                                                            {uploadedDocuments[docType.key].name}
                                                        </p>
                                                        <p className="text-xs text-green-600">
                                                            {(uploadedDocuments[docType.key].size / 1024 / 1024).toFixed(2)} MB
                                                        </p>
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={() => removeDocument(docType.key)}
                                                    className="p-1 hover:bg-green-100 rounded-full transition-colors"
                                                >
                                                    <X className="w-4 h-4 text-green-600" />
                                                </button>
                                            </div>
                                            
                                            {extractedTexts[docType.key] && (
                                                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                                                    <div className="flex items-center gap-2 text-blue-700 text-sm font-medium">
                                                        <Sparkles className="w-4 h-4" />
                                                        Text Extracted Successfully
                                                    </div>
                                                    <p className="text-xs text-blue-600 mt-1">
                                                        {extractedTexts[docType.key].extracted_text?.length || 0} characters extracted
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <FileUpload
                                            onUpload={(file) => handleDocumentUpload(docType.key, file)}
                                            helperText="PDF, JPG, PNG up to 10MB"
                                            compact={true}
                                        />
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>

                {/* Processing Controls */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.5 }}
                    className="grid lg:grid-cols-2 gap-8"
                >
                    {/* OCR Settings */}
                    <div className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))]">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-10 h-10 bg-[hsl(var(--gov-green))] rounded-xl flex items-center justify-center">
                                <Settings className="w-5 h-5 text-white" />
                            </div>
                            <h3 className="text-2xl font-bold text-[hsl(var(--foreground))]">Processing Settings</h3>
                        </div>

                        {/* OCR Engine Selection */}
                        <div className="mb-6 p-4 bg-[hsl(var(--muted))]/30 rounded-xl border border-[hsl(var(--border))]">
                            <h4 className="flex items-center gap-2 text-sm font-semibold text-[hsl(var(--foreground))] mb-4">
                                <Zap className="w-4 h-4" />
                                OCR Engine Selection
                            </h4>
                            
                            <div className="space-y-3">
                                <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-[hsl(var(--muted))]/50 transition-colors">
                                    <input
                                        type="radio"
                                        name="ocrType"
                                        checked={!useEnhancedOCR}
                                        onChange={() => setUseEnhancedOCR(false)}
                                        className="w-4 h-4 text-[hsl(var(--gov-green))]"
                                    />
                                    <span className="text-[hsl(var(--foreground))]">Basic OCR (EasyOCR)</span>
                                </label>
                                
                                <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-[hsl(var(--muted))]/50 transition-colors">
                                    <input
                                        type="radio"
                                        name="ocrType"
                                        checked={useEnhancedOCR}
                                        onChange={() => setUseEnhancedOCR(true)}
                                        className="w-4 h-4 text-[hsl(var(--gov-green))]"
                                    />
                                    <div className="flex items-center gap-2">
                                        <Zap className="w-4 h-4 text-[hsl(var(--gov-gold))]" />
                                        <span className="text-[hsl(var(--foreground))]">Enhanced OCR (Multi-Engine)</span>
                                    </div>
                                </label>
                            </div>

                            {/* Engine Status Display */}
                            {engineStatus && (
                                <div className="mt-4 p-3 bg-[hsl(var(--gov-green))]/5 rounded-lg border border-[hsl(var(--gov-green))]/20">
                                    <div className="text-xs text-[hsl(var(--muted-foreground))] mb-2">
                                        Available Engines: {engineStatus.summary?.available_engines || 0}/{engineStatus.summary?.total_engines || 0}
                                    </div>
                                    {useEnhancedOCR && (
                                        <div className="flex flex-wrap gap-2">
                                            {Object.entries(engineStatus.engines || {}).map(([engine, info]) => (
                                                <span key={engine} className="text-xs px-2 py-1 rounded-full bg-white/50 flex items-center gap-1">
                                                    {info.available ? '✅' : '❌'} {engine}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Auto-fill Information */}
                        <div className="p-4 bg-gradient-to-r from-[hsl(var(--gov-green))]/10 to-[hsl(var(--gov-gold))]/10 rounded-xl border border-[hsl(var(--gov-green))]/20">
                            <div className="flex items-center gap-2 mb-2">
                                <TrendingUp className="w-5 h-5 text-[hsl(var(--gov-green))]" />
                                <span className="font-semibold text-[hsl(var(--gov-green))]">Smart Auto-Fill</span>
                            </div>
                            <p className="text-sm text-[hsl(var(--muted-foreground))]">
                                Our AI will automatically extract and combine data from all uploaded documents to fill your ITR form intelligently.
                            </p>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex gap-4 mt-8">
                            <Button
                                onClick={() => navigate('/')}
                                className="flex-1 bg-white text-[hsl(var(--foreground))] border-2 border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))] font-semibold py-3 px-6 rounded-xl flex items-center justify-center gap-2 transition-all"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                Back to Home
                            </Button>

                            <Button
                                onClick={handleProcessAllDocuments}
                                disabled={!hasUploadedDocuments || isProcessing}
                                className="flex-1 bg-[hsl(var(--gov-green))] hover:bg-[hsl(var(--gov-green-dark))] text-white font-semibold py-3 px-6 rounded-xl flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isProcessing ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Processing...
                                    </>
                                ) : (
                                    <>
                                        <Activity className="w-4 h-4" />
                                        Process & Auto-Fill ({uploadedCount})
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>

                    {/* Upload Status */}
                    <div className="space-y-6">
                        {/* Upload Summary */}
                        <div className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))]">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="w-10 h-10 bg-[hsl(var(--gov-gold))] rounded-xl flex items-center justify-center">
                                    <FileText className="w-5 h-5 text-white" />
                                </div>
                                <h3 className="text-xl font-bold text-[hsl(var(--foreground))]">Upload Summary</h3>
                            </div>
                            
                            <div className="space-y-4">
                                <div className="flex justify-between items-center p-4 bg-[hsl(var(--muted))]/30 rounded-xl">
                                    <span className="text-[hsl(var(--foreground))] font-medium">Documents Uploaded</span>
                                    <span className="text-2xl font-bold text-[hsl(var(--gov-green))]">{uploadedCount}</span>
                                </div>
                                
                                <div className="flex justify-between items-center p-4 bg-[hsl(var(--muted))]/30 rounded-xl">
                                    <span className="text-[hsl(var(--foreground))] font-medium">Texts Extracted</span>
                                    <span className="text-2xl font-bold text-[hsl(var(--gov-gold))]">{Object.keys(extractedTexts).length}</span>
                                </div>

                                {combinedData && (
                                    <div className="p-4 bg-green-50 rounded-xl border border-green-200">
                                        <div className="flex items-center gap-2 text-green-700 font-semibold mb-2">
                                            <CheckCircle className="w-5 h-5" />
                                            Ready for Auto-Fill
                                        </div>
                                        <div className="text-sm text-green-600">
                                            <div>Combined Text: {combinedData.combined_text.length} characters</div>
                                            <div>NER Entities: {combinedData.ner_results?.entities?.length || 0}</div>
                                        </div>
                                    </div>
                                )}

                                {qrCodeData && (
                                    <div className="p-4 bg-blue-50 rounded-xl border border-blue-200">
                                        <div className="flex items-center gap-2 text-blue-700 font-semibold mb-3">
                                            <QrCode className="w-5 h-5" />
                                            ITR QR Code Generated
                                        </div>
                                        <div className="text-sm text-blue-600 mb-3">
                                            <div>Taxpayer: {qrCodeData.analysis_summary?.taxpayer_name}</div>
                                            <div>Total Income: ₹{qrCodeData.analysis_summary?.total_income?.toLocaleString()}</div>
                                            <div>Expected Refund: ₹{qrCodeData.analysis_summary?.refund_amount?.toLocaleString()}</div>
                                        </div>
                                        <div className="flex gap-2">
                                            <Button
                                                onClick={() => setShowQRCode(true)}
                                                className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-lg"
                                            >
                                                <QrCode className="w-3 h-3 mr-1" />
                                                View QR Code
                                            </Button>
                                            <Button
                                                onClick={() => navigate('/itr-filing')}
                                                className="text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded-lg"
                                            >
                                                <ArrowRight className="w-3 h-3 mr-1" />
                                                Go to ITR Filing
                                            </Button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Processing Status */}
                        {hasUploadedDocuments && (
                            <div className="bg-gradient-to-r from-[hsl(var(--gov-green))] to-[hsl(var(--gov-green-light))] rounded-2xl p-6 text-white">
                                <h4 className="font-bold text-lg mb-2">Ready to Process</h4>
                                <p className="opacity-90 mb-4 text-sm">
                                    {uploadedCount} document{uploadedCount !== 1 ? 's' : ''} ready for intelligent processing and auto-fill
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    {Object.entries(uploadedDocuments)
                                        .filter(([_, file]) => file !== null)
                                        .map(([docType, _]) => (
                                            <span key={docType} className="bg-white/20 px-3 py-1 rounded-full text-xs font-medium">
                                                {documentTypes.find(dt => dt.key === docType)?.title}
                                            </span>
                                        ))}
                                </div>
                            </div>
                        )}

                        {/* Security Notice */}
                        <div className="bg-[hsl(var(--gov-green))]/5 border border-[hsl(var(--gov-green))]/20 rounded-xl p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Lock className="w-4 h-4 text-[hsl(var(--gov-green))]" />
                                <span className="text-sm font-semibold text-[hsl(var(--gov-green))]">Secure Multi-Document Processing</span>
                            </div>
                            <p className="text-xs text-[hsl(var(--muted-foreground))]">
                                All documents are encrypted during upload and processing. Data is combined intelligently while maintaining security.
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* Error Display */}
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-8 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3 max-w-4xl mx-auto"
                    >
                        <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                        <span className="text-red-700 text-sm">{error}</span>
                    </motion.div>
                )}
            </div>

            {/* Processing Overlay */}
            <AnimatePresence>
                {isProcessing && (
                    <motion.div
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        <motion.div
                            className="bg-white rounded-2xl p-8 max-w-md mx-4 text-center shadow-2xl"
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                        >
                            <div className="w-16 h-16 bg-[hsl(var(--gov-green))]/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                <motion.div
                                    className="w-8 h-8 border-3 border-[hsl(var(--gov-green))]/30 border-t-[hsl(var(--gov-green))] rounded-full"
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                />
                            </div>
                            <h3 className="text-xl font-bold text-[hsl(var(--foreground))] mb-2">Processing Document</h3>
                            <p className="text-[hsl(var(--muted-foreground))] mb-4">
                                {useEnhancedOCR 
                                    ? "Analyzing document with Enhanced OCR (Multiple Engines)..." 
                                    : "Analyzing document with OCR..."
                                }
                            </p>
                            <div className="text-xs text-[hsl(var(--muted-foreground))]">
                                <div>Connecting to backend at http://127.0.0.1:5000</div>
                                {useEnhancedOCR && (
                                    <div className="mt-2 text-[hsl(var(--gov-gold))]">
                                        Using Tesseract + EasyOCR + TrOCR for maximum accuracy
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* QR Code Modal */}
            <AnimatePresence>
                {showQRCode && qrCodeData && (
                    <motion.div
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setShowQRCode(false)}
                    >
                        <motion.div
                            className="bg-white rounded-2xl p-8 max-w-md w-full text-center shadow-2xl"
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-xl font-bold text-[hsl(var(--foreground))]">ITR QR Code</h3>
                                <button
                                    onClick={() => setShowQRCode(false)}
                                    className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            {/* QR Code Image */}
                            <div className="mb-6">
                                <img 
                                    src={qrCodeData.qr_code?.qr_image} 
                                    alt="ITR QR Code"
                                    className="w-64 h-64 mx-auto border-2 border-gray-200 rounded-lg"
                                />
                            </div>

                            {/* QR Code Summary */}
                            <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left">
                                <h4 className="font-semibold text-gray-800 mb-2">ITR Summary</h4>
                                <div className="space-y-1 text-sm text-gray-600">
                                    <div className="flex justify-between">
                                        <span>Taxpayer:</span>
                                        <span className="font-medium">{qrCodeData.analysis_summary?.taxpayer_name}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Total Income:</span>
                                        <span className="font-medium">₹{qrCodeData.analysis_summary?.total_income?.toLocaleString()}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Tax Regime:</span>
                                        <span className="font-medium">{qrCodeData.analysis_summary?.recommended_regime?.toUpperCase()}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Expected Refund:</span>
                                        <span className="font-medium text-green-600">₹{qrCodeData.analysis_summary?.refund_amount?.toLocaleString()}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex gap-3">
                                <Button
                                    onClick={() => {
                                        const link = document.createElement('a');
                                        link.href = qrCodeData.qr_code?.qr_image;
                                        link.download = 'itr-qr-code.png';
                                        link.click();
                                    }}
                                    className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg flex items-center justify-center gap-2"
                                >
                                    <Download className="w-4 h-4" />
                                    Download
                                </Button>
                                <Button
                                    onClick={() => {
                                        navigator.clipboard.writeText(qrCodeData.qr_code?.qr_data);
                                        alert('QR data copied to clipboard!');
                                    }}
                                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg flex items-center justify-center gap-2"
                                >
                                    <Copy className="w-4 h-4" />
                                    Copy Data
                                </Button>
                                <Button
                                    onClick={() => {
                                        setShowQRCode(false);
                                        navigate('/itr-filing');
                                    }}
                                    className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg flex items-center justify-center gap-2"
                                >
                                    <ArrowRight className="w-4 h-4" />
                                    File ITR
                                </Button>
                            </div>

                            <p className="text-xs text-gray-500 mt-4">
                                Use this QR code in the ITR Filing section to auto-fill your tax return form.
                            </p>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    </div>
    );
};

export default UploadPage;
