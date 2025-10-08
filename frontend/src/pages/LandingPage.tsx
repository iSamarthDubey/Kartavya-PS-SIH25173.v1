/**
 * KARTAVYA SIEM - Enterprise Landing Page
 * Professional marketing page - Splunk/IBM QRadar/Elastic level
 */

import React, { useState, useEffect } from 'react';
import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  Zap,
  Eye,
  Target,
  Crosshair,
  Radar,
  Brain,
  Bot,
  Cpu,
  Database,
  Network,
  Globe,
  Lock,
  Unlock,
  Key,
  Fingerprint,
  Search,
  Filter,
  BarChart3,
  TrendingUp,
  Activity,
  Users,
  Clock,
  CheckCircle,
  ArrowRight,
  Play,
  Star,
  Award,
  Trophy,
  Crown,
  Sparkles,
  Flame,
  Bug,
  Skull,
  AlertTriangle,
  Terminal,
  Code,
  FileText,
  Download,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Mail,
  Phone,
  MapPin,
  Building,
  Building2,
  Briefcase,
  GraduationCap,
  BookOpen,
  Lightbulb,
  Heart,
  MessageSquare,
  Share2,
  Linkedin,
  Twitter,
  Github,
  Youtube
} from 'lucide-react';

const LandingPage: React.FC = () => {
  const [activeFeature, setActiveFeature] = useState(0);
  const [isVisible, setIsVisible] = useState({
    hero: false,
    features: false,
    stats: false,
    testimonials: false
  });

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible({ hero: true, features: true, stats: true, testimonials: true });
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // Auto-rotate features
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveFeature(prev => (prev + 1) % 4);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white overflow-hidden">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center">
        {/* Animated Background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-cyan-900/20" />
          {/* Animated grid */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:60px_60px]" />
          </div>
          {/* Floating particles */}
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-blue-400 rounded-full animate-pulse"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 3}s`,
                animationDuration: `${3 + Math.random() * 2}s`
              }}
            />
          ))}
        </div>

        <div className={`relative z-10 text-center space-y-12 px-6 transition-all duration-1000 ${
          isVisible.hero ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}>
          {/* Logo & Badge */}
          <div className="space-y-6">
            <div className="inline-flex items-center space-x-3 px-4 py-2 bg-gray-800/50 backdrop-blur-sm border border-blue-500/30 rounded-full">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-blue-400">Next-Generation SIEM Platform</span>
            </div>
            
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 rounded-3xl blur-3xl opacity-20 scale-150" />
              <div className="relative p-8 bg-gradient-to-br from-blue-600 via-purple-600 to-cyan-600 rounded-3xl shadow-2xl">
                <Shield className="w-20 h-20 text-white mx-auto" />
              </div>
            </div>
          </div>

          {/* Main Headline */}
          <div className="space-y-6 max-w-4xl mx-auto">
            <h1 className="text-6xl md:text-8xl font-bold bg-gradient-to-r from-white via-blue-100 to-cyan-100 bg-clip-text text-transparent leading-tight">
              KARTAVYA
              <span className="block text-4xl md:text-6xl bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                Security Intelligence Platform
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
              Enterprise-grade SIEM powered by advanced AI. Detect, analyze, and respond to cyber threats
              in real-time with unprecedented accuracy and speed.
            </p>

            {/* Key Benefits */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto text-center">
              <div className="p-4 bg-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-lg">
                <Zap className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">99.9%</div>
                <div className="text-sm text-gray-400">Threat Detection Rate</div>
              </div>
              <div className="p-4 bg-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-lg">
                <Clock className="w-8 h-8 text-green-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">&lt;3s</div>
                <div className="text-sm text-gray-400">Mean Time to Detect</div>
              </div>
              <div className="p-4 bg-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-lg">
                <Brain className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">AI-Powered</div>
                <div className="text-sm text-gray-400">Threat Intelligence</div>
              </div>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <a 
              href="/login"
              className="group px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 flex items-center space-x-2"
            >
              <Play className="w-5 h-5" />
              <span>Start Free Trial</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </a>
            
            <button className="px-8 py-4 bg-gray-800/50 backdrop-blur-sm border border-gray-600 text-white font-semibold rounded-lg hover:bg-gray-700/50 transition-all duration-300 flex items-center space-x-2">
              <Download className="w-5 h-5" />
              <span>Watch Demo Video</span>
            </button>
          </div>

          {/* Scroll Indicator */}
          <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
            <ChevronDown className="w-6 h-6 text-gray-400" />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-6">
        <div className={`max-w-7xl mx-auto transition-all duration-1000 ${
          isVisible.features ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}>
          {/* Section Header */}
          <div className="text-center space-y-6 mb-20">
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-900/30 border border-blue-700/50 rounded-full">
              <Sparkles className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-medium text-blue-400">Advanced Capabilities</span>
            </div>
            <h2 className="text-4xl md:text-6xl font-bold text-white">
              Built for Modern
              <span className="block bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                Cyber Defense
              </span>
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Experience the most advanced SIEM platform designed for enterprise security operations.
              Real-time threat detection, AI-powered analysis, and automated response capabilities.
            </p>
          </div>

          {/* Interactive Feature Showcase */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Feature Navigation */}
            <div className="space-y-6">
              {[
                {
                  icon: <Brain className="w-6 h-6" />,
                  title: "AI-Powered Threat Detection",
                  description: "Advanced machine learning algorithms detect known and unknown threats with 99.9% accuracy.",
                  color: "blue"
                },
                {
                  icon: <Radar className="w-6 h-6" />,
                  title: "Real-Time Monitoring",
                  description: "Monitor your entire infrastructure 24/7 with millisecond response times and instant alerts.",
                  color: "green"
                },
                {
                  icon: <Target className="w-6 h-6" />,
                  title: "Automated Response",
                  description: "Intelligent playbooks automatically contain threats and minimize damage before human intervention.",
                  color: "purple"
                },
                {
                  icon: <BarChart3 className="w-6 h-6" />,
                  title: "Executive Reporting",
                  description: "Comprehensive dashboards and reports provide actionable insights for all stakeholders.",
                  color: "cyan"
                }
              ].map((feature, index) => (
                <FeatureCard
                  key={index}
                  feature={feature}
                  isActive={activeFeature === index}
                  onClick={() => setActiveFeature(index)}
                />
              ))}
            </div>

            {/* Feature Visualization */}
            <div className="relative">
              <div className="aspect-square bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl border border-gray-700 overflow-hidden">
                <FeatureVisualization activeFeature={activeFeature} />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-24 px-6 bg-gray-800/30">
        <div className={`max-w-7xl mx-auto transition-all duration-1000 ${
          isVisible.stats ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}>
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Trusted by Security Leaders
            </h2>
            <p className="text-xl text-gray-300">
              Join thousands of organizations protecting their digital assets with KARTAVYA
            </p>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { number: "10,000+", label: "Organizations Protected", icon: <Building2 className="w-8 h-8" /> },
              { number: "99.99%", label: "Uptime SLA", icon: <CheckCircle className="w-8 h-8" /> },
              { number: "50M+", label: "Events Processed Daily", icon: <Activity className="w-8 h-8" /> },
              { number: "24/7", label: "Global Support", icon: <Globe className="w-8 h-8" /> }
            ].map((stat, index) => (
              <div key={index} className="text-center p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-700/50 rounded-xl hover:border-blue-500/30 transition-all duration-300">
                <div className="text-blue-400 mb-4 flex justify-center">{stat.icon}</div>
                <div className="text-3xl font-bold text-white mb-2">{stat.number}</div>
                <div className="text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-24 px-6">
        <TestimonialsSection />
      </section>

      {/* Footer */}
      <footer className="py-16 px-6 border-t border-gray-800">
        <FooterSection />
      </footer>
    </div>
  );
};

// Feature Card Component
interface FeatureCardProps {
  feature: {
    icon: React.ReactNode;
    title: string;
    description: string;
    color: string;
  };
  isActive: boolean;
  onClick: () => void;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ feature, isActive, onClick }) => {
  const colorClasses = {
    blue: 'border-blue-500/50 bg-blue-900/20 text-blue-400',
    green: 'border-green-500/50 bg-green-900/20 text-green-400',
    purple: 'border-purple-500/50 bg-purple-900/20 text-purple-400',
    cyan: 'border-cyan-500/50 bg-cyan-900/20 text-cyan-400'
  };

  return (
    <div
      className={`p-6 rounded-xl border cursor-pointer transition-all duration-300 hover:scale-105 ${
        isActive
          ? colorClasses[feature.color as keyof typeof colorClasses]
          : 'border-gray-700 bg-gray-800/30 hover:border-gray-600'
      }`}
      onClick={onClick}
    >
      <div className="flex items-start space-x-4">
        <div className={`p-3 rounded-lg ${isActive ? 'bg-current/20' : 'bg-gray-700'}`}>
          <div className={isActive ? 'text-current' : 'text-gray-400'}>
            {feature.icon}
          </div>
        </div>
        <div>
          <h3 className={`text-xl font-semibold mb-2 ${isActive ? 'text-white' : 'text-gray-300'}`}>
            {feature.title}
          </h3>
          <p className={`${isActive ? 'text-gray-300' : 'text-gray-400'}`}>
            {feature.description}
          </p>
        </div>
      </div>
    </div>
  );
};

// Feature Visualization Component
const FeatureVisualization: React.FC<{ activeFeature: number }> = ({ activeFeature }) => {
  const visualizations = [
    // AI-Powered Threat Detection
    <div className="p-8 h-full flex items-center justify-center">
      <div className="relative">
        <div className="w-32 h-32 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
          <Brain className="w-16 h-16 text-white" />
        </div>
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            className="absolute w-4 h-4 bg-blue-400 rounded-full animate-ping"
            style={{
              left: '50%',
              top: '50%',
              transform: `translate(-50%, -50%) rotate(${i * 45}deg) translateY(-80px)`,
              animationDelay: `${i * 0.2}s`
            }}
          />
        ))}
      </div>
    </div>,
    
    // Real-Time Monitoring
    <div className="p-8 h-full flex items-center justify-center">
      <div className="space-y-4 w-full">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="flex items-center space-x-4">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />
            <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-green-400 to-blue-400 transition-all duration-2000"
                style={{ width: `${20 + Math.random() * 80}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>,
    
    // Automated Response
    <div className="p-8 h-full flex items-center justify-center">
      <div className="relative w-full h-full">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-24 h-24 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center">
            <Target className="w-12 h-12 text-white" />
          </div>
        </div>
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="absolute w-8 h-8 border-2 border-purple-400 rounded-full animate-ping"
            style={{
              left: '50%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
              animationDelay: `${i * 0.5}s`
            }}
          />
        ))}
      </div>
    </div>,
    
    // Executive Reporting
    <div className="p-8 h-full flex items-center justify-center">
      <div className="grid grid-cols-2 gap-4 w-full">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="p-4 bg-gray-700 rounded-lg">
            <BarChart3 className="w-8 h-8 text-cyan-400 mb-2" />
            <div className="h-2 bg-gray-600 rounded mb-1" />
            <div className="h-2 bg-cyan-400 rounded w-3/4" />
          </div>
        ))}
      </div>
    </div>
  ];

  return (
    <div className="relative w-full h-full transition-all duration-500">
      {visualizations[activeFeature]}
    </div>
  );
};

// Testimonials Section
const TestimonialsSection: React.FC = () => (
  <div className="max-w-7xl mx-auto">
    <div className="text-center mb-16">
      <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
        What Security Experts Say
      </h2>
      <p className="text-xl text-gray-300">
        Hear from cybersecurity professionals who trust KARTAVYA
      </p>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {[
        {
          quote: "KARTAVYA has transformed our security operations. The AI-powered threat detection caught advanced persistent threats our previous tools missed.",
          author: "Sarah Chen",
          role: "CISO, Fortune 500 Financial Services",
          company: "SecureBank Corp",
          avatar: "SC"
        },
        {
          quote: "The real-time monitoring and automated response capabilities have reduced our incident response time from hours to minutes.",
          author: "Michael Rodriguez",
          role: "Head of Cybersecurity",
          company: "TechGlobal Industries", 
          avatar: "MR"
        },
        {
          quote: "Best SIEM investment we've made. The executive dashboards finally give our board the security insights they need.",
          author: "Dr. Emily Watson",
          role: "Chief Security Officer",
          company: "MedTech Solutions",
          avatar: "EW"
        }
      ].map((testimonial, index) => (
        <div key={index} className="p-6 bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl hover:border-blue-500/30 transition-all duration-300">
          <div className="flex items-center space-x-1 mb-4">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
            ))}
          </div>
          <p className="text-gray-300 mb-6 italic">
            "{testimonial.quote}"
          </p>
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
              {testimonial.avatar}
            </div>
            <div>
              <div className="font-semibold text-white">{testimonial.author}</div>
              <div className="text-sm text-gray-400">{testimonial.role}</div>
              <div className="text-sm text-blue-400">{testimonial.company}</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Footer Section
const FooterSection: React.FC = () => (
  <div className="max-w-7xl mx-auto">
    <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
      {/* Company Info */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white">KARTAVYA</span>
        </div>
        <p className="text-gray-400">
          Next-generation SIEM platform for enterprise security operations.
        </p>
        <div className="flex space-x-4">
          <Twitter className="w-5 h-5 text-gray-400 hover:text-blue-400 cursor-pointer transition-colors" />
          <Linkedin className="w-5 h-5 text-gray-400 hover:text-blue-400 cursor-pointer transition-colors" />
          <Github className="w-5 h-5 text-gray-400 hover:text-blue-400 cursor-pointer transition-colors" />
          <Youtube className="w-5 h-5 text-gray-400 hover:text-blue-400 cursor-pointer transition-colors" />
        </div>
      </div>

      {/* Product Links */}
      <div>
        <h3 className="font-semibold text-white mb-4">Product</h3>
        <div className="space-y-2 text-gray-400">
          <div className="hover:text-white cursor-pointer transition-colors">Features</div>
          <div className="hover:text-white cursor-pointer transition-colors">Pricing</div>
          <div className="hover:text-white cursor-pointer transition-colors">Documentation</div>
          <div className="hover:text-white cursor-pointer transition-colors">API Reference</div>
        </div>
      </div>

      {/* Company Links */}
      <div>
        <h3 className="font-semibold text-white mb-4">Company</h3>
        <div className="space-y-2 text-gray-400">
          <div className="hover:text-white cursor-pointer transition-colors">About</div>
          <div className="hover:text-white cursor-pointer transition-colors">Careers</div>
          <div className="hover:text-white cursor-pointer transition-colors">Blog</div>
          <div className="hover:text-white cursor-pointer transition-colors">Contact</div>
        </div>
      </div>

      {/* Support Links */}
      <div>
        <h3 className="font-semibold text-white mb-4">Support</h3>
        <div className="space-y-2 text-gray-400">
          <div className="hover:text-white cursor-pointer transition-colors">Help Center</div>
          <div className="hover:text-white cursor-pointer transition-colors">Community</div>
          <div className="hover:text-white cursor-pointer transition-colors">Status</div>
          <div className="hover:text-white cursor-pointer transition-colors">Security</div>
        </div>
      </div>
    </div>

    <div className="border-t border-gray-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
      <div className="text-gray-400">
        © 2024 KARTAVYA. All rights reserved.
      </div>
      <div className="flex space-x-6 text-gray-400 text-sm">
        <div className="hover:text-white cursor-pointer transition-colors">Privacy Policy</div>
        <div className="hover:text-white cursor-pointer transition-colors">Terms of Service</div>
        <div className="hover:text-white cursor-pointer transition-colors">Cookie Policy</div>
      </div>
    </div>
  </div>
);

export default LandingPage;
