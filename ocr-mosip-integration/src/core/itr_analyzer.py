#!/usr/bin/env python3
"""
ITR Analysis Engine
Analyzes multiple documents and calculates tax refunds with AI suggestions
"""
import re
from typing import Dict, List, Tuple
from datetime import datetime
import json

class ITRAnalyzer:
    """
    Comprehensive ITR analysis engine that processes multiple documents
    and provides tax calculations with AI suggestions
    """
    
    def __init__(self):
        # Tax slabs for AY 2024-25 (Old Regime)
        self.tax_slabs_old = [
            (250000, 0.0),      # Up to 2.5L - 0%
            (500000, 0.05),     # 2.5L to 5L - 5%
            (1000000, 0.20),    # 5L to 10L - 20%
            (float('inf'), 0.30) # Above 10L - 30%
        ]
        
        # Tax slabs for AY 2024-25 (New Regime)
        self.tax_slabs_new = [
            (300000, 0.0),      # Up to 3L - 0%
            (600000, 0.05),     # 3L to 6L - 5%
            (900000, 0.10),     # 6L to 9L - 10%
            (1200000, 0.15),    # 9L to 12L - 15%
            (1500000, 0.20),    # 12L to 15L - 20%
            (float('inf'), 0.30) # Above 15L - 30%
        ]
        
        # Standard deductions and exemptions
        self.standard_deduction = 50000
        self.hra_exemption_rate = 0.5
        self.section_80c_limit = 150000
        self.section_80d_limit = 25000
        
    def analyze_documents(self, documents: Dict[str, Dict]) -> Dict:
        """
        Analyze multiple documents and extract consolidated information
        
        Args:
            documents: Dictionary with document type as key and extracted data as value
            
        Returns:
            Comprehensive analysis with tax calculations and suggestions
        """
        analysis = {
            'personal_info': {},
            'income_details': {},
            'deductions': {},
            'tax_calculations': {},
            'refund_analysis': {},
            'ai_suggestions': [],
            'document_summary': {},
            'compliance_check': {}
        }
        
        # Extract and consolidate information from all documents
        analysis['personal_info'] = self._extract_personal_info(documents)
        analysis['income_details'] = self._extract_income_details(documents)
        analysis['deductions'] = self._extract_deductions(documents)
        analysis['document_summary'] = self._create_document_summary(documents)
        
        # Perform tax calculations
        analysis['tax_calculations'] = self._calculate_taxes(
            analysis['income_details'], 
            analysis['deductions']
        )
        
        # Analyze refund potential
        analysis['refund_analysis'] = self._analyze_refund(
            analysis['tax_calculations'],
            analysis['income_details']
        )
        
        # Generate AI suggestions
        analysis['ai_suggestions'] = self._generate_ai_suggestions(
            analysis['income_details'],
            analysis['deductions'],
            analysis['tax_calculations'],
            documents
        )
        
        # Compliance checks
        analysis['compliance_check'] = self._perform_compliance_checks(
            analysis['personal_info'],
            analysis['income_details'],
            documents
        )
        
        return analysis
    
    def _extract_personal_info(self, documents: Dict) -> Dict:
        """Extract consolidated personal information"""
        personal_info = {
            'name': None,
            'pan': None,
            'aadhaar': None,
            'date_of_birth': None,
            'address': None,
            'phone': None,
            'email': None
        }
        
        # Priority order for data sources
        priority_order = ['aadhaar', 'pan_card', 'form16', 'bank_statement']
        
        for doc_type in priority_order:
            if doc_type in documents:
                doc_data = documents[doc_type].get('structured_data', {})
                
                # Extract with priority
                if not personal_info['name'] and doc_data.get('name'):
                    personal_info['name'] = doc_data['name']
                if not personal_info['pan'] and doc_data.get('pan_number'):
                    personal_info['pan'] = doc_data['pan_number']
                if not personal_info['aadhaar'] and doc_data.get('aadhaar_number'):
                    personal_info['aadhaar'] = doc_data['aadhaar_number']
                if not personal_info['date_of_birth'] and doc_data.get('date_of_birth'):
                    personal_info['date_of_birth'] = doc_data['date_of_birth']
                if not personal_info['address'] and doc_data.get('address'):
                    personal_info['address'] = doc_data['address']
                if not personal_info['phone'] and doc_data.get('phone'):
                    personal_info['phone'] = doc_data['phone']
                if not personal_info['email'] and doc_data.get('email'):
                    personal_info['email'] = doc_data['email']
        
        return personal_info
    
    def _extract_income_details(self, documents: Dict) -> Dict:
        """Extract income information from documents"""
        income_details = {
            'gross_salary': 0,
            'basic_salary': 0,
            'hra_received': 0,
            'other_allowances': 0,
            'tds_deducted': 0,
            'employer_name': None,
            'employment_period': None,
            'other_income': 0,
            'interest_income': 0,
            'rental_income': 0
        }
        
        # Extract from Form 16
        if 'form16' in documents:
            form16_data = documents['form16'].get('structured_data', {})
            raw_text = documents['form16'].get('extracted_text', '')
            
            if form16_data.get('income'):
                income_details['gross_salary'] = int(form16_data['income'])
            if form16_data.get('employer'):
                income_details['employer_name'] = form16_data['employer']
            
            # Extract TDS from text
            tds_match = re.search(r'tds\s*(?:deducted|amount)[\s:]*(?:rs\.?|₹)?\s*([0-9,]+)', raw_text, re.IGNORECASE)
            if tds_match:
                income_details['tds_deducted'] = int(tds_match.group(1).replace(',', ''))
            
            # Extract HRA
            hra_match = re.search(r'hra[\s:]*(?:rs\.?|₹)?\s*([0-9,]+)', raw_text, re.IGNORECASE)
            if hra_match:
                income_details['hra_received'] = int(hra_match.group(1).replace(',', ''))
        
        # Extract from Bank Statement
        if 'bank_statement' in documents:
            bank_data = documents['bank_statement'].get('structured_data', {})
            raw_text = documents['bank_statement'].get('extracted_text', '')
            
            # Look for salary credits
            salary_matches = re.findall(r'salary[\s:]*(?:rs\.?|₹)?\s*([0-9,]+)', raw_text, re.IGNORECASE)
            if salary_matches:
                monthly_salary = max([int(s.replace(',', '')) for s in salary_matches])
                if not income_details['gross_salary']:
                    income_details['gross_salary'] = monthly_salary * 12
            
            # Look for interest income
            interest_matches = re.findall(r'interest[\s:]*(?:rs\.?|₹)?\s*([0-9,]+)', raw_text, re.IGNORECASE)
            if interest_matches:
                income_details['interest_income'] = sum([int(i.replace(',', '')) for i in interest_matches])
        
        return income_details
    
    def _extract_deductions(self, documents: Dict) -> Dict:
        """Extract deduction information"""
        deductions = {
            'section_80c': 0,
            'section_80d': 0,
            'hra_exemption': 0,
            'standard_deduction': self.standard_deduction,
            'professional_tax': 0,
            'other_deductions': 0
        }
        
        # Calculate HRA exemption if HRA is received
        for doc_type, doc_data in documents.items():
            raw_text = doc_data.get('extracted_text', '')
            
            # Look for 80C investments
            pf_matches = re.findall(r'(?:pf|provident\s*fund)[\s:]*(?:rs\.?|₹)?\s*([0-9,]+)', raw_text, re.IGNORECASE)
            if pf_matches:
                deductions['section_80c'] += sum([int(p.replace(',', '')) for p in pf_matches])
            
            # Look for insurance premiums (80D)
            insurance_matches = re.findall(r'(?:insurance|medical)[\s:]*(?:rs\.?|₹)?\s*([0-9,]+)', raw_text, re.IGNORECASE)
            if insurance_matches:
                deductions['section_80d'] += sum([int(i.replace(',', '')) for i in insurance_matches])
            
            # Professional tax
            pt_matches = re.findall(r'professional\s*tax[\s:]*(?:rs\.?|₹)?\s*([0-9,]+)', raw_text, re.IGNORECASE)
            if pt_matches:
                deductions['professional_tax'] += sum([int(p.replace(',', '')) for p in pt_matches])
        
        # Cap deductions at limits
        deductions['section_80c'] = min(deductions['section_80c'], self.section_80c_limit)
        deductions['section_80d'] = min(deductions['section_80d'], self.section_80d_limit)
        
        return deductions
    
    def _calculate_taxes(self, income_details: Dict, deductions: Dict) -> Dict:
        """Calculate tax liability under both regimes"""
        gross_income = income_details['gross_salary'] + income_details['other_income'] + income_details['interest_income']
        
        # Old regime calculation
        taxable_income_old = gross_income - deductions['standard_deduction'] - deductions['section_80c'] - deductions['section_80d'] - deductions['professional_tax']
        tax_old = self._calculate_tax_by_slabs(taxable_income_old, self.tax_slabs_old)
        
        # New regime calculation (no deductions except standard)
        taxable_income_new = gross_income - deductions['standard_deduction']
        tax_new = self._calculate_tax_by_slabs(taxable_income_new, self.tax_slabs_new)
        
        # Add cess (4% on tax)
        cess_old = tax_old * 0.04
        cess_new = tax_new * 0.04
        
        total_tax_old = tax_old + cess_old
        total_tax_new = tax_new + cess_new
        
        return {
            'gross_income': gross_income,
            'old_regime': {
                'taxable_income': taxable_income_old,
                'tax_before_cess': tax_old,
                'cess': cess_old,
                'total_tax': total_tax_old,
                'total_deductions': sum(deductions.values())
            },
            'new_regime': {
                'taxable_income': taxable_income_new,
                'tax_before_cess': tax_new,
                'cess': cess_new,
                'total_tax': total_tax_new,
                'total_deductions': deductions['standard_deduction']
            },
            'recommended_regime': 'old' if total_tax_old < total_tax_new else 'new',
            'tax_savings': abs(total_tax_old - total_tax_new)
        }
    
    def _calculate_tax_by_slabs(self, taxable_income: float, tax_slabs: List[Tuple]) -> float:
        """Calculate tax based on income slabs"""
        if taxable_income <= 0:
            return 0
        
        tax = 0
        previous_limit = 0
        
        for limit, rate in tax_slabs:
            if taxable_income > previous_limit:
                taxable_in_slab = min(taxable_income, limit) - previous_limit
                tax += taxable_in_slab * rate
                previous_limit = limit
            else:
                break
        
        return tax
    
    def _analyze_refund(self, tax_calculations: Dict, income_details: Dict) -> Dict:
        """Analyze potential tax refund"""
        recommended_regime = tax_calculations['recommended_regime']
        total_tax_liability = tax_calculations[f'{recommended_regime}_regime']['total_tax']
        tds_deducted = income_details['tds_deducted']
        
        refund_amount = tds_deducted - total_tax_liability
        
        return {
            'tds_deducted': tds_deducted,
            'tax_liability': total_tax_liability,
            'refund_amount': max(0, refund_amount),
            'additional_tax_due': max(0, -refund_amount),
            'refund_status': 'refund_due' if refund_amount > 0 else 'tax_due' if refund_amount < 0 else 'no_refund_no_tax',
            'recommended_regime': recommended_regime
        }
    
    def _generate_ai_suggestions(self, income_details: Dict, deductions: Dict, tax_calculations: Dict, documents: Dict) -> List[Dict]:
        """Generate AI-powered tax optimization suggestions"""
        suggestions = []
        
        # Regime selection suggestion
        old_tax = tax_calculations['old_regime']['total_tax']
        new_tax = tax_calculations['new_regime']['total_tax']
        savings = abs(old_tax - new_tax)
        
        if old_tax < new_tax:
            suggestions.append({
                'type': 'regime_selection',
                'priority': 'high',
                'title': 'Choose Old Tax Regime',
                'description': f'You can save ₹{savings:,.0f} by choosing the old tax regime instead of the new regime.',
                'action': 'Select old regime in your ITR filing',
                'potential_savings': savings
            })
        else:
            suggestions.append({
                'type': 'regime_selection',
                'priority': 'high',
                'title': 'Choose New Tax Regime',
                'description': f'You can save ₹{savings:,.0f} by choosing the new tax regime instead of the old regime.',
                'action': 'Select new regime in your ITR filing',
                'potential_savings': savings
            })
        
        # 80C investment suggestions
        current_80c = deductions['section_80c']
        remaining_80c = self.section_80c_limit - current_80c
        if remaining_80c > 0:
            tax_saved = remaining_80c * 0.30  # Assuming 30% tax bracket
            suggestions.append({
                'type': 'investment',
                'priority': 'medium',
                'title': 'Maximize Section 80C Investments',
                'description': f'You can invest ₹{remaining_80c:,.0f} more in 80C instruments (PPF, ELSS, etc.) to save ₹{tax_saved:,.0f} in taxes.',
                'action': f'Invest ₹{remaining_80c:,.0f} in PPF, ELSS, or life insurance',
                'potential_savings': tax_saved
            })
        
        # Health insurance suggestions
        current_80d = deductions['section_80d']
        remaining_80d = self.section_80d_limit - current_80d
        if remaining_80d > 0:
            tax_saved = remaining_80d * 0.30
            suggestions.append({
                'type': 'insurance',
                'priority': 'medium',
                'title': 'Health Insurance Premium Deduction',
                'description': f'You can claim ₹{remaining_80d:,.0f} more in health insurance premiums to save ₹{tax_saved:,.0f} in taxes.',
                'action': f'Pay ₹{remaining_80d:,.0f} in health insurance premiums',
                'potential_savings': tax_saved
            })
        
        # HRA optimization
        if income_details['hra_received'] > 0:
            suggestions.append({
                'type': 'hra',
                'priority': 'low',
                'title': 'HRA Optimization',
                'description': 'Ensure you have proper rent receipts and agreements to claim maximum HRA exemption.',
                'action': 'Maintain rent receipts and rental agreement',
                'potential_savings': 0
            })
        
        # Document completeness check
        required_docs = ['form16', 'bank_statement', 'aadhaar', 'pan_card']
        missing_docs = [doc for doc in required_docs if doc not in documents]
        if missing_docs:
            suggestions.append({
                'type': 'documentation',
                'priority': 'high',
                'title': 'Complete Document Submission',
                'description': f'Missing documents: {", ".join(missing_docs)}. Complete documentation ensures accurate tax calculation.',
                'action': f'Upload missing documents: {", ".join(missing_docs)}',
                'potential_savings': 0
            })
        
        # Interest income reporting
        if income_details['interest_income'] > 10000:
            suggestions.append({
                'type': 'compliance',
                'priority': 'high',
                'title': 'TDS on Interest Income',
                'description': f'Your interest income of ₹{income_details["interest_income"]:,.0f} may be subject to TDS. Ensure proper reporting.',
                'action': 'Report all interest income and claim TDS credit',
                'potential_savings': 0
            })
        
        return sorted(suggestions, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
    
    def _create_document_summary(self, documents: Dict) -> Dict:
        """Create summary of analyzed documents"""
        summary = {
            'total_documents': len(documents),
            'document_types': list(documents.keys()),
            'completeness_score': 0,
            'confidence_scores': {}
        }
        
        required_docs = ['form16', 'bank_statement', 'aadhaar', 'pan_card']
        available_docs = len([doc for doc in required_docs if doc in documents])
        summary['completeness_score'] = (available_docs / len(required_docs)) * 100
        
        for doc_type, doc_data in documents.items():
            summary['confidence_scores'][doc_type] = doc_data.get('confidence', 0)
        
        return summary
    
    def _perform_compliance_checks(self, personal_info: Dict, income_details: Dict, documents: Dict) -> Dict:
        """Perform compliance and validation checks"""
        checks = {
            'pan_aadhaar_linked': False,
            'form16_available': 'form16' in documents,
            'bank_statement_available': 'bank_statement' in documents,
            'high_value_transactions': False,
            'tds_mismatch': False,
            'compliance_score': 0
        }
        
        # Basic compliance scoring
        score = 0
        if personal_info.get('pan') and personal_info.get('aadhaar'):
            checks['pan_aadhaar_linked'] = True
            score += 25
        
        if checks['form16_available']:
            score += 25
        
        if checks['bank_statement_available']:
            score += 25
        
        if income_details['gross_salary'] > 0:
            score += 25
        
        checks['compliance_score'] = score
        
        return checks