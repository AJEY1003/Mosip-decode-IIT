import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { Save, ArrowRight, CheckCircle, AlertCircle, Zap, User, CreditCard, FileText, DollarSign, Shield, Database, TrendingUp, RefreshCw, FileCheck, Merge } from 'lucide-react';
import Input from '../components/Input';
import Button from '../components/Button';
import nerExtractor from '../utils/nerExtractor';
import apiService from '../services/api';

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
    const [isAutoFilling, setIsAutoFilling] = useState(false);
    const [hasProcessedAutoFill, setHasProcessedAutoFill] = useState(false);
    const [nerResults, setNerResults] = useState(null);
    const [autoFillResults, setAutoFillResults] = useState(null);
    const [documentSources, setDocumentSources] = useState({});

    // Get data from multi-document upload or single document extraction
    const multiDocumentData = location.state?.multiDocumentData;
    const extractedData = location.state?.extractedData?.extracted_data?.structured_data || {};
    const rawText = location.state?.extractedData?.extracted_data?.raw_text || '';
    const fieldConfidenceScores = location.state?.extractedData?.extracted_data?.field_confidence_scores || {};
    const processingDetails = location.state?.processingDetails;

    // Enhanced form data with auto-fill support
    const [formData, setFormData] = useState({
        // Personal Information
        name: '',
        pan: '',
        aadhaar: '',
        date_of_birth: '',
        
        // Financial Information
        gross_salary: '',
        tds_deducted: '',
        total_income: '',
        
        // Bank Information
        account_number: '',
        ifsc: '',
        bank_name: '',
        
        // Employer Information
        employer: '',
        tan: '',
        
        // Contact Information
        mobile: '',
        email: '',
        address: '',
        pincode: '',
        
        // Assessment Information
        assessment_year: '',
        financial_year: ''
    });

    const tabs = [
        { id: 'pre-reg', label: 'Personal Info', icon: User, color: 'bg-blue-500' },
        { id: 'bank', label: 'Bank Details', icon: CreditCard, color: 'bg-emerald-500' },
        { id: 'form16', label: 'Form 16', icon: FileText, color: 'bg-purple-500' },
        { id: 'income', label: 'Income Details', icon: DollarSign, color: 'bg-orange-500' }
    ];

    useEffect(() => {
        const initializeFormData = async () => {
            setIsLoading(true);
            
            try {
                if (multiDocumentData && !hasProcessedAutoFill) {
                    // Handle multi-document auto-fill with client-side merging
                    handleClientSideAutoFill();
                    setHasProcessedAutoFill(true);
                } else if (extractedData && Object.keys(extractedData).length > 0) {
                    // Handle single document extraction
                    setFormData(prev => ({
                        ...prev,
                        ...extractedData
                    }));
                } else if (rawText) {
                    // Process raw text with client-side NER
                    const clientNerResults = nerExtractor.extractFields(rawText, 'ITR');
                    setNerResults(clientNerResults);
                    setFormData(prev => ({
                        ...prev,
                        ...clientNerResults.fields
                    }));
                }
            } catch (error) {
                console.error('Error initializing form data:', error);
            } finally {
                setIsLoading(false);
            }
        };

        initializeFormData();
    }, []); // Empty dependency array - only run once on mount

    const handleClientSideAutoFill = () => {
        if (!multiDocumentData) {
            console.log('⏭️ No multi-document data available');
            return;
        }

        console.log('🔄 Starting client-side auto-fill...');
        
        // Define field priorities (higher priority documents override lower priority)
        const fieldPriorities = {
            name: ['aadhaar', 'form16', 'preregistration'],
            pan: ['form16', 'preregistration', 'aadhaar'],
            aadhaar: ['aadhaar'],
            date_of_birth: ['aadhaar', 'preregistration'],
            email: ['preregistration', 'form16'],
            mobile: ['preregistration', 'aadhaar'],
            address: ['aadhaar', 'preregistration'],
            pincode: ['aadhaar', 'preregistration'],
            gross_salary: ['form16', 'bankSlip'],
            tds_deducted: ['form16'],
            total_income: ['form16', 'income'],
            account_number: ['bankSlip'],
            ifsc: ['bankSlip'],
            bank_name: ['bankSlip'],
            employer: ['form16'],
            tan: ['form16'],
            assessment_year: ['form16', 'preregistration'],
            financial_year: ['form16', 'preregistration']
        };

        const mergedData = {};
        const fieldSources = {};
        const conflicts = [];
        const confidenceScores = {};

        // Process each field
        Object.keys(fieldPriorities).forEach(fieldName => {
            const priorities = fieldPriorities[fieldName];
            let bestValue = null;
            let bestSource = null;
            let bestConfidence = 0;
            const fieldConflicts = [];

            // Check each document type in priority order
            priorities.forEach(docType => {
                if (multiDocumentData[docType] && multiDocumentData[docType].extracted_data) {
                    const docData = multiDocumentData[docType].extracted_data;
                    
                    // Check structured_data first
                    let value = docData.structured_data?.[fieldName];
                    let confidence = docData.field_confidence_scores?.[fieldName] || 0.7;

                    if (!value && docData.raw_text) {
                        // Fallback to client-side NER extraction
                        const nerResults = nerExtractor.extractFields(docData.raw_text, 'ITR');
                        value = nerResults.fields[fieldName];
                        confidence = nerResults.confidenceScores[fieldName] || 0.5;
                    }

                    if (value && value.trim()) {
                        // Track conflicts
                        if (bestValue && bestValue !== value) {
                            fieldConflicts.push({
                                source: docType,
                                value: value,
                                confidence: confidence
                            });
                        }

                        // Use highest priority source (first in priority array)
                        if (!bestValue) {
                            bestValue = value;
                            bestSource = docType;
                            bestConfidence = confidence;
                        }
                    }
                }
            });

            // Store the best value found
            if (bestValue) {
                mergedData[fieldName] = bestValue;
                fieldSources[fieldName] = bestSource;
                confidenceScores[fieldName] = bestConfidence;

                // Record conflicts if any
                if (fieldConflicts.length > 0) {
                    conflicts.push({
                        field: fieldName,
                        chosen_source: bestSource,
                        chosen_value: bestValue,
                        conflicting_sources: fieldConflicts.map(c => c.source),
                        conflicting_values: fieldConflicts
                    });
                }
            }
        });

        // Update form data with merged results
        setFormData(prev => ({
            ...prev,
            ...mergedData
        }));
        
        // Store document sources for each field
        setDocumentSources(fieldSources);
        
        // Store auto-fill results for display
        setAutoFillResults({
            merged_data: mergedData,
            field_sources: fieldSources,
            conflicts,
            confidence_scores: confidenceScores
        });

        console.log('✅ Client-side auto-fill completed:', {
            fieldsExtracted: Object.keys(mergedData).length,
            conflicts: conflicts.length,
            sources: Object.keys(fieldSources).length
        });
    };

    const handleFallbackProcessing = () => {
        // If client-side merging fails, process documents individually
        if (multiDocumentData) {
            const fallbackData = {};
            
            Object.entries(multiDocumentData).forEach(([docType, docData]) => {
                if (docData.extracted_data?.structured_data) {
                    Object.entries(docData.extracted_data.structured_data).forEach(([field, value]) => {
                        if (value && !fallbackData[field]) {
                            fallbackData[field] = value;
                        }
                    });
                }
            });
            
            setFormData(prev => ({
                ...prev,
                ...fallbackData
            }));
        }
    };

    const getFieldConfidence = (fieldName) => {
        // Priority: auto-fill results > field confidence scores > NER results
        return autoFillResults?.confidence_scores?.[fieldName] || 
               fieldConfidenceScores[fieldName] || 
               nerResults?.confidenceScores?.[fieldName] || 0;
    };

    const getFieldSource = (fieldName) => {
        return documentSources[fieldName] || 'manual';
    };

    const getSourceColor = (source) => {
        const sourceColors = {
            'aadhaar': 'text-blue-600',
            'form16': 'text-purple-600',
            'preregistration': 'text-green-600',
            'bankSlip': 'text-orange-600',
            'income': 'text-red-600',
            'manual': 'text-gray-600'
        };
        return sourceColors[source] || 'text-gray-600';
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
        const source = getFieldSource(field);
        const ConfidenceIcon = getConfidenceIcon(confidence);
        const hasConflict = autoFillResults?.conflicts?.some(conflict => 
            conflict.field === field
        );
        
        return (
            <div key={field} className="space-y-2">
                <div className="flex items-center justify-between">
                    <label className="text-sm font-semibold text-[hsl(var(--foreground))]">{label}</label>
                    <div className="flex items-center gap-2">
                        {/* Source indicator */}
                        {source !== 'manual' && (
                            <div className={`flex items-center gap-1 text-xs ${getSourceColor(source)}`}>
                                <FileCheck className="w-3 h-3" />
                                <span className="capitalize">{source}</span>
                            </div>
                        )}
                        
                        {/* Confidence indicator */}
                        {confidence > 0 && (
                            <div className={`flex items-center gap-1 text-xs ${getConfidenceColor(confidence)}`}>
                                <ConfidenceIcon className="w-3 h-3" />
                                <span>{Math.round(confidence * 100)}%</span>
                            </div>
                        )}
                        
                        {/* Conflict indicator */}
                        {hasConflict && (
                            <div className="flex items-center gap-1 text-xs text-amber-600">
                                <AlertCircle className="w-3 h-3" />
                                <span>Conflict</span>
                            </div>
                        )}
                    </div>
                </div>
                <Input
                    value={formData[field]}
                    type={type}
                    readOnly={readOnly}
                    onChange={(e) => handleInputChange(field, e.target.value)}
                    className={`w-full ${
                        hasConflict ? 'border-amber-300 bg-amber-50' :
                        confidence >= 0.8 ? 'border-green-300 bg-green-50' : 
                        confidence >= 0.6 ? 'border-yellow-300 bg-yellow-50' : 
                        confidence > 0 ? 'border-red-300 bg-red-50' : ''
                    }`}
                />
                
                {/* Show conflict details */}
                {hasConflict && (
                    <div className="text-xs text-amber-700 bg-amber-50 p-2 rounded border border-amber-200">
                        <div className="font-medium mb-1">Multiple values found:</div>
                        {autoFillResults.conflicts
                            .filter(conflict => conflict.field === field)
                            .map((conflict, idx) => (
                                <div key={idx} className="flex justify-between">
                                    <span className="capitalize">{conflict.source}:</span>
                                    <span className="font-mono">{conflict.value}</span>
                                </div>
                            ))
                        }
                    </div>
                )}
            </div>
        );
    };

    if (isLoading || isAutoFilling) {
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
                            {isAutoFilling ? (
                                <Merge className="w-8 h-8 text-[hsl(var(--gov-green))]" />
                            ) : (
                                <Zap className="w-8 h-8 text-[hsl(var(--gov-green))]" />
                            )}
                        </motion.div>
                    </div>
                    <h3 className="text-xl font-bold text-[hsl(var(--foreground))] mb-2">
                        {isAutoFilling ? 'Auto-Filling Form' : 'Processing Data'}
                    </h3>
                    <p className="text-[hsl(var(--muted-foreground))]">
                        {isAutoFilling ? 
                            'Intelligently merging data from multiple documents...' : 
                            'Processing extracted data with NER...'
                        }
                    </p>
                </motion.div>
            </div>
        );
    }

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
            <div className="pt-12 pb-8 overflow-hidden">
                <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="text-center mb-8"
                    >
                        <div className="inline-flex items-center gap-3 mb-4">
                            <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
                            <span className="text-sm font-semibold text-white/70">
                                AI Auto-Filled Forms
                            </span>
                            <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
                        </div>
                        
                        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold leading-tight mb-4 text-white">
                            Review Extracted Data
                        </h1>
                        
                        <p className="text-lg text-white/80 leading-relaxed max-w-3xl mx-auto">
                            Review and edit the data extracted using advanced NER techniques. All fields are automatically populated from your documents.
                        </p>
                    </motion.div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 pb-12 min-h-[70vh]">
                {/* Auto-Fill Summary (if multi-document) */}
                {autoFillResults && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.1 }}
                        className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 mb-6 border border-white/20"
                    >
                        <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                            <Merge className="w-4 h-4" />
                            Auto-Fill Summary
                        </h3>
                        
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 text-sm">
                            {/* Document Sources */}
                            <div>
                                <h4 className="font-semibold text-white/80 mb-2">Document Sources</h4>
                                <div className="space-y-1">
                                    {Object.entries(
                                        Object.values(documentSources).reduce((acc, source) => {
                                            acc[source] = (acc[source] || 0) + 1;
                                            return acc;
                                        }, {})
                                    ).map(([source, count]) => (
                                        <div key={source} className="flex justify-between items-center">
                                            <span className={`capitalize ${getSourceColor(source)} font-medium`}>
                                                {source}
                                            </span>
                                            <span className="text-white/70">{count} fields</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            
                            {/* Conflicts */}
                            {autoFillResults.conflicts && autoFillResults.conflicts.length > 0 && (
                                <div>
                                    <h4 className="font-semibold text-white/80 mb-2">
                                        Conflicts Resolved ({autoFillResults.conflicts.length})
                                    </h4>
                                    <div className="space-y-1 max-h-24 overflow-y-auto">
                                        {autoFillResults.conflicts.slice(0, 2).map((conflict, idx) => (
                                            <div key={idx} className="bg-white/5 rounded p-2">
                                                <div className="font-medium text-white/90 capitalize text-xs">
                                                    {conflict.field.replace('_', ' ')}
                                                </div>
                                                <div className="text-white/60 text-xs">
                                                    Used {conflict.chosen_source}
                                                </div>
                                            </div>
                                        ))}
                                        {autoFillResults.conflicts.length > 2 && (
                                            <div className="text-xs text-white/60 text-center">
                                                +{autoFillResults.conflicts.length - 2} more
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    </motion.div>
                )}
                {/* Tabs */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.3 }}
                    className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))] overflow-hidden min-h-[600px]"
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
                        className="p-8 lg:p-12"
                    >
                        {activeTab === 'pre-reg' && (
                            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {renderFieldWithConfidence('name', 'Full Name')}
                                {renderFieldWithConfidence('pan', 'PAN Number')}
                                {renderFieldWithConfidence('aadhaar', 'Aadhaar Number')}
                                {renderFieldWithConfidence('date_of_birth', 'Date of Birth', 'date')}
                                {renderFieldWithConfidence('mobile', 'Mobile Number', 'tel')}
                                {renderFieldWithConfidence('email', 'Email Address', 'email')}
                            </div>
                        )}
                        
                        {activeTab === 'bank' && (
                            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {renderFieldWithConfidence('account_number', 'Account Number')}
                                {renderFieldWithConfidence('ifsc', 'IFSC Code')}
                                {renderFieldWithConfidence('bank_name', 'Bank Name')}
                                {renderFieldWithConfidence('address', 'Address')}
                                {renderFieldWithConfidence('pincode', 'PIN Code')}
                            </div>
                        )}
                        
                        {activeTab === 'form16' && (
                            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {renderFieldWithConfidence('employer', 'Employer Name')}
                                {renderFieldWithConfidence('tan', 'TAN Number')}
                                {renderFieldWithConfidence('assessment_year', 'Assessment Year')}
                                {renderFieldWithConfidence('financial_year', 'Financial Year')}
                                {renderFieldWithConfidence('gross_salary', 'Gross Salary', 'number')}
                                {renderFieldWithConfidence('tds_deducted', 'TDS Deducted', 'number')}
                            </div>
                        )}
                        
                        {activeTab === 'income' && (
                            <div className="space-y-8">
                                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
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
                            
                            {multiDocumentData && (
                                <Button
                                    onClick={() => {
                                        setHasProcessedAutoFill(false);
                                        handleClientSideAutoFill();
                                        setHasProcessedAutoFill(true);
                                    }}
                                    className="bg-[hsl(var(--gov-purple))] hover:bg-[hsl(var(--gov-purple-dark))] text-white font-semibold py-2 px-4 rounded-xl flex items-center gap-2 transition-all"
                                >
                                    <Merge className="w-4 h-4" />
                                    Re-merge Documents
                                </Button>
                            )}
                            
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
                                multiDocumentData,
                                autoFillResults,
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
    </div>
    );
};

export default FormsPage;