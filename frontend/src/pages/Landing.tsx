import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { ArrowRight, Zap, Shield, BarChart3, MessageSquare, FileText, Network } from 'lucide-react'

export default function LandingPage() {
  const features = [
    {
      icon: MessageSquare,
      title: "Conversational Investigation",
      description: "Ask questions in natural language and get instant insights from your SIEM data."
    },
    {
      icon: FileText,
      title: "Automated Reports",
      description: "Generate comprehensive security reports with charts and narratives automatically."
    },
    {
      icon: Network,
      title: "SIEM Integrations",
      description: "Connect to Elastic Security, Wazuh, and other leading SIEM platforms."
    },
    {
      icon: BarChart3,
      title: "Visual Analytics",
      description: "Transform complex security data into intuitive visualizations and dashboards."
    },
    {
      icon: Shield,
      title: "Enterprise Security",
      description: "Built for government and enterprise with RBAC, audit logging, and compliance."
    },
    {
      icon: Zap,
      title: "Real-time Intelligence",
      description: "Get instant threat intelligence and investigation results as you type."
    }
  ]

  return (
    <div className="min-h-screen bg-synrgy-bg-900">
      {/* Header */}
      <header className="relative z-10 px-4 sm:px-6 lg:px-8 py-6">
        <nav className="flex items-center justify-between max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="flex items-center space-x-3"
          >
            <div className="w-10 h-10 bg-gradient-to-br from-synrgy-primary to-synrgy-accent rounded-lg flex items-center justify-center">
              <span className="text-synrgy-bg-900 font-bold text-lg">S</span>
            </div>
            <span className="text-2xl font-heading font-bold text-gradient">
              ＳＹＮＲＧＹ
            </span>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="flex items-center space-x-6"
          >
            <Link
              to="/login"
              className="text-synrgy-muted hover:text-synrgy-primary transition-colors font-medium"
            >
              Sign In
            </Link>
            <Link
              to="/login"
              className="btn-primary"
            >
              Get Started
              <ArrowRight className="ml-2 w-4 h-4" />
            </Link>
          </motion.div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative px-4 sm:px-6 lg:px-8 pt-20 pb-32">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <h1 className="heading-xl mb-6">
              Human + AI. In Perfect{' '}
              <span className="text-synrgy-primary">ＳＹＮＲＧＹ</span>
            </h1>
            
            <p className="text-xl text-synrgy-muted max-w-3xl mx-auto mb-12 leading-relaxed">
              Investigate, visualize and report security threats using natural conversation. 
              Transform your SIEM into an intelligent conversational partner for investigations.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/login" className="btn-primary text-lg px-8 py-4">
                Try ＳＹＮＲＧＹ Now
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              
              <button className="btn-secondary text-lg px-8 py-4">
                Watch Demo
              </button>
            </div>
          </motion.div>
        </div>

        {/* Background decoration */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-synrgy-primary/5 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-synrgy-accent/5 rounded-full blur-3xl" />
        </div>
      </section>

      {/* Features Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-24">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="heading-lg mb-4">
              Powerful Features for Modern Security Teams
            </h2>
            <p className="text-lg text-synrgy-muted max-w-2xl mx-auto">
              Everything you need to transform your security operations with 
              conversational AI and intelligent automation.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="card-hover p-8 text-center group"
              >
                <div className="w-16 h-16 mx-auto mb-6 bg-synrgy-primary/10 rounded-2xl flex items-center justify-center group-hover:bg-synrgy-primary/20 transition-colors">
                  <feature.icon className="w-8 h-8 text-synrgy-primary" />
                </div>
                
                <h3 className="heading-md mb-4">
                  {feature.title}
                </h3>
                
                <p className="text-synrgy-muted leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-24">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="card-glow p-12 relative overflow-hidden"
          >
            <div className="relative z-10">
              <h2 className="heading-lg mb-6">
                Ready to Transform Your Security Operations?
              </h2>
              
              <p className="text-lg text-synrgy-muted mb-8">
                Join security teams using ＳＹＮＲＧＹ to investigate threats faster
                and generate reports effortlessly.
              </p>
              
              <Link to="/login" className="btn-primary text-lg px-8 py-4 inline-flex items-center">
                Get Started Today
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
            </div>
            
            {/* Background decoration */}
            <div className="absolute inset-0 bg-gradient-to-br from-synrgy-primary/5 via-transparent to-synrgy-accent/5" />
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-synrgy-primary/10 px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-gradient-to-br from-synrgy-primary to-synrgy-accent rounded-lg flex items-center justify-center">
                <span className="text-synrgy-bg-900 font-bold">S</span>
              </div>
              <span className="text-xl font-heading font-bold text-gradient">
                ＳＹＮＲＧＹ
              </span>
            </div>
            
            <div className="text-synrgy-muted text-sm">
              <p>Team Kartavya | Smart India Hackathon 2025</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
