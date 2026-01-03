import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    CheckCircle, 
    XCircle, 
    ArrowRight, 
    Home, 
    Database, 
    AlertCircle, 
    BarChart3,
    Upload,
    Settings,
    User,
    Shield,
    FileText,
    TrendingUp,
    Calendar,
    Clock,
    Activity,
    Eye,
    Info,
    Wallet,
    Search,
    Bell,
    Menu,
    ChevronRight,
    Download,
    RefreshCw,
    Sparkles,
    Star,
    Zap
} from 'lucide-react';

// Sparkle Component for glitter effects
const Sparkle = ({ delay = 0, duration = 2 }) => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0, rotate: 0 }}
            animate={{ 
                opacity: [0, 1, 0], 
                scale: [0, 1, 0], 
                rotate: [0, 180, 360],
                x: [0, Math.random() * 100 - 50],
                y: [0, Math.random() * 100 - 50]
            }}
            transition={{ 
                duration, 
                delay, 
                repeat: Infinity, 
                repeatDelay: Math.random() * 3 + 2 
            }}
            className="absolute pointer-events-none"
        >
            <Star className="w-3 h-3 text-yellow-300 fill-current" />
        </motion.div>
    );
};

// Animated Progress Ring Component
const ProgressRing = ({ progress, size = 160, strokeWidth = 10, color = '#10b981' }) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const strokeDasharray = `${circumference} ${circumference}`;
    const strokeDashoffset = circumference - (progress / 100) * circumference;

    return (
        <div className="relative">
            <svg width={size} height={size} className="transform -rotate-90">
                {/* Background circle */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth={strokeWidth}
                    fill="transparent"
                />
                {/* Progress circle */}
                <motion.circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke={color}
                    strokeWidth={strokeWidth}
                    fill="transparent"
                    strokeDasharray={strokeDasharray}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset }}
                    transition={{ duration: 2, ease: "easeInOut", delay: 0.5 }}
                    strokeLinecap="round"
                    style={{
                        filter: `drop-shadow(0 0 10px ${color}40)`
                    }}
                />
            </svg>
            {/* Sparkles around the ring */}
            {[...Array(8)].map((_, i) => (
                <Sparkle key={i} delay={i * 0.3} />
            ))}
        </div>
    );
};

// Mini Chart Component
const MiniChart = ({ data, color = '#10b981' }) => {
    const maxValue = Math.max(...data);
    const points = data.map((value, index) => {
        const x = (index / (data.length - 1)) * 100;
        const y = 100 - (value / maxValue) * 80;
        return `${x},${y}`;
    }).join(' ');

    return (
        <div className="w-full h-16 relative">
            <svg width="100%" height="100%" viewBox="0 0 100 100" className="absolute inset-0">
                <motion.polyline
                    fill="none"
                    stroke={color}
                    strokeWidth="2"
                    points={points}
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 2, ease: "easeInOut" }}
                    style={{
                        filter: `drop-shadow(0 0 4px ${color}60)`
                    }}
                />
                {data.map((value, index) => (
                    <motion.circle
                        key={index}
                        cx={(index / (data.length - 1)) * 100}
                        cy={100 - (value / maxValue) * 80}
                        r="2"
                        fill={color}
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: index * 0.1 + 1, duration: 0.3 }}
                    />
                ))}
            </svg>
        </div>
    );
};

// Bar Chart Component
const BarChart = ({ data, colors = ['#10b981', '#f59e0b', '#ef4444'] }) => {
    const maxValue = Math.max(...data.map(d => d.value));
    
    return (
        <div className="w-full h-32 flex items-end gap-2 px-2">
            {data.map((item, index) => (
                <div key={index} className="flex-1 flex flex-col items-center">
                    <motion.div
                        className="w-full rounded-t-lg relative overflow-hidden"
                        style={{ 
                            backgroundColor: colors[index % colors.length],
                            filter: `drop-shadow(0 0 8px ${colors[index % colors.length]}40)`
                        }}
                        initial={{ height: 0 }}
                        animate={{ height: `${(item.value / maxValue) * 100}%` }}
                        transition={{ delay: index * 0.2, duration: 1, ease: "easeOut" }}
                    >
                        <motion.div
                            className="absolute inset-0 bg-gradient-to-t from-white/20 to-transparent"
                            animate={{ y: [-20, 0] }}
                            transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
                        />
                    </motion.div>
                    <div className="text-xs text-white/60 mt-2 text-center">
                        {item.label}
                    </div>
                    <div className="text-sm font-bold text-white">
                        {item.value}%
                    </div>
                </div>
            ))}
        </div>
    );
};

// Donut Chart Component
const DonutChart = ({ data, size = 120 }) => {
    const total = data.reduce((sum, item) => sum + item.value, 0);
    let cumulativePercentage = 0;
    
    const radius = 40;
    const strokeWidth = 12;
    const circumference = 2 * Math.PI * radius;
    
    return (
        <div className="relative" style={{ width: size, height: size }}>
            <svg width={size} height={size} className="transform -rotate-90">
                {data.map((item, index) => {
                    const percentage = (item.value / total) * 100;
                    const strokeDasharray = `${(percentage / 100) * circumference} ${circumference}`;
                    const strokeDashoffset = -((cumulativePercentage / 100) * circumference);
                    
                    cumulativePercentage += percentage;
                    
                    return (
                        <motion.circle
                            key={index}
                            cx={size / 2}
                            cy={size / 2}
                            r={radius}
                            fill="transparent"
                            stroke={item.color}
                            strokeWidth={strokeWidth}
                            strokeDasharray={strokeDasharray}
                            strokeDashoffset={strokeDashoffset}
                            initial={{ strokeDasharray: `0 ${circumference}` }}
                            animate={{ strokeDasharray }}
                            transition={{ delay: index * 0.3, duration: 1.5, ease: "easeInOut" }}
                            strokeLinecap="round"
                            style={{
                                filter: `drop-shadow(0 0 6px ${item.color}40)`
                            }}
                        />
                    );
                })}
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-lg font-bold text-white">{total}</div>
                    <div className="text-xs text-white/60">Total</div>
                </div>
            </div>
        </div>
    );
};

// Area Chart Component
const AreaChart = ({ data, color = '#10b981' }) => {
    const maxValue = Math.max(...data);
    const points = data.map((value, index) => {
        const x = (index / (data.length - 1)) * 100;
        const y = 100 - (value / maxValue) * 70;
        return `${x},${y}`;
    }).join(' ');
    
    const areaPoints = `0,100 ${points} 100,100`;
    
    return (
        <div className="w-full h-24 relative">
            <svg width="100%" height="100%" viewBox="0 0 100 100" className="absolute inset-0">
                <defs>
                    <linearGradient id={`gradient-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor={color} stopOpacity="0.6" />
                        <stop offset="100%" stopColor={color} stopOpacity="0.1" />
                    </linearGradient>
                </defs>
                <motion.polygon
                    fill={`url(#gradient-${color})`}
                    points={areaPoints}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 1.5, delay: 0.5 }}
                />
                <motion.polyline
                    fill="none"
                    stroke={color}
                    strokeWidth="2"
                    points={points}
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 2, ease: "easeInOut" }}
                    style={{
                        filter: `drop-shadow(0 0 4px ${color}60)`
                    }}
                />
                {data.map((value, index) => (
                    <motion.circle
                        key={index}
                        cx={(index / (data.length - 1)) * 100}
                        cy={100 - (value / maxValue) * 70}
                        r="2"
                        fill={color}
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: index * 0.1 + 1.5, duration: 0.3 }}
                        style={{
                            filter: `drop-shadow(0 0 4px ${color}80)`
                        }}
                    />
                ))}
            </svg>
        </div>
    );
};

// Floating Particles Background
const FloatingParticles = () => {
    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {[...Array(20)].map((_, i) => (
                <motion.div
                    key={i}
                    className="absolute w-1 h-1 bg-white/20 rounded-full"
                    initial={{
                        x: Math.random() * 1200,
                        y: Math.random() * 800,
                    }}
                    animate={{
                        x: Math.random() * 1200,
                        y: Math.random() * 800,
                    }}
                    transition={{
                        duration: Math.random() * 20 + 10,
                        repeat: Infinity,
                        repeatType: "reverse",
                        ease: "linear"
                    }}
                />
            ))}
        </div>
    );
};

const ITRDashboard = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [currentTime, setCurrentTime] = useState(new Date());
    
    // Handle demo data
    const isDemoMode = window.location.pathname === '/dashboard-demo';
    
    const demoResult = {
        score: 79.76,
        is_match: true,
        match_label: 'medium_match'
    };
    
    const demoExtractedData = {
        name: 'Rajesh Kumar Singh',
        pan: 'ABCDE1234F',
        aadhaar: '123456789012',
        email: 'rajesh.kumar@email.com',
        mobile: '9876543210',
        date_of_birth: '15/08/1985',
        gross_salary: '850000',
        tds_deducted: '85000'
    };
    
    // Use demo data if in demo mode, otherwise use location state
    const result = isDemoMode ? demoResult : location.state?.result;
    const extractedData = isDemoMode ? demoExtractedData : (location.state?.extractedData || {});

    useEffect(() => {
        console.log('🔍 ITRDashboard - Location State:', location.state);
        console.log('🔍 ITRDashboard - Demo Mode:', isDemoMode);
        
        if (!result && !isDemoMode) {
            navigate('/validation');
        }

        // Update time every minute
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 60000);

        return () => clearInterval(timer);
    }, [result, navigate, isDemoMode]);

    // Helper function to calculate individual field validation scores
    const getFieldValidationScore = (fieldName, fieldValue, validationResult) => {
        if (!fieldValue || !validationResult) return 0;
        
        // Base score from overall validation
        const baseScore = validationResult.score || 0;
        
        // Field-specific scoring logic
        const fieldScores = {
            name: () => {
                const hasProperFormat = /^[a-zA-Z\s]{2,50}$/.test(fieldValue);
                const hasMultipleWords = fieldValue.trim().split(' ').length >= 2;
                return hasProperFormat && hasMultipleWords ? Math.min(baseScore + 10, 100) : Math.max(baseScore - 15, 0);
            },
            pan: () => {
                const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
                return panRegex.test(fieldValue) ? Math.min(baseScore + 15, 100) : Math.max(baseScore - 25, 0);
            },
            aadhaar: () => {
                const aadhaarRegex = /^\d{12}$/;
                return aadhaarRegex.test(fieldValue.replace(/\s/g, '')) ? Math.min(baseScore + 10, 100) : Math.max(baseScore - 20, 0);
            },
            email: () => {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return emailRegex.test(fieldValue) ? Math.min(baseScore + 5, 100) : Math.max(baseScore - 10, 0);
            },
            mobile: () => {
                const mobileRegex = /^[6-9]\d{9}$/;
                return mobileRegex.test(fieldValue.replace(/\D/g, '')) ? Math.min(baseScore + 5, 100) : Math.max(baseScore - 10, 0);
            },
            date_of_birth: () => {
                const dateRegex = /^\d{1,2}[-\/]\d{1,2}[-\/]\d{4}$/;
                return dateRegex.test(fieldValue) ? Math.min(baseScore + 5, 100) : Math.max(baseScore - 10, 0);
            },
            gross_salary: () => {
                const salaryNum = parseFloat(fieldValue.replace(/[^\d.]/g, ''));
                return !isNaN(salaryNum) && salaryNum > 0 ? Math.min(baseScore + 5, 100) : Math.max(baseScore - 15, 0);
            },
            tds_deducted: () => {
                const tdsNum = parseFloat(fieldValue.replace(/[^\d.]/g, ''));
                return !isNaN(tdsNum) && tdsNum >= 0 ? Math.min(baseScore + 5, 100) : Math.max(baseScore - 10, 0);
            }
        };
        
        if (fieldScores[fieldName]) {
            return Math.round(fieldScores[fieldName]());
        } else {
            const lengthScore = fieldValue.length > 2 ? 5 : -5;
            const formatScore = /^[a-zA-Z0-9\s\-\.@]+$/.test(fieldValue) ? 5 : -10;
            return Math.round(Math.max(Math.min(baseScore + lengthScore + formatScore, 100), 0));
        }
    };

    if (!result && !isDemoMode) return null;

    const { score, is_match, match_label } = result;

    // Calculate statistics
    const validFields = Object.entries(extractedData).filter(([_, value]) => value);
    const verifiedFields = validFields.filter(([field, value]) => 
        getFieldValidationScore(field, value, result) >= 85
    );
    const averageScore = validFields.length > 0 ? Math.round(
        validFields.reduce((sum, [field, value]) => 
            sum + getFieldValidationScore(field, value, result), 0
        ) / validFields.length
    ) : 0;

    const getMatchColor = (score) => {
        if (score >= 90) return 'text-green-400';
        if (score >= 75) return 'text-yellow-400';
        return 'text-red-400';
    };

    const getMatchLabel = (score, isMatch) => {
        if (score >= 90) return 'HIGH MATCH';
        if (score >= 75) return 'MEDIUM MATCH';
        return 'LOW MATCH';
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-emerald-950 via-emerald-900 to-emerald-800 text-white flex relative overflow-hidden">
            {/* Floating Particles Background */}
            <FloatingParticles />
            
            {/* Enhanced Background Effects */}
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-950/50 via-emerald-900/30 to-emerald-800/50" />
            <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-gradient-radial from-yellow-400/10 to-transparent rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-gradient-radial from-emerald-400/10 to-transparent rounded-full blur-3xl" />
            
            {/* Sidebar */}
            <aside className="w-64 bg-emerald-950/70 backdrop-blur-xl border-r border-white/10 p-6 relative z-10">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <h2 className="text-xl font-semibold mb-8 flex items-center gap-3">
                        <motion.div
                            animate={{ rotate: [0, 360] }}
                            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                        >
                            <Shield className="w-6 h-6 text-emerald-400" />
                        </motion.div>
                        ITR Portal
                        <motion.div
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 2, repeat: Infinity }}
                        >
                            <Sparkles className="w-4 h-4 text-yellow-400" />
                        </motion.div>
                    </h2>
                    <nav className="space-y-4">
                        {[
                            { name: 'Overview', icon: BarChart3, active: true },
                            { name: 'Validation', icon: CheckCircle, onClick: () => navigate('/validation') },
                            { name: 'Upload', icon: Upload, onClick: () => navigate('/upload') },
                            { name: 'Wallet', icon: Wallet, onClick: () => navigate('/wallet') },
                            { name: 'Settings', icon: Settings }
                        ].map((item, index) => (
                            <motion.div 
                                key={item.name}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                whileHover={{ scale: 1.05, x: 5 }}
                                className={`px-4 py-3 rounded-lg cursor-pointer transition-all flex items-center gap-3 relative overflow-hidden ${
                                    item.active 
                                        ? 'bg-emerald-600/30 border border-emerald-400/30 text-emerald-300' 
                                        : 'bg-white/5 hover:bg-white/10 text-white/70 hover:text-white'
                                }`}
                                onClick={item.onClick}
                            >
                                {item.active && (
                                    <motion.div
                                        className="absolute inset-0 bg-gradient-to-r from-emerald-400/20 to-transparent"
                                        animate={{ x: [-100, 300] }}
                                        transition={{ duration: 3, repeat: Infinity, repeatDelay: 2 }}
                                    />
                                )}
                                <item.icon className="w-5 h-5 relative z-10" />
                                <span className="relative z-10">{item.name}</span>
                            </motion.div>
                        ))}
                    </nav>
                </motion.div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-8 space-y-8 overflow-y-auto">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="flex justify-between items-center"
                >
                    <div>
                        <h1 className="text-3xl font-bold text-white mb-2">Validation Dashboard</h1>
                        <p className="text-white/70">AI-powered document verification results</p>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="text-right text-sm text-white/60">
                            <div>Last Updated</div>
                            <div>{currentTime.toLocaleTimeString()}</div>
                        </div>
                        <button 
                            onClick={() => navigate('/')}
                            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                        >
                            <Home className="w-5 h-5" />
                        </button>
                    </div>
                </motion.div>

                {/* Top Cards */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Score Card */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="bg-white/10 backdrop-blur-xl rounded-2xl p-8 shadow-xl border border-white/10 relative overflow-hidden"
                    >
                        {/* Sparkles around the card */}
                        <div className="absolute inset-0 pointer-events-none">
                            {[...Array(12)].map((_, i) => (
                                <Sparkle key={i} delay={i * 0.2} />
                            ))}
                        </div>
                        
                        <div className="flex flex-col items-center relative z-10">
                            <motion.div
                                initial={{ scale: 0.8, rotate: -10 }}
                                animate={{ scale: 1, rotate: 0 }}
                                transition={{ type: 'spring', stiffness: 100, delay: 0.4 }}
                                className="relative mb-6"
                            >
                                <ProgressRing 
                                    progress={score} 
                                    size={180} 
                                    strokeWidth={12}
                                    color={score >= 90 ? '#10b981' : score >= 75 ? '#f59e0b' : '#ef4444'}
                                />
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="text-center">
                                        <motion.span 
                                            className="text-4xl font-bold"
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            transition={{ delay: 1.5 }}
                                        >
                                            {score}%
                                        </motion.span>
                                        <div className="text-xs text-white/60 mt-1">CONFIDENCE</div>
                                    </div>
                                </div>
                            </motion.div>
                            
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.6 }}
                                className={`px-6 py-2 rounded-full font-semibold text-lg ${getMatchColor(score)} bg-white/10 border border-white/20 mb-4 relative`}
                            >
                                <motion.div
                                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
                                    animate={{ x: [-100, 200] }}
                                    transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
                                />
                                <span className="relative z-10">{getMatchLabel(score, is_match)}</span>
                            </motion.div>
                            
                            <p className="text-center text-sm text-white/70 mb-6 max-w-sm">
                                AI validated document semantics. {is_match ? 'Document verified successfully.' : 'Manual verification recommended.'}
                            </p>
                            
                            <motion.button
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.8 }}
                                whileHover={{ scale: 1.05, boxShadow: "0 10px 30px rgba(16,185,129,0.4)" }}
                                whileTap={{ scale: 0.95 }}
                                onClick={() => navigate('/wallet', {
                                    state: {
                                        score,
                                        verified: is_match,
                                        signedQR: location.state?.signedQR,
                                        extractedData: location.state?.extractedData,
                                        qrImageData: location.state?.qrImageData
                                    }
                                })}
                                disabled={!is_match}
                                className={`px-6 py-3 rounded-xl font-semibold transition-all flex items-center gap-2 relative overflow-hidden ${
                                    is_match 
                                        ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg' 
                                        : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                                }`}
                            >
                                {is_match && (
                                    <motion.div
                                        className="absolute inset-0 bg-gradient-to-r from-emerald-400/30 to-transparent"
                                        animate={{ x: [-100, 200] }}
                                        transition={{ duration: 2, repeat: Infinity, repeatDelay: 1 }}
                                    />
                                )}
                                <Wallet className="w-4 h-4 relative z-10" />
                                <span className="relative z-10">Proceed to Wallet</span>
                            </motion.button>
                        </div>
                    </motion.div>

                    {/* Field Validation Table */}
                    <motion.div
                        initial={{ opacity: 0, x: 40 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.6, delay: 0.3 }}
                        className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 shadow-xl border border-white/10 relative overflow-hidden"
                    >
                        {/* Background sparkles */}
                        <div className="absolute inset-0 pointer-events-none">
                            {[...Array(8)].map((_, i) => (
                                <Sparkle key={i} delay={i * 0.4} duration={3} />
                            ))}
                        </div>
                        
                        <div className="flex items-center justify-between mb-4 relative z-10">
                            <h3 className="text-lg font-semibold flex items-center gap-2">
                                <motion.div
                                    animate={{ rotate: [0, 360] }}
                                    transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                                >
                                    <Database className="w-5 h-5 text-emerald-400" />
                                </motion.div>
                                Field Validation Report
                            </h3>
                            <div className="flex items-center gap-2">
                                <span className="text-sm text-white/60">{validFields.length} fields</span>
                                <motion.div
                                    animate={{ scale: [1, 1.2, 1] }}
                                    transition={{ duration: 2, repeat: Infinity }}
                                >
                                    <Zap className="w-4 h-4 text-yellow-400" />
                                </motion.div>
                            </div>
                        </div>
                        
                        {/* Mini trend chart */}
                        <div className="mb-4 relative z-10">
                            <div className="text-xs text-white/60 mb-2">Validation Trend</div>
                            <MiniChart 
                                data={validFields.slice(0, 8).map(([field, value]) => 
                                    getFieldValidationScore(field, value, result)
                                )} 
                                color="#10b981"
                            />
                        </div>
                        
                        <div className="space-y-1 max-h-80 overflow-y-auto relative z-10">
                            <div className="grid grid-cols-4 gap-4 text-xs font-semibold text-white/60 pb-2 border-b border-white/10">
                                <div>Field</div>
                                <div className="text-center">Score</div>
                                <div className="text-center">Status</div>
                                <div></div>
                            </div>
                            
                            {validFields.slice(0, 8).map(([field, value], index) => {
                                const fieldScore = getFieldValidationScore(field, value, result);
                                const isVerified = fieldScore >= 85;
                                const isWarning = fieldScore >= 70 && fieldScore < 85;
                                
                                return (
                                    <motion.div
                                        key={field}
                                        initial={{ opacity: 0, x: 20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.1 * index }}
                                        whileHover={{ scale: 1.02, backgroundColor: "rgba(255,255,255,0.1)" }}
                                        className="grid grid-cols-4 gap-4 py-3 border-b border-white/5 hover:bg-white/5 rounded-lg px-2 transition-colors relative overflow-hidden"
                                    >
                                        <motion.div
                                            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"
                                            animate={{ x: [-100, 300] }}
                                            transition={{ duration: 4, repeat: Infinity, repeatDelay: index * 0.5 }}
                                        />
                                        <div className="text-sm capitalize text-white/90 relative z-10">
                                            {field.replace(/_/g, ' ')}
                                        </div>
                                        <div className="text-center relative z-10">
                                            <motion.span 
                                                className={`font-bold ${
                                                    isVerified ? 'text-green-400' : 
                                                    isWarning ? 'text-yellow-400' : 'text-red-400'
                                                }`}
                                                initial={{ scale: 0 }}
                                                animate={{ scale: 1 }}
                                                transition={{ delay: 0.5 + index * 0.1, type: "spring" }}
                                            >
                                                {fieldScore}%
                                            </motion.span>
                                        </div>
                                        <div className="text-center relative z-10">
                                            <motion.div
                                                initial={{ scale: 0, rotate: -180 }}
                                                animate={{ scale: 1, rotate: 0 }}
                                                transition={{ delay: 0.7 + index * 0.1, type: "spring" }}
                                            >
                                                {isVerified ? (
                                                    <CheckCircle className="w-4 h-4 text-green-400 mx-auto" />
                                                ) : isWarning ? (
                                                    <AlertCircle className="w-4 h-4 text-yellow-400 mx-auto" />
                                                ) : (
                                                    <XCircle className="w-4 h-4 text-red-400 mx-auto" />
                                                )}
                                            </motion.div>
                                        </div>
                                        <div className="text-xs text-white/60 truncate relative z-10">
                                            {isVerified ? 'Verified' : isWarning ? 'Warning' : 'Failed'}
                                        </div>
                                    </motion.div>
                                );
                            })}
                        </div>
                    </motion.div>
                </div>

                {/* Analytics Dashboard Section */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                    className="grid grid-cols-1 lg:grid-cols-3 gap-6"
                >
                    {/* Bar Chart - Field Scores */}
                    <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/10 relative overflow-hidden">
                        <div className="absolute inset-0 pointer-events-none">
                            {[...Array(6)].map((_, i) => (
                                <Sparkle key={i} delay={i * 0.3} duration={2.5} />
                            ))}
                        </div>
                        
                        <div className="relative z-10">
                            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <BarChart3 className="w-5 h-5 text-blue-400" />
                                Field Scores
                            </h3>
                            <BarChart 
                                data={validFields.slice(0, 4).map(([field, value]) => ({
                                    label: field.replace(/_/g, ' ').substring(0, 6),
                                    value: getFieldValidationScore(field, value, result)
                                }))}
                                colors={['#10b981', '#f59e0b', '#ef4444', '#8b5cf6']}
                            />
                        </div>
                    </div>

                    {/* Donut Chart - Validation Status */}
                    <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/10 relative overflow-hidden">
                        <div className="absolute inset-0 pointer-events-none">
                            {[...Array(6)].map((_, i) => (
                                <Sparkle key={i} delay={i * 0.3 + 0.5} duration={2.5} />
                            ))}
                        </div>
                        
                        <div className="relative z-10">
                            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <Activity className="w-5 h-5 text-purple-400" />
                                Status Distribution
                            </h3>
                            <div className="flex items-center justify-center">
                                <DonutChart 
                                    data={[
                                        { value: verifiedFields.length, color: '#10b981', label: 'Verified' },
                                        { value: validFields.filter(([field, value]) => {
                                            const score = getFieldValidationScore(field, value, result);
                                            return score >= 70 && score < 85;
                                        }).length, color: '#f59e0b', label: 'Warning' },
                                        { value: validFields.filter(([field, value]) => {
                                            const score = getFieldValidationScore(field, value, result);
                                            return score < 70;
                                        }).length, color: '#ef4444', label: 'Failed' }
                                    ]}
                                    size={140}
                                />
                            </div>
                            <div className="flex justify-center gap-4 mt-4">
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                                    <span className="text-xs text-white/70">Verified</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                                    <span className="text-xs text-white/70">Warning</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                                    <span className="text-xs text-white/70">Failed</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Area Chart - Confidence Trend */}
                    <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/10 relative overflow-hidden">
                        <div className="absolute inset-0 pointer-events-none">
                            {[...Array(6)].map((_, i) => (
                                <Sparkle key={i} delay={i * 0.3 + 1} duration={2.5} />
                            ))}
                        </div>
                        
                        <div className="relative z-10">
                            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <TrendingUp className="w-5 h-5 text-emerald-400" />
                                Confidence Trend
                            </h3>
                            <AreaChart 
                                data={[
                                    score * 0.7, score * 0.8, score * 0.9, score, 
                                    score * 1.1 > 100 ? 100 : score * 1.1,
                                    score * 1.05 > 100 ? 100 : score * 1.05,
                                    score
                                ]}
                                color="#10b981"
                            />
                            <div className="flex justify-between text-xs text-white/60 mt-2">
                                <span>Start</span>
                                <span>Current: {score}%</span>
                                <span>End</span>
                            </div>
                        </div>
                    </div>
                </motion.div>

                {/* Bottom Statistics */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.5 }}
                    className="grid grid-cols-1 lg:grid-cols-3 gap-6"
                >
                    <motion.div 
                        whileHover={{ scale: 1.05, y: -5 }}
                        className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/10 relative overflow-hidden"
                    >
                        {/* Sparkle effects */}
                        <div className="absolute inset-0 pointer-events-none">
                            {[...Array(4)].map((_, i) => (
                                <Sparkle key={i} delay={i * 0.5} duration={2} />
                            ))}
                        </div>
                        
                        <div className="flex items-center gap-4 relative z-10">
                            <motion.div 
                                className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center relative"
                                animate={{ rotate: [0, 360] }}
                                transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                            >
                                <FileText className="w-6 h-6 text-blue-400" />
                                <motion.div
                                    className="absolute inset-0 bg-blue-400/20 rounded-xl"
                                    animate={{ scale: [1, 1.2, 1] }}
                                    transition={{ duration: 2, repeat: Infinity }}
                                />
                            </motion.div>
                            <div>
                                <div className="text-sm text-white/60">Total Fields</div>
                                <motion.div 
                                    className="text-3xl font-bold"
                                    initial={{ opacity: 0, scale: 0 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: 1, type: "spring" }}
                                >
                                    {validFields.length}
                                </motion.div>
                                {/* Mini progress bar */}
                                <div className="w-full bg-white/10 rounded-full h-1 mt-2">
                                    <motion.div 
                                        className="bg-blue-400 h-1 rounded-full"
                                        initial={{ width: 0 }}
                                        animate={{ width: `${(validFields.length / 20) * 100}%` }}
                                        transition={{ delay: 1.5, duration: 1 }}
                                    />
                                </div>
                            </div>
                        </div>
                    </motion.div>
                    
                    <motion.div 
                        whileHover={{ scale: 1.05, y: -5 }}
                        className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/10 relative overflow-hidden"
                    >
                        {/* Sparkle effects */}
                        <div className="absolute inset-0 pointer-events-none">
                            {[...Array(4)].map((_, i) => (
                                <Sparkle key={i} delay={i * 0.5 + 0.5} duration={2} />
                            ))}
                        </div>
                        
                        <div className="flex items-center gap-4 relative z-10">
                            <motion.div 
                                className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center relative"
                                animate={{ scale: [1, 1.1, 1] }}
                                transition={{ duration: 2, repeat: Infinity }}
                            >
                                <CheckCircle className="w-6 h-6 text-green-400" />
                                <motion.div
                                    className="absolute inset-0 bg-green-400/20 rounded-xl"
                                    animate={{ rotate: [0, 360] }}
                                    transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                                />
                            </motion.div>
                            <div>
                                <div className="text-sm text-white/60">Verified Fields</div>
                                <motion.div 
                                    className="text-3xl font-bold text-green-400"
                                    initial={{ opacity: 0, scale: 0 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: 1.2, type: "spring" }}
                                >
                                    {verifiedFields.length}
                                </motion.div>
                                {/* Mini progress bar */}
                                <div className="w-full bg-white/10 rounded-full h-1 mt-2">
                                    <motion.div 
                                        className="bg-green-400 h-1 rounded-full"
                                        initial={{ width: 0 }}
                                        animate={{ width: `${(verifiedFields.length / validFields.length) * 100}%` }}
                                        transition={{ delay: 1.7, duration: 1 }}
                                    />
                                </div>
                            </div>
                        </div>
                    </motion.div>
                    
                    <motion.div 
                        whileHover={{ scale: 1.05, y: -5 }}
                        className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/10 relative overflow-hidden"
                    >
                        {/* Sparkle effects */}
                        <div className="absolute inset-0 pointer-events-none">
                            {[...Array(4)].map((_, i) => (
                                <Sparkle key={i} delay={i * 0.5 + 1} duration={2} />
                            ))}
                        </div>
                        
                        <div className="flex items-center gap-4 relative z-10">
                            <motion.div 
                                className="w-12 h-12 bg-yellow-500/20 rounded-xl flex items-center justify-center relative"
                                animate={{ y: [0, -5, 0] }}
                                transition={{ duration: 2, repeat: Infinity }}
                            >
                                <TrendingUp className="w-6 h-6 text-yellow-400" />
                                <motion.div
                                    className="absolute inset-0 bg-yellow-400/20 rounded-xl"
                                    animate={{ scale: [1, 1.2, 1] }}
                                    transition={{ duration: 3, repeat: Infinity }}
                                />
                            </motion.div>
                            <div>
                                <div className="text-sm text-white/60">Average Score</div>
                                <motion.div 
                                    className="text-3xl font-bold text-yellow-400"
                                    initial={{ opacity: 0, scale: 0 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: 1.4, type: "spring" }}
                                >
                                    {averageScore}%
                                </motion.div>
                                {/* Mini progress bar */}
                                <div className="w-full bg-white/10 rounded-full h-1 mt-2">
                                    <motion.div 
                                        className="bg-yellow-400 h-1 rounded-full"
                                        initial={{ width: 0 }}
                                        animate={{ width: `${averageScore}%` }}
                                        transition={{ delay: 1.9, duration: 1 }}
                                    />
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </motion.div>

                {/* Action Buttons */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.7 }}
                    className="flex flex-wrap gap-4 justify-center pt-8"
                >
                    <button
                        onClick={() => navigate('/validation-result', { state: location.state })}
                        className="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-xl font-semibold transition-all flex items-center gap-2 border border-white/20"
                    >
                        <Eye className="w-4 h-4" />
                        Detailed View
                    </button>
                    
                    <button
                        onClick={() => navigate('/upload')}
                        className="px-6 py-3 bg-emerald-600/20 hover:bg-emerald-600/30 rounded-xl font-semibold transition-all flex items-center gap-2 border border-emerald-400/30"
                    >
                        <RefreshCw className="w-4 h-4" />
                        New Validation
                    </button>
                </motion.div>
            </main>
        </div>
    );
};

export default ITRDashboard;