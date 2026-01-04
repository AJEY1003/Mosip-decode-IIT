/**
 * NER-based Field Extractor for ITR Documents
 * Extracts structured data from OCR text using pattern matching and NER techniques
 */

class NERExtractor {
    constructor() {
        // ITR-specific field patterns
        this.patterns = {
            // Personal Information
            name: [
                /name[:\s]*([A-Za-z\s]+)/i,
                /applicant[:\s]*([A-Za-z\s]+)/i,
                /full\s*name[:\s]*([A-Za-z\s]+)/i,
                /taxpayer[:\s]*([A-Za-z\s]+)/i
            ],
            
            pan: [
                /pan[:\s]*([A-Z]{5}[0-9]{4}[A-Z]{1})/i,
                /permanent\s*account\s*number[:\s]*([A-Z]{5}[0-9]{4}[A-Z]{1})/i,
                /\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b/g
            ],
            
            aadhaar: [
                /aadhaar[:\s]*(\d{4}\s*\d{4}\s*\d{4})/i,
                /aadhar[:\s]*(\d{4}\s*\d{4}\s*\d{4})/i,
                /\b(\d{4}\s*\d{4}\s*\d{4})\b/g
            ],
            
            date_of_birth: [
                /date\s*of\s*birth[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})/i,
                /dob[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})/i,
                /birth\s*date[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})/i,
                /born[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})/i,
                // Additional date formats
                /date\s*of\s*birth[:\s]*(\d{1,2}\s+\w+\s+\d{4})/i,  // 15 March 1990
                /dob[:\s]*(\d{1,2}\s+\w+\s+\d{4})/i,
                /birth\s*date[:\s]*(\d{1,2}\s+\w+\s+\d{4})/i,
                /date\s*of\s*birth[:\s]*(\w+\s+\d{1,2},?\s+\d{4})/i,  // March 15, 1990
                /dob[:\s]*(\w+\s+\d{1,2},?\s+\d{4})/i,
                /birth\s*date[:\s]*(\w+\s+\d{1,2},?\s+\d{4})/i,
                // Indian format variations
                /date\s*of\s*birth[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2})/i,  // DD/MM/YY
                /dob[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2})/i,
                // Flexible date patterns
                /(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})/g,  // Generic date pattern
                /(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4})/gi,  // 15 Jan 1990
                /((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2},?\s+\d{4})/gi  // Jan 15, 1990
            ],
            
            // Financial Information
            gross_salary: [
                /gross\s*salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /total\s*salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /annual\s*salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /gross\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                // Enhanced patterns for different formats
                /gross\s+salary\s+₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,  // "Gross Salary ₹ 8,50,000"
                /gross\s+income:\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,      // "Gross Income: 850,000"
                /total\s+income\s+₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i   // "Total Income ₹ 8,50,000"
            ],
            
            basic_salary: [
                /basic\s*salary[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /basic\s*pay[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /basic[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                // Enhanced patterns for Form-16 format
                /basic\s+salary\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,  // "Basic Salary 6,00,000"
                /basic\s+salary\s+(\d+(?:,\d+)*(?:\.\d{2})?)/i,       // "Basic Salary 600000"
                /basic\s+pay\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i     // "Basic Pay ₹ 6,00,000"
            ],
            
            hra_received: [
                /hra\s*received[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /house\s*rent\s*allowance[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /hra[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                // Enhanced patterns for Form-16 format
                /hra\s+received\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,  // "HRA Received 2,40,000"
                /hra\s+received\s+(\d+(?:,\d+)*(?:\.\d{2})?)/i,       // "HRA Received 240000"
                /house\s+rent\s+allowance\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i  // "House Rent Allowance ₹ 2,40,000"
            ],
            
            other_allowances: [
                /other\s*allowances[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /other\s*allowance[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /allowances[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /miscellaneous\s*allowances[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                // Enhanced patterns for Form-16 format
                /other\s+allowances\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,  // "Other Allowances 1,10,000"
                /other\s+allowances\s+(\d+(?:,\d+)*(?:\.\d{2})?)/i,       // "Other Allowances 110000"
                /miscellaneous\s+allowances\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i  // "Miscellaneous Allowances ₹ 1,10,000"
            ],
            
            professional_tax: [
                /professional\s*tax[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /prof\s*tax[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /pt[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                // Enhanced patterns for Form-16 format
                /professional\s+tax\s+₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,  // "Professional Tax 2,400"
                /professional\s+tax\s+(\d+(?:,\d+)*(?:\.\d{2})?)/i        // "Professional Tax 2400"
            ],
            
            tds_deducted: [
                /tds\s*deducted[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /tax\s*deducted[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /tds[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                // Enhanced patterns
                /tds\s+deducted\s+₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,   // "TDS Deducted ₹ 75,000"
                /tds\s+deducted:\s*रे\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i, // "TDS Deducted: रे 75,000"
                /tds\s+deducted:\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i       // "TDS Deducted: 75,000"
            ],
            
            total_income: [
                /total\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /gross\s*total\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                /annual\s*income[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,
                // Enhanced patterns
                /total\s+income\s+₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,   // "Total Income ₹ 8,50,000"
                /net\s+income:\s*&\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i,    // "Net Income: & 7,75,000"
                /net\s+income:\s*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)/i    // "Net Income: 7,75,000"
            ],
            
            // Bank Information
            account_number: [
                /account\s*number[:\s]*(\d{9,18})/i,
                /bank\s*account[:\s]*(\d{9,18})/i,
                /a\/c\s*no[:\s]*(\d{9,18})/i
            ],
            
            ifsc: [
                /ifsc[:\s]*([A-Z]{4}0[A-Z0-9]{6})/i,
                /ifsc\s*code[:\s]*([A-Z]{4}0[A-Z0-9]{6})/i,
                /\b([A-Z]{4}0[A-Z0-9]{6})\b/g
            ],
            
            bank_name: [
                /bank\s*name[:\s]*([A-Za-z\s&]+)/i,
                /bank[:\s]*([A-Za-z\s&]+)/i
            ],
            
            // Employer Information
            employer: [
                /employer[:\s]*([A-Za-z\s&\.]+)/i,
                /company[:\s]*([A-Za-z\s&\.]+)/i,
                /organization[:\s]*([A-Za-z\s&\.]+)/i,
                /firm[:\s]*([A-Za-z\s&\.]+)/i
            ],
            
            // Address Information
            address: [
                /address[:\s]*([A-Za-z0-9\s,\-\.]+)/i,
                /residential\s*address[:\s]*([A-Za-z0-9\s,\-\.]+)/i,
                /permanent\s*address[:\s]*([A-Za-z0-9\s,\-\.]+)/i
            ],
            
            pincode: [
                /pin\s*code[:\s]*(\d{6})/i,
                /pincode[:\s]*(\d{6})/i,
                /postal\s*code[:\s]*(\d{6})/i,
                /\b(\d{6})\b/g
            ],
            
            // Contact Information
            mobile: [
                /mobile[:\s]*(\+?91\s*\d{10})/i,
                /phone[:\s]*(\+?91\s*\d{10})/i,
                /contact[:\s]*(\+?91\s*\d{10})/i,
                /\b(\+?91\s*\d{10})\b/g
            ],
            
            email: [
                /email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i,
                /e-mail[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i,
                /\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b/g
            ],
            
            // Assessment Year
            assessment_year: [
                /assessment\s*year[:\s]*(\d{4}-\d{2})/i,
                /ay[:\s]*(\d{4}-\d{2})/i,
                /a\.y[:\s]*(\d{4}-\d{2})/i
            ],
            
            financial_year: [
                /financial\s*year[:\s]*(\d{4}-\d{2})/i,
                /fy[:\s]*(\d{4}-\d{2})/i,
                /f\.y[:\s]*(\d{4}-\d{2})/i
            ]
        };
        
        // Field confidence scoring
        this.confidenceWeights = {
            exact_match: 1.0,
            pattern_match: 0.8,
            context_match: 0.6,
            fuzzy_match: 0.4
        };
    }
    
    /**
     * Extract structured data from OCR text
     * @param {string} text - Raw OCR text
     * @param {string} documentType - Type of document (ITR, Form16, etc.)
     * @returns {object} Extracted structured data with confidence scores
     */
    extractFields(text, documentType = 'ITR') {
        if (!text || typeof text !== 'string') {
            return { fields: {}, confidence: 0, metadata: { error: 'Invalid input text' } };
        }
        
        const extractedFields = {};
        const confidenceScores = {};
        const metadata = {
            documentType,
            textLength: text.length,
            extractionTimestamp: new Date().toISOString(),
            patternsMatched: []
        };
        
        // Clean and normalize text
        const cleanText = this.cleanText(text);
        
        // Extract each field type
        for (const [fieldName, patterns] of Object.entries(this.patterns)) {
            const result = this.extractField(cleanText, fieldName, patterns);
            if (result.value) {
                extractedFields[fieldName] = result.value;
                confidenceScores[fieldName] = result.confidence;
                metadata.patternsMatched.push({
                    field: fieldName,
                    pattern: result.matchedPattern,
                    confidence: result.confidence
                });
            }
        }
        
        // Calculate overall confidence
        const overallConfidence = this.calculateOverallConfidence(confidenceScores);
        
        // Post-process and validate fields
        const validatedFields = this.validateAndCleanFields(extractedFields);
        
        return {
            fields: validatedFields,
            confidence: overallConfidence,
            confidenceScores,
            metadata
        };
    }
    
    /**
     * Extract a specific field using multiple patterns
     */
    extractField(text, fieldName, patterns) {
        let bestMatch = null;
        let highestConfidence = 0;
        let matchedPattern = null;
        
        for (const pattern of patterns) {
            const matches = text.match(pattern);
            if (matches) {
                const value = matches[1] || matches[0];
                const confidence = this.calculateFieldConfidence(fieldName, value, pattern);
                
                if (confidence > highestConfidence) {
                    bestMatch = value;
                    highestConfidence = confidence;
                    matchedPattern = pattern.toString();
                }
            }
        }
        
        return {
            value: bestMatch ? this.cleanFieldValue(fieldName, bestMatch) : null,
            confidence: highestConfidence,
            matchedPattern
        };
    }
    
    /**
     * Clean and normalize text for better pattern matching
     */
    cleanText(text) {
        return text
            .replace(/\s+/g, ' ')  // Normalize whitespace
            .replace(/[^\w\s@.\-\/₹,]/g, ' ')  // Remove special chars except important ones
            .trim();
    }
    
    /**
     * Clean and format field values
     */
    cleanFieldValue(fieldName, value) {
        if (!value) return null;
        
        value = value.trim();
        
        switch (fieldName) {
            case 'name':
            case 'employer':
            case 'bank_name':
                return value.replace(/\s+/g, ' ').replace(/[^\w\s&\.]/g, '');
            
            case 'date_of_birth':
                return this.normalizeDate(value);
            
            case 'pan':
                return value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            
            case 'aadhaar':
                return value.replace(/[^\d\s]/g, '').replace(/(\d{4})(\d{4})(\d{4})/, '$1 $2 $3');
            
            case 'ifsc':
                return value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            
            case 'mobile':
                return value.replace(/[^\d+]/g, '');
            
            case 'email':
                return value.toLowerCase();
            
            case 'gross_salary':
            case 'tds_deducted':
            case 'total_income':
                return value.replace(/[^\d.,]/g, '');
            
            default:
                return value;
        }
    }
    
    /**
     * Normalize various date formats to YYYY-MM-DD format
     * Handles multiple input formats commonly found in Indian documents
     */
    normalizeDate(dateStr) {
        if (!dateStr) return dateStr;
        
        // Clean the date string
        dateStr = dateStr.trim();
        
        // Month name mappings
        const monthNames = {
            'jan': '01', 'january': '01',
            'feb': '02', 'february': '02',
            'mar': '03', 'march': '03',
            'apr': '04', 'april': '04',
            'may': '05',
            'jun': '06', 'june': '06',
            'jul': '07', 'july': '07',
            'aug': '08', 'august': '08',
            'sep': '09', 'september': '09',
            'oct': '10', 'october': '10',
            'nov': '11', 'november': '11',
            'dec': '12', 'december': '12'
        };
        
        try {
            // Pattern 1: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
            if (/\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4}/.test(dateStr)) {
                const parts = dateStr.split(/[\/\-\.]/);
                const day = parts[0].padStart(2, '0');
                const month = parts[1].padStart(2, '0');
                const year = parts[2];
                return `${year}-${month}-${day}`;
            }
            
            // Pattern 2: DD/MM/YY (assuming 20YY for YY < 50, 19YY otherwise)
            else if (/\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2}/.test(dateStr)) {
                const parts = dateStr.split(/[\/\-\.]/);
                const day = parts[0].padStart(2, '0');
                const month = parts[1].padStart(2, '0');
                let year = parseInt(parts[2]);
                // Convert 2-digit year to 4-digit
                year = year < 50 ? `20${parts[2]}` : `19${parts[2]}`;
                return `${year}-${month}-${day}`;
            }
            
            // Pattern 3: DD Month YYYY (15 March 1990)
            else if (/\d{1,2}\s+\w+\s+\d{4}/.test(dateStr)) {
                const parts = dateStr.split(/\s+/);
                const day = parts[0].padStart(2, '0');
                const monthName = parts[1].toLowerCase();
                const year = parts[2];
                
                // Convert month name to number
                for (const [name, num] of Object.entries(monthNames)) {
                    if (monthName.startsWith(name)) {
                        return `${year}-${num}-${day}`;
                    }
                }
                return dateStr; // Return original if month not found
            }
            
            // Pattern 4: Month DD, YYYY (March 15, 1990)
            else if (/\w+\s+\d{1,2},?\s+\d{4}/.test(dateStr)) {
                // Remove comma if present
                const cleanStr = dateStr.replace(',', '');
                const parts = cleanStr.split(/\s+/);
                const monthName = parts[0].toLowerCase();
                const day = parts[1].padStart(2, '0');
                const year = parts[2];
                
                // Convert month name to number
                for (const [name, num] of Object.entries(monthNames)) {
                    if (monthName.startsWith(name)) {
                        return `${year}-${num}-${day}`;
                    }
                }
                return dateStr; // Return original if month not found
            }
            
            // Pattern 5: DD Mon YYYY (15 Jan 1990)
            else if (/\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}/i.test(dateStr)) {
                const parts = dateStr.split(/\s+/);
                const day = parts[0].padStart(2, '0');
                const monthName = parts[1].toLowerCase();
                const year = parts[2];
                
                // Convert month name to number
                for (const [name, num] of Object.entries(monthNames)) {
                    if (monthName.startsWith(name)) {
                        return `${year}-${num}-${day}`;
                    }
                }
                return dateStr; // Return original if month not found
            }
            
            // If no pattern matches, return original
            return dateStr;
            
        } catch (error) {
            console.warn(`Date normalization failed for '${dateStr}':`, error);
            return dateStr;
        }
    }
    
    /**
     * Calculate confidence score for a field match
     */
    calculateFieldConfidence(fieldName, value, pattern) {
        let confidence = this.confidenceWeights.pattern_match;
        
        // Boost confidence for well-formatted values
        switch (fieldName) {
            case 'pan':
                confidence = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(value) ? 0.95 : 0.7;
                break;
            case 'aadhaar':
                confidence = /^\d{4}\s*\d{4}\s*\d{4}$/.test(value) ? 0.9 : 0.6;
                break;
            case 'ifsc':
                confidence = /^[A-Z]{4}0[A-Z0-9]{6}$/.test(value) ? 0.9 : 0.6;
                break;
            case 'email':
                confidence = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? 0.9 : 0.5;
                break;
            case 'mobile':
                confidence = /^\+?91\s*\d{10}$/.test(value) ? 0.9 : 0.6;
                break;
            case 'pincode':
                confidence = /^\d{6}$/.test(value) ? 0.9 : 0.6;
                break;
        }
        
        return Math.min(confidence, 1.0);
    }
    
    /**
     * Calculate overall extraction confidence
     */
    calculateOverallConfidence(confidenceScores) {
        const scores = Object.values(confidenceScores);
        if (scores.length === 0) return 0;
        
        const average = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        const weightedScore = Math.min(average * (scores.length / 10), 1.0); // Boost for more fields
        
        return Math.round(weightedScore * 100) / 100;
    }
    
    /**
     * Validate and clean extracted fields
     */
    validateAndCleanFields(fields) {
        const validated = {};
        
        for (const [key, value] of Object.entries(fields)) {
            if (value && this.isValidField(key, value)) {
                validated[key] = value;
            }
        }
        
        return validated;
    }
    
    /**
     * Validate individual field values
     */
    isValidField(fieldName, value) {
        if (!value || typeof value !== 'string') return false;
        
        switch (fieldName) {
            case 'pan':
                return /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(value);
            case 'aadhaar':
                return /^\d{4}\s\d{4}\s\d{4}$/.test(value);
            case 'ifsc':
                return /^[A-Z]{4}0[A-Z0-9]{6}$/.test(value);
            case 'email':
                return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
            case 'mobile':
                return /^\+?91\s*\d{10}$/.test(value);
            case 'pincode':
                return /^\d{6}$/.test(value);
            case 'account_number':
                return /^\d{9,18}$/.test(value);
            default:
                return value.length > 0 && value.length < 200;
        }
    }
    
    /**
     * Get field mapping for different form types
     */
    getFieldMapping(formType) {
        const mappings = {
            'pre-registration': ['name', 'pan', 'date_of_birth', 'aadhaar', 'mobile', 'email', 'address', 'pincode'],
            'bank-details': ['account_number', 'ifsc', 'bank_name'],
            'form16': ['employer', 'gross_salary', 'tds_deducted', 'assessment_year', 'financial_year'],
            'income-details': ['total_income', 'gross_salary', 'tds_deducted'],
            'contact-info': ['mobile', 'email', 'address', 'pincode']
        };
        
        return mappings[formType] || Object.keys(this.patterns);
    }
}

// Export singleton instance
export default new NERExtractor();