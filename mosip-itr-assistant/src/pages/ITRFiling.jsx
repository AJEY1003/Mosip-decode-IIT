import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { NavLink } from 'react-router-dom';
import { Calculator, Send, Check } from 'lucide-react';
import Input from '../components/Input';
import Button from '../components/Button';
import Card from '../components/Card';
import './ITRFiling.css';

const ITRFilingPage = () => {
    const [formData, setFormData] = useState({
        income: 1200000,
        deductions: 150000,
    });

    const [result, setResult] = useState({
        taxableIncome: 0,
        taxPercentage: 0,
        taxAmount: 0
    });

    const [submitted, setSubmitted] = useState(false);

    useEffect(() => {
        // Auto-calculate on mount for demo
        handleCalculate();
    }, []);

    const handleCalculate = () => {
        const taxable = Math.max(0, formData.income - formData.deductions);
        let tax = 0;

        // Simple mock tax logic
        if (taxable > 1000000) {
            tax = 112500 + (taxable - 1000000) * 0.3;
        } else if (taxable > 500000) {
            tax = 12500 + (taxable - 500000) * 0.2;
        }

        const percentage = taxable > 0 ? ((tax / taxable) * 100).toFixed(1) : 0;

        setResult({
            taxableIncome: taxable,
            taxAmount: tax,
            taxPercentage: percentage
        });
    };

    const handleSubmit = () => {
        setSubmitted(true);
    };

    if (submitted) {
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
                    <p>Your return for AY 2026-27 has been filed.</p>
                    <NavLink to="/">
                        <Button>Return to Home</Button>
                    </NavLink>
                </motion.div>
                    </div>
                </div>
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
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
            >
                <div className="itr-header">
                    <h2>File Income Tax Return</h2>
                    <p>Calculate and submit your final liability.</p>
                </div>

                <div className="itr-grid">
                    <Card title="Income Details">
                        <Input
                            label="Total Income"
                            type="number"
                            value={formData.income}
                            onChange={(e) => setFormData({ ...formData, income: Number(e.target.value) })}
                        />
                        <Input
                            label="Total Deductions"
                            type="number"
                            value={formData.deductions}
                            onChange={(e) => setFormData({ ...formData, deductions: Number(e.target.value) })}
                        />
                        <Button onClick={handleCalculate} icon={Calculator} className="full-width">
                            Calculate Tax
                        </Button>
                    </Card>

                    <Card title="Tax Calculation" className="result-card">
                        <div className="result-row">
                            <span>Taxable Income:</span>
                            <span className="amount">₹ {result.taxableIncome.toLocaleString()}</span>
                        </div>
                        <div className="result-row">
                            <span>Effective Tax Rate:</span>
                            <span>{result.taxPercentage}%</span>
                        </div>

                        <div className="tax-highlight">
                            <p>Estimated Tax Liability</p>
                            <h3>₹ {result.taxAmount.toLocaleString()}</h3>
                        </div>

                        <Button
                            variant="primary"
                            onClick={handleSubmit}
                            icon={Send}
                            className="full-width submit-btn"
                        >
                            Submit ITR
                        </Button>
                    </Card>
                </div>
            </motion.div>
                </div>
            </div>
        </div>
    );
};

export default ITRFilingPage;
