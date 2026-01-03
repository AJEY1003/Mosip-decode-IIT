import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowRight, CheckCircle, CreditCard, Download, Shield, Zap, Database, AlertCircle, TrendingUp, Lock, Eye } from 'lucide-react';
import ValidationStatus from '../components/ValidationStatus';
import SimpleQR from '../components/SimpleQR';
import Button from '../components/Button';
import apiService from '../services/api';
import QRCodeLib from 'qrcode';

const ValidationPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [isVerifying, setIsVerifying] = useState(false);
    const [verified, setVerified] = useState(false);
    const [isGeneratingQR, setIsGeneratingQR] = useState(false);
    const [qrData, setQrData] = useState(null);
    const [qrImageData, setQrImageData] = useState(null);
    const qrImageRef = useRef(null);
    const [signedQR, setSignedQR] = useState(null);
    const [validationScore, setValidationScore] = useState(85);
    const [error, setError] = useState(null);

    // Get extracted data from previous page
    const extractedData = location.state?.extractedData?.extracted_data?.structured_data || {};
    const rawText = location.state?.extractedData?.extracted_data?.raw_text || "";
    const requestId = location.state?.extractedData?.request_id;
    const processingDetails = location.state?.processingDetails;
    const usedEnhancedOCR = location.state?.usedEnhancedOCR;

    useEffect(() => {
        // Always show animated QR, try to generate real QR if data exists
        if (Object.keys(extractedData).length > 0) {
            generateQRCodes();
        } else {
            // Show animated placeholder even without data
            setQrData("Demo QR code for Injinet credential verification system");
        }
    }, [extractedData]);

    const generateQRCodes = async () => {
        setIsGeneratingQR(true);
        setError(null);

        try {
            console.log('🔐 Generating QR codes with real signatures...');

            // Generate signed QR code with real Ed25519 signatures
            const signedQRResult = await apiService.generateSignedQR(extractedData);

            if (signedQRResult.success) {
                setSignedQR(signedQRResult);
                console.log('✅ Signed QR generated successfully');
            }

            // Generate simple QR for display (now uses PixelPass)
            const simpleQRResult = await apiService.generateSimpleQR(extractedData, 'json');

            console.log('🔍 PixelPass QR Result:', simpleQRResult);

            if (simpleQRResult.success) {
                // PixelPass returns the QR in qr_code.qr_image format
                const qrImageData = simpleQRResult.qr_code?.qr_image ||
                    simpleQRResult.qr_image ||
                    simpleQRResult.qr_data;

                console.log('🖼️ QR Image Data:', qrImageData ? qrImageData.substring(0, 100) + '...' : 'No image data');

                if (qrImageData) {
                    setQrData(qrImageData);
                    console.log('✅ PixelPass QR generated successfully');
                } else {
                    console.warn('⚠️ No QR image data found in PixelPass response');
                    // Fallback to demo data
                    setQrData("Demo QR code for Injinet credential verification system");
                }
            } else {
                console.error('❌ PixelPass QR generation failed:', simpleQRResult.error);
                // Fallback to demo data
                setQrData("Demo QR code for Injinet credential verification system");
            }

            // Generate renderable QR image for Wallet storage from extracted data
            console.log('🎨 Starting QR image generation for Wallet...');
            console.log('  - extractedData:', extractedData);
            try {
                const dataForQR = JSON.stringify(extractedData);
                console.log('  - dataForQR (stringified):', dataForQR.substring(0, 100) + '...');
                const qrImage = await QRCodeLib.toDataURL(dataForQR, { width: 400, margin: 2 });
                setQrImageData(qrImage);
                qrImageRef.current = qrImage; // Store in ref for immediate access
                console.log('✅ Generated QR image for Wallet:', qrImage.substring(0, 50) + '...');
            } catch (err) {
                console.error('❌ Failed to generate QR image for Wallet:', err);
            }

            // Perform data verification
            if (requestId) {
                const verificationResult = await apiService.verifyData(requestId, extractedData);
                if (verificationResult.verification_status === 'passed') {
                    setValidationScore(95);
                } else {
                    setValidationScore(Math.max(70, 95 - (verificationResult.discrepancies?.length || 0) * 10));
                }
            }

        } catch (error) {
            console.error('❌ QR generation failed:', error);
            setError(error.message || 'QR generation failed');

            // Fallback to mock data
            const mockQRData = JSON.stringify({
                name: extractedData.name || "User",
                pan: extractedData.pan_number || extractedData.pan || "XXXXX1234X",
                verified: false,
                timestamp: new Date().toISOString(),
                note: "Generated offline - backend unavailable"
            });
            setQrData(`data:image/svg+xml;base64,${btoa(mockQRData)}`);
        } finally {
            setIsGeneratingQR(false);
        }
    };

    const handleVerify = async () => {
        if (!qrData && !signedQR) {
            setError("QR validation failed: No valid QR data found. Please ensure the QR code is generated before verifying.");
            return;
        }

        setIsVerifying(true);
        setError(null);

        try {
            console.log('🔍 Verifying with Semantic Validator...');

            // Perform Semantic Validation
            const semanticResult = await apiService.validateSemantic(
                rawText || JSON.stringify(extractedData), // Fallback if raw text missing
                extractedData
            );

            console.log("✅ Semantic Validation Result:", semanticResult);

            if (semanticResult) {
                const qrImageToPass = qrImageRef.current || qrImageData;
                console.log('📤 Navigating to ValidationResult with:');
                console.log('  - qrImageData (from ref):', qrImageToPass ? qrImageToPass.substring(0, 50) + '...' : 'NULL/UNDEFINED');
                console.log('  - signedQR:', signedQR);
                console.log('  - extractedData:', extractedData);

                navigate('/validation-result', {
                    state: {
                        result: semanticResult,
                        verified: semanticResult.is_match,
                        signedQR: signedQR,
                        qrData: qrImageToPass, // Use ref value for immediate access
                        extractedData: extractedData
                    }
                });
            }

        } catch (error) {
            console.error('❌ Validation failed:', error);
            setError(error.message || 'Verification failed');
            setIsVerifying(false); // Stop loading only on error
        }
    };

    const downloadQR = () => {
        // Try multiple possible QR image sources from PixelPass response
        const qrImageSrc = signedQR?.qr_code?.qr_image ||
            signedQR?.qr_image ||
            qrData;

        if (qrImageSrc) {
            const link = document.createElement('a');
            link.href = qrImageSrc;
            link.download = 'signed-credential-qr.png';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            console.warn('No QR image data available for download');
        }
    };

    const features = [
        {
            icon: Shield,
            title: "MOSIP Compliant",
            description: "Validated against official MOSIP ITR schemas"
        },
        {
            icon: Lock,
            title: "Cryptographically Signed",
            description: "Ed25519 digital signatures for authenticity"
        },
        {
            icon: Eye,
            title: "Semantic Validation",
            description: "AI-powered content verification and analysis"
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
                                Schema Validation
                            </span>
                            <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
                        </div>
                        
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-[hsl(var(--foreground))]">
                            Document Validation
                        </h1>
                        
                        <p className="text-xl text-[hsl(var(--muted-foreground))] leading-relaxed max-w-3xl mx-auto">
                            Validation results against verified MOSIP ITR schemas with cryptographic signatures and semantic analysis.
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
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-8 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3"
                    >
                        <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                        <span className="text-red-700 text-sm">{error}</span>
                    </motion.div>
                )}

                <div className="grid lg:grid-cols-2 gap-12 items-start">
                    
                    {/* Validation Score Section */}
                    <motion.div
                        initial={{ opacity: 0, x: -40 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.6, delay: 0.3 }}
                        className="space-y-6"
                    >
                        <div className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))]">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="w-10 h-10 bg-[hsl(var(--gov-green))] rounded-xl flex items-center justify-center">
                                    <TrendingUp className="w-5 h-5 text-white" />
                                </div>
                                <h2 className="text-2xl font-bold text-[hsl(var(--foreground))]">Validation Score</h2>
                            </div>
                            
                            <ValidationStatus score={validationScore} status={validationScore >= 90 ? "Passed" : "Warning"} />

                            {/* Enhanced OCR Processing Details */}
                            {usedEnhancedOCR && processingDetails && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-4"
                                >
                                    <div className="flex items-center gap-2 text-blue-700 font-semibold mb-3">
                                        <Zap className="w-5 h-5" />
                                        Enhanced OCR Results
                                    </div>
                                    <div className="space-y-1 text-sm text-blue-600">
                                        <div>Engines Used: {processingDetails.engines_used.join(', ')}</div>
                                        <div>Confidence: {(processingDetails.confidence_score * 100).toFixed(1)}%</div>
                                        <div>Processing Time: {processingDetails.processing_time.toFixed(2)}s</div>
                                        <div>Best Engine: {processingDetails.selected_engine}</div>
                                    </div>
                                </motion.div>
                            )}
                        </div>

                        {/* Verification Details */}
                        {signedQR && (
                            <div className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))]">
                                <div className="flex items-center gap-3 mb-6">
                                    <div className="w-10 h-10 bg-[hsl(var(--gov-gold))] rounded-xl flex items-center justify-center">
                                        <Shield className="w-5 h-5 text-white" />
                                    </div>
                                    <h3 className="text-xl font-bold text-[hsl(var(--foreground))]">Verification Details</h3>
                                </div>
                                
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                        <span className="text-[hsl(var(--muted-foreground))]">Workflow ID:</span>
                                        <span className="font-medium text-[hsl(var(--foreground))]">{signedQR.workflow_id}</span>
                                    </div>
                                    <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                        <span className="text-[hsl(var(--muted-foreground))]">Signature Type:</span>
                                        <span className="font-medium text-[hsl(var(--foreground))]">Ed25519Signature2018</span>
                                    </div>
                                    <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                        <span className="text-[hsl(var(--muted-foreground))]">Encoding:</span>
                                        <span className="font-medium text-[hsl(var(--foreground))]">{signedQR.qr_code?.encoding || 'CBOR'}</span>
                                    </div>
                                    <div className="flex justify-between items-center py-2">
                                        <span className="text-[hsl(var(--muted-foreground))]">Compatible With:</span>
                                        <span className="font-medium text-[hsl(var(--foreground))]">Inji Verify Portal</span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </motion.div>

                    {/* QR Code Section */}
                    <motion.div
                        initial={{ opacity: 0, x: 40 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.6, delay: 0.4 }}
                        className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))]"
                    >
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-10 h-10 bg-[hsl(var(--gov-green))] rounded-xl flex items-center justify-center">
                                <Database className="w-5 h-5 text-white" />
                            </div>
                            <h2 className="text-2xl font-bold text-[hsl(var(--foreground))]">Injinet QR Generation</h2>
                        </div>
                        
                        <div className="text-center">
                            {/* Always show the animated QR component */}
                            <div className="mb-6">
                                <SimpleQR
                                    data={qrData || "Generating QR code for Injinet credential verification..."}
                                    size="280px"
                                    label="Injinet Credential"
                                />
                            </div>

                            <div className="space-y-4">
                                {signedQR && (
                                    <Button
                                        onClick={downloadQR}
                                        className="w-full bg-white text-[hsl(var(--foreground))] border-2 border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))] font-semibold py-3 px-6 rounded-xl flex items-center justify-center gap-2 transition-all"
                                    >
                                        <Download className="w-4 h-4" />
                                        Download Signed QR
                                    </Button>
                                )}

                                {!verified ? (
                                    <Button
                                        onClick={handleVerify}
                                        disabled={isVerifying}
                                        className="w-full bg-[hsl(var(--gov-green))] hover:bg-[hsl(var(--gov-green-dark))] text-white font-semibold py-4 px-6 rounded-xl flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {isVerifying ? (
                                            <>
                                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                                Verifying with Injinet...
                                            </>
                                        ) : (
                                            <>
                                                <Shield className="w-4 h-4" />
                                                Verify with Injinet
                                            </>
                                        )}
                                    </Button>
                                ) : (
                                    <motion.div
                                        initial={{ scale: 0.9, opacity: 0 }}
                                        animate={{ scale: 1, opacity: 1 }}
                                        className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center justify-center gap-2 text-green-700 font-semibold"
                                    >
                                        <CheckCircle className="w-5 h-5" />
                                        <span>Verified Successfully!</span>
                                    </motion.div>
                                )}
                            </div>
                        </div>
                    </motion.div>
                </div>

                {/* Action Buttons */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.5 }}
                    className="flex justify-center mt-12"
                >
                    <Button
                        onClick={() => navigate('/wallet', {
                            state: {
                                extractedData,
                                signedQR,
                                verified
                            }
                        })}
                        className="bg-[hsl(var(--gov-gold))] hover:bg-[hsl(var(--gov-gold-dark))] text-white font-bold px-8 py-4 rounded-xl text-lg shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
                    >
                        <CreditCard className="w-5 h-5" />
                        Go to Wallet
                        <ArrowRight className="w-5 h-5" />
                    </Button>
                </motion.div>
            </div>
        </div>
    );
};

export default ValidationPage;
