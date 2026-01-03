import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import Button from './Button';
import './FileUpload.css';

const FileUpload = ({
    label = "Upload Document",
    accept = ".pdf,.jpg,.jpeg,.png",
    maxSize = "10MB",
    onUpload,
    helperText,
    compact = false
}) => {
    const [dragActive, setDragActive] = useState(false);
    const [file, setFile] = useState(null);
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState('idle'); // idle, uploading, success, error
    const inputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (file) => {
        setFile(file);
        setStatus('uploading');

        // Simulate upload progress
        let currentProgress = 0;
        const interval = setInterval(() => {
            currentProgress += 5;
            if (currentProgress >= 100) {
                clearInterval(interval);
                setStatus('success');
                if (onUpload) onUpload(file);
            }
            setProgress(currentProgress);
        }, 100);
    };

    const resetUpload = () => {
        setFile(null);
        setProgress(0);
        setStatus('idle');
    };

    return (
        <div className={`file-upload-container ${compact ? 'compact' : ''}`}>
            {!compact && (
                <div className="upload-label">
                    <h3>{label}</h3>
                    {helperText && <p>{helperText}</p>}
                </div>
            )}

            <AnimatePresence mode='wait'>
                {!file ? (
                    <motion.div
                        className={`drop-zone ${dragActive ? 'active' : ''} ${compact ? 'compact' : ''}`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                        onClick={() => inputRef.current.click()}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        key="dropzone"
                    >
                        <input
                            ref={inputRef}
                            type="file"
                            className="file-input"
                            accept={accept}
                            onChange={handleChange}
                        />
                        <div className="drop-content">
                            <div className={`icon-wrapper ${compact ? 'compact' : ''}`}>
                                <Upload size={compact ? 20 : 32} />
                            </div>
                            <p className={compact ? 'compact' : ''}>
                                {compact ? 'Click to upload' : 'Drag & Drop your file here or '}
                                {!compact && <span>Browse</span>}
                            </p>
                            {helperText && (
                                <span className={`file-meta ${compact ? 'compact' : ''}`}>
                                    {compact ? helperText : `Supports ${accept} (Max ${maxSize})`}
                                </span>
                            )}
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        className={`file-preview ${compact ? 'compact' : ''}`}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        key="preview"
                    >
                        <div className="file-info-row">
                            <div className="file-icon">
                                <FileText size={compact ? 16 : 24} />
                            </div>
                            <div className="file-details">
                                <span className={`file-name ${compact ? 'compact' : ''}`}>{file.name}</span>
                                <span className={`file-size ${compact ? 'compact' : ''}`}>{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                            </div>
                            <div className="file-status">
                                {status === 'success' && <CheckCircle className="text-success" size={compact ? 16 : 20} />}
                            </div>
                        </div>

                        <div className="progress-container">
                            <motion.div
                                className="progress-bar"
                                initial={{ width: 0 }}
                                animate={{ width: `${progress}%` }}
                            />
                        </div>

                        {status === 'success' && (
                            <div className="file-actions">
                                <Button variant="ghost" size="small" onClick={resetUpload}>Remove</Button>
                            </div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default FileUpload;
