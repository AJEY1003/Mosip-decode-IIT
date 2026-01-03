#!/usr/bin/env node
/**
 * PixelPass Setup Script
 * Following official Inji documentation for QR code generation
 * 
 * Usage:
 * 1. Create directory: mkdir pixelpass-qr && cd pixelpass-qr
 * 2. Initialize npm: npm init -y
 * 3. Install PixelPass: npm install @mosip/pixelpass
 * 4. Run this script: node setup_pixelpass.js
 */

const fs = require('fs');
const path = require('path');

// Sample Verifiable Credential for testing
const sampleCredential = {
    "@context": [
        "https://www.w3.org/2018/credentials/v1",
        "https://www.w3.org/2018/credentials/examples/v1"
    ],
    "id": "urn:uuid:12345678-1234-5678-9012-123456789012",
    "type": ["VerifiableCredential", "IdentityCredential"],
    "issuer": {
        "id": "did:inji:issuer:government-of-india",
        "name": "Government of India - Digital Identity Authority"
    },
    "issuanceDate": "2024-01-01T00:00:00Z",
    "expirationDate": "2025-01-01T00:00:00Z",
    "credentialSubject": {
        "id": "did:inji:citizen:test-user",
        "name": "Test User",
        "dateOfBirth": "01/01/1990",
        "nationality": "Indian",
        "aadhaarNumber": "****-****-1234",
        "documentType": "Test Identity Document"
    }
};

function setupPixelPass() {
    console.log('🚀 PixelPass Setup - Following Official Inji Documentation');
    console.log('=' * 60);
    
    try {
        // Check if PixelPass is installed
        const { generateQRData } = require('@mosip/pixelpass');
        console.log('✓ @mosip/pixelpass library found');
        
        // Generate QR code following official documentation
        console.log('\n📱 Generating QR Code...');
        
        // Use generateQRData as per documentation
        const credentialString = JSON.stringify(sampleCredential);
        const qrData = generateQRData(credentialString);
        
        console.log('✓ QR code generated successfully');
        console.log('📊 QR Data Info:');
        console.log(`  Type: ${typeof qrData}`);
        console.log(`  Length: ${qrData.length} characters`);
        
        // Save QR data
        const qrResult = {
            success: true,
            timestamp: new Date().toISOString(),
            qr_data: qrData,
            qr_image: qrData, // This should be base64 image data
            encoding: 'PixelPass-CBOR',
            library: '@mosip/pixelpass',
            compatible_with: 'Inji Verify Portal',
            instructions: {
                view_qr: 'Copy qr_data and paste in browser URL to view QR code',
                save_qr: 'Right-click on QR image and save',
                verify_qr: 'Upload saved QR to Inji Verify portal'
            },
            sample_credential: sampleCredential
        };
        
        // Write result to file
        fs.writeFileSync('pixelpass_qr_result.json', JSON.stringify(qrResult, null, 2));
        console.log('💾 QR result saved to: pixelpass_qr_result.json');
        
        // Instructions
        console.log('\n📋 Next Steps:');
        console.log('1. Copy the qr_data from pixelpass_qr_result.json');
        console.log('2. Paste it in your browser URL bar to view the QR code');
        console.log('3. Save the QR code image');
        console.log('4. Upload to Inji Verify portal for verification');
        
        console.log('\n🎯 Integration with Python:');
        console.log('- Use the Python PixelPassQRGenerator class');
        console.log('- It will call this Node.js script automatically');
        console.log('- QR codes will be compatible with Inji Verify');
        
        return qrResult;
        
    } catch (error) {
        console.error('❌ PixelPass setup failed:', error.message);
        
        if (error.code === 'MODULE_NOT_FOUND') {
            console.log('\n📦 To install PixelPass:');
            console.log('1. Create directory: mkdir pixelpass-qr && cd pixelpass-qr');
            console.log('2. Initialize npm: npm init -y');
            console.log('3. Install PixelPass: npm install @mosip/pixelpass');
            console.log('4. Run this script again: node setup_pixelpass.js');
        }
        
        return { success: false, error: error.message };
    }
}

// Create package.json template
function createPackageJson() {
    const packageJson = {
        "name": "pixelpass-qr-generator",
        "version": "1.0.0",
        "description": "QR code generation using MOSIP PixelPass library",
        "main": "setup_pixelpass.js",
        "scripts": {
            "test": "node setup_pixelpass.js",
            "generate-qr": "node setup_pixelpass.js"
        },
        "dependencies": {
            "@mosip/pixelpass": "latest"
        },
        "keywords": ["mosip", "pixelpass", "qr", "verifiable-credentials", "inji"],
        "author": "OCR-MOSIP Integration",
        "license": "MIT"
    };
    
    if (!fs.existsSync('package.json')) {
        fs.writeFileSync('package.json', JSON.stringify(packageJson, null, 2));
        console.log('📦 Created package.json');
    }
}

// Main execution
if (require.main === module) {
    createPackageJson();
    setupPixelPass();
}

module.exports = { setupPixelPass, createPackageJson };