/**
 * API Service for MOSIP ITR Assistant
 * Connects frontend to OCR-MOSIP Integration backend
 */

const API_BASE_URL = 'http://127.0.0.1:5000';

class APIService {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }

    /**
     * Generic API request handler
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.headers,
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    /**
     * Health check - Test backend connectivity
     */
    async healthCheck() {
        return this.request('/health');
    }

    /**
     * Enhanced OCR Text Extraction with multiple engines (Tesseract + EasyOCR + TrOCR)
     * @param {File} file - Document file
     * @param {string} documentType - Type of document
     * @param {boolean} useAllEngines - Whether to use all available engines
     */
    async enhancedExtractText(file, documentType = 'ITR Document', useAllEngines = true) {
        try {
            // Check file size and warn user
            const fileSizeMB = file.size / (1024 * 1024);
            console.log(`📄 Processing file: ${file.name} (${fileSizeMB.toFixed(1)}MB)`);

            if (fileSizeMB > 20) {
                console.warn('⚠️ Large file detected, this may take longer to process');
            }

            // Convert file to base64 with compression for large files
            const base64Data = await this.fileToBase64(file, 15, 0.85); // Compress files > 15MB

            const payload = {
                document_type: documentType,
                image_data: base64Data,
                image_format: file.name.split('.').pop().toLowerCase(),
                use_all_engines: useAllEngines
            };

            // Calculate payload size
            const payloadSize = JSON.stringify(payload).length / (1024 * 1024);
            console.log(`📦 Payload size: ${payloadSize.toFixed(1)}MB`);

            if (payloadSize > 45) {
                throw new Error('Document is too large even after compression. Please use a smaller image or reduce the number of pages.');
            }

            return this.request('/api/enhanced-ocr/extract', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
        } catch (error) {
            console.error('Enhanced OCR extraction error:', error);

            // Provide user-friendly error messages
            if (error.message.includes('413') || error.message.includes('Request Entity Too Large')) {
                throw new Error('Document is too large. Please try with a smaller file or fewer pages.');
            } else if (error.message.includes('timeout')) {
                throw new Error('Processing timeout. Large documents may take longer - please try again.');
            } else {
                throw error;
            }
        }
    }

    /**
     * Get Enhanced OCR engine status
     */
    async getEnhancedOCRStatus() {
        return this.request('/api/enhanced-ocr/status');
    }

    /**
     * Convert File to base64 with compression for large files
     * @param {File} file - File object
     * @param {number} maxSizeMB - Maximum size in MB before compression
     * @param {number} quality - Compression quality (0.1 to 1.0)
     */
    async fileToBase64(file, maxSizeMB = 10, quality = 0.8) {
        return new Promise((resolve, reject) => {
            // Check file size
            const fileSizeMB = file.size / (1024 * 1024);

            if (fileSizeMB <= maxSizeMB) {
                // File is small enough, no compression needed
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result);
                reader.onerror = reject;
                reader.readAsDataURL(file);
            } else {
                // File is too large, compress it
                this.compressImage(file, quality).then(compressedFile => {
                    const reader = new FileReader();
                    reader.onload = () => {
                        console.log(`📦 Compressed ${fileSizeMB.toFixed(1)}MB → ${(compressedFile.size / (1024 * 1024)).toFixed(1)}MB`);
                        resolve(reader.result);
                    };
                    reader.onerror = reject;
                    reader.readAsDataURL(compressedFile);
                }).catch(reject);
            }
        });
    }

    /**
     * Compress image file
     * @param {File} file - Image file
     * @param {number} quality - Compression quality (0.1 to 1.0)
     */
    async compressImage(file, quality = 0.8) {
        return new Promise((resolve, reject) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();

            img.onload = () => {
                // Calculate new dimensions (max 2048px on longest side)
                const maxDimension = 2048;
                let { width, height } = img;

                if (width > height && width > maxDimension) {
                    height = (height * maxDimension) / width;
                    width = maxDimension;
                } else if (height > maxDimension) {
                    width = (width * maxDimension) / height;
                    height = maxDimension;
                }

                canvas.width = width;
                canvas.height = height;

                // Draw and compress
                ctx.drawImage(img, 0, 0, width, height);

                canvas.toBlob(
                    (blob) => {
                        if (blob) {
                            const compressedFile = new File([blob], file.name, {
                                type: 'image/jpeg',
                                lastModified: Date.now()
                            });
                            resolve(compressedFile);
                        } else {
                            reject(new Error('Image compression failed'));
                        }
                    },
                    'image/jpeg',
                    quality
                );
            };

            img.onerror = () => reject(new Error('Failed to load image for compression'));
            img.src = URL.createObjectURL(file);
        });
    }

    /**
     * OCR Text Extraction (Original)
     * @param {File} file - Document file
     * @param {string} documentType - Type of document
     */
    async extractText(file, documentType = 'ITR Document') {
        const formData = new FormData();
        formData.append('document', file);
        formData.append('document_type', documentType);

        try {
            const response = await fetch(`${this.baseURL}/ocr/extract`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`OCR extraction failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('OCR extraction error:', error);
            throw error;
        }
    }

    /**
     * Alternative OCR extraction with base64 data
     * @param {string} base64Data - Base64 encoded image
     * @param {string} documentType - Document type
     * @param {string} imageFormat - Image format
     */
    async extractTextFromBase64(base64Data, documentType = 'ITR Document', imageFormat = 'jpg') {
        const payload = {
            document_type: documentType,
            image_data: base64Data,
            image_format: imageFormat
        };

        return this.request('/ocr/extract', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    /**
     * Generate QR code with real Ed25519 signatures (PixelPass)
     * @param {Object} ocrData - Extracted OCR data
     */
    async generateSignedQR(ocrData) {
        const payload = {
            ocr_data: ocrData
        };

        return this.request('/api/pixelpass/generate-qr', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    /**
     * Generate QR code (uses PixelPass with fallback)
     * @param {Object} ocrData - Extracted OCR data
     * @param {string} format - Format preference (will use PixelPass regardless)
     */
    async generateSimpleQR(ocrData, format = 'json') {
        // Use PixelPass endpoint for all QR generation
        return this.generateSignedQR(ocrData);
    }

    /**
     * Verify extracted data
     * @param {string} requestId - OCR request ID
     * @param {Object} extractedData - Data to verify
     * @param {Object} verificationRules - Validation rules
     */
    async verifyData(requestId, extractedData, verificationRules = {}) {
        const payload = {
            request_id: requestId,
            extracted_data: extractedData,
            verification_rules: {
                required_fields: ['name', 'pan', 'date_of_birth'],
                field_formats: {
                    pan: 'alphanumeric',
                    date_of_birth: 'date',
                    email: 'email',
                    phone: 'phone'
                },
                min_confidence: 0.7,
                ...verificationRules
            }
        };

        return this.request('/ocr/verify', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    /**
     * Validate with InjINet
     * @param {Object} extractedData - OCR extracted data
     * @param {string} documentType - Document type
     */
    async validateWithInjINet(extractedData, documentType) {
        const payload = {
            extracted_data: extractedData,
            document_type: documentType
        };

        return this.request('/api/injinet/validate', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }
    /**
     * Validate semantic similarity between PDF content and QR data
     * @param {string} pdfText - Text extracted from PDF
     * @param {Object} qrData - Data from QR code
     */
    async validateSemantic(pdfText, qrData) {
        const payload = {
            pdf_text: pdfText,
            qr_data: qrData
        };

        return this.request('/api/validate-semantic', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    /**
     * Comprehensive ITR Analysis with multiple documents
     * @param {Object} documents - Object with document type as key and extracted data as value
     */
    async analyzeITRDocuments(documents) {
        const payload = {
            documents: documents
        };

        return this.request('/api/itr/analyze', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    /**
     * Process multiple documents for ITR filing
     * @param {Array} files - Array of file objects
     * @param {Array} documentTypes - Array of document type strings
     */
    async processMultipleDocuments(files, documentTypes) {
        const formData = new FormData();
        
        files.forEach((file, index) => {
            formData.append('files', file);
        });
        
        documentTypes.forEach((type) => {
            formData.append('document_types', type);
        });

        try {
            const response = await fetch(`${this.baseURL}/api/itr/process-documents`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Multi-document processing failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Multi-document processing error:', error);
            throw error;
        }
    }

    /**
     * Calculate tax refund based on income and deduction details
     * @param {Object} incomeDetails - Income information
     * @param {Object} deductions - Deduction information
     */
    async calculateTaxRefund(incomeDetails, deductions) {
        const payload = {
            income_details: incomeDetails,
            deductions: deductions
        };

        return this.request('/api/itr/calculate-refund', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    /**
     * Generate QR code from processed documents
     * @param {Object} documents - Object with document type as key and extracted data as value
     */
    async generateDocumentsQR(documents) {
        const payload = {
            documents: documents
        };

        return this.request('/api/documents/generate-qr', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    /**
     * Decode QR code data for ITR form filling
     * @param {string} qrData - QR code data string
     */
    async decodeQRData(qrData) {
        const payload = {
            qr_data: qrData
        };

        return this.request('/api/qr/decode', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    /**
     * Extract Named Entity Recognition (NER) from text
     * @param {string} text - Combined text from multiple documents
     * @param {Array} fieldTypes - Specific field types to extract
     */
    async extractNER(text, fieldTypes = []) {
        const payload = {
            text: text,
            field_types: fieldTypes.length > 0 ? fieldTypes : [
                'name', 'pan', 'aadhaar', 'email', 'mobile', 'date_of_birth',
                'gross_salary', 'tds_deducted', 'total_income', 'account_number',
                'ifsc', 'bank_name', 'employer', 'address', 'pincode'
            ]
        };

        return this.request('/api/ner/extract', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    /**
     * Auto-fill form fields using NER results
     * @param {Object} nerResults - NER extraction results
     * @param {Object} documentSources - Source documents for each field
     */
    async autoFillForm(nerResults, documentSources = {}) {
        const payload = {
            ner_results: nerResults,
            document_sources: documentSources,
            confidence_threshold: 0.7
        };

        return this.request('/api/form/auto-fill', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    /**
     * Combine multiple document extractions
     * @param {Object} documentExtractions - Object with document type as key and extraction data as value
     */
    async combineDocumentExtractions(documentExtractions) {
        const payload = {
            document_extractions: documentExtractions,
            merge_strategy: 'priority_based', // Use priority-based merging
            field_priorities: {
                name: ['aadhaar', 'form16', 'preregistration'],
                pan: ['form16', 'preregistration', 'aadhaar'],
                aadhaar: ['aadhaar'],
                email: ['preregistration', 'form16'],
                mobile: ['preregistration', 'aadhaar'],
                gross_salary: ['form16', 'bankSlip'],
                account_number: ['bankSlip'],
                bank_name: ['bankSlip']
            }
        };

        return this.request('/api/documents/combine', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }
}

// Create singleton instance
const apiService = new APIService();

export default apiService;