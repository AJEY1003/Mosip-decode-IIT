import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NavLink } from 'react-router-dom';
import { 
    Calculator, 
    Send, 
    Check, 
    Upload, 
    FileText, 
    CreditCard, 
    Building, 
    User, 
    TrendingUp, 
    AlertCircle, 
    CheckCircle, 
    DollarSign,
    Lightbulb,
    Download,
    Eye
} from 'lucide-react';
import Input from '../components/Input';
import Button from '../components/Button';
import Card from '../components/Card';
import apiService from '../services/api';
import './ITRFiling.css';

const ITRFilingPage = () => {
    const [currentStep, setCurrentStep] = useState(1);
    const [uploadedDocuments, setUploadedDocuments] = useState({});
    const [analysisResult, setAnalysisResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);

    const documentTypes = [
        { key: 'form16', label: 'Form 16', icon: FileText, required: true },
        { key: 'aadhaar', label: 'Aadhaar Card', icon: CreditCard, required: true },
        { key: 'pan_card', label: 'PAN Card', icon: CreditCard, required: true },
        { key: 'bank_statement', label: 'Bank Statement', icon: Building, required: false },
        { key: 'investment_proof', label: 'Investment Proofs', icon: TrendingUp, required: false }
    ];

    const handleFileUpload = async (docType, file) => {
        if (!file) return;

        setLoading(true);
        try {
            // Process document with OCR
            const result = await apiService.enhancedExtractText(file, docType);
            
            setUploadedDocuments(prev => ({
                ...prev,
                [docType]: {
                    file: file,
                    filename: file.name,
                    extracted_text: result.extracted_text,
                    structured_data: result.structured_data,
                    confidence: result.confidence_score || result.confidence || 0
                }
            }));

            console.log(`Uploaded and processed ${docType}:`, result);
        } catch (error) {
            console.error(`Error processing ${docType}:`, error);
            alert(`Error processing ${docType}: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleAnalyzeDocuments = async () => {
        if (Object.keys(uploadedDocuments).length === 0) {
            alert('Please upload at least one document before analyzing.');
            return;
        }

        setLoading(true);
        try {
            // Analyze documents using ITR analyzer
            const response = await fetch('/api/itr/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    documents: uploadedDocuments
                })
            });

            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.status}`);
            }

            const result = await response.json();
            setAnalysisResult(result);
            setCurrentStep(3);
            console.log('Analysis result:', result);
        } catch (error) {
            console.error('Analysis error:', error);
            alert(`Analysis failed: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmitITR = () => {
        setSubmitted(true);
    };

    const renderDocumentUpload = () => (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="document-upload-section"
        >
            <div className="section-header">
                <h3>Upload Required Documents</h3>
                <p>Upload your documents for automated analysis and ITR preparation</p>
            </div>

            <div className="documents-grid">
                {documentTypes.map((docType) => (
                    <Card key={docType.key} className="document-card">
                        <div className="document-header">
                            <docType.icon size={24} />
                            <div>
                                <h4>{docType.label}</h4>
                                <span className={`status ${docType.required ? 'required' : 'optional'}`}>
                                    {docType.required ? 'Required' : 'Optional'}
                                </span>
                            </div>
                        </div>

                        <div className="upload-area">
                            {uploadedDocuments[docType.key] ? (
                                <div className="uploaded-file">
                                    <CheckCircle className="success-icon" size={20} />
                                    <span>{uploadedDocuments[docType.key].filename}</span>
                                    <span className="confidence">
                                        {(uploadedDocuments[docType.key].confidence * 100).toFixed(1)}% confidence
                                    </span>
                                </div>
                            ) : (
                                <label className="upload-label">
                                    <input
                                        type="file"
                                        accept="image/*,.pdf"
                                        onChange={(e) => handleFileUpload(docType.key, e.target.files[0])}
                                        style={{ display: 'none' }}
                                    />
                                    <Upload size={20} />
                                    <span>Click to upload {docType.label}</span>
                                </label>
                            )}
                        </div>
                    </Card>
                ))}
            </div>

            <div className="step-actions">
                <Button 
                    onClick={() => setCurrentStep(2)} 
                    disabled={Object.keys(uploadedDocuments).length === 0}
                    className="next-step-btn"
                >
                    Continue to Review
                </Button>
            </div>
        </motion.div>
    );

    const renderDocumentReview = () => (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="document-review-section"
        >
            <div className="section-header">
                <h3>Review Extracted Information</h3>
                <p>Verify the information extracted from your documents</p>
            </div>

            <div className="extracted-data-grid">
                {Object.entries(uploadedDocuments).map(([docType, docData]) => (
                    <Card key={docType} className="extracted-data-card">
                        <h4>{documentTypes.find(d => d.key === docType)?.label}</h4>
                        
                        <div className="extracted-fields">
                            {Object.entries(docData.structured_data || {}).map(([field, value]) => (
                                value && (
                                    <div key={field} className="field-row">
                                        <span className="field-label">
                                            {field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                                        </span>
                                        <span className="field-value">{value}</span>
                                    </div>
                                )
                            ))}
                        </div>

                        <div className="document-actions">
                            <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => {
                                    alert(`Raw text from ${docType}:\n\n${docData.extracted_text.substring(0, 500)}...`);
                                }}
                            >
                                <Eye size={16} />
                                View Raw Text
                            </Button>
                        </div>
                    </Card>
                ))}
            </div>

            <div className="step-actions">
                <Button variant="outline" onClick={() => setCurrentStep(1)}>
                    Back to Upload
                </Button>
                <Button onClick={handleAnalyzeDocuments} disabled={loading}>
                    {loading ? 'Analyzing...' : 'Analyze & Calculate'}
                </Button>
            </div>
        </motion.div>
    );

    const renderAnalysisResults = () => (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="analysis-results-section"
        >
            <div className="section-header">
                <h3>ITR Analysis & Tax Calculation</h3>
                <p>Comprehensive analysis of your tax situation with AI recommendations</p>
            </div>

            {analysisResult && (
                <div className="analysis-grid">
                    {/* Personal Information */}
                    <Card className="personal-info-card">
                        <h4><User size={20} /> Personal Information</h4>
                        <div className="info-grid">
                            {Object.entries(analysisResult.personal_info || {}).map(([key, value]) => (
                                value && (
                                    <div key={key} className="info-item">
                                        <span className="label">{key.replace(/_/g, ' ').toUpperCase()}:</span>
                                        <span className="value">{value}</span>
                                    </div>
                                )
                            ))}
                        </div>
                    </Card>

                    {/* Tax Calculation */}
                    <Card className="tax-calculation-card">
                        <h4><Calculator size={20} /> Tax Calculation</h4>
                        
                        <div className="regime-comparison">
                            <div className="regime old-regime">
                                <h5>Old Regime</h5>
                                <div className="tax-amount">₹{analysisResult.tax_calculations?.old_regime?.total_tax?.toLocaleString() || 0}</div>
                                <div className="tax-details">
                                    <span>Taxable Income: ₹{analysisResult.tax_calculations?.old_regime?.taxable_income?.toLocaleString() || 0}</span>
                                    <span>Deductions: ₹{analysisResult.tax_calculations?.old_regime?.total_deductions?.toLocaleString() || 0}</span>
                                </div>
                            </div>
                            
                            <div className="regime new-regime">
                                <h5>New Regime</h5>
                                <div className="tax-amount">₹{analysisResult.tax_calculations?.new_regime?.total_tax?.toLocaleString() || 0}</div>
                                <div className="tax-details">
                                    <span>Taxable Income: ₹{analysisResult.tax_calculations?.new_regime?.taxable_income?.toLocaleString() || 0}</span>
                                    <span>Deductions: ₹{analysisResult.tax_calculations?.new_regime?.total_deductions?.toLocaleString() || 0}</span>
                                </div>
                            </div>
                        </div>

                        <div className="recommended-regime">
                            <CheckCircle size={16} />
                            <span>Recommended: {analysisResult.tax_calculations?.recommended_regime?.toUpperCase()} Regime</span>
                            <span className="savings">Save ₹{analysisResult.tax_calculations?.tax_savings?.toLocaleString() || 0}</span>
                        </div>
                    </Card>

                    {/* Refund Analysis */}
                    <Card className="refund-analysis-card">
                        <h4><DollarSign size={20} /> Refund Analysis</h4>
                        
                        <div className="refund-summary">
                            <div className="refund-item">
                                <span>TDS Deducted:</span>
                                <span className="amount">₹{analysisResult.refund_analysis?.tds_deducted?.toLocaleString() || 0}</span>
                            </div>
                            <div className="refund-item">
                                <span>Tax Liability:</span>
                                <span className="amount">₹{analysisResult.refund_analysis?.tax_liability?.toLocaleString() || 0}</span>
                            </div>
                            <div className={`refund-result ${analysisResult.refund_analysis?.refund_status}`}>
                                {analysisResult.refund_analysis?.refund_amount > 0 ? (
                                    <>
                                        <CheckCircle size={20} />
                                        <span>Refund Due: ₹{analysisResult.refund_analysis?.refund_amount?.toLocaleString()}</span>
                                    </>
                                ) : analysisResult.refund_analysis?.additional_tax_due > 0 ? (
                                    <>
                                        <AlertCircle size={20} />
                                        <span>Additional Tax: ₹{analysisResult.refund_analysis?.additional_tax_due?.toLocaleString()}</span>
                                    </>
                                ) : (
                                    <>
                                        <Check size={20} />
                                        <span>No Refund, No Additional Tax</span>
                                    </>
                                )}
                            </div>
                        </div>
                    </Card>

                    {/* AI Suggestions */}
                    <Card className="ai-suggestions-card full-width">
                        <h4><Lightbulb size={20} /> AI Tax Optimization Suggestions</h4>
                        
                        <div className="suggestions-list">
                            {analysisResult.ai_suggestions?.map((suggestion, index) => (
                                <div key={index} className={`suggestion-item priority-${suggestion.priority}`}>
                                    <div className="suggestion-header">
                                        <span className={`priority-badge ${suggestion.priority}`}>
                                            {suggestion.priority.toUpperCase()}
                                        </span>
                                        <h5>{suggestion.title}</h5>
                                        {suggestion.potential_savings > 0 && (
                                            <span className="savings-badge">
                                                Save ₹{suggestion.potential_savings.toLocaleString()}
                                            </span>
                                        )}
                                    </div>
                                    <p>{suggestion.description}</p>
                                    <div className="suggestion-action">
                                        <strong>Action:</strong> {suggestion.action}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </Card>

                    {/* Document Summary */}
                    <Card className="document-summary-card">
                        <h4><FileText size={20} /> Document Summary</h4>
                        
                        <div className="summary-stats">
                            <div className="stat">
                                <span className="stat-value">{analysisResult.document_summary?.total_documents || 0}</span>
                                <span className="stat-label">Documents Processed</span>
                            </div>
                            <div className="stat">
                                <span className="stat-value">{analysisResult.document_summary?.completeness_score?.toFixed(0) || 0}%</span>
                                <span className="stat-label">Completeness Score</span>
                            </div>
                            <div className="stat">
                                <span className="stat-value">{analysisResult.compliance_check?.compliance_score || 0}%</span>
                                <span className="stat-label">Compliance Score</span>
                            </div>
                        </div>
                    </Card>
                </div>
            )}

            <div className="step-actions">
                <Button variant="outline" onClick={() => setCurrentStep(2)}>
                    Back to Review
                </Button>
                <Button onClick={handleSubmitITR} className="submit-itr-btn">
                    <Send size={16} />
                    Submit ITR Return
                </Button>
            </div>
        </motion.div>
    );

    if (submitted) {
        return (
            <div className="relative min-h-screen w-full overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-[hsl(var(--gov-navy))] via-[hsl(var(--gov-green-dark))] to-[hsl(var(--gov-green))]" />
                <div className="absolute inset-0 opacity-[0.03]" style={{
                    backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
                    backgroundSize: '40px 40px'
                }} />
                <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-[hsl(var(--gov-gold))] opacity-[0.08] blur-[150px] rounded-full -translate-y-1/2 translate-x-1/3" />

                <div className="relative z-10">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 flex items-center justify-center min-h-screen">
                        <motion.div
                            className="success-state"
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                        >
                            <div className="success-icon">
                                <Check size={64} />
                            </div>
                            <h2>ITR Submitted Successfully!</h2>
                            <p>Your return for AY 2024-25 has been filed.</p>
                            {analysisResult?.refund_analysis?.refund_amount > 0 && (
                                <div className="refund-info">
                                    <h3>Expected Refund: ₹{analysisResult.refund_analysis.refund_amount.toLocaleString()}</h3>
                                    <p>Refund will be processed within 30-45 days</p>
                                </div>
                            )}
                            <div className="success-actions">
                                <Button onClick={() => window.print()}>
                                    <Download size={16} />
                                    Download Receipt
                                </Button>
                                <NavLink to="/">
                                    <Button variant="outline">Return to Home</Button>
                                </NavLink>
                            </div>
                        </motion.div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="relative min-h-screen w-full overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-[hsl(var(--gov-navy))] via-[hsl(var(--gov-green-dark))] to-[hsl(var(--gov-green))]" />
            <div className="absolute inset-0 opacity-[0.03]" style={{
                backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
                backgroundSize: '40px 40px'
            }} />
            <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-[hsl(var(--gov-gold))] opacity-[0.08] blur-[150px] rounded-full -translate-y-1/2 translate-x-1/3" />

            <div className="relative z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                        <div className="itr-header">
                            <h2>Smart ITR Filing Assistant</h2>
                            <p>Upload documents, get AI analysis, and file your return with confidence</p>
                        </div>

                        {/* Progress Steps */}
                        <div className="progress-steps">
                            <div className={`step ${currentStep >= 1 ? 'active' : ''}`}>
                                <span className="step-number">1</span>
                                <span className="step-label">Upload Documents</span>
                            </div>
                            <div className={`step ${currentStep >= 2 ? 'active' : ''}`}>
                                <span className="step-number">2</span>
                                <span className="step-label">Review Data</span>
                            </div>
                            <div className={`step ${currentStep >= 3 ? 'active' : ''}`}>
                                <span className="step-number">3</span>
                                <span className="step-label">Analysis & Filing</span>
                            </div>
                        </div>

                        {/* Step Content */}
                        <AnimatePresence mode="wait">
                            {currentStep === 1 && renderDocumentUpload()}
                            {currentStep === 2 && renderDocumentReview()}
                            {currentStep === 3 && renderAnalysisResults()}
                        </AnimatePresence>

                        {loading && (
                            <div className="loading-overlay">
                                <div className="loading-spinner"></div>
                                <p>Processing documents and analyzing tax situation...</p>
                            </div>
                        )}
                    </motion.div>
                </div>
            </div>
        </div>
    );
};

export default ITRFilingPage;
