#!/usr/bin/env python3
"""
QR Code Generator for ITR Data
Generates secure QR codes containing all ITR form data
"""
import qrcode
import json
import base64
from io import BytesIO
from datetime import datetime
import hashlib
import uuid
from typing import Dict, Any

class ITRQRGenerator:
    """
    Generates QR codes containing ITR form data extracted from documents
    """
    
    def __init__(self):
        self.version = "1.0"
        self.max_data_size = 2000  # QR code data limit
    
    def generate_itr_qr(self, analysis_result: Dict, documents_summary: Dict) -> Dict:
        """
        Generate QR code containing ITR form data
        
        Args:
            analysis_result: Complete ITR analysis result
            documents_summary: Summary of processed documents
            
        Returns:
            Dictionary with QR code data and image
        """
        try:
            # Extract essential ITR data
            itr_data = self._extract_itr_form_data(analysis_result)
            
            # Create QR payload
            qr_payload = {
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "qr_id": str(uuid.uuid4()),
                "data_hash": self._generate_data_hash(itr_data),
                "itr_data": itr_data,
                "documents_processed": documents_summary.get('total_documents', 0),
                "confidence_score": self._calculate_overall_confidence(documents_summary)
            }
            
            # Convert to JSON and check size
            json_data = json.dumps(qr_payload, separators=(',', ':'))
            
            if len(json_data) > self.max_data_size:
                # Compress data if too large
                qr_payload = self._compress_qr_data(qr_payload)
                json_data = json.dumps(qr_payload, separators=(',', ':'))
            
            # Generate QR code image
            qr_image_data = self._create_qr_image(json_data)
            
            return {
                "qr_id": qr_payload["qr_id"],
                "qr_data": json_data,
                "qr_image": qr_image_data,
                "data_size": len(json_data),
                "itr_summary": self._create_itr_summary(itr_data),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": f"QR generation failed: {str(e)}",
                "status": "error"
            }
    
    def _extract_itr_form_data(self, analysis_result: Dict) -> Dict:
        """Extract essential ITR form fields from analysis result"""
        personal_info = analysis_result.get('personal_info', {})
        income_details = analysis_result.get('income_details', {})
        deductions = analysis_result.get('deductions', {})
        tax_calculations = analysis_result.get('tax_calculations', {})
        refund_analysis = analysis_result.get('refund_analysis', {})
        
        # ITR Form 1 (Sahaj) essential fields
        itr_data = {
            # Personal Information
            "name": personal_info.get('name', ''),
            "pan": personal_info.get('pan', ''),
            "aadhaar": personal_info.get('aadhaar', ''),
            "date_of_birth": personal_info.get('date_of_birth', ''),
            "address": personal_info.get('address', ''),
            "phone": personal_info.get('phone', ''),
            "email": personal_info.get('email', ''),
            
            # Income Details (Schedule S - Salary)
            "gross_salary": income_details.get('gross_salary', 0),
            "basic_salary": income_details.get('basic_salary', 0),
            "hra_received": income_details.get('hra_received', 0),
            "other_allowances": income_details.get('other_allowances', 0),
            "employer_name": income_details.get('employer_name', ''),
            
            # Deductions
            "standard_deduction": deductions.get('standard_deduction', 50000),
            "section_80c": deductions.get('section_80c', 0),
            "section_80d": deductions.get('section_80d', 0),
            "hra_exemption": deductions.get('hra_exemption', 0),
            "professional_tax": deductions.get('professional_tax', 0),
            
            # Other Income
            "interest_income": income_details.get('interest_income', 0),
            "other_income": income_details.get('other_income', 0),
            
            # Tax Details
            "tds_deducted": income_details.get('tds_deducted', 0),
            "advance_tax": 0,  # Usually 0 for salaried
            "self_assessment_tax": 0,
            
            # Calculated Fields
            "total_income": tax_calculations.get('gross_income', 0),
            "taxable_income": tax_calculations.get(f"{tax_calculations.get('recommended_regime', 'new')}_regime", {}).get('taxable_income', 0),
            "tax_liability": refund_analysis.get('tax_liability', 0),
            "refund_amount": refund_analysis.get('refund_amount', 0),
            "tax_payable": refund_analysis.get('additional_tax_due', 0),
            
            # Regime Selection
            "tax_regime": tax_calculations.get('recommended_regime', 'new'),
            
            # Assessment Year
            "assessment_year": "2024-25",
            "financial_year": "2023-24"
        }
        
        return itr_data
    
    def _generate_data_hash(self, data: Dict) -> str:
        """Generate hash for data integrity"""
        data_string = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(data_string.encode()).hexdigest()[:16]
    
    def _calculate_overall_confidence(self, documents_summary: Dict) -> float:
        """Calculate overall confidence score"""
        confidence_scores = documents_summary.get('confidence_scores', {})
        if confidence_scores:
            return sum(confidence_scores.values()) / len(confidence_scores)
        return 0.0
    
    def _compress_qr_data(self, qr_payload: Dict) -> Dict:
        """Compress QR data if it's too large"""
        # Remove less critical fields to fit QR code size limit
        compressed_payload = {
            "v": qr_payload["version"],
            "ts": qr_payload["timestamp"][:10],  # Date only
            "id": qr_payload["qr_id"][:8],  # Shorter ID
            "hash": qr_payload["data_hash"],
            "data": {
                # Essential fields only
                "name": qr_payload["itr_data"].get("name", "")[:30],
                "pan": qr_payload["itr_data"].get("pan", ""),
                "aadhaar": qr_payload["itr_data"].get("aadhaar", ""),
                "gross_salary": qr_payload["itr_data"].get("gross_salary", 0),
                "tds_deducted": qr_payload["itr_data"].get("tds_deducted", 0),
                "section_80c": qr_payload["itr_data"].get("section_80c", 0),
                "tax_regime": qr_payload["itr_data"].get("tax_regime", "new"),
                "refund_amount": qr_payload["itr_data"].get("refund_amount", 0),
                "tax_payable": qr_payload["itr_data"].get("tax_payable", 0)
            }
        }
        
        return compressed_payload
    
    def _create_qr_image(self, data: str) -> str:
        """Create QR code image and return as base64"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def _create_itr_summary(self, itr_data: Dict) -> Dict:
        """Create human-readable summary of ITR data"""
        return {
            "taxpayer_name": itr_data.get("name", "N/A"),
            "pan_number": itr_data.get("pan", "N/A"),
            "total_income": f"₹{itr_data.get('total_income', 0):,}",
            "tax_regime": itr_data.get("tax_regime", "new").upper(),
            "refund_or_payable": f"₹{max(itr_data.get('refund_amount', 0), itr_data.get('tax_payable', 0)):,}",
            "refund_status": "Refund Due" if itr_data.get('refund_amount', 0) > 0 else "Tax Payable" if itr_data.get('tax_payable', 0) > 0 else "No Refund/Tax",
            "assessment_year": itr_data.get("assessment_year", "2024-25")
        }
    
    def decode_qr_data(self, qr_data: str) -> Dict:
        """
        Decode QR data back to ITR form data
        
        Args:
            qr_data: JSON string from QR code
            
        Returns:
            Decoded ITR data
        """
        try:
            payload = json.loads(qr_data)
            
            # Handle both full and compressed formats
            if "itr_data" in payload:
                # Full format
                itr_data = payload["itr_data"]
                metadata = {
                    "qr_id": payload.get("qr_id"),
                    "timestamp": payload.get("timestamp"),
                    "data_hash": payload.get("data_hash"),
                    "confidence_score": payload.get("confidence_score", 0)
                }
            else:
                # Compressed format
                itr_data = payload.get("data", {})
                metadata = {
                    "qr_id": payload.get("id"),
                    "timestamp": payload.get("ts"),
                    "data_hash": payload.get("hash"),
                    "confidence_score": 0.8  # Default for compressed
                }
            
            return {
                "itr_data": itr_data,
                "metadata": metadata,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": f"QR decode failed: {str(e)}",
                "status": "error"
            }