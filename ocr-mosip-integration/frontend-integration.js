/**
 * OCR-MOSIP Frontend Integration
 * JavaScript client for connecting frontend to Flask backend
 */

class OCRMOSIPClient {
    constructor(baseURL = 'http://127.0.0.1:5000') {
        this.baseURL = baseURL;
        this.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }

    /**
     * Health check - Test if backend is running
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            return await response.json();
        } catch (error) {
            console.error('Backend health check failed:', error);
            return { status: 'error', error: error.message };
        }
    }

    /**
     * Extract text using Enhanced OCR (Tesseract + Google + AWS)
     * @param {File|string} imageData - Image file or base64 data
     * @param {string} documentType - Type of document (Passport, Aadhaar, etc.)
     * @param {boolean} useAllEngines - Whether to use all available engines
     */
    async enhancedExtractText(imageData, documentType = 'Unknown', useAllEngines = true) {
        try {
            let base64Data;
            
            // Handle File object
            if (imageData instanceof File) {
                base64Data = await this.fileToBase64(imageData);
            } else {
                base64Data = imageData;
            }

            const payload = {
                document_type: documentType,
                image_data: base64Data,
                use_all_engines: useAllEngines
            };

            const response = await fetch(`${this.baseURL}/api/enhanced-ocr/extract`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(payload)
            });

            return await response.json();
        } catch (error) {
            console.error('Enhanced OCR extraction failed:', error);
            return { status: 'error', error: error.message };
        }
    }

    /**
     * Extract Hindi text using Tesseract OCR (Based on your Colab implementation)
     * @param {File|string} imageData - Image file or base64 data
     * @param {string} documentType - Type of document
     * @param {string} language - 'hindi', 'english', or 'hindi_english'
     * @param {string} fileType - 'image' or 'pdf'
     */
    async hindiExtractText(imageData, documentType = 'Unknown', language = 'hindi_english', fileType = 'image') {
        try {
            let base64Data;
            
            // Handle File object
            if (imageData instanceof File) {
                base64Data = await this.fileToBase64(imageData);
                // Detect if it's a PDF
                if (imageData.type === 'application/pdf' || imageData.name.toLowerCase().endsWith('.pdf')) {
                    fileType = 'pdf';
                }
            } else {
                base64Data = imageData;
            }

            const payload = {
                document_type: documentType,
                image_data: base64Data,
                language: language,
                file_type: fileType
            };

            const response = await fetch(`${this.baseURL}/api/hindi-ocr/extract`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(payload)
            });

            return await response.json();
        } catch (error) {
            console.error('Hindi OCR extraction failed:', error);
            return { status: 'error', error: error.message };
        }
    }

    /**
     * Get Hindi OCR status and language availability
     */
    async getHindiOCRStatus() {
        try {
            const response = await fetch(`${this.baseURL}/api/hindi-ocr/status`);
            return await response.json();
        } catch (error) {
            console.error('Hindi OCR status check failed:', error);
            return { error: error.message };
        }
    }
    /**
     * Get Enhanced OCR engine status
     */
    async getEnhancedOCRStatus() {
        try {
            const response = await fetch(`${this.baseURL}/api/enhanced-ocr/status`);
            return await response.json();
        } catch (error) {
            console.error('Enhanced OCR status check failed:', error);
            return { error: error.message };
        }
    }

    /**
     * Get OCR engine status (legacy)
     */
    async getEngineStatus() {
        try {
            const response = await fetch(`${this.baseURL}/api/enhanced-ocr/status`);
            return await response.json();
        } catch (error) {
            console.error('Engine status check failed:', error);
            return { error: error.message };
        }
    }
     * @param {File|string} imageData - Image file or base64 data
     * @param {string} documentType - Type of document (Passport, Aadhaar, etc.)
     * @param {string} imageFormat - Image format (jpg, png, etc.)
     */
    async extractText(imageData, documentType = 'Unknown', imageFormat = 'jpg') {
        try {
            let base64Data;
            
            // Handle File object
            if (imageData instanceof File) {
                base64Data = await this.fileToBase64(imageData);
            } else {
                base64Data = imageData;
            }

            const payload = {
                document_type: documentType,
                image_data: base64Data,
                image_format: imageFormat
            };

            const response = await fetch(`${this.baseURL}/ocr/extract`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(payload)
            });

            return await response.json();
        } catch (error) {
            console.error('OCR extraction failed:', error);
            return { status: 'error', error: error.message };
        }
    }

    /**
     * Generate QR code with real Ed25519 signatures
     * @param {Object} ocrData - Extracted OCR data
     */
    async generateQRWithSignatures(ocrData) {
        try {
            const payload = {
                ocr_data: ocrData
            };

            const response = await fetch(`${this.baseURL}/api/pixelpass/generate-qr`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(payload)
            });

            return await response.json();
        } catch (error) {
            console.error('QR generation with signatures failed:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Generate simple human-readable QR code
     * @param {Object} ocrData - Extracted OCR data
     * @param {string} format - 'text' or 'json'
     */
    async generateSimpleQR(ocrData, format = 'text') {
        try {
            const payload = {
                ocr_data: ocrData,
                format: format
            };

            const response = await fetch(`${this.baseURL}/api/simple-qr/generate`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(payload)
            });

            return await response.json();
        } catch (error) {
            console.error('Simple QR generation failed:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Verify QR code with Inji Verify
     * @param {string} qrImageBase64 - Base64 encoded QR image
     */
    async verifyQR(qrImageBase64) {
        try {
            const payload = {
                qr_image: qrImageBase64,
                verification_method: 'opencv'
            };

            const response = await fetch(`${this.baseURL}/api/inji/verify-qr`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(payload)
            });

            return await response.json();
        } catch (error) {
            console.error('QR verification failed:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Enhanced complete workflow: OCR → Validation → QR Generation
     * Uses multiple OCR engines for maximum accuracy
     * @param {File|string} imageData - Document image
     * @param {string} documentType - Document type
     * @param {boolean} useAllEngines - Whether to use all OCR engines
     */
    async enhancedCompleteWorkflow(imageData, documentType = 'Unknown', useAllEngines = true) {
        try {
            // Step 1: Extract text with Enhanced OCR
            console.log('🚀 Step 1: Extracting text with Enhanced OCR (Multiple Engines)...');
            const ocrResult = await this.enhancedExtractText(imageData, documentType, useAllEngines);
            
            if (ocrResult.status !== 'success') {
                throw new Error(`Enhanced OCR failed: ${ocrResult.message}`);
            }

            console.log(`✅ OCR completed using engines: ${ocrResult.engines_used.join(', ')}`);
            console.log(`📊 Confidence: ${(ocrResult.confidence_score * 100).toFixed(1)}%`);

            // Step 2: Generate QR with real signatures
            console.log('🔐 Step 2: Generating QR with real signatures...');
            const qrResult = await this.generateQRWithSignatures(ocrResult.extracted_data.structured_data);
            
            if (!qrResult.success) {
                throw new Error(`QR generation failed: ${qrResult.error}`);
            }

            // Step 3: Generate simple QR for comparison
            console.log('📱 Step 3: Generating simple QR for comparison...');
            const simpleQR = await this.generateSimpleQR(ocrResult.extracted_data.structured_data);

            return {
                success: true,
                workflow_id: qrResult.workflow_id,
                enhanced_ocr_result: ocrResult,
                signed_qr: qrResult,
                simple_qr: simpleQR,
                summary: {
                    engines_used: ocrResult.engines_used,
                    confidence_score: ocrResult.confidence_score,
                    processing_time: ocrResult.processing_time,
                    text_extracted: true,
                    signatures_generated: qrResult.success,
                    qr_codes_created: true,
                    ready_for_verification: true
                },
                processing_details: ocrResult.processing_details
            };

        } catch (error) {
            console.error('Enhanced complete workflow failed:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Compare OCR engines performance
     * @param {File|string} imageData - Document image
     * @param {string} documentType - Document type
     */
    async compareOCREngines(imageData, documentType = 'Unknown') {
        try {
            console.log('🔍 Comparing OCR engines...');
            
            // Test original OCR
            const originalResult = await this.extractText(imageData, documentType);
            
            // Test enhanced OCR
            const enhancedResult = await this.enhancedExtractText(imageData, documentType, true);
            
            // Get engine status
            const engineStatus = await this.getEngineStatus();
            
            return {
                success: true,
                comparison: {
                    original_ocr: {
                        confidence: originalResult.confidence_score || 0,
                        text_length: originalResult.extracted_data?.raw_text?.length || 0,
                        engines: ['easyocr'],
                        processing_time: originalResult.processing_time || 0
                    },
                    enhanced_ocr: {
                        confidence: enhancedResult.confidence_score || 0,
                        text_length: enhancedResult.extracted_data?.raw_text?.length || 0,
                        engines: enhancedResult.engines_used || [],
                        processing_time: enhancedResult.processing_time || 0
                    }
                },
                engine_status: engineStatus,
                recommendation: this._getOCRRecommendation(originalResult, enhancedResult)
            };
            
        } catch (error) {
            console.error('OCR comparison failed:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Get OCR recommendation based on comparison
     * @private
     */
    _getOCRRecommendation(originalResult, enhancedResult) {
        const originalConf = originalResult.confidence_score || 0;
        const enhancedConf = enhancedResult.confidence_score || 0;
        
        if (enhancedConf > originalConf + 0.1) {
            return {
                recommended: 'enhanced',
                reason: 'Enhanced OCR provides significantly better confidence',
                improvement: `${((enhancedConf - originalConf) * 100).toFixed(1)}% better confidence`
            };
        } else if (originalConf > enhancedConf + 0.1) {
            return {
                recommended: 'original',
                reason: 'Original OCR performs better for this document',
                improvement: `${((originalConf - enhancedConf) * 100).toFixed(1)}% better confidence`
            };
        } else {
            return {
                recommended: 'enhanced',
                reason: 'Enhanced OCR provides better reliability with multiple engines',
                improvement: 'Similar confidence but better fallback options'
            };
        }
    }
     * @param {File|string} imageData - Document image
     * @param {string} documentType - Document type
     */
    async completeWorkflow(imageData, documentType = 'Unknown') {
        try {
            // Step 1: Extract text with OCR
            console.log('🔍 Step 1: Extracting text with OCR...');
            const ocrResult = await this.extractText(imageData, documentType);
            
            if (ocrResult.status !== 'success') {
                throw new Error(`OCR failed: ${ocrResult.message}`);
            }

            // Step 2: Generate QR with real signatures
            console.log('🔐 Step 2: Generating QR with real signatures...');
            const qrResult = await this.generateQRWithSignatures(ocrResult.extracted_data.structured_data);
            
            if (!qrResult.success) {
                throw new Error(`QR generation failed: ${qrResult.error}`);
            }

            // Step 3: Generate simple QR for comparison
            console.log('📱 Step 3: Generating simple QR for comparison...');
            const simpleQR = await this.generateSimpleQR(ocrResult.extracted_data.structured_data);

            return {
                success: true,
                workflow_id: qrResult.workflow_id,
                ocr_result: ocrResult,
                signed_qr: qrResult,
                simple_qr: simpleQR,
                summary: {
                    text_extracted: true,
                    signatures_generated: qrResult.success,
                    qr_codes_created: true,
                    ready_for_verification: true
                }
            };

        } catch (error) {
            console.error('Complete workflow failed:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Convert File to base64
     * @param {File} file - File object
     */
    async fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    /**
     * Download QR code image
     * @param {string} base64Data - Base64 image data
     * @param {string} filename - Download filename
     */
    downloadQRImage(base64Data, filename = 'qr-code.png') {
        const link = document.createElement('a');
        link.href = base64Data;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    /**
     * Display QR code in HTML element
     * @param {string} base64Data - Base64 image data
     * @param {string} elementId - HTML element ID
     */
    displayQRCode(base64Data, elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `<img src="${base64Data}" alt="QR Code" style="max-width: 100%; height: auto;">`;
        }
    }
}

// Export for use in frontend
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OCRMOSIPClient;
}

// Global variable for browser use
window.OCRMOSIPClient = OCRMOSIPClient;