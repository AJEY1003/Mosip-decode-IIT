import { motion } from 'framer-motion'
import { Landmark, Mail, Phone, MapPin, Facebook, Twitter, Linkedin, Instagram, ArrowUp } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export function NewFooter() {
  const navigate = useNavigate()

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const footerLinks = {
    services: [
      { label: 'Document Upload', route: '/upload' },
      { label: 'OCR Processing', route: '/upload' },
      { label: 'Data Extraction', route: '/forms' },
      { label: 'MOSIP Validation', route: '/validation' },
      { label: 'Digital Wallet', route: '/wallet' }
    ],
    support: [
      { label: 'Help Center', route: '#contact' },
      { label: 'Documentation', route: '#about' },
      { label: 'API Reference', route: '#contact' },
      { label: 'System Status', route: '#contact' },
      { label: 'Contact Support', route: '#contact' }
    ],
    legal: [
      { label: 'Privacy Policy', route: '#contact' },
      { label: 'Terms of Service', route: '#contact' },
      { label: 'Data Protection', route: '#contact' },
      { label: 'MOSIP Compliance', route: '#contact' },
      { label: 'Security', route: '#contact' }
    ]
  }

  const socialLinks = [
    { icon: Facebook, href: '#', label: 'Facebook' },
    { icon: Twitter, href: '#', label: 'Twitter' },
    { icon: Linkedin, href: '#', label: 'LinkedIn' },
    { icon: Instagram, href: '#', label: 'Instagram' }
  ]

  return (
    <footer className="relative bg-[hsl(var(--gov-navy))] text-white overflow-hidden">
      
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-[hsl(var(--gov-navy))] via-[hsl(var(--gov-green-dark))] to-[hsl(var(--gov-navy))]" />
        <div className="absolute inset-0 opacity-[0.03]" style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, rgba(255,255,255,0.3) 1px, transparent 0)`,
          backgroundSize: '30px 30px'
        }} />
        
        {/* Subtle glow effects */}
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-[hsl(var(--gov-gold))]/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-72 h-72 bg-[hsl(var(--gov-green))]/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10">
        
        {/* Main Footer Content */}
        <div className="container mx-auto px-6 sm:px-8 lg:px-12 py-16">
          <div className="grid lg:grid-cols-4 gap-12">
            
            {/* Brand Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="lg:col-span-1"
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-[hsl(var(--gov-gold))] rounded-xl">
                  <Landmark className="w-8 h-8 text-[hsl(var(--gov-navy))]" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold">MOSIP ITR</h3>
                  <p className="text-sm text-white/70">Assistant Portal</p>
                </div>
              </div>
              
              <p className="text-white/80 leading-relaxed mb-6">
                Streamlining ITR processing with cutting-edge technology and MOSIP-compliant security. 
                Your trusted partner for secure document processing.
              </p>
              
              {/* Contact Info */}
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-sm">
                  <Mail className="w-4 h-4 text-[hsl(var(--gov-gold))]" />
                  <span className="text-white/80">support@mosip-itr.gov.in</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <Phone className="w-4 h-4 text-[hsl(var(--gov-gold))]" />
                  <span className="text-white/80">+91-1800-XXX-XXXX</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <MapPin className="w-4 h-4 text-[hsl(var(--gov-gold))]" />
                  <span className="text-white/80">Digital India Building, New Delhi</span>
                </div>
              </div>
            </motion.div>

            {/* Services Links */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <h4 className="text-lg font-semibold mb-6 text-[hsl(var(--gov-gold))]">Services</h4>
              <ul className="space-y-3">
                {footerLinks.services.map((link, index) => (
                  <li key={index}>
                    <button
                      onClick={() => navigate(link.route)}
                      className="text-white/80 hover:text-white hover:translate-x-1 transition-all duration-200 text-sm"
                    >
                      {link.label}
                    </button>
                  </li>
                ))}
              </ul>
            </motion.div>

            {/* Support Links */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <h4 className="text-lg font-semibold mb-6 text-[hsl(var(--gov-gold))]">Support</h4>
              <ul className="space-y-3">
                {footerLinks.support.map((link, index) => (
                  <li key={index}>
                    <a
                      href={link.route}
                      className="text-white/80 hover:text-white hover:translate-x-1 transition-all duration-200 text-sm"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </motion.div>

            {/* Legal & Newsletter */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <h4 className="text-lg font-semibold mb-6 text-[hsl(var(--gov-gold))]">Legal</h4>
              <ul className="space-y-3 mb-8">
                {footerLinks.legal.map((link, index) => (
                  <li key={index}>
                    <a
                      href={link.route}
                      className="text-white/80 hover:text-white hover:translate-x-1 transition-all duration-200 text-sm"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>

              {/* Newsletter Signup */}
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                <h5 className="font-semibold mb-3">Stay Updated</h5>
                <p className="text-sm text-white/70 mb-4">
                  Get the latest updates on new features and improvements.
                </p>
                <div className="flex gap-2">
                  <input
                    type="email"
                    placeholder="Enter your email"
                    className="flex-1 px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-sm placeholder-white/50 focus:outline-none focus:border-[hsl(var(--gov-gold))]"
                  />
                  <button className="px-4 py-2 bg-[hsl(var(--gov-gold))] text-[hsl(var(--gov-navy))] rounded-lg font-semibold text-sm hover:bg-[hsl(var(--gov-gold-dark))] transition-colors">
                    Subscribe
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-white/10">
          <div className="container mx-auto px-6 sm:px-8 lg:px-12 py-6">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              
              {/* Copyright */}
              <motion.div
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
                className="text-sm text-white/60"
              >
                © 2025 MOSIP ITR Assistant. All rights reserved. | Built with ❤️ for Digital India
              </motion.div>

              {/* Social Links */}
              <motion.div
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="flex items-center gap-4"
              >
                {socialLinks.map((social, index) => (
                  <motion.a
                    key={social.label}
                    href={social.href}
                    whileHover={{ scale: 1.1, y: -2 }}
                    className="w-10 h-10 bg-white/10 hover:bg-[hsl(var(--gov-gold))] rounded-lg flex items-center justify-center transition-all duration-300 group"
                    aria-label={social.label}
                  >
                    <social.icon className="w-5 h-5 text-white/70 group-hover:text-[hsl(var(--gov-navy))] transition-colors" />
                  </motion.a>
                ))}
              </motion.div>

              {/* Back to Top */}
              <motion.button
                onClick={scrollToTop}
                whileHover={{ scale: 1.1, y: -2 }}
                whileTap={{ scale: 0.9 }}
                className="w-10 h-10 bg-[hsl(var(--gov-green))] hover:bg-[hsl(var(--gov-green-light))] rounded-lg flex items-center justify-center transition-all duration-300 shadow-lg"
                aria-label="Back to top"
              >
                <ArrowUp className="w-5 h-5 text-white" />
              </motion.button>
            </div>
          </div>
        </div>

        {/* Government Compliance Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="bg-[hsl(var(--gov-green))]/20 border-t border-[hsl(var(--gov-green))]/30"
        >
          <div className="container mx-auto px-6 sm:px-8 lg:px-12 py-4">
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 text-center">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-[hsl(var(--gov-gold))] rounded-full flex items-center justify-center">
                  <Landmark className="w-4 h-4 text-[hsl(var(--gov-navy))]" />
                </div>
                <span className="text-sm font-semibold text-[hsl(var(--gov-gold))]">MOSIP Certified</span>
              </div>
              <div className="hidden sm:block w-px h-4 bg-white/20" />
              <span className="text-xs text-white/60">
                This platform is certified and compliant with MOSIP standards for secure identity processing
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </footer>
  )
}