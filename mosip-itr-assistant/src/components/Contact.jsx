import { motion } from 'framer-motion'
import { useState } from 'react'
import { Mail, Phone, MapPin, Clock, Send, CheckCircle, AlertCircle } from 'lucide-react'

export function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState(null)

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    // Simulate form submission
    setTimeout(() => {
      setIsSubmitting(false)
      setSubmitStatus('success')
      setFormData({ name: '', email: '', subject: '', message: '' })
      
      // Reset status after 5 seconds
      setTimeout(() => setSubmitStatus(null), 5000)
    }, 2000)
  }

  const contactInfo = [
    {
      icon: Mail,
      title: "Email Support",
      details: "support@mosip-itr.gov.in",
      description: "Get help via email within 24 hours"
    },
    {
      icon: Phone,
      title: "Phone Support",
      details: "+91-1800-XXX-XXXX",
      description: "Mon-Fri, 9:00 AM - 6:00 PM IST"
    },
    {
      icon: MapPin,
      title: "Office Address",
      details: "Digital India Building, New Delhi",
      description: "Visit us for in-person assistance"
    },
    {
      icon: Clock,
      title: "Response Time",
      details: "< 24 hours",
      description: "Average response time for queries"
    }
  ]

  const faqs = [
    {
      question: "How secure is my data?",
      answer: "We use bank-grade encryption and MOSIP-compliant security measures to protect your data."
    },
    {
      question: "What document formats are supported?",
      answer: "We support PDF, JPG, PNG, and TIFF formats for document upload."
    },
    {
      question: "How long does processing take?",
      answer: "Most documents are processed within 2 minutes with 99.9% accuracy."
    },
    {
      question: "Is there a mobile app available?",
      answer: "Yes, our mobile app is available on both Android and iOS platforms."
    }
  ]

  return (
    <section id="contact" className="relative py-20 bg-gradient-to-br from-[hsl(var(--muted))] to-background">
      
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 opacity-[0.02]" style={{
          backgroundImage: `linear-gradient(45deg, rgba(0,0,0,0.1) 25%, transparent 25%), linear-gradient(-45deg, rgba(0,0,0,0.1) 25%, transparent 25%)`,
          backgroundSize: '20px 20px'
        }} />
        
        <div className="absolute top-10 right-10 w-72 h-72 bg-[hsl(var(--gov-green))]/5 rounded-full blur-3xl" />
        <div className="absolute bottom-10 left-10 w-96 h-96 bg-[hsl(var(--gov-gold))]/5 rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
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
              Get in Touch
            </span>
            <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
          </div>
          
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-[hsl(var(--foreground))]">
            Contact Us
          </h2>
          
          <p className="text-xl text-[hsl(var(--muted-foreground))] leading-relaxed max-w-3xl mx-auto">
            Have questions about ITR processing? Our support team is here to help you 24/7
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-16">
          
          {/* Left: Contact Form */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))]">
              <h3 className="text-2xl font-bold text-[hsl(var(--foreground))] mb-6">Send us a Message</h3>
              
              {submitStatus === 'success' && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6 flex items-center gap-3"
                >
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-green-700">Message sent successfully! We'll get back to you soon.</span>
                </motion.div>
              )}
              
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-semibold text-[hsl(var(--foreground))] mb-2">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 rounded-xl border border-[hsl(var(--border))] focus:border-[hsl(var(--gov-green))] focus:ring-2 focus:ring-[hsl(var(--gov-green))]/20 outline-none transition-all"
                      placeholder="Enter your full name"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-semibold text-[hsl(var(--foreground))] mb-2">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 rounded-xl border border-[hsl(var(--border))] focus:border-[hsl(var(--gov-green))] focus:ring-2 focus:ring-[hsl(var(--gov-green))]/20 outline-none transition-all"
                      placeholder="Enter your email"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-semibold text-[hsl(var(--foreground))] mb-2">
                    Subject *
                  </label>
                  <input
                    type="text"
                    name="subject"
                    value={formData.subject}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 rounded-xl border border-[hsl(var(--border))] focus:border-[hsl(var(--gov-green))] focus:ring-2 focus:ring-[hsl(var(--gov-green))]/20 outline-none transition-all"
                    placeholder="What's this about?"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-semibold text-[hsl(var(--foreground))] mb-2">
                    Message *
                  </label>
                  <textarea
                    name="message"
                    value={formData.message}
                    onChange={handleInputChange}
                    required
                    rows={5}
                    className="w-full px-4 py-3 rounded-xl border border-[hsl(var(--border))] focus:border-[hsl(var(--gov-green))] focus:ring-2 focus:ring-[hsl(var(--gov-green))]/20 outline-none transition-all resize-none"
                    placeholder="Tell us how we can help you..."
                  />
                </div>
                
                <motion.button
                  type="submit"
                  disabled={isSubmitting}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full bg-[hsl(var(--gov-green))] text-white font-semibold py-4 px-6 rounded-xl flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      Send Message
                    </>
                  )}
                </motion.button>
              </form>
            </div>
          </motion.div>

          {/* Right: Contact Info & FAQs */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="space-y-8"
          >
            
            {/* Contact Information */}
            <div className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))]">
              <h3 className="text-2xl font-bold text-[hsl(var(--foreground))] mb-6">Get in Touch</h3>
              
              <div className="space-y-6">
                {contactInfo.map((info, index) => (
                  <motion.div
                    key={info.title}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className="flex items-start gap-4"
                  >
                    <div className="w-12 h-12 bg-[hsl(var(--gov-green))]/10 rounded-xl flex items-center justify-center flex-shrink-0">
                      <info.icon className="w-6 h-6 text-[hsl(var(--gov-green))]" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-[hsl(var(--foreground))] mb-1">{info.title}</h4>
                      <p className="text-[hsl(var(--gov-green))] font-medium mb-1">{info.details}</p>
                      <p className="text-sm text-[hsl(var(--muted-foreground))]">{info.description}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* FAQs */}
            <div className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.1)] border border-[hsl(var(--border))]">
              <h3 className="text-2xl font-bold text-[hsl(var(--foreground))] mb-6">Frequently Asked Questions</h3>
              
              <div className="space-y-4">
                {faqs.map((faq, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className="border border-[hsl(var(--border))] rounded-xl p-4 hover:bg-[hsl(var(--muted))]/30 transition-colors"
                  >
                    <h4 className="font-semibold text-[hsl(var(--foreground))] mb-2">{faq.question}</h4>
                    <p className="text-sm text-[hsl(var(--muted-foreground))] leading-relaxed">{faq.answer}</p>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Emergency Contact */}
            <div className="bg-gradient-to-r from-[hsl(var(--gov-green))] to-[hsl(var(--gov-green-light))] rounded-2xl p-6 text-white">
              <div className="flex items-center gap-3 mb-3">
                <AlertCircle className="w-6 h-6" />
                <h4 className="font-bold text-lg">Emergency Support</h4>
              </div>
              <p className="opacity-90 mb-4">
                For urgent technical issues or security concerns, contact our emergency helpline.
              </p>
              <div className="flex items-center gap-2 font-semibold">
                <Phone className="w-4 h-4" />
                <span>+91-1800-XXX-HELP (24/7)</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}