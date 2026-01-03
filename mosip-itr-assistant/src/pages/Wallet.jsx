import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { QrCode, Download, Clock, FileText, CheckCircle, XCircle, Eye } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import SimpleQR from '../components/SimpleQR';
import './Wallet.css';
import { useLocation } from 'react-router-dom';

const WalletPage = () => {
    const location = useLocation();
    const [qrDatabase, setQrDatabase] = useState([]);
    const [selectedQR, setSelectedQR] = useState(null);

    useEffect(() => {
        // Debug logging
        console.log('🔍 Wallet - Location State:', location.state);

        // Load existing QR codes from localStorage
        const stored = localStorage.getItem('qr_database');
        let existing = stored ? JSON.parse(stored) : [];

        console.log('📦 Wallet - Existing QR Database:', existing);

        // Add new QR from validation if available
        if (location.state?.signedQR || location.state?.extractedData) {
            console.log('✅ Wallet - New QR Data Found!');
            console.log('  - signedQR:', location.state?.signedQR);
            console.log('  - extractedData:', location.state?.extractedData);
            console.log('  - qrImageData:', location.state?.qrImageData);

            // Extract QR image - prioritize the captured QR image from validation
            let qrImage = null;
            if (location.state?.qrImageData && typeof location.state.qrImageData === 'string' && location.state.qrImageData.startsWith('data:image')) {
                qrImage = location.state.qrImageData;
            } else if (location.state?.qrData && typeof location.state.qrData === 'string' && location.state.qrData.startsWith('data:image')) {
                qrImage = location.state.qrData;
            } else if (location.state?.extractedData) {
                // Generate QR code as fallback
                const generateFallbackQR = async () => {
                    try {
                        const QRCode = (await import('qrcode')).default;
                        const qrText = JSON.stringify(location.state.extractedData);
                        const qrImageUrl = await QRCode.toDataURL(qrText, {
                            width: 400,
                            margin: 2,
                            color: {
                                dark: '#000000',
                                light: '#ffffff'
                            }
                        });
                        return qrImageUrl;
                    } catch (error) {
                        console.error('Failed to generate fallback QR:', error);
                        return null;
                    }
                };
                
                generateFallbackQR().then(fallbackQR => {
                    if (fallbackQR) {
                        qrImage = fallbackQR;
                        console.log('🔄 Wallet - Generated fallback QR image');
                        
                        // Update the QR database with the fallback image
                        const newQR = {
                            id: Date.now(),
                            timestamp: new Date().toISOString(),
                            qrImage: qrImage,
                            workflowId: location.state?.signedQR?.workflow_id,
                            verified: location.state?.verified || false,
                            validationScore: location.state?.score || null,
                            metadata: {
                                name: location.state?.extractedData?.name || 'Unknown',
                                pan: location.state?.extractedData?.pan || location.state?.extractedData?.pan_number || 'N/A',
                                documentType: 'ITR Document',
                                encoding: location.state?.signedQR?.qr_code?.encoding || 'CBOR'
                            }
                        };

                        const isDuplicate = existing.some(qr => qr.workflowId === newQR.workflowId);
                        if (!isDuplicate && newQR.qrImage) {
                            const updatedDatabase = [newQR, ...existing];
                            localStorage.setItem('qr_database', JSON.stringify(updatedDatabase));
                            setQrDatabase(updatedDatabase);
                            console.log('💾 Wallet - Saved fallback QR to localStorage');
                        }
                    }
                });
                return; // Exit early for async fallback generation
            }

            console.log('🖼️ Wallet - QR Image:', qrImage ? qrImage.substring(0, 50) + '...' : 'No valid image');

            const newQR = {
                id: Date.now(),
                timestamp: new Date().toISOString(),
                qrImage: qrImage,
                workflowId: location.state?.signedQR?.workflow_id,
                verified: location.state?.verified || false,
                validationScore: location.state?.score || null,
                metadata: {
                    name: location.state?.extractedData?.name || 'Unknown',
                    pan: location.state?.extractedData?.pan || location.state?.extractedData?.pan_number || 'N/A',
                    documentType: 'ITR Document',
                    encoding: location.state?.signedQR?.qr_code?.encoding || 'CBOR'
                }
            };

            console.log('📝 Wallet - New QR Object:', newQR);

            // Check if not duplicate and has QR image
            const isDuplicate = existing.some(qr => qr.workflowId === newQR.workflowId);
            if (!isDuplicate && newQR.qrImage) {
                existing = [newQR, ...existing];
                localStorage.setItem('qr_database', JSON.stringify(existing));
                console.log('💾 Wallet - Saved to localStorage');
            } else {
                console.log('⚠️ Wallet - Duplicate or missing QR image', { isDuplicate, hasQrImage: !!newQR.qrImage });
            }
        } else {
            console.log('❌ Wallet - No new QR data in location.state');
        }

        setQrDatabase(existing);
        console.log('🎯 Wallet - Final Database:', existing);
    }, [location.state]);

    const formatTimestamp = (isoString) => {
        const date = new Date(isoString);
        return {
            date: date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }),
            time: date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
        };
    };

    const downloadQR = (qr) => {
        if (qr.qrImage) {
            const link = document.createElement('a');
            link.href = qr.qrImage;
            link.download = `QR_${qr.metadata.name}_${qr.timestamp}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    };

    const exportAllData = () => {
        const dataStr = JSON.stringify(qrDatabase, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `QR_Database_${new Date().toISOString()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    return (
        <div className="relative min-h-screen w-full overflow-hidden">
            {/* Dark gradient background with texture */}
            <div className="absolute inset-0 bg-gradient-to-br from-[hsl(var(--gov-navy))] via-[hsl(var(--gov-green-dark))] to-[hsl(var(--gov-green))]" />
            
            {/* Subtle grid pattern */}
            <div 
                className="absolute inset-0 opacity-[0.03]"
                style={{
                    backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
                    backgroundSize: '40px 40px'
                }}
            />
            
            {/* Radial glow accent */}
            <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-[hsl(var(--gov-gold))] opacity-[0.08] blur-[150px] rounded-full -translate-y-1/2 translate-x-1/3" />
            <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-[hsl(var(--gov-green-light))] opacity-[0.1] blur-[120px] rounded-full translate-y-1/2 -translate-x-1/3" />

            <div className="relative z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8"
            >
                {/* Header Section */}
                <div className="text-center mb-16">
                    <div className="inline-flex items-center gap-3 mb-6">
                        <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
                        <span className="text-sm font-semibold text-white/70">
                            Digital Wallet
                        </span>
                        <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
                    </div>
                    
                    <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-white">
                        QR Code Database
                    </h1>
                    
                    <p className="text-xl text-white/80 leading-relaxed max-w-3xl mx-auto">
                        Verified credentials with timestamps and metadata stored securely in your digital wallet
                    </p>
                </div>

                {qrDatabase.length === 0 ? (
                    <div className="bg-white rounded-2xl p-12 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))] text-center">
                        <div className="w-20 h-20 bg-[hsl(var(--muted))] rounded-2xl flex items-center justify-center mx-auto mb-6">
                            <QrCode className="w-10 h-10 text-[hsl(var(--muted-foreground))]" />
                        </div>
                        <h3 className="text-2xl font-bold text-[hsl(var(--foreground))] mb-4">No QR Codes Yet</h3>
                        <p className="text-[hsl(var(--muted-foreground))] text-lg">
                            Upload and verify documents to generate QR codes for your digital wallet
                        </p>
                    </div>
                ) : (
                    <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))] overflow-hidden">
                        {/* Table Header */}
                        <div className="bg-[hsl(var(--muted))]/30 px-6 py-4 border-b border-[hsl(var(--border))]">
                            <div className="flex items-center justify-between">
                                <h2 className="text-2xl font-bold text-[hsl(var(--foreground))] flex items-center gap-3">
                                    <div className="w-10 h-10 bg-[hsl(var(--gov-green))] rounded-xl flex items-center justify-center">
                                        <QrCode className="w-5 h-5 text-white" />
                                    </div>
                                    Stored Credentials ({qrDatabase.length})
                                </h2>
                                <Button
                                    onClick={exportAllData}
                                    className="bg-[hsl(var(--gov-gold))] hover:bg-[hsl(var(--gov-gold-dark))] text-white font-semibold py-2 px-4 rounded-xl flex items-center gap-2 transition-all"
                                >
                                    <Download className="w-4 h-4" />
                                    Export All
                                </Button>
                            </div>
                        </div>

                        {/* Table Content */}
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-[hsl(var(--muted))]/20">
                                    <tr>
                                        <th className="text-left py-4 px-6 font-semibold text-[hsl(var(--foreground))] text-sm">QR Code</th>
                                        <th className="text-left py-4 px-6 font-semibold text-[hsl(var(--foreground))] text-sm">Document Info</th>
                                        <th className="text-left py-4 px-6 font-semibold text-[hsl(var(--foreground))] text-sm">Status</th>
                                        <th className="text-left py-4 px-6 font-semibold text-[hsl(var(--foreground))] text-sm">Created</th>
                                        <th className="text-left py-4 px-6 font-semibold text-[hsl(var(--foreground))] text-sm">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {qrDatabase.map((qr, index) => {
                                        const { date, time } = formatTimestamp(qr.timestamp);
                                        return (
                                            <motion.tr
                                                key={qr.id}
                                                initial={{ opacity: 0, y: 20 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                transition={{ delay: index * 0.05 }}
                                                className="border-b border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]/20 transition-colors"
                                            >
                                                {/* QR Code Column */}
                                                <td className="py-4 px-6">
                                                    <div className="flex items-center gap-4">
                                                        <div 
                                                            className="w-16 h-16 bg-white rounded-xl border-2 border-[hsl(var(--border))] flex items-center justify-center cursor-pointer hover:border-[hsl(var(--gov-green))] transition-colors"
                                                            onClick={() => setSelectedQR(qr)}
                                                        >
                                                            {qr.qrImage ? (
                                                                <img
                                                                    src={qr.qrImage}
                                                                    alt="QR Code"
                                                                    className="w-full h-full object-contain rounded-lg"
                                                                />
                                                            ) : (
                                                                <QrCode className="w-8 h-8 text-[hsl(var(--muted-foreground))]" />
                                                            )}
                                                        </div>
                                                        <div className="text-xs text-[hsl(var(--muted-foreground))]">
                                                            {qr.workflowId ? qr.workflowId.substring(0, 8) + '...' : 'No ID'}
                                                        </div>
                                                    </div>
                                                </td>

                                                {/* Document Info Column */}
                                                <td className="py-4 px-6">
                                                    <div className="space-y-1">
                                                        <div className="font-semibold text-[hsl(var(--foreground))]">
                                                            {qr.metadata.name}
                                                        </div>
                                                        <div className="text-sm text-[hsl(var(--muted-foreground))] flex items-center gap-2">
                                                            <FileText className="w-3 h-3" />
                                                            {qr.metadata.documentType}
                                                        </div>
                                                        <div className="text-sm text-[hsl(var(--muted-foreground))]">
                                                            PAN: <span className="font-mono">{qr.metadata.pan}</span>
                                                        </div>
                                                    </div>
                                                </td>

                                                {/* Status Column */}
                                                <td className="py-4 px-6">
                                                    <div className="space-y-2">
                                                        <div className="flex items-center gap-2">
                                                            {qr.verified ? (
                                                                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                                                                    <CheckCircle className="w-3 h-3" />
                                                                    Verified
                                                                </span>
                                                            ) : (
                                                                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800">
                                                                    <XCircle className="w-3 h-3" />
                                                                    Unverified
                                                                </span>
                                                            )}
                                                        </div>
                                                        {qr.validationScore && (
                                                            <div className="text-xs text-[hsl(var(--muted-foreground))]">
                                                                Score: <span className="font-semibold">{qr.validationScore}%</span>
                                                            </div>
                                                        )}
                                                    </div>
                                                </td>

                                                {/* Created Column */}
                                                <td className="py-4 px-6">
                                                    <div className="space-y-1">
                                                        <div className="text-sm font-medium text-[hsl(var(--foreground))]">
                                                            {date}
                                                        </div>
                                                        <div className="text-xs text-[hsl(var(--muted-foreground))] flex items-center gap-1">
                                                            <Clock className="w-3 h-3" />
                                                            {time}
                                                        </div>
                                                    </div>
                                                </td>

                                                {/* Actions Column */}
                                                <td className="py-4 px-6">
                                                    <div className="flex items-center gap-2">
                                                        <button
                                                            onClick={() => setSelectedQR(qr)}
                                                            className="p-2 text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--gov-green))] hover:bg-[hsl(var(--gov-green))]/10 rounded-lg transition-colors"
                                                            title="View Details"
                                                        >
                                                            <Eye className="w-4 h-4" />
                                                        </button>
                                                        <button
                                                            onClick={() => downloadQR(qr)}
                                                            className="p-2 text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--gov-gold))] hover:bg-[hsl(var(--gov-gold))]/10 rounded-lg transition-colors"
                                                            title="Download QR"
                                                        >
                                                            <Download className="w-4 h-4" />
                                                        </button>
                                                    </div>
                                                </td>
                                            </motion.tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* QR Detail Modal */}
                {selectedQR && (
                    <motion.div
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        onClick={() => setSelectedQR(null)}
                    >
                        <motion.div
                            className="bg-white rounded-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-2xl font-bold text-[hsl(var(--foreground))]">QR Code Details</h2>
                                <button
                                    onClick={() => setSelectedQR(null)}
                                    className="p-2 text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))] rounded-lg transition-colors"
                                >
                                    <XCircle className="w-5 h-5" />
                                </button>
                            </div>
                            
                            <div className="grid md:grid-cols-2 gap-8">
                                {/* QR Code Display */}
                                <div className="text-center">
                                    <div className="bg-[hsl(var(--muted))]/30 rounded-2xl p-6 mb-4">
                                        {selectedQR.qrImage ? (
                                            <img
                                                src={selectedQR.qrImage}
                                                alt="QR Code"
                                                className="w-full max-w-[300px] mx-auto rounded-xl"
                                            />
                                        ) : (
                                            <div className="w-full aspect-square bg-[hsl(var(--muted))] rounded-xl flex items-center justify-center">
                                                <QrCode className="w-20 h-20 text-[hsl(var(--muted-foreground))]" />
                                            </div>
                                        )}
                                    </div>
                                    <Button
                                        onClick={() => downloadQR(selectedQR)}
                                        className="bg-[hsl(var(--gov-green))] hover:bg-[hsl(var(--gov-green-dark))] text-white font-semibold py-2 px-4 rounded-xl flex items-center gap-2 mx-auto transition-all"
                                    >
                                        <Download className="w-4 h-4" />
                                        Download QR
                                    </Button>
                                </div>

                                {/* Metadata */}
                                <div className="space-y-4">
                                    <div className="space-y-3">
                                        <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                            <span className="text-[hsl(var(--muted-foreground))] font-medium">Name:</span>
                                            <span className="font-semibold text-[hsl(var(--foreground))]">{selectedQR.metadata.name}</span>
                                        </div>
                                        <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                            <span className="text-[hsl(var(--muted-foreground))] font-medium">PAN:</span>
                                            <span className="font-mono text-[hsl(var(--foreground))]">{selectedQR.metadata.pan}</span>
                                        </div>
                                        <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                            <span className="text-[hsl(var(--muted-foreground))] font-medium">Document:</span>
                                            <span className="text-[hsl(var(--foreground))]">{selectedQR.metadata.documentType}</span>
                                        </div>
                                        <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                            <span className="text-[hsl(var(--muted-foreground))] font-medium">Encoding:</span>
                                            <span className="text-[hsl(var(--foreground))]">{selectedQR.metadata.encoding}</span>
                                        </div>
                                        {selectedQR.workflowId && (
                                            <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                                <span className="text-[hsl(var(--muted-foreground))] font-medium">Workflow ID:</span>
                                                <span className="text-xs font-mono text-[hsl(var(--foreground))] break-all">
                                                    {selectedQR.workflowId}
                                                </span>
                                            </div>
                                        )}
                                        <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                            <span className="text-[hsl(var(--muted-foreground))] font-medium">Created:</span>
                                            <span className="text-[hsl(var(--foreground))]">
                                                {formatTimestamp(selectedQR.timestamp).date} at {formatTimestamp(selectedQR.timestamp).time}
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center py-2 border-b border-[hsl(var(--border))]">
                                            <span className="text-[hsl(var(--muted-foreground))] font-medium">Status:</span>
                                            <span className={`flex items-center gap-1 ${selectedQR.verified ? 'text-green-600' : 'text-red-600'}`}>
                                                {selectedQR.verified ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                                                {selectedQR.verified ? 'Verified' : 'Unverified'}
                                            </span>
                                        </div>
                                        {selectedQR.validationScore && (
                                            <div className="flex justify-between items-center py-2">
                                                <span className="text-[hsl(var(--muted-foreground))] font-medium">Validation Score:</span>
                                                <span className="font-semibold text-[hsl(var(--gov-green))]">{selectedQR.validationScore}%</span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </motion.div>
                </div>
            </div>
        </div>
    );
};

export default WalletPage;
