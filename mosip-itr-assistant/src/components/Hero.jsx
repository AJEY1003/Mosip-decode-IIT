import { motion } from 'framer-motion'
import { Menu, X, Shield, FileCheck, Clock, ChevronRight, BadgeCheck, Landmark, Upload, Database, ShieldCheck, Wallet } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export function Hero() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isMobileMenuOpen])

  const navLinks = [
    { href: '#how-it-works', label: 'How It Works' },
    { href: '#services', label: 'Services' },
    { href: '#about', label: 'About' },
    { href: '#contact', label: 'Contact' },
  ]

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

      {/* Navigation */}
      <motion.nav
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="fixed top-0 left-0 right-0 w-full z-50"
      >
        <div 
          className={`w-full px-6 sm:px-8 lg:px-16 py-4 transition-all duration-500 ${
            isScrolled 
              ? 'bg-white/95 backdrop-blur-xl shadow-[0_4px_30px_rgba(0,0,0,0.1)] border-b border-[hsl(var(--border))]' 
              : 'bg-transparent'
          }`}
        >
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            {/* Logo */}
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="flex items-center gap-3 cursor-pointer"
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            >
              <div className={`p-2.5 rounded-xl transition-all duration-300 ${isScrolled ? 'bg-[hsl(var(--gov-green))]' : 'bg-white/15 backdrop-blur-sm border border-white/20'}`}>
                <Landmark className={`w-6 h-6 ${isScrolled ? 'text-white' : 'text-[hsl(var(--gov-gold))]'}`} />
              </div>
              <div>
                <span className={`font-bold text-xl tracking-tight ${isScrolled ? 'text-[hsl(var(--foreground))]' : 'text-white'}`}>
                  MOSIP ITR
                </span>
                <span className={`block text-xs font-medium tracking-wide ${isScrolled ? 'text-[hsl(var(--muted-foreground))]' : 'text-white/70'}`}>
                  Assistant Portal
                </span>
              </div>
            </motion.div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => (
                <a 
                  key={link.href}
                  href={link.href} 
                  className={`px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 ${
                    isScrolled 
                      ? 'text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))] hover:text-[hsl(var(--primary))]' 
                      : 'text-white/90 hover:text-white hover:bg-white/10'
                  }`}
                >
                  {link.label}
                </a>
              ))}
            </div>

            {/* CTA + Mobile Menu Button */}
            <div className="flex items-center gap-3">
              <motion.button
                whileHover={{ scale: 1.03, y: -1 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => navigate('/upload')}
                className={`hidden sm:flex items-center gap-2 font-semibold px-5 py-2.5 rounded-xl transition-all duration-300 shadow-lg ${
                  isScrolled
                    ? 'bg-[hsl(var(--gov-green))] text-white hover:bg-[hsl(var(--gov-green-dark))] shadow-[hsl(var(--gov-green))]/25'
                    : 'bg-[hsl(var(--gov-gold))] text-[hsl(var(--gov-navy))] hover:bg-[hsl(var(--gov-gold-dark))] shadow-[hsl(var(--gov-gold))]/30'
                }`}
              >
                <Upload className="w-4 h-4" />
                Start Upload
              </motion.button>

              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className={`md:hidden p-2.5 rounded-xl transition-colors ${
                  isScrolled 
                    ? 'text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]' 
                    : 'text-white hover:bg-white/15'
                }`}
              >
                {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="md:hidden fixed inset-0 bg-[hsl(var(--gov-navy))]/80 backdrop-blur-sm z-40"
            onClick={() => setIsMobileMenuOpen(false)}
          />
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            transition={{ type: 'spring', damping: 25 }}
            className="md:hidden fixed top-0 right-0 h-full w-80 bg-white z-50 p-8 shadow-2xl"
          >
            <div className="flex justify-between items-center mb-10">
              <span className="font-bold text-lg text-[hsl(var(--foreground))]">Menu</span>
              <button onClick={() => setIsMobileMenuOpen(false)} className="p-2 hover:bg-[hsl(var(--muted))] rounded-lg">
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="flex flex-col gap-2">
              {navLinks.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="text-[hsl(var(--foreground))] font-medium py-3 px-4 rounded-xl hover:bg-[hsl(var(--muted))] transition-colors flex items-center justify-between"
                >
                  {link.label}
                  <ChevronRight className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                </a>
              ))}
              <button
                onClick={() => {
                  navigate('/upload')
                  setIsMobileMenuOpen(false)
                }}
                className="bg-[hsl(var(--gov-green))] text-white font-semibold py-3.5 px-4 rounded-xl mt-6 flex items-center justify-center gap-2"
              >
                <Upload className="w-5 h-5" />
                Start Upload
              </button>
            </div>
          </motion.div>
        </>
      )}

      {/* Hero Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 sm:px-8 lg:px-16 pt-32 lg:pt-40 pb-24">
        <div className="grid lg:grid-cols-2 gap-16 lg:gap-20 items-center min-h-[calc(100vh-10rem)]">
          {/* Left Content */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="inline-flex items-center gap-2.5 bg-white/10 backdrop-blur-md border border-white/20 text-white px-5 py-2.5 rounded-full text-sm font-semibold mb-8 shadow-lg"
            >
              <div className="w-2 h-2 rounded-full bg-[hsl(var(--gov-gold))] animate-pulse" />
              Official MOSIP ITR Portal
            </motion.div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-extrabold text-white leading-[1.1] mb-6 tracking-tight">
              Smart ITR
              <span className="block text-[hsl(var(--gov-gold))] mt-2 drop-shadow-[0_2px_10px_rgba(234,179,8,0.3)]">Processing</span>
              <span className="block mt-2">Assistant</span>
            </h1>
            
            <p className="text-lg lg:text-xl text-white/80 mb-10 max-w-xl leading-relaxed">
              Streamline your Income Tax Return filing with secure OCR, automated data extraction, 
              and MOSIP-compliant validation. Fast, secure, and trusted.
            </p>

            {/* Stats */}
            <div className="flex flex-wrap gap-8 mb-12">
              {[
                { icon: FileCheck, value: '1M+', label: 'Documents Processed' },
                { icon: Clock, value: '<2min', label: 'Processing Time' },
                { icon: Shield, value: '99.9%', label: 'Accuracy Rate' },
              ].map((stat, i) => (
                <motion.div 
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 + i * 0.1 }}
                  className="flex items-center gap-4"
                >
                  <div className="p-3 bg-white/10 backdrop-blur-sm rounded-xl border border-white/10">
                    <stat.icon className="w-5 h-5 text-[hsl(var(--gov-gold))]" />
                  </div>
                  <div>
                    <p className="text-2xl lg:text-3xl font-bold text-white">{stat.value}</p>
                    <p className="text-sm text-white/60 font-medium">{stat.label}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap gap-4">
              <motion.button
                whileHover={{ scale: 1.03, y: -2 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => navigate('/upload')}
                className="bg-[hsl(var(--gov-gold))] text-[hsl(var(--gov-navy))] font-bold px-8 py-4 rounded-xl text-lg shadow-[0_8px_30px_rgba(234,179,8,0.4)] hover:shadow-[0_12px_40px_rgba(234,179,8,0.5)] transition-all flex items-center gap-2"
              >
                <Upload className="w-5 h-5" />
                Start Processing
                <ChevronRight className="w-5 h-5" />
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.03, y: -2 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                className="bg-white/10 backdrop-blur-md text-white font-semibold px-8 py-4 rounded-xl text-lg border border-white/25 hover:bg-white/20 hover:border-white/40 transition-all"
              >
                Learn How It Works
              </motion.button>
            </div>
          </motion.div>

          {/* Right Content - Process Flow */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="relative"
          >
            <div className="relative bg-white rounded-2xl shadow-[0_25px_80px_-15px_rgba(0,0,0,0.4)] overflow-hidden ring-1 ring-white/20 p-8">
              {/* Process Steps */}
              <div className="space-y-6">
                <h3 className="text-2xl font-bold text-[hsl(var(--foreground))] mb-6">ITR Processing Flow</h3>
                
                {[
                  { icon: Upload, title: "Upload Documents", desc: "Securely upload your scanned ITR documents" },
                  { icon: Database, title: "OCR Extraction", desc: "AI extracts data automatically from documents" },
                  { icon: ShieldCheck, title: "MOSIP Validation", desc: "Validate against MOSIP standards" },
                  { icon: Wallet, title: "Digital Wallet", desc: "Store verifiable credentials securely" }
                ].map((step, index) => (
                  <motion.div
                    key={step.title}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                    className="flex items-center gap-4 p-4 rounded-xl bg-[hsl(var(--muted))] hover:bg-[hsl(var(--muted))]/80 transition-colors"
                  >
                    <div className="p-3 bg-[hsl(var(--gov-green))] rounded-xl">
                      <step.icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-[hsl(var(--foreground))]">{step.title}</h4>
                      <p className="text-sm text-[hsl(var(--muted-foreground))]">{step.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Floating Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 1 }}
              className="absolute -bottom-6 -left-6 bg-white rounded-2xl shadow-[0_15px_50px_-10px_rgba(0,0,0,0.25)] p-5 flex items-center gap-4 ring-1 ring-black/5"
            >
              <div className="p-3 bg-[hsl(var(--gov-green))]/10 rounded-xl">
                <Shield className="w-7 h-7 text-[hsl(var(--gov-green))]" />
              </div>
              <div>
                <p className="font-bold text-[hsl(var(--foreground))] text-lg">MOSIP Compliant</p>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Secure & Verified</p>
              </div>
            </motion.div>

            {/* Top right accent badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 1.2 }}
              className="absolute -top-4 -right-4 bg-[hsl(var(--gov-gold))] text-[hsl(var(--gov-navy))] rounded-full p-3 shadow-lg"
            >
              <BadgeCheck className="w-6 h-6" />
            </motion.div>
          </motion.div>
        </div>
      </div>

      {/* Wave divider with better contrast */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full" preserveAspectRatio="none">
          <path d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" fill="hsl(var(--background))"/>
        </svg>
      </div>
    </div>
  )
}