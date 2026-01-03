import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import { FileText, Scan, Database, ShieldCheck, FileCheck, Wallet, Upload, Eye, Download } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export function Services() {
  const [isVisible, setIsVisible] = useState(false)
  const [hoveredService, setHoveredService] = useState(null)
  const navigate = useNavigate()

  const services = [
    {
      id: 'document-upload',
      title: "Document Upload & OCR",
      description: "Secure upload and processing of ITR documents with advanced OCR technology supporting multiple formats.",
      icon: Upload,
      color: 'bg-blue-500',
      route: '/upload',
      features: ['Multi-format support', 'Secure encryption', '99.9% accuracy']
    },
    {
      id: 'data-extraction',
      title: "Smart Data Extraction", 
      description: "AI-powered extraction of key information from ITR documents using advanced NER technology.",
      icon: Database,
      color: 'bg-emerald-500',
      route: '/forms',
      features: ['AI-powered NER', 'Multi-language support', 'Real-time processing']
    },
    {
      id: 'mosip-validation',
      title: "MOSIP Validation",
      description: "Comprehensive validation against MOSIP standards and government databases for compliance.",
      icon: ShieldCheck,
      color: 'bg-purple-500',
      route: '/validation',
      features: ['MOSIP compliant', 'Government verified', 'Instant validation']
    },
    {
      id: 'form-generation',
      title: "Automated Form Filling",
      description: "Generate pre-filled ITR forms ready for submission with extracted and validated data.",
      icon: FileCheck,
      color: 'bg-orange-500',
      route: '/forms',
      features: ['Auto-fill forms', 'Error checking', 'Multiple formats']
    },
    {
      id: 'document-verification',
      title: "Document Verification",
      description: "Verify authenticity and integrity of processed documents with blockchain-based verification.",
      icon: Eye,
      color: 'bg-indigo-500',
      route: '/validation',
      features: ['Blockchain verified', 'Tamper-proof', 'Instant verification']
    },
    {
      id: 'digital-wallet',
      title: "Secure Digital Wallet",
      description: "Store and manage your verified ITR documents and credentials in a secure digital wallet.",
      icon: Wallet,
      color: 'bg-teal-500',
      route: '/wallet',
      features: ['Secure storage', 'Easy access', 'Compliance ready']
    }
  ]

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 300)
    return () => clearTimeout(timer)
  }, [])

  return (
    <section id="services" className="relative py-20 bg-gradient-to-br from-[hsl(var(--muted))] to-background">
      
      {/* Background Elements */}
      <div className="absolute inset-0">
        {/* Subtle pattern */}
        <div className="absolute inset-0 opacity-[0.02]" style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, rgba(0,0,0,0.15) 1px, transparent 0)`,
          backgroundSize: '20px 20px'
        }} />
        
        {/* Gradient orbs */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-[hsl(var(--gov-green))]/10 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-[hsl(var(--gov-gold))]/10 rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-6 sm:px-8 lg:px-12 relative z-10">
        
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-3 mb-6">
            <div className="w-3 h-3 bg-[hsl(var(--gov-green))] rounded-full animate-pulse" />
            <span className="text-sm font-semibold text-[hsl(var(--muted-foreground))]">
              Complete ITR Solution
            </span>
            <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
          </div>
          
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-[hsl(var(--foreground))]">
            Our Services
          </h2>
          
          <p className="text-xl text-[hsl(var(--muted-foreground))] leading-relaxed max-w-3xl mx-auto">
            Comprehensive ITR processing services powered by AI and secured by MOSIP standards
          </p>
        </motion.div>

        {/* Services Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((service, index) => (
            <motion.div
              key={service.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -8, scale: 1.02 }}
              className="group cursor-pointer"
              onMouseEnter={() => setHoveredService(service.id)}
              onMouseLeave={() => setHoveredService(null)}
              onClick={() => navigate(service.route)}
            >
              {/* Service Card */}
              <div className="relative bg-white rounded-2xl p-8 shadow-[0_4px_20px_rgba(0,0,0,0.08)] border border-[hsl(var(--border))] hover:shadow-[0_12px_40px_rgba(0,0,0,0.15)] transition-all duration-500 h-full overflow-hidden">
                
                {/* Background Gradient */}
                <div className={`absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity duration-500 ${service.color.replace('bg-', 'bg-gradient-to-br from-')}-500 to-transparent`} />
                
                {/* Icon */}
                <div className={`w-16 h-16 ${service.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 shadow-lg`}>
                  <service.icon className="w-8 h-8 text-white" />
                </div>
                
                {/* Content */}
                <h3 className="text-xl font-bold text-[hsl(var(--foreground))] mb-4 group-hover:text-[hsl(var(--gov-green))] transition-colors duration-300">
                  {service.title}
                </h3>
                
                <p className="text-[hsl(var(--muted-foreground))] leading-relaxed mb-6">
                  {service.description}
                </p>
                
                {/* Features */}
                <div className="space-y-2 mb-6">
                  {service.features.map((feature, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-sm">
                      <div className="w-1.5 h-1.5 bg-[hsl(var(--gov-green))] rounded-full" />
                      <span className="text-[hsl(var(--muted-foreground))]">{feature}</span>
                    </div>
                  ))}
                </div>
                
                {/* CTA */}
                <div className="flex items-center justify-between">
                  <span className="text-[hsl(var(--gov-green))] font-semibold group-hover:translate-x-2 transition-transform duration-300">
                    Try Now →
                  </span>
                  
                  {hoveredService === service.id && (
                    <motion.div
                      initial={{ scale: 0, rotate: -180 }}
                      animate={{ scale: 1, rotate: 0 }}
                      className="w-8 h-8 bg-[hsl(var(--gov-gold))] rounded-full flex items-center justify-center"
                    >
                      <service.icon className="w-4 h-4 text-white" />
                    </motion.div>
                  )}
                </div>
                
                {/* Decorative elements */}
                <div className="absolute top-4 right-4 w-20 h-20 bg-gradient-to-br from-[hsl(var(--gov-gold))]/10 to-transparent rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="absolute -bottom-4 -right-4 w-16 h-16 bg-gradient-to-tl from-[hsl(var(--gov-green))]/10 to-transparent rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-16"
        >
          <div className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))] max-w-4xl mx-auto">
            <h3 className="text-2xl font-bold text-[hsl(var(--foreground))] mb-4">
              Need Help Choosing the Right Service?
            </h3>
            <p className="text-[hsl(var(--muted-foreground))] mb-6">
              Our ITR processing experts are here to guide you through the best solution for your needs.
            </p>
            
            <div className="flex flex-wrap gap-4 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/upload')}
                className="bg-[hsl(var(--gov-green))] text-white font-semibold px-6 py-3 rounded-xl flex items-center gap-2 shadow-lg hover:shadow-xl transition-all"
              >
                <Upload className="w-5 h-5" />
                Get Started
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' })}
                className="bg-white text-[hsl(var(--gov-green))] font-semibold px-6 py-3 rounded-xl border-2 border-[hsl(var(--gov-green))] hover:bg-[hsl(var(--gov-green))] hover:text-white transition-all"
              >
                Contact Support
              </motion.button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}