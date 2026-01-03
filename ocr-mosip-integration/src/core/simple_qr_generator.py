"""
Simple QR Code Generator
Generates human-readable QR codes from OCR data
"""

import qrcode
import json
import base64
import io
import uuid
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def generate_simple_text_qr(ocr_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate simple text-based QR code
    
    Args:
        ocr_data: Dictionary containing OCR extracted data
        
    Returns:
        Dictionary with QR generation results
    """
    try:
        # Create human-readable text
        text_lines = []
        text_lines.append("=== DIGITAL IDENTITY CREDENTIAL ===")
        text_lines.append("")
        
        # Add personal information
        if ocr_data.get('name'):
            text_lines.append(f"Name: {ocr_data['name']}")
        if ocr_data.get('date_of_birth'):
            text_lines.append(f"Date of Birth: {ocr_data['date_of_birth']}")
        if ocr_data.get('pan'):
            text_lines.append(f"PAN: {ocr_data['pan']}")
        if ocr_data.get('aadhaar'):
            text_lines.append(f"Aadhaar: {ocr_data['aadhaar']}")
        
        # Add contact information
        if ocr_data.get('mobile'):
            text_lines.append(f"Mobile: {ocr_data['mobile']}")
        if ocr_data.get('email'):
            text_lines.append(f"Email: {ocr_data['email']}")
        
        # Add financial information
        if ocr_data.get('gross_salary'):
            text_lines.append(f"Gross Salary: ₹{ocr_data['gross_salary']}")
        if ocr_data.get('tds_deducted'):
            text_lines.append(f"TDS Deducted: ₹{ocr_data['tds_deducted']}")
        
        text_lines.append("")
        text_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        text_lines.append("Scan with any QR reader")
        
        qr_content = "\n".join(text_lines)
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        # Create image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        img_buffer = io.BytesIO()
        qr_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        qr_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        qr_data_url = f"data:image/png;base64,{qr_base64}"
        
        return {
            'success': True,
            'qr_id': str(uuid.uuid4()),
            'qr_image_base64': qr_data_url,
            'qr_content': qr_content,
            'format': 'text',
            'readable_by': 'Any QR scanner',
            'generation_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Simple text QR generation failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'qr_id': str(uuid.uuid4()),
            'generation_timestamp': datetime.now().isoformat()
        }

def generate_json_qr(ocr_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate JSON-based QR code
    
    Args:
        ocr_data: Dictionary containing OCR extracted data
        
    Returns:
        Dictionary with QR generation results
    """
    try:
        # Create structured JSON
        json_data = {
            'type': 'DigitalIdentityCredential',
            'version': '1.0',
            'issuer': 'ITR Processing System',
            'issuanceDate': datetime.now().isoformat(),
            'credentialSubject': ocr_data,
            'metadata': {
                'generated_by': 'MOSIP ITR Assistant',
                'format': 'JSON',
                'readable_by': 'QR scanners with JSON support'
            }
        }
        
        qr_content = json.dumps(json_data, ensure_ascii=False, separators=(',', ':'))
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        # Create image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        img_buffer = io.BytesIO()
        qr_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        qr_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        qr_data_url = f"data:image/png;base64,{qr_base64}"
        
        return {
            'success': True,
            'qr_id': str(uuid.uuid4()),
            'qr_image_base64': qr_data_url,
            'qr_content': qr_content,
            'format': 'json',
            'readable_by': 'QR scanners with JSON support',
            'generation_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"JSON QR generation failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'qr_id': str(uuid.uuid4()),
            'generation_timestamp': datetime.now().isoformat()
        }