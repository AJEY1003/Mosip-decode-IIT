import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { FileText, ArrowRight, ArrowLeft, Zap, Settings, Upload, Shield, Database, CheckCircle, AlertCircle, X, Cloud, Lock } from 'lucide-react';
import FileUpload from '../components/FileUpload';
import Button from '../components/Button';
import apiService from '../services/api';

const UploadPage = () => {
    const navigate = useNavigate();
    const [fileUploaded, setFileUploaded] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [error, setError] = useState(null);
    const [useEnhancedOCR, setUseEnhancedOCR] = useState(true);
    const [engineStatus, setEngineStatus] = useState(null);
    const [processingDetails, setProcessingDetails] = useState(null);

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

    const handleUpload = (file) => {
        setSelectedFile(file);
        setFileUploaded(true);
        setError(null);
        setProcessingDetails(null);
        
        // Check file size and show warning
        const fileSizeMB = file.size / (1024 * 1024);
        if (fileSizeMB > 15) {
            setError(`Large file detected (${fileSizeMB.toFixed(1)}MB). Processing may take longer and the file will be compressed automatically.`);
        } else if (fileSizeMB > 25) {
            setError(`File is very large (${fileSizeMB.toFixed(1)}MB). Please consider reducing the file size or number of pages for better performance.`);
        }
    };

    const handleProcess = async () => {
        if (!selectedFile) return;

        setIsProcessing(true);
        setError(null);
        setProcessingDetails(null);

        try {
            console.log(`🔍 Starting ${useEnhancedOCR ? 'Enhanced' : 'Basic'} OCR processing...`);
            
            let data;
            if (useEnhancedOCR) {
                // Use Enhanced OCR with multiple engines
                data = await apiService.enhancedExtractText(selectedFile, 'ITR Document', true);
                console.log('✅ Enhanced OCR processing successful:', data);
                
                // Store processing details for display
                setProcessingDetails({
                    engines_used: data.engines_used || [],
                    confidence_score: data.confidence_score || 0,
                    processing_time: data.processing_time || 0,
                    selected_engine: data.processing_details?.selected_engine || 'unknown'
                });
            } else {
                // Use basic OCR
                data = await apiService.extractText(selectedFile, 'ITR Document');
                console.log('✅ Basic OCR processing successful:', data);
            }
            
            // Navigate to forms page with extracted data
            navigate('/forms', { 
                state: { 
                    extractedData: data,
                    originalFile: selectedFile,
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
        <div className="min-h-screen bg-gradient-to-br from-background via-[hsl(var(--muted))]/30 to-background">
            {/* Hero Section */}
            <div className="relative pt-24 pb-16 overflow-hidden">
                {/* Background Elements */}
                <div className="absolute inset-0">
                    <div className="absolute top-20 left-20 w-72 h-72 bg-[hsl(var(--gov-green))]/5 rounded-full blur-3xl animate-pulse" />
                    <div className="absolute bottom-20 right-20 w-96 h-96 bg-[hsl(var(--gov-gold))]/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
                </div>

                <div className="container mx-auto px-6 sm:px-8 lg:px-12 relative z-10">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="text-center mb-16"
                    >
                        <div className="inline-flex items-center gap-3 mb-6">
                            <div className="w-3 h-3 bg-[hsl(var(--gov-green))] rounded-full animate-pulse" />
                            <span className="text-sm font-semibold text-[hsl(var(--muted-foreground))]">
                                Secure Document Upload
                            </span>
                            <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
                        </div>
                        
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-[hsl(var(--foreground))]">
                            Upload Your Documents
                        </h1>
                        
                        <p className="text-xl text-[hsl(var(--muted-foreground))] leading-relaxed max-w-3xl mx-auto">
                            Securely upload your ITR documents for processing. We support PDF, JPG, PNG formats with advanced OCR technology.
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
                                <div className="w-16 h-16 bg-[hsl(var(--gov-green))]/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                    <feature.icon className="w-8 h-8 text-[hsl(var(--gov-green))]" />
                                </div>
                                <h3 className="text-lg font-semibold text-[hsl(var(--foreground))] mb-2">{feature.title}</h3>
                                <p className="text-[hsl(var(--muted-foreground))] text-sm">{feature.description}</p>
                            </div>
                        ))}
                    </motion.div>
                </div>
            </div>

            {/* Main Content */}
            <div className="container mx-auto px-6 sm:px-8 lg:px-12 pb-20">
                <div className="grid lg:grid-cols-2 gap-12 items-start">
                    
                    {/* Upload Section */}
                    <motion.div
                        initial={{ opacity: 0, x: -40 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.6, delay: 0.3 }}
                        className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))]"
                    >
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-10 h-10 bg-[hsl(var(--gov-green))] rounded-xl flex items-center justify-center">
                                <Upload className="w-5 h-5 text-white" />
                            </div>
                            <h2 className="text-2xl font-bold text-[hsl(var(--foreground))]">Upload Documents</h2>
                        </div>
                        
                        <FileUpload
                            onUpload={handleUpload}
                            helperText="Supports PDF, JPG, PNG files up to 10MB"
                        />

                        {/* OCR Engine Selection */}
                        <motion.div
                            className="mt-6 p-4 bg-[hsl(var(--muted))]/30 rounded-xl border border-[hsl(var(--border))]"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <h4 className="flex items-center gap-2 text-sm font-semibold text-[hsl(var(--foreground))] mb-4">
                                <Settings className="w-4 h-4" />
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
                                        <span className="text-[hsl(var(--foreground))]">Enhanced OCR (Tesseract + EasyOCR + TrOCR)</span>
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
                        </motion.div>

                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="mt-6 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3"
                            >
                                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                                <span className="text-red-700 text-sm">{error}</span>
                            </motion.div>
                        )}

                        {/* Processing Details */}
                        {processingDetails && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="mt-6 bg-green-50 border border-green-200 rounded-xl p-4"
                            >
                                <div className="flex items-center gap-2 text-green-700 font-semibold mb-3">
                                    <CheckCircle className="w-5 h-5" />
                                    Processing Complete
                                </div>
                                <div className="space-y-1 text-sm text-green-600">
                                    <div>Engines Used: {processingDetails.engines_used.join(', ')}</div>
                                    <div>Confidence: {(processingDetails.confidence_score * 100).toFixed(1)}%</div>
                                    <div>Processing Time: {processingDetails.processing_time.toFixed(2)}s</div>
                                    <div>Selected Engine: {processingDetails.selected_engine}</div>
                                </div>
                            </motion.div>
                        )}

                        {/* Security Notice */}
                        <div className="mt-6 bg-[hsl(var(--gov-green))]/5 border border-[hsl(var(--gov-green))]/20 rounded-xl p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Lock className="w-4 h-4 text-[hsl(var(--gov-green))]" />
                                <span className="text-sm font-semibold text-[hsl(var(--gov-green))]">Secure Upload</span>
                            </div>
                            <p className="text-xs text-[hsl(var(--muted-foreground))]">
                                All files are encrypted during upload and processing. Your data is protected with bank-grade security.
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
                                onClick={handleProcess}
                                disabled={!fileUploaded || isProcessing}
                                className="flex-1 bg-[hsl(var(--gov-green))] hover:bg-[hsl(var(--gov-green-dark))] text-white font-semibold py-3 px-6 rounded-xl flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isProcessing ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Processing...
                                    </>
                                ) : (
                                    <>
                                        {useEnhancedOCR ? <Zap className="w-4 h-4" /> : <ArrowRight className="w-4 h-4" />}
                                        {useEnhancedOCR ? "Enhanced Process" : "Process Document"}
                                    </>
                                )}
                            </Button>
                        </div>
                    </motion.div>

                    {/* File Status Section */}
                    <motion.div
                        initial={{ opacity: 0, x: 40 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.6, delay: 0.4 }}
                        className="space-y-6"
                    >
                        {selectedFile ? (
                            <div className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))]">
                                <div className="flex items-center gap-3 mb-6">
                                    <div className="w-10 h-10 bg-[hsl(var(--gov-gold))] rounded-xl flex items-center justify-center">
                                        <FileText className="w-5 h-5 text-white" />
                                    </div>
                                    <h3 className="text-xl font-bold text-[hsl(var(--foreground))]">Selected File</h3>
                                </div>
                                
                                <div className="flex items-center justify-between p-4 bg-[hsl(var(--muted))]/30 rounded-xl border border-[hsl(var(--border))]">
                                    <div className="flex items-center gap-4">
                                        <div className="w-12 h-12 bg-[hsl(var(--gov-green))]/10 rounded-xl flex items-center justify-center">
                                            <FileText className="w-6 h-6 text-[hsl(var(--gov-green))]" />
                                        </div>
                                        <div>
                                            <p className="font-medium text-[hsl(var(--foreground))]">{selectedFile.name}</p>
                                            <p className="text-sm text-[hsl(var(--muted-foreground))]">
                                                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                                            </p>
                                        </div>
                                    </div>
                                    
                                    <div className="flex items-center gap-2 text-green-600">
                                        <CheckCircle className="w-5 h-5" />
                                        <span className="text-sm font-medium">Ready</span>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))] text-center">
                                <div className="w-16 h-16 bg-[hsl(var(--muted))] rounded-2xl flex items-center justify-center mx-auto mb-4">
                                    <Cloud className="w-8 h-8 text-[hsl(var(--muted-foreground))]" />
                                </div>
                                <h3 className="text-lg font-semibold text-[hsl(var(--foreground))] mb-2">No File Selected</h3>
                                <p className="text-[hsl(var(--muted-foreground))] text-sm">
                                    Upload your ITR documents to get started with processing
                                </p>
                            </div>
                        )}

                        {/* Quick Actions */}
                        <div className="bg-gradient-to-r from-[hsl(var(--gov-green))] to-[hsl(var(--gov-green-light))] rounded-2xl p-6 text-white">
                            <h4 className="font-bold text-lg mb-2">Supported Formats</h4>
                            <p className="opacity-90 mb-4 text-sm">
                                We support multiple document formats for maximum compatibility
                            </p>
                            <div className="flex flex-wrap gap-2">
                                <span className="bg-white/20 px-3 py-1 rounded-full text-xs font-medium">PDF</span>
                                <span className="bg-white/20 px-3 py-1 rounded-full text-xs font-medium">JPG</span>
                                <span className="bg-white/20 px-3 py-1 rounded-full text-xs font-medium">PNG</span>
                                <span className="bg-white/20 px-3 py-1 rounded-full text-xs font-medium">Max 10MB</span>
                            </div>
                        </div>
                    </motion.div>
                </div>
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
        </div>
    );
};

export default UploadPage;
