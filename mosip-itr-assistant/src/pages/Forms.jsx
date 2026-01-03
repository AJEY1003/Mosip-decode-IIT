import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { Save, ArrowRight, CheckCircle, AlertCircle, Zap, User, CreditCard, FileText, DollarSign, Shield, Database, TrendingUp } from 'lucide-react';
import Input from '../components/Input';
import Button from '../components/Button';
import nerExtractor from '../utils/nerExtractor';

// Helper function to get fields for each tab
const getFieldsForTab = (tabId) => {
    const fieldMappings = {
        'pre-reg': ['name', 'pan', 'aadhaar', 'date_of_birth', 'mobile', 'email'],
        'bank': ['account_number', 'ifsc', 'bank_name', 'address', 'pincode'],
        'form16': ['employer', 'tan', 'assessment_year', 'financial_year', 'gross_salary', 'tds_deducted'],
        'income': ['total_income', 'gross_salary', 'tds_deducted']
    };
    
    return fieldMappings[tabId] || [];
};

const FormsPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [activeTab, setActiveTab] = useState('pre-reg');
    const [isLoading, setIsLoading] = useState(true);
    const [nerResults, setNerResults] = useState(null);

    // Get extracted data from backend
    const extractedData = location.state?.extractedData?.extracted_data?.structured_data || {};
    const rawText = location.state?.extractedData?.extracted_data?.raw_text || '';
    const fieldConfidenceScores = location.state?.extractedData?.extracted_data?.field_confidence_scores || {};
    const processingDetails = location.state?.processingDetails;

    // Enhanced form data with NER extraction
    const [formData, setFormData] = useState({
        // Personal Information
        name: extractedData.name || '',
        pan: extractedData.pan || '',
        aadhaar: extractedData.aadhaar || '',
        date_of_birth: extractedData.date_of_birth || '',
        
        // Financial Information
        gross_salary: extractedData.gross_salary || '',
        tds_deducted: extractedData.tds_deducted || '',
        total_income: extractedData.total_income || '',
        
        // Bank Information
        account_number: extractedData.account_number || '',
        ifsc: extractedData.ifsc || '',
        bank_name: extractedData.bank_name || '',
        
        // Employer Information
        employer: extractedData.employer || '',
        tan: extractedData.tan || '',
        
        // Contact Information
        mobile: extractedData.mobile || '',
        email: extractedData.email || '',
        address: extractedData.address || '',
        pincode: extractedData.pincode || '',
        
        // Assessment Information
        assessment_year: extractedData.assessment_year || '',
        financial_year: extractedData.financial_year || ''
    });

    const tabs = [
        { id: 'pre-reg', label: 'Personal Info', icon: User, color: 'bg-blue-500' },
        { id: 'bank', label: 'Bank Details', icon: CreditCard, color: 'bg-emerald-500' },
        { id: 'form16', label: 'Form 16', icon: FileText, color: 'bg-purple-500' },
        { id: 'income', label: 'Income Details', icon: DollarSign, color: 'bg-orange-500' }
    ];

    useEffect(() => {
        // Process raw text with client-side NER if no structured data from backend
        if (rawText && Object.keys(extractedData).length === 0) {
            setIsLoading(true);
            const clientNerResults = nerExtractor.extractFields(rawText, 'ITR');
            setNerResults(clientNerResults);
            
            // Update form data with client-side NER results
            setFormData(prev => ({
                ...prev,
                ...clientNerResults.fields
            }));
        }
        setIsLoading(false);
    }, [rawText, extractedData]);

    const getFieldConfidence = (fieldName) => {
        return fieldConfidenceScores[fieldName] || nerResults?.confidenceScores?.[fieldName] || 0;
    };

    const getConfidenceColor = (confidence) => {
        if (confidence >= 0.8) return 'text-green-600';
        if (confidence >= 0.6) return 'text-yellow-600';
        return 'text-red-600';
    };

    const getConfidenceIcon = (confidence) => {
        if (confidence >= 0.8) return CheckCircle;
        if (confidence >= 0.6) return AlertCircle;
        return AlertCircle;
    };

    const handleInputChange = (field, value) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const renderFieldWithConfidence = (field, label, type = 'text', readOnly = false) => {
        const confidence = getFieldConfidence(field);
        const ConfidenceIcon = getConfidenceIcon(confidence);
        
        return (
            <div key={field} className="space-y-2">
                <div className="flex items-center justify-between">
                    <label className="text-sm font-semibold text-[hsl(var(--foreground))]">{label}</label>
                    {confidence > 0 && (
                        <div className={`flex items-center gap-1 text-xs ${getConfidenceColor(confidence)}`}>
                            <ConfidenceIcon className="w-3 h-3" />
                            <span>{Math.round(confidence * 100)}%</span>
                        </div>
                    )}
                </div>
                <Input
                    value={formData[field]}
                    type={type}
                    readOnly={readOnly}
                    onChange={(e) => handleInputChange(field, e.target.value)}
                    className={`w-full ${
                        confidence >= 0.8 ? 'border-green-300 bg-green-50' : 
                        confidence >= 0.6 ? 'border-yellow-300 bg-yellow-50' : 
                        confidence > 0 ? 'border-red-300 bg-red-50' : ''
                    }`}
                />
            </div>
        );
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-background via-[hsl(var(--muted))]/30 to-background flex items-center justify-center">
                <motion.div
                    className="text-center"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                >
                    <div className="w-16 h-16 bg-[hsl(var(--gov-green))]/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        >
                            <Zap className="w-8 h-8 text-[hsl(var(--gov-green))]" />
                        </motion.div>
                    </div>
                    <h3 className="text-xl font-bold text-[hsl(var(--foreground))] mb-2">Processing Data</h3>
                    <p className="text-[hsl(var(--muted-foreground))]">Processing extracted data with NER...</p>
                </motion.div>
            </div>
        );
    }

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
                                AI Auto-Filled Forms
                            </span>
                            <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
                        </div>
                        
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-[hsl(var(--foreground))]">
                            Review Extracted Data
                        </h1>
                        
                        <p className="text-xl text-[hsl(var(--muted-foreground))] leading-relaxed max-w-3xl mx-auto">
                            Review and edit the data extracted using advanced NER techniques. All fields are automatically populated from your documents.
                        </p>
                    </motion.div>

                    {/* Extraction Summary */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="grid md:grid-cols-3 gap-8 mb-16"
                    >
                        {[
                            {
                                icon: Database,
                                value: Object.keys(formData).filter(key => formData[key]).length,
                                label: "Fields Extracted",
                                color: "text-blue-600"
                            },
                            {
                                icon: TrendingUp,
                                value: `${Math.round((nerResults?.confidence || 
                                    (Object.keys(fieldConfidenceScores).length > 0 ? 
                                        Object.values(fieldConfidenceScores).reduce((a, b) => a + b, 0) / Object.values(fieldConfidenceScores).length : 
                                        0.85)) * 100)}%`,
                                label: "Avg Confidence",
                                color: "text-green-600"
                            },
                            {
                                icon: Shield,
                                value: processingDetails?.engines_used?.length || 3,
                                label: "OCR Engines",
                                color: "text-purple-600"
                            }
                        ].map((stat, index) => (
                            <div key={index} className="text-center">
                                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                                    <stat.icon className={`w-8 h-8 ${stat.color}`} />
                                </div>
                                <div className="text-3xl font-bold text-[hsl(var(--foreground))] mb-2">{stat.value}</div>
                                <div className="text-sm text-[hsl(var(--muted-foreground))]">{stat.label}</div>
                            </div>
                        ))}
                    </motion.div>
                </div>
            </div>

            {/* Main Content */}
            <div className="container mx-auto px-6 sm:px-8 lg:px-12 pb-20">
                {/* Tabs */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.3 }}
                    className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))] overflow-hidden"
                >
                    {/* Tab Headers */}
                    <div className="flex overflow-x-auto bg-[hsl(var(--muted))]/30">
                        {tabs.map((tab) => {
                            const fieldsForTab = getFieldsForTab(tab.id);
                            const filledFields = fieldsForTab.filter(field => formData[field]);
                            const TabIcon = tab.icon;
                            
                            return (
                                <button
                                    key={tab.id}
                                    className={`flex items-center gap-3 px-6 py-4 font-semibold text-sm whitespace-nowrap transition-all relative ${
                                        activeTab === tab.id 
                                            ? 'text-[hsl(var(--gov-green))] bg-white border-b-2 border-[hsl(var(--gov-green))]' 
                                            : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-white/50'
                                    }`}
                                    onClick={() => setActiveTab(tab.id)}
                                >
                                    <div className={`w-8 h-8 ${activeTab === tab.id ? 'bg-[hsl(var(--gov-green))]' : tab.color} rounded-lg flex items-center justify-center`}>
                                        <TabIcon className="w-4 h-4 text-white" />
                                    </div>
                                    <span>{tab.label}</span>
                                    <span className={`px-2 py-1 rounded-full text-xs ${
                                        activeTab === tab.id ? 'bg-[hsl(var(--gov-green))]/10 text-[hsl(var(--gov-green))]' : 'bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))]'
                                    }`}>
                                        {filledFields.length}/{fieldsForTab.length}
                                    </span>
                                </button>
                            );
                        })}
                    </div>

                    {/* Tab Content */}
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.3 }}
                        className="p-8"
                    >
                        {activeTab === 'pre-reg' && (
                            <div className="grid md:grid-cols-2 gap-6">
                                {renderFieldWithConfidence('name', 'Full Name')}
                                {renderFieldWithConfidence('pan', 'PAN Number')}
                                {renderFieldWithConfidence('aadhaar', 'Aadhaar Number')}
                                {renderFieldWithConfidence('date_of_birth', 'Date of Birth', 'date')}
                                {renderFieldWithConfidence('mobile', 'Mobile Number', 'tel')}
                                {renderFieldWithConfidence('email', 'Email Address', 'email')}
                            </div>
                        )}
                        
                        {activeTab === 'bank' && (
                            <div className="grid md:grid-cols-2 gap-6">
                                {renderFieldWithConfidence('account_number', 'Account Number')}
                                {renderFieldWithConfidence('ifsc', 'IFSC Code')}
                                {renderFieldWithConfidence('bank_name', 'Bank Name')}
                                {renderFieldWithConfidence('address', 'Address')}
                                {renderFieldWithConfidence('pincode', 'PIN Code')}
                            </div>
                        )}
                        
                        {activeTab === 'form16' && (
                            <div className="grid md:grid-cols-2 gap-6">
                                {renderFieldWithConfidence('employer', 'Employer Name')}
                                {renderFieldWithConfidence('tan', 'TAN Number')}
                                {renderFieldWithConfidence('assessment_year', 'Assessment Year')}
                                {renderFieldWithConfidence('financial_year', 'Financial Year')}
                                {renderFieldWithConfidence('gross_salary', 'Gross Salary', 'number')}
                                {renderFieldWithConfidence('tds_deducted', 'TDS Deducted', 'number')}
                            </div>
                        )}
                        
                        {activeTab === 'income' && (
                            <div className="space-y-6">
                                <div className="grid md:grid-cols-2 gap-6">
                                    {renderFieldWithConfidence('total_income', 'Total Income', 'number')}
                                    {renderFieldWithConfidence('gross_salary', 'Gross Salary', 'number')}
                                    {renderFieldWithConfidence('tds_deducted', 'TDS Deducted', 'number')}
                                </div>
                                
                                {/* Income Summary */}
                                <div className="bg-[hsl(var(--muted))]/30 rounded-xl p-6 border border-[hsl(var(--border))]">
                                    <h4 className="text-lg font-bold text-[hsl(var(--foreground))] mb-4">Income Summary</h4>
                                    <div className="space-y-3">
                                        <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                            <span className="text-[hsl(var(--muted-foreground))]">Gross Income:</span>
                                            <span className="font-semibold text-[hsl(var(--foreground))]">
                                                ₹{formData.gross_salary ? parseInt(formData.gross_salary).toLocaleString() : '0'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                            <span className="text-[hsl(var(--muted-foreground))]">TDS Deducted:</span>
                                            <span className="font-semibold text-red-600">
                                                ₹{formData.tds_deducted ? parseInt(formData.tds_deducted).toLocaleString() : '0'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center py-2 bg-[hsl(var(--gov-green))]/10 px-4 rounded-lg">
                                            <span className="font-semibold text-[hsl(var(--foreground))]">Net Income:</span>
                                            <span className="font-bold text-[hsl(var(--gov-green))] text-lg">
                                                ₹{formData.gross_salary && formData.tds_deducted ? 
                                                    (parseInt(formData.gross_salary) - parseInt(formData.tds_deducted)).toLocaleString() : '0'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Form Actions */}
                        <div className="flex flex-wrap gap-4 mt-8 pt-6 border-t border-[hsl(var(--border))]">
                            <Button
                                className="bg-white text-[hsl(var(--foreground))] border-2 border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))] font-semibold py-2 px-4 rounded-xl flex items-center gap-2 transition-all"
                            >
                                <Save className="w-4 h-4" />
                                Save Draft
                            </Button>
                            
                            <Button
                                onClick={() => {
                                    // Re-run NER extraction
                                    if (rawText) {
                                        const newResults = nerExtractor.extractFields(rawText, 'ITR');
                                        setNerResults(newResults);
                                        setFormData(prev => ({
                                            ...prev,
                                            ...newResults.fields
                                        }));
                                    }
                                }}
                                className="bg-[hsl(var(--gov-gold))] hover:bg-[hsl(var(--gov-gold-dark))] text-white font-semibold py-2 px-4 rounded-xl flex items-center gap-2 transition-all"
                            >
                                <Zap className="w-4 h-4" />
                                Re-extract Fields
                            </Button>
                        </div>
                    </motion.div>
                </motion.div>

                {/* Proceed Button */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.5 }}
                    className="flex justify-end mt-8"
                >
                    <Button
                        onClick={() => navigate('/validation', {
                            state: {
                                extractedData: {
                                    extracted_data: {
                                        structured_data: formData,
                                        raw_text: rawText
                                    }
                                },
                                processingDetails,
                                usedEnhancedOCR: true
                            }
                        })}
                        className="bg-[hsl(var(--gov-green))] hover:bg-[hsl(var(--gov-green-dark))] text-white font-bold px-8 py-4 rounded-xl text-lg shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
                    >
                        Proceed to Validation
                        <ArrowRight className="w-5 h-5" />
                    </Button>
                </motion.div>
            </div>
        </div>
    );
};

export default FormsPage;