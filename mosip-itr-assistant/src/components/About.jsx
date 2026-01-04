import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { Shield, Zap, Users, Award, CheckCircle, TrendingUp } from 'lucide-react'

export function About() {
  const [activeFeature, setActiveFeature] = useState(0)
  const [animationStarted, setAnimationStarted] = useState(false)

  const features = [
    {
      icon: Shield,
      title: "MOSIP Compliant",
      description: "Built on MOSIP standards ensuring highest security and government compliance",
      color: "text-blue-500"
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Process ITR documents in under 2 minutes with 99.9% accuracy",
      color: "text-emerald-500"
    },
    {
      icon: Users,
      title: "Trusted by Thousands",
      description: "Over 100,000+ users trust our platform for their ITR processing needs",
      color: "text-purple-500"
    },
    {
      icon: Award,
      title: "Award Winning",
      description: "Recognized for excellence in digital governance and citizen services",
      color: "text-orange-500"
    }
  ]

  const stats = [
    { value: "1M+", label: "Documents Processed", icon: CheckCircle },
    { value: "99.9%", label: "Accuracy Rate", icon: TrendingUp },
    { value: "100K+", label: "Happy Users", icon: Users },
    { value: "<2min", label: "Processing Time", icon: Zap }
  ]

  const timeline = [
    {
      year: "2023",
      title: "Platform Launch",
      description: "Launched MOSIP ITR Assistant with basic OCR capabilities"
    },
    {
      year: "2024",
      title: "AI Integration",
      description: "Integrated advanced AI for smart data extraction and validation"
    },
    {
      year: "2024",
      title: "MOSIP Compliance",
      description: "Achieved full MOSIP compliance and government certification"
    },
    {
      year: "2025",
      title: "Digital Wallet",
      description: "Launched secure digital wallet for credential storage"
    }
  ]

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimationStarted(true)
      // Cycle through features
      const interval = setInterval(() => {
        setActiveFeature(prev => (prev + 1) % features.length)
      }, 3000)
      return () => clearInterval(interval)
    }, 1000)
    return () => clearTimeout(timer)
  }, [])

  return (
    <section id="about" className="relative py-20 bg-background overflow-hidden">
      
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-b from-background via-[hsl(var(--muted))]/20 to-background" />
        
        {/* Animated background pattern */}
        <div className="absolute inset-0 opacity-[0.02]" style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, rgba(0,0,0,0.15) 1px, transparent 0)`,
          backgroundSize: '30px 30px',
          animation: animationStarted ? 'drift-right 20s ease-in-out infinite' : 'none'
        }} />
        
        {/* Floating orbs */}
        <div className="absolute top-20 left-20 w-64 h-64 bg-[hsl(var(--gov-green))]/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-20 w-80 h-80 bg-[hsl(var(--gov-gold))]/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
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
              About Our Platform
            </span>
            <div className="w-3 h-3 bg-[hsl(var(--gov-gold))] rounded-full animate-pulse" />
          </div>
          
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-[hsl(var(--foreground))]">
            Revolutionizing ITR Processing
          </h2>
          
          <p className="text-xl text-[hsl(var(--muted-foreground))] leading-relaxed max-w-3xl mx-auto">
            Built on cutting-edge technology and MOSIP standards, we're transforming how citizens interact with government services
          </p>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-20"
        >
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="text-center group"
            >
              <div className="w-16 h-16 bg-[hsl(var(--gov-green))]/10 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:bg-[hsl(var(--gov-green))]/20 transition-colors">
                <stat.icon className="w-8 h-8 text-[hsl(var(--gov-green))]" />
              </div>
              <div className="text-3xl font-bold text-[hsl(var(--foreground))] mb-2">{stat.value}</div>
              <div className="text-sm text-[hsl(var(--muted-foreground))]">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>

        {/* Features Showcase */}
        <div className="grid lg:grid-cols-2 gap-16 items-center mb-20">
          
          {/* Left: Feature List */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h3 className="text-3xl font-bold text-[hsl(var(--foreground))] mb-8">
              Why Choose Our Platform?
            </h3>
            
            <div className="space-y-6">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className={`flex items-start gap-4 p-4 rounded-xl transition-all duration-300 cursor-pointer ${
                    activeFeature === index 
                      ? 'bg-[hsl(var(--gov-green))]/10 border-l-4 border-[hsl(var(--gov-green))]' 
                      : 'hover:bg-[hsl(var(--muted))]/50'
                  }`}
                  onClick={() => setActiveFeature(index)}
                >
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    activeFeature === index ? 'bg-[hsl(var(--gov-green))]' : 'bg-[hsl(var(--muted))]'
                  } transition-colors`}>
                    <feature.icon className={`w-6 h-6 ${
                      activeFeature === index ? 'text-white' : 'text-[hsl(var(--muted-foreground))]'
                    }`} />
                  </div>
                  <div>
                    <h4 className="font-semibold text-[hsl(var(--foreground))] mb-2">{feature.title}</h4>
                    <p className="text-[hsl(var(--muted-foreground))] text-sm leading-relaxed">{feature.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Right: Visual Representation */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative"
          >
            <div className="relative bg-gradient-to-br from-[hsl(var(--gov-green))]/5 to-[hsl(var(--gov-gold))]/5 rounded-3xl p-8 border border-[hsl(var(--border))]">
              
              {/* Central Hub */}
              <div className="relative w-32 h-32 bg-[hsl(var(--gov-green))] rounded-full flex items-center justify-center mx-auto mb-8 shadow-lg">
                <Shield className="w-16 h-16 text-white" />
                
                {/* Orbiting Elements */}
                {features.map((feature, index) => (
                  <motion.div
                    key={index}
                    className={`absolute w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-all duration-500 ${
                      activeFeature === index ? 'bg-[hsl(var(--gov-gold))] scale-110' : 'bg-white border-2 border-[hsl(var(--border))]'
                    }`}
                    style={{
                      top: '50%',
                      left: '50%',
                      transform: `translate(-50%, -50%) rotate(${index * 90}deg) translateY(-80px) rotate(-${index * 90}deg)`,
                    }}
                    animate={{
                      rotate: animationStarted ? 360 : 0,
                    }}
                    transition={{
                      duration: 20,
                      repeat: Infinity,
                      ease: "linear"
                    }}
                  >
                    <feature.icon className={`w-6 h-6 ${
                      activeFeature === index ? 'text-white' : 'text-[hsl(var(--muted-foreground))]'
                    }`} />
                  </motion.div>
                ))}
              </div>
              
              <div className="text-center">
                <h4 className="text-xl font-bold text-[hsl(var(--foreground))] mb-2">
                  {features[activeFeature].title}
                </h4>
                <p className="text-[hsl(var(--muted-foreground))]">
                  {features[activeFeature].description}
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-16"
        >
          <h3 className="text-3xl font-bold text-[hsl(var(--foreground))] text-center mb-12">
            Our Journey
          </h3>
          
          <div className="relative">
            {/* Timeline Line */}
            <div className="absolute left-1/2 transform -translate-x-1/2 w-1 h-full bg-[hsl(var(--border))]" />
            
            <div className="space-y-12">
              {timeline.map((item, index) => (
                <motion.div
                  key={`${item.year}-${index}`}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -40 : 40 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                  className={`flex items-center ${index % 2 === 0 ? 'flex-row' : 'flex-row-reverse'}`}
                >
                  <div className={`w-1/2 ${index % 2 === 0 ? 'pr-8 text-right' : 'pl-8'}`}>
                    <div className="bg-white rounded-xl p-6 shadow-lg border border-[hsl(var(--border))]">
                      <div className="text-2xl font-bold text-[hsl(var(--gov-green))] mb-2">{item.year}</div>
                      <h4 className="text-lg font-semibold text-[hsl(var(--foreground))] mb-2">{item.title}</h4>
                      <p className="text-[hsl(var(--muted-foreground))]">{item.description}</p>
                    </div>
                  </div>
                  
                  {/* Timeline Dot */}
                  <div className="w-4 h-4 bg-[hsl(var(--gov-green))] rounded-full border-4 border-white shadow-lg z-10" />
                  
                  <div className="w-1/2" />
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Mission Statement */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center bg-gradient-to-r from-[hsl(var(--gov-green))] to-[hsl(var(--gov-green-light))] rounded-2xl p-12 text-white"
        >
          <h3 className="text-3xl font-bold mb-6">Our Mission</h3>
          <p className="text-xl leading-relaxed max-w-4xl mx-auto opacity-90">
            To democratize access to government services through innovative technology, 
            making ITR processing simple, secure, and accessible for every citizen while 
            maintaining the highest standards of data privacy and MOSIP compliance.
          </p>
        </motion.div>
      </div>
    </section>
  )
}