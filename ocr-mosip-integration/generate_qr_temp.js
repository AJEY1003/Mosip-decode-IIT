
const { generateQRData } = require('@mosip/pixelpass');

// Get credential data from command line argument
const credentialData = process.argv[2];

if (!credentialData) {
    console.error('Error: Credential data is required');
    process.exit(1);
}

try {
    // Parse credential data - expecting the credential body as per Inji Certify docs
    const parsedCredential = JSON.parse(credentialData);
    
    // Use generateQRData as per official documentation
    // Pass the credential body (value of 'credential' from credential response)
    const qrData = generateQRData(JSON.stringify(parsedCredential));
    
    // Output QR data as base64 image
    console.log(JSON.stringify({
        success: true,
        qr_data: qrData,
        qr_image_data: qrData, // This should be base64 image data
        encoding: 'PixelPass-CBOR',
        timestamp: new Date().toISOString()
    }));
} catch (error) {
    console.error(JSON.stringify({
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
    }));
    process.exit(1);
}
