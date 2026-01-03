import { motion } from 'framer-motion'
import { Upload, Scan, Database, ShieldCheck, FileCheck, Wallet, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export function HowItWorks() {
  const navigate = useNavigate()

  const steps = [
    {
      number: "01",
      icon: Upload,
      title: "Upload Documents",
      description: "Securely upload your scanned ITR documents (PDF, JPG, PNG). Our system supports multiple file formats and ensures data privacy.",
      color: "bg-blue-500",
      route: "/upload"
    },
    {
      number: "02", 
      icon: Scan,
      title: "OCR Processing",
      description: "Advanced OCR technology extracts text and data from your documents with 99.9% accuracy, supporting multiple languages including Hindi.",
      color: "bg-emerald-500",
      route: "/upload"
    },
    {
      number: "03",
      icon: Database,
      title: "Data Extraction",
      description: "AI-powered NER (Named Entity Recognition) identifies and extracts relevant ITR information like PAN, income details, and tax calculations.",
      color: "bg-purple-500",
      route: "/forms"
    },
    {
      number: "04",
      icon: ShieldCheck,
      title: "MOSIP Validation",
      description: "Validate extracted data against MOSIP standards and government databases to ensure accuracy and compliance.",
      color: "bg-orange-500",
      route: "/validation"
    },
    {
      number: "05",
      icon: FileCheck,
      title: "Form Generation",
      description: "Automatically populate ITR forms with extracted data, ready for review and submission to income tax authorities.",
      color: "bg-indigo-500",
      route: "/forms"
    },
    {
      number: "06",
      icon: Wallet,
      title: "Digital Wallet",
      description: "Store verified credentials and processed documents in your secure digital wallet for future reference and compliance.",
      color: "bg-teal-500",
      route: "/wallet"
    }
  ]

  return (
    <section id="how-it-works" className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
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
              Step by Step Process
            </span>
            <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
          </div>
          
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-[hsl(var(--foreground))]">
            How It Works
          </h2>
          
          <p className="text-xl text-[hsl(var(--muted-foreground))] leading-relaxed max-w-3xl mx-auto">
            From document upload to digital wallet storage - experience seamless ITR processing
          </p>
        </motion.div>

        {/* Steps Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className="relative group cursor-pointer"
              onClick={() => navigate(step.route)}
            >
              {/* Card */}
              <div className="relative bg-white rounded-2xl p-8 shadow-[0_4px_20px_rgba(0,0,0,0.08)] border border-[hsl(var(--border))] hover:shadow-[0_8px_40px_rgba(0,0,0,0.12)] transition-all duration-300 h-full">
                
                {/* Step Number */}
                <div className="absolute -top-4 -left-4 w-12 h-12 bg-[hsl(var(--gov-green))] text-white rounded-full flex items-center justify-center font-bold text-lg shadow-lg">
                  {step.number}
                </div>
                
                {/* Icon */}
                <div className={`w-16 h-16 ${step.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <step.icon className="w-8 h-8 text-white" />
                </div>
                
                {/* Content */}
                <h3 className="text-xl font-bold text-[hsl(var(--foreground))] mb-4 group-hover:text-[hsl(var(--gov-green))] transition-colors">
                  {step.title}
                </h3>
                
                <p className="text-[hsl(var(--muted-foreground))] leading-relaxed mb-6">
                  {step.description}
                </p>
                
                {/* Arrow */}
                <div className="flex items-center text-[hsl(var(--gov-green))] font-semibold group-hover:translate-x-2 transition-transform duration-300">
                  <span className="text-sm">Try Now</span>
                  <ArrowRight className="w-4 h-4 ml-2" />
                </div>
                
                {/* Connecting Line (for larger screens) */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-[hsl(var(--border))] to-transparent" />
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="text-center"
        >
          <div className="bg-gradient-to-r from-[hsl(var(--gov-green))] to-[hsl(var(--gov-green-light))] rounded-2xl p-8 md:p-12 text-white">
            <h3 className="text-2xl md:text-3xl font-bold mb-4">
              Ready to Process Your ITR Documents?
            </h3>
            <p className="text-lg opacity-90 mb-8 max-w-2xl mx-auto">
              Join thousands of users who trust our secure, MOSIP-compliant platform for their ITR processing needs.
            </p>
            
            <div className="flex flex-wrap gap-4 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/upload')}
                className="bg-white text-[hsl(var(--gov-green))] font-bold px-8 py-4 rounded-xl text-lg shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
              >
                <Upload className="w-5 h-5" />
                Start Processing
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/validation')}
                className="bg-white/10 backdrop-blur-sm text-white font-semibold px-8 py-4 rounded-xl text-lg border border-white/20 hover:bg-white/20 transition-all flex items-center gap-2"
              >
                <ShieldCheck className="w-5 h-5" />
                Validate Documents
              </motion.button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}