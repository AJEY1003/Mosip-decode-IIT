#!/usr/bin/env node
/**
 * Generate Real QR Code using PixelPass
 * This script uses the installed @mosip/pixelpass library
 */

const { generateQRData } = require('@mosip/pixelpass');
const fs = require('fs');

// Sample Verifiable Credential for testing
const sampleCredential = {
    "@context": [
        "https://www.w3.org/2018/credentials/v1",
        "https://www.w3.org/2018/credentials/examples/v1"
    ],
    "id": "urn:uuid:real-qr-test-2025",
    "type": ["VerifiableCredential", "IdentityCredential"],
    "issuer": {
        "id": "did:inji:issuer:government-of-india",
        "name": "Government of India - Digital Identity Authority"
    },
    "issuanceDate": "2025-12-31T00:00:00Z",
    "expirationDate": "2026-12-31T00:00:00Z",
    "credentialSubject": {
        "id": "did:inji:citizen:real-test-user",
        "name": "Amit Kumar Sharma",
        "dateOfBirth": "15/06/1988",
        "nationality": "Indian",
        "aadhaarNumber": "2345-6789-0123",
        "panNumber": "DEFGH5678I",
        "phoneNumber": "+91-9876543210",
        "emailAddress": "amit.sharma@example.com",
        "address": {
            "fullAddress": "789 Park Street, Delhi, Delhi 110001",
            "country": "India"
        },
        "documentType": "Aadhaar Card"
    },
    "proof": {
        "type": "Ed25519Signature2018",
        "created": "2025-12-31T00:00:00Z",
        "proofPurpose": "assertionMethod",
        "verificationMethod": "did:inji:issuer:government-of-india#key-1",
        "jws": "real_qr_test_signature_2025"
    }
};

console.log('🚀 Generating Real QR Code with PixelPass');
console.log('=' * 50);

try {
    // Generate QR code using PixelPass
    console.log('📱 Creating QR code...');
    const credentialString = JSON.stringify(sampleCredential);
    const qrData = generateQRData(credentialString);
    
    console.log('✓ QR code generated successfully!');
    console.log(`📊 QR Data Length: ${qrData.length} characters`);
    console.log(`🔧 Encoding: PixelPass-CBOR`);
    console.log(`📱 Compatible with: Inji Verify Portal`);
    
    // Create result object
    const result = {
        success: true,
        timestamp: new Date().toISOString(),
        qr_data: qrData,
        qr_image: qrData, // This is the base64 image data
        encoding: 'PixelPass-CBOR',
        library: '@mosip/pixelpass',
        compatible_with: 'Inji Verify Portal',
        credential_subject: sampleCredential.credentialSubject.name,
        instructions: {
            view_qr: 'Copy qr_data and paste in browser URL to view QR code',
            save_qr: 'Right-click on QR image in browser and save as PNG',
            verify_qr: 'Upload saved QR image to Inji Verify portal',
            test_api: 'Use /api/inji/verify-qr endpoint to test verification'
        },
        sample_credential: sampleCredential
    };
    
    // Save to file
    fs.writeFileSync('real_qr_code.json', JSON.stringify(result, null, 2));
    console.log('💾 Real QR code saved to: real_qr_code.json');
    
    console.log('\n📋 Next Steps:');
    console.log('1. Copy the qr_data from real_qr_code.json');
    console.log('2. Paste it in your browser URL bar');
    console.log('3. You will see the QR code image');
    console.log('4. Right-click and save the QR code as PNG');
    console.log('5. Upload to Inji Verify portal for verification');
    
    console.log('\n🧪 Test with Flask API:');
    console.log('curl -X POST http://localhost:5000/api/inji/verify-qr \\');
    console.log('  -H "Content-Type: application/json" \\');
    console.log('  -d \'{"qr_image": "' + qrData.substring(0, 50) + '..."}\'');
    
    console.log('\n✅ Real PixelPass QR code generated successfully!');
    
} catch (error) {
    console.error('❌ Error generating QR code:', error.message);
    process.exit(1);
}