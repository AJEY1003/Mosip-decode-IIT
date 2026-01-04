import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { NavLink } from 'react-router-dom';
import { 
    Send, 
    Check, 
    Upload, 
    QrCode, 
    User, 
    DollarSign,
    Calculator,
    CreditCard,
    AlertCircle,
    CheckCircle,
    Download
} from 'lucide-react';
import Button from '../components/Button';
import apiService from '../services/api';
import './ITRFiling.css';

const ITRFilingPage = () => {
    const [itrFormData, setItrFormData] = useState({
        // Personal Information
        name: '',
        pan: '',
        aadhaar: '',
        date_of_birth: '',
        address: '',
        phone: '',
        email: '',
        
        // Income Details
        gross_salary: 0,
        basic_salary: 0,
        hra_received: 0,
        other_allowances: 0,
        interest_income: 0,
        other_income: 0,
        
        // Deductions
        standard_deduction: 50000,
        section_80c: 0,
        section_80d: 0,
        professional_tax: 0,
        
        // Tax Details
        tds_deducted: 0,
        advance_tax: 0,
        tax_regime: 'new'
    });

    const [loading, setLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState(null);
    const [qrProcessed, setQrProcessed] = useState(false);

    // Handle QR code upload
    const handleQRUpload = async (file) => {
        if (!file) return;

        setLoading(true);
        setError(null);

        try {
            // For demo, we'll use manual input since QR image reading requires additional libraries
            const qrText = prompt('Please paste the QR code data (JSON string):');
            
            if (qrText) {
                const decoded = await apiService.decodeQRData(qrText);
                
                if (decoded.status === 'success') {
                    const formSections = decoded.form_sections;
                    
                    // Auto-fill the form with decoded data
                    setItrFormData({
                        // Personal Information
                        name: formSections.personal_info?.name || '',
                        pan: formSections.personal_info?.pan || '',
                        aadhaar: formSections.personal_info?.aadhaar || '',
                        date_of_birth: formSections.personal_info?.date_of_birth || '',
                        address: formSections.personal_info?.address || '',
                        phone: formSections.personal_info?.phone || '',
                        email: formSections.personal_info?.email || '',
                        
                        // Income Details
                        gross_salary: formSections.income_details?.gross_salary || 0,
                        basic_salary: formSections.income_details?.basic_salary || 0,
                        hra_received: formSections.income_details?.hra_received || 0,
                        other_allowances: formSections.income_details?.other_allowances || 0,
                        interest_income: formSections.income_details?.interest_income || 0,
                        other_income: formSections.income_details?.other_income || 0,
                        
                        // Deductions
                        standard_deduction: formSections.deductions?.standard_deduction || 50000,
                        section_80c: formSections.deductions?.section_80c || 0,
                        section_80d: formSections.deductions?.section_80d || 0,
                        professional_tax: formSections.deductions?.professional_tax || 0,
                        
                        // Tax Details
                        tds_deducted: formSections.tax_details?.tds_deducted || 0,
                        advance_tax: formSections.tax_details?.advance_tax || 0,
                        tax_regime: formSections.tax_details?.tax_regime || 'new'
                    });
                    
                    setQrProcessed(true);
                    console.log('✅ QR Code processed and form auto-filled');
                } else {
                    setError('Failed to decode QR code data');
                }
            }
        } catch (error) {
            console.error('QR processing error:', error);
            setError('Failed to process QR code. Please check the data format.');
        } finally {
            setLoading(false);
        }
    };

    // Handle form field changes
    const handleFormChange = (field, value) => {
        setItrFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    // Calculate tax liability
    const calculateTax = () => {
        const totalIncome = itrFormData.gross_salary + itrFormData.interest_income + itrFormData.other_income;
        const totalDeductions = itrFormData.standard_deduction + itrFormData.section_80c + itrFormData.section_80d + itrFormData.professional_tax;
        const taxableIncome = Math.max(0, totalIncome - totalDeductions);
        
        let tax = 0;
        if (itrFormData.tax_regime === 'new') {
            // New regime tax slabs
            if (taxableIncome > 1500000) {
                tax = 187500 + (taxableIncome - 1500000) * 0.30;
            } else if (taxableIncome > 1200000) {
                tax = 112500 + (taxableIncome - 1200000) * 0.20;
            } else if (taxableIncome > 900000) {
                tax = 67500 + (taxableIncome - 900000) * 0.15;
            } else if (taxableIncome > 600000) {
                tax = 37500 + (taxableIncome - 600000) * 0.10;
            } else if (taxableIncome > 300000) {
                tax = (taxableIncome - 300000) * 0.05;
            }
        } else {
            // Old regime tax slabs
            if (taxableIncome > 1000000) {
                tax = 112500 + (taxableIncome - 1000000) * 0.30;
            } else if (taxableIncome > 500000) {
                tax = 12500 + (taxableIncome - 500000) * 0.20;
            } else if (taxableIncome > 250000) {
                tax = (taxableIncome - 250000) * 0.05;
            }
        }

        // Add cess (4%)
        tax = tax * 1.04;
        
        return Math.round(tax);
    };

    // Calculate refund or tax due
    const getRefundOrTaxDue = () => {
        const taxLiability = calculateTax();
        const taxPaid = itrFormData.tds_deducted + itrFormData.advance_tax;
        return taxPaid - taxLiability;
    };

    // Check if form is complete
    const isFormComplete = () => {
        return itrFormData.name && 
               itrFormData.pan && 
               itrFormData.aadhaar && 
               itrFormData.gross_salary > 0;
    };

    // Submit ITR
    const handleSubmitITR = () => {
        if (!isFormComplete()) {
            setError('Please fill all required fields (Name, PAN, Aadhaar, Gross Salary)');
            return;
        }
        setSubmitted(true);
    };

    if (submitted) {
        const refundOrTaxDue = getRefundOrTaxDue();
        const isRefund = refundOrTaxDue >= 0;

        return (
            <div className="relative min-h-screen w-full overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-[hsl(var(--gov-navy))] via-[hsl(var(--gov-green-dark))] to-[hsl(var(--gov-green))]" />
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
                            
                            <div className="refund-info">
                                <h3>
                                    {isRefund 
                                        ? `Expected Refund: ₹${Math.abs(refundOrTaxDue).toLocaleString()}`
                                        : `Tax Due: ₹${Math.abs(refundOrTaxDue).toLocaleString()}`
                                    }
                                </h3>
                                <p>
                                    {isRefund 
                                        ? 'Refund will be processed within 30-45 days'
                                        : 'Please pay the due amount before the deadline'
                                    }
                                </p>
                            </div>
                            
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
            <div className="relative z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                        <div className="itr-header">
                            <h2>File Income Tax Return (ITR-1)</h2>
                            <p>Fill the form manually or upload QR code to auto-fill</p>
                        </div>

                        <div className="itr-main-layout">
                            {/* Left Side - ITR Form */}
                            <div className="itr-form-container">
                                <div className="form-header">
                                    <h3>ITR-1 (Sahaj) Form</h3>
                                    <div className="form-status">
                                        {qrProcessed && (
                                            <div className="qr-status">
                                                <CheckCircle size={16} />
                                                <span>Auto-filled from QR Code</span>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className="form-sections">
                                    {/* Personal Information */}
                                    <div className="form-section">
                                        <h4><User size={18} /> Personal Information</h4>
                                        <div className="form-grid">
                                            <div className="form-field">
                                                <label>Full Name *</label>
                                                <input
                                                    type="text"
                                                    value={itrFormData.name}
                                                    onChange={(e) => handleFormChange('name', e.target.value)}
                                                    placeholder="Enter full name"
                                                    className="form-input"
                                                />
                                            </div>
                                            
                                            <div className="form-field">
                                                <label>PAN Number *</label>
                                                <input
                                                    type="text"
                                                    value={itrFormData.pan}
                                                    onChange={(e) => handleFormChange('pan', e.target.value.toUpperCase())}
                                                    placeholder="ABCDE1234F"
                                                    maxLength={10}
                                                    className="form-input"
                                                />
                                            </div>
                                            
                                            <div className="form-field">
                                                <label>Aadhaar Number *</label>
                                                <input
                                                    type="text"
                                                    value={itrFormData.aadhaar}
                                                    onChange={(e) => handleFormChange('aadhaar', e.target.value)}
                                                    placeholder="123456789012"
                                                    maxLength={12}
                                                    className="form-input"
                                                />
                                            </div>
                                            
                                            <div className="form-field">
                                                <label>Date of Birth</label>
                                                <input
                                                    type="text"
                                                    value={itrFormData.date_of_birth}
                                                    onChange={(e) => handleFormChange('date_of_birth', e.target.value)}
                                                    placeholder="DD/MM/YYYY"
                                                    className="form-input"
                                                />
                                            </div>
                                            
                                            <div className="form-field full-width">
                                                <label>Address</label>
                                                <textarea
                                                    value={itrFormData.address}
                                                    onChange={(e) => handleFormChange('address', e.target.value)}
                                                    placeholder="Enter complete address"
                                                    className="form-textarea"
                                                    rows={2}
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Income Details */}
                                    <div className="form-section">
                                        <h4><DollarSign size={18} /> Income Details</h4>
                                        <div className="form-grid">
                                            <div className="form-field">
                                                <label>Gross Salary *</label>
                                                <input
                                                    type="number"
                                                    value={itrFormData.gross_salary}
                                                    onChange={(e) => handleFormChange('gross_salary', parseInt(e.target.value) || 0)}
                                                    placeholder="0"
                                                    className="form-input"
                                                />
                                            </div>
                                            
                                            <div className="form-field">
                                                <label>HRA Received</label>
                                                <input
                                                    type="number"
                                                    value={itrFormData.hra_received}
                                                    onChange={(e) => handleFormChange('hra_received', parseInt(e.target.value) || 0)}
                                                    placeholder="0"
                                                    className="form-input"
                                                />
                                            </div>
                                            
                                            <div className="form-field">
                                                <label>Other Allowances</label>
                                                <input
                                                    type="number"
                                                    value={itrFormData.other_allowances}
                                                    onChange={(e) => handleFormChange('other_allowances', parseInt(e.target.value) || 0)}
                                                    placeholder="0"
                                                    className="form-input"
                                                />
                                            </div>
                                            
                                            <div className="form-field">
                                                <label>Interest Income</label>
                                                <input
                                                    type="number"
                                                    value={itrFormData.interest_income}
                                                    onChange={(e) => handleFormChange('interest_income', parseInt(e.target.value) || 0)}
                                                    placeholder="0"
                                                    className="form-input"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Deductions */}
                                    <div className="form-section">
                                        <h4><Calculator size={18} /> Deductions</h4>
                                        <div className="form-grid">
                                            <div className="form-field">
                                                <label>Standard Deduction</label>
                                                <input
                                                    type="number"
                                                    value={itrFormData.standard_deduction}
                                                    onChange={(e) => handleFormChange('standard_deduction', parseInt(e.target.value) || 0)}
                                                    className="form-input"
                                                />
                                            </div>
                                            
                                            <div className="form-field">
                                                <label>Section 80C (Max ₹1.5L)</label>
                                                <input
                                                    type="number"
                                                    value={itrFormData.section_80c}
                                                    onChange={(e) => handleFormChange('section_80c', Math.min(parseInt(e.target.value) || 0, 150000))}
                                                    placeholder="0"
                                                    max={150000}
                                                    className="form-input"
                                                />
                                            </div>
                                            
                                            <div className="form-field">
                                                <label>Section 80D (Max ₹25K)</label>
                                                <input
                                                    type="number"
                                                    value={itrFormData.section_80d}
                                                    onChange={(e) => handleFormChange('section_80d', Math.min(parseInt(e.target.value) || 0, 25000))}
                                                    placeholder="0"
                                                    max={25000}
                                                    className="form-input"
                                                />
                                            </div>
                                            
                                            <div className="form-field">
                                                <label>Professional Tax</label>
                                                <input
                                                    type="number"
                                                    value={itrFormData.professional_tax}
                                                    onChange={(e) => handleFormChange('professional_tax', parseInt(e.target.value) || 0)}
                                                    placeholder="0"
                                                    className="form-input"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Tax Details */}
                                    <div className="form-section">
                                        <h4><CreditCard size={18} /> Tax Details</h4>
                                        <div className="form-grid">
                                            <div className="form-field">
                                                <label>TDS Deducted</label>
                                                <input
                                                    type="number"
                                                    value={itrFormData.tds_deducted}
                                                    onChange={(e) => handleFormChange('tds_deducted', parseInt(e.target.value) || 0)}
                                                    placeholder="0"
                                                    className="form-input"
                                                />
                                            </div>
                                            
                                            <div className="form-field">
                                                <label>Advance Tax</label>
                                                <input
                                                    type="number"
                                                    value={itrFormData.advance_tax}
                                                    onChange={(e) => handleFormChange('advance_tax', parseInt(e.target.value) || 0)}
                                                    placeholder="0"
                                                    className="form-input"
                                                />
                                            </div>
                                            
                                            <div className="form-field">
                                                <label>Tax Regime</label>
                                                <select
                                                    value={itrFormData.tax_regime}
                                                    onChange={(e) => handleFormChange('tax_regime', e.target.value)}
                                                    className="form-select"
                                                >
                                                    <option value="new">New Tax Regime</option>
                                                    <option value="old">Old Tax Regime</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Tax Summary */}
                                    <div className="tax-summary">
                                        <h4>Tax Calculation Summary</h4>
                                        <div className="summary-grid">
                                            <div className="summary-item">
                                                <span>Total Income:</span>
                                                <span>₹{(itrFormData.gross_salary + itrFormData.interest_income + itrFormData.other_income).toLocaleString()}</span>
                                            </div>
                                            <div className="summary-item">
                                                <span>Tax Liability:</span>
                                                <span>₹{calculateTax().toLocaleString()}</span>
                                            </div>
                                            <div className="summary-item">
                                                <span>Tax Paid (TDS + Advance):</span>
                                                <span>₹{(itrFormData.tds_deducted + itrFormData.advance_tax).toLocaleString()}</span>
                                            </div>
                                            <div className={`summary-item highlight ${getRefundOrTaxDue() >= 0 ? 'refund' : 'tax-due'}`}>
                                                <span>{getRefundOrTaxDue() >= 0 ? 'Refund Due:' : 'Tax Due:'}</span>
                                                <span>₹{Math.abs(getRefundOrTaxDue()).toLocaleString()}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Submit Button */}
                                <div className="form-submit">
                                    <Button
                                        onClick={handleSubmitITR}
                                        disabled={!isFormComplete()}
                                        className="submit-itr-btn"
                                    >
                                        <Send size={16} />
                                        Submit ITR Return
                                    </Button>
                                </div>
                            </div>

                            {/* Right Side - QR Code Upload */}
                            <div className="qr-upload-container">
                                <div className="qr-upload-card">
                                    <div className="qr-header">
                                        <QrCode size={32} />
                                        <h3>Upload QR Code</h3>
                                        <p>Upload the QR code generated from your documents to auto-fill the form</p>
                                    </div>

                                    <div className="qr-upload-area">
                                        <input
                                            type="file"
                                            accept="image/*"
                                            onChange={(e) => handleQRUpload(e.target.files[0])}
                                            style={{ display: 'none' }}
                                            id="qr-upload"
                                        />
                                        
                                        <label htmlFor="qr-upload" className="qr-upload-label">
                                            <Upload size={24} />
                                            <span>Click to upload QR code image</span>
                                            <small>Supports PNG, JPG, JPEG</small>
                                        </label>
                                    </div>

                                    <div className="qr-help">
                                        <AlertCircle size={16} />
                                        <span>Don't have a QR code? Go to <NavLink to="/upload" className="help-link">Upload Documents</NavLink> to generate one.</span>
                                    </div>

                                    {loading && (
                                        <div className="qr-loading">
                                            <div className="loading-spinner"></div>
                                            <span>Processing QR code...</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Error Display */}
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="error-message"
                            >
                                <AlertCircle size={16} />
                                <span>{error}</span>
                            </motion.div>
                        )}
                    </motion.div>
                </div>
            </div>
        </div>
    );
};

export default ITRFilingPage;