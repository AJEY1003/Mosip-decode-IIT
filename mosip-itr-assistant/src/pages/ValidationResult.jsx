import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
    CheckCircle, 
    XCircle, 
    ArrowRight, 
    Home, 
    Database, 
    AlertCircle, 
    BarChart3,
    Upload,
    Settings,
    User,
    Shield,
    FileText,
    TrendingUp,
    Calendar,
    Clock,
    Activity,
    Eye,
    Info,
    Wallet,
    Search,
    Bell,
    Menu,
    ChevronRight,
    Download,
    RefreshCw
} from 'lucide-react';
import Button from '../components/Button';

const ValidationResult = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const result = location.state?.result;
    const extractedData = location.state?.extractedData || {};
    const [currentTime, setCurrentTime] = useState(new Date());
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    useEffect(() => {
        console.log('🔍 ValidationResult - Location State:', location.state);
        console.log('  - qrData:', location.state?.qrData);

        if (!result) {
            navigate('/validation');
        }

        // Update time every minute
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 60000);

        return () => clearInterval(timer);
    }, [result, navigate]);

    // Helper function to calculate individual field validation scores
    const getFieldValidationScore = (fieldName, fieldValue, validationResult) => {
        if (!fieldValue || !validationResult) return 0;
        
        // Base score from overall validation
        const baseScore = validationResult.score || 0;
        
        // Field-specific scoring logic
        const fieldScores = {
            name: () => {
                // Name validation: check if it's a proper name format
                const hasProperFormat = /^[a-zA-Z\s]{2,50}$/.test(fieldValue);
                const hasMultipleWords = fieldValue.trim().split(' ').length >= 2;
                return hasProperFormat && hasMultipleWords ? Math.min(baseScore + 10, 100) : Math.max(baseScore - 15, 0);
            },
            pan: () => {
                // PAN validation: check PAN format (AAAAA9999A)
                const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
                return panRegex.test(fieldValue) ? Math.min(baseScore + 15, 100) : Math.max(baseScore - 25, 0);
            },
            aadhaar: () => {
                // Aadhaar validation: check 12-digit format
                const aadhaarRegex = /^\d{12}$/;
                return aadhaarRegex.test(fieldValue.replace(/\s/g, '')) ? Math.min(baseScore + 10, 100) : Math.max(baseScore - 20, 0);
            },
            email: () => {
                // Email validation
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return emailRegex.test(fieldValue) ? Math.min(baseScore + 5, 100) : Math.max(baseScore - 10, 0);
            },
            mobile: () => {
                // Mobile validation: Indian mobile number format
                const mobileRegex = /^[6-9]\d{9}$/;
                return mobileRegex.test(fieldValue.replace(/\D/g, '')) ? Math.min(baseScore + 5, 100) : Math.max(baseScore - 10, 0);
            },
            date_of_birth: () => {
                // Date validation: check if it's a valid date format
                const dateRegex = /^\d{1,2}[-\/]\d{1,2}[-\/]\d{4}$/;
                return dateRegex.test(fieldValue) ? Math.min(baseScore + 5, 100) : Math.max(baseScore - 10, 0);
            },
            gross_salary: () => {
                // Salary validation: check if it's a valid number
                const salaryNum = parseFloat(fieldValue.replace(/[^\d.]/g, ''));
                return !isNaN(salaryNum) && salaryNum > 0 ? Math.min(baseScore + 5, 100) : Math.max(baseScore - 15, 0);
            },
            tds_deducted: () => {
                // TDS validation: check if it's a valid number
                const tdsNum = parseFloat(fieldValue.replace(/[^\d.]/g, ''));
                return !isNaN(tdsNum) && tdsNum >= 0 ? Math.min(baseScore + 5, 100) : Math.max(baseScore - 10, 0);
            }
        };
        
        // Use field-specific scoring if available, otherwise use base score with slight variation
        if (fieldScores[fieldName]) {
            return Math.round(fieldScores[fieldName]());
        } else {
            // Generic field scoring based on content length and format
            const lengthScore = fieldValue.length > 2 ? 5 : -5;
            const formatScore = /^[a-zA-Z0-9\s\-\.@]+$/.test(fieldValue) ? 5 : -10;
            return Math.round(Math.max(Math.min(baseScore + lengthScore + formatScore, 100), 0));
        }
    };

    // Helper function to get field type description
    const getFieldType = (fieldName) => {
        const fieldTypes = {
            name: 'Personal Name',
            pan: 'PAN Number',
            aadhaar: 'Aadhaar ID',
            email: 'Email Address',
            mobile: 'Mobile Number',
            date_of_birth: 'Date Field',
            gross_salary: 'Currency Amount',
            tds_deducted: 'Tax Amount',
            total_income: 'Currency Amount',
            account_number: 'Bank Account',
            ifsc: 'IFSC Code',
            bank_name: 'Bank Name',
            employer: 'Organization',
            tan: 'TAN Number',
            address: 'Address',
            pincode: 'PIN Code',
            assessment_year: 'Year',
            financial_year: 'Year'
        };
        
        return fieldTypes[fieldName] || 'Text Field';
    };

    if (!result) return null;

    const { score, is_match, match_label, status } = result;

    const getColor = (value) => {
        if (value >= 90) return '#10b981'; // Green
        if (value >= 75) return '#f59e0b'; // Amber
        return '#ef4444'; // Red
    };

    const color = getColor(score);

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
                                    Semantic Validation Result
                                </span>
                                <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
                            </div>
                            
                            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-white">
                                Verification Complete
                            </h1>
                            
                            <p className="text-xl text-white/80 leading-relaxed max-w-3xl mx-auto">
                                AI-powered comparison between Document Text and QR Data with semantic analysis
                            </p>
                        </motion.div>
                    </div>
                </div>

                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-24">
                    <div className="grid lg:grid-cols-2 gap-12 items-start">
                        
                        {/* Overall Score Card */}
                        <motion.div
                            initial={{ opacity: 0, x: -40 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.6, delay: 0.3 }}
                            className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))]"
                        >
                            <div className="text-center">
                                <motion.div
                                    initial={{ scale: 0.8 }}
                                    animate={{ scale: 1 }}
                                    transition={{ type: 'spring', stiffness: 100 }}
                                    style={{
                                        width: '180px',
                                        height: '180px',
                                        borderRadius: '50%',
                                        border: `10px solid ${color}20`,
                                        borderTop: `10px solid ${color}`,
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        margin: '0 auto',
                                        boxShadow: `0 0 30px ${color}30`
                                    }}
                                >
                                    <span style={{ fontSize: '3rem', fontWeight: '800', color }}>{score}%</span>
                                    <span style={{ fontSize: '0.9rem', color: '#6b7280', fontWeight: '600' }}>OVERALL</span>
                                </motion.div>

                                <div style={{ marginTop: '2rem' }}>
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: 0.3 }}
                                        style={{
                                            display: 'inline-flex',
                                            alignItems: 'center',
                                            gap: '0.5rem',
                                            padding: '0.75rem 1.5rem',
                                            background: `${color}15`,
                                            borderRadius: '30px',
                                            color: color,
                                            fontWeight: '700',
                                            fontSize: '1.2rem',
                                            border: `1px solid ${color}30`
                                        }}
                                    >
                                        {is_match ? <CheckCircle size={24} /> : <XCircle size={24} />}
                                        {match_label.toUpperCase()}
                                    </motion.div>
                                </div>

                                <p style={{ marginTop: '1.5rem', color: '#4b5563', maxWidth: '400px', marginInline: 'auto' }}>
                                    The AI model validated the semantic meaning of your document against the secure verification code.
                                    {is_match
                                        ? " The content strongly matches, confirming the document's authenticity."
                                        : " Significant discrepancies were found. Please verify the document manually."}
                                </p>
                            </div>
                        </motion.div>

                        {/* Individual Field Validation Scores - Professional Table */}
                        <motion.div
                            initial={{ opacity: 0, x: 40 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.6, delay: 0.4 }}
                            className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))] overflow-hidden"
                        >
                            <div className="bg-[hsl(var(--muted))]/30 px-6 py-4 border-b border-[hsl(var(--border))]">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-2xl font-bold text-[hsl(var(--foreground))] flex items-center gap-3">
                                        <div className="w-10 h-10 bg-[hsl(var(--gov-green))] rounded-xl flex items-center justify-center">
                                            <Database className="w-5 h-5 text-white" />
                                        </div>
                                        Field Validation Report
                                    </h3>
                                    <div className="text-sm text-[hsl(var(--muted-foreground))]">
                                        {Object.keys(extractedData).filter(key => extractedData[key]).length} fields analyzed
                                    </div>
                                </div>
                            </div>

                            {/* Table Header */}
                            <div className="bg-[hsl(var(--muted))]/20">
                                <div className="grid grid-cols-12 gap-4 px-6 py-3 text-sm font-semibold text-[hsl(var(--foreground))]">
                                    <div className="col-span-1">#</div>
                                    <div className="col-span-3">Field Name</div>
                                    <div className="col-span-4">Extracted Value</div>
                                    <div className="col-span-2">Score</div>
                                    <div className="col-span-2">Status</div>
                                </div>
                            </div>

                            {/* Table Body */}
                            <div className="max-h-96 overflow-y-auto">
                                {Object.entries(extractedData).map(([field, value], index) => {
                                    if (!value || typeof value !== 'string') return null;
                                    
                                    const fieldScore = getFieldValidationScore(field, value, result);
                                    const scoreColor = fieldScore >= 85 ? 'text-green-600' : 
                                                     fieldScore >= 70 ? 'text-yellow-600' : 'text-red-600';
                                    const bgColor = fieldScore >= 85 ? 'bg-green-50' : 
                                                   fieldScore >= 70 ? 'bg-yellow-50' : 'bg-red-50';
                                    const statusIcon = fieldScore >= 85 ? CheckCircle : 
                                                      fieldScore >= 70 ? AlertCircle : XCircle;
                                    const statusText = fieldScore >= 85 ? 'Verified' : 
                                                      fieldScore >= 70 ? 'Warning' : 'Failed';
                                    const StatusIcon = statusIcon;
                                    
                                    return (
                                        <motion.div 
                                            key={field}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.1 * index }}
                                            className={`grid grid-cols-12 gap-4 px-6 py-4 border-b border-[hsl(var(--border))] hover:${bgColor} transition-colors`}
                                        >
                                            {/* Row Number */}
                                            <div className="col-span-1 flex items-center">
                                                <span className="text-sm font-medium text-[hsl(var(--muted-foreground))]">
                                                    {index + 1}
                                                </span>
                                            </div>

                                            {/* Field Name */}
                                            <div className="col-span-3 flex items-center">
                                                <div className={`w-3 h-3 rounded-full mr-3 ${
                                                    fieldScore >= 85 ? 'bg-green-500' : 
                                                    fieldScore >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                                                }`}></div>
                                                <div>
                                                    <div className="font-semibold text-[hsl(var(--foreground))] capitalize">
                                                        {field.replace(/_/g, ' ')}
                                                    </div>
                                                    <div className="text-xs text-[hsl(var(--muted-foreground))]">
                                                        {getFieldType(field)}
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Extracted Value */}
                                            <div className="col-span-4 flex items-center">
                                                <div className="truncate">
                                                    <div className="font-mono text-sm text-[hsl(var(--foreground))]">
                                                        {value}
                                                    </div>
                                                    <div className="text-xs text-[hsl(var(--muted-foreground))]">
                                                        {value.length} characters
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Score with Progress Bar */}
                                            <div className="col-span-2 flex items-center">
                                                <div className="w-full">
                                                    <div className="flex items-center justify-between mb-1">
                                                        <span className={`font-bold text-lg ${scoreColor}`}>
                                                            {fieldScore}%
                                                        </span>
                                                    </div>
                                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                                        <div 
                                                            className={`h-2 rounded-full transition-all duration-500 ${
                                                                fieldScore >= 85 ? 'bg-green-500' : 
                                                                fieldScore >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                                                            }`}
                                                            style={{ width: `${fieldScore}%` }}
                                                        ></div>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Status */}
                                            <div className="col-span-2 flex items-center">
                                                <div className="flex items-center gap-2">
                                                    <StatusIcon className={`w-5 h-5 ${scoreColor}`} />
                                                    <span className={`font-medium text-sm ${scoreColor}`}>
                                                        {statusText}
                                                    </span>
                                                </div>
                                            </div>
                                        </motion.div>
                                    );
                                })}
                            </div>

                            {/* Table Footer with Summary */}
                            <div className="bg-[hsl(var(--muted))]/30 px-6 py-4 border-t border-[hsl(var(--border))]">
                                <div className="grid grid-cols-3 gap-6 text-center">
                                    <div>
                                        <div className="text-2xl font-bold text-[hsl(var(--foreground))]">
                                            {Object.keys(extractedData).filter(key => extractedData[key]).length}
                                        </div>
                                        <div className="text-sm text-[hsl(var(--muted-foreground))]">Total Fields</div>
                                    </div>
                                    <div>
                                        <div className="text-2xl font-bold text-[hsl(var(--gov-green))]">
                                            {Object.entries(extractedData)
                                                .filter(([_, value]) => value)
                                                .filter(([field, value]) => getFieldValidationScore(field, value, result) >= 85)
                                                .length}
                                        </div>
                                        <div className="text-sm text-[hsl(var(--muted-foreground))]">Verified Fields</div>
                                    </div>
                                    <div>
                                        <div className="text-2xl font-bold text-[hsl(var(--gov-gold))]">
                                            {Math.round(
                                                Object.entries(extractedData)
                                                    .filter(([_, value]) => value)
                                                    .reduce((sum, [field, value]) => sum + getFieldValidationScore(field, value, result), 0) /
                                                Object.entries(extractedData).filter(([_, value]) => value).length
                                            )}%
                                        </div>
                                        <div className="text-sm text-[hsl(var(--muted-foreground))]">Average Score</div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </div>

                    {/* Action Buttons */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.6 }}
                        className="flex flex-wrap gap-4 justify-center mt-12"
                    >
                        <Button
                            onClick={() => navigate('/')}
                            className="bg-white text-[hsl(var(--foreground))] border-2 border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))] font-semibold py-3 px-6 rounded-xl flex items-center gap-2 transition-all"
                        >
                            <Home className="w-4 h-4" />
                            Back to Home
                        </Button>
                        <Button
                            onClick={() => navigate('/wallet', {
                                state: {
                                    score,
                                    verified: is_match,
                                    signedQR: location.state?.signedQR,
                                    extractedData: location.state?.extractedData,
                                    qrImageData: location.state?.qrImageData
                                }
                            })}
                            disabled={!is_match}
                            className={`font-semibold py-3 px-6 rounded-xl flex items-center gap-2 transition-all ${
                                is_match 
                                    ? 'bg-[hsl(var(--gov-green))] hover:bg-[hsl(var(--gov-green-dark))] text-white shadow-lg hover:shadow-xl' 
                                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            }`}
                        >
                            <ArrowRight className="w-4 h-4" />
                            Proceed to Wallet
                        </Button>
                    </motion.div>
                </div>
            </div>
        </div>
    );
};

export default ValidationResult;
