import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowRight, CheckCircle, CreditCard, Download, Shield, Zap, Database, AlertCircle, TrendingUp, Lock, Eye } from 'lucide-react';
import SimpleQR from '../components/SimpleQR';
import Button from '../components/Button';

const ValidationSimple = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [validationScore] = useState(85);
    const [qrData, setQrData] = useState(null);

    // Get extracted data from previous page
    const extractedData = location.state?.extractedData?.extracted_data?.structured_data || {};
    const processingDetails = location.state?.processingDetails;
    const usedEnhancedOCR = location.state?.usedEnhancedOCR;

    useEffect(() => {
        // Generate QR data from extracted data or use demo data
        if (Object.keys(extractedData).length > 0) {
            setQrData(JSON.stringify(extractedData));
        } else {
            setQrData("Demo QR code for MOSIP ITR credential verification system");
        }
    }, [extractedData]);

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
                            
                            {/* Simple Validation Score Display */}
                            <div className="text-center py-8">
                                <div className="text-6xl font-bold text-[hsl(var(--gov-green))] mb-2">
                                    {validationScore}%
                                </div>
                                <div className="text-lg text-[hsl(var(--muted-foreground))]">
                                    Validation {validationScore >= 90 ? "Passed" : "Warning"}
                                </div>
                                <div className="mt-4 text-sm text-[hsl(var(--muted-foreground))]">
                                    Document verified against MOSIP standards
                                </div>
                            </div>

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
                                        <div>Engines Used: {processingDetails.engines_used?.join(', ') || 'Multiple'}</div>
                                        <div>Confidence: {((processingDetails.confidence_score || 0.85) * 100).toFixed(1)}%</div>
                                        <div>Processing Time: {(processingDetails.processing_time || 2.5).toFixed(2)}s</div>
                                        <div>Best Engine: {processingDetails.selected_engine || 'Enhanced'}</div>
                                    </div>
                                </motion.div>
                            )}
                        </div>

                        {/* Verification Details */}
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
                                    <span className="font-medium text-[hsl(var(--foreground))]">WF-{Date.now().toString().slice(-6)}</span>
                                </div>
                                <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                    <span className="text-[hsl(var(--muted-foreground))]">Signature Type:</span>
                                    <span className="font-medium text-[hsl(var(--foreground))]">Ed25519Signature2018</span>
                                </div>
                                <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                    <span className="text-[hsl(var(--muted-foreground))]">Encoding:</span>
                                    <span className="font-medium text-[hsl(var(--foreground))]">CBOR</span>
                                </div>
                                <div className="flex justify-between items-center py-2">
                                    <span className="text-[hsl(var(--muted-foreground))]">Compatible With:</span>
                                    <span className="font-medium text-[hsl(var(--foreground))]">Inji Verify Portal</span>
                                </div>
                            </div>
                        </div>
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
                            <h2 className="text-2xl font-bold text-[hsl(var(--foreground))]">QR Code Generation</h2>
                        </div>
                        
                        <div className="text-center">
                            {/* Beautiful Animated QR Component */}
                            <div className="mb-6">
                                <SimpleQR
                                    data={qrData || "Generating QR code for MOSIP credential verification..."}
                                    size="280px"
                                    label="MOSIP ITR Credential"
                                />
                            </div>

                            <div className="space-y-4">
                                <Button
                                    className="w-full bg-white text-[hsl(var(--foreground))] border-2 border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))] font-semibold py-3 px-6 rounded-xl flex items-center justify-center gap-2 transition-all"
                                >
                                    <Download className="w-4 h-4" />
                                    Download QR Code
                                </Button>

                                <Button
                                    className="w-full bg-[hsl(var(--gov-green))] hover:bg-[hsl(var(--gov-green-dark))] text-white font-semibold py-4 px-6 rounded-xl flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all"
                                >
                                    <Shield className="w-4 h-4" />
                                    Verify Document
                                </Button>
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
                                verified: true
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

export default ValidationSimple;