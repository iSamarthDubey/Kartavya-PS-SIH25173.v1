/**
 * KARTAVYA SIEM - Professional Onboarding Flow
 * Guided introduction for new users with role-based content
 */

import React, { useState, useEffect } from 'react';
import {
  Shield,
  CheckCircle,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Target,
  Brain,
  Users,
  BarChart3,
  Globe,
  Zap,
  Eye,
  Settings,
  BookOpen,
  Play,
  Star,
  Crown,
  Award,
  Lightbulb,
  HeadphonesIcon,
  MessageSquare,
  Clock,
  TrendingUp,
  Activity,
  Database,
  Lock,
  Radar,
  X
} from 'lucide-react';

import { useAuth } from '../store/appStore';
import { useNotifications } from './ui/NotificationSystem';

interface OnboardingFlowProps {
  onComplete: () => void;
}

const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);
  const { user } = useAuth();
  const { showSuccess } = useNotifications();

  // Role-based onboarding content
  const getRoleBasedContent = () => {
    switch (user?.role) {
      case 'Security Analyst':
        return {
          title: 'Welcome, Security Analyst!',
          subtitle: 'Your front-line defense starts here',
          description: 'As a Security Analyst, you\'ll be the first to spot and respond to potential threats. Let\'s get you familiar with the tools that will make you more effective.',
          icon: <Shield className="w-12 h-12 text-blue-400" />,
          color: 'blue',
          steps: [
            {
              title: 'Threat Detection Dashboard',
              description: 'Monitor real-time security events and alerts with advanced filtering and prioritization.',
              features: ['Real-time threat feeds', 'SIEM event correlation', 'Custom alert rules'],
              icon: <Radar className="w-8 h-8" />,
              demo: 'dashboard'
            },
            {
              title: 'AI-Powered Analysis',
              description: 'Use our intelligent assistant to quickly analyze threats and get response recommendations.',
              features: ['Natural language queries', 'Automated threat hunting', 'Incident playbooks'],
              icon: <Brain className="w-8 h-8" />,
              demo: 'chat'
            },
            {
              title: 'Investigation Tools',
              description: 'Deep-dive into security incidents with comprehensive forensic capabilities.',
              features: ['Log analysis', 'Network flow investigation', 'Malware sandbox'],
              icon: <Eye className="w-8 h-8" />,
              demo: 'investigate'
            }
          ]
        };
        
      case 'SOC Manager':
        return {
          title: 'Welcome, SOC Manager!',
          subtitle: 'Command center for security operations',
          description: 'Oversee your security team\'s operations with comprehensive visibility and management tools.',
          icon: <Crown className="w-12 h-12 text-purple-400" />,
          color: 'purple',
          steps: [
            {
              title: 'Operations Dashboard',
              description: 'Get complete visibility into your SOC\'s performance and security posture.',
              features: ['Team performance metrics', 'SLA tracking', 'Resource allocation'],
              icon: <Activity className="w-8 h-8" />,
              demo: 'dashboard'
            },
            {
              title: 'Team Coordination',
              description: 'Manage incidents, assign tasks, and coordinate response efforts across your team.',
              features: ['Incident assignment', 'Team communication', 'Workflow automation'],
              icon: <Users className="w-8 h-8" />,
              demo: 'team'
            },
            {
              title: 'Executive Reporting',
              description: 'Generate comprehensive reports for stakeholders and leadership.',
              features: ['Custom dashboards', 'Automated reports', 'Trend analysis'],
              icon: <BarChart3 className="w-8 h-8" />,
              demo: 'reports'
            }
          ]
        };
        
      case 'System Administrator':
        return {
          title: 'Welcome, System Administrator!',
          subtitle: 'Master of security infrastructure',
          description: 'Configure and manage the KARTAVYA platform to optimize security operations.',
          icon: <Settings className="w-12 h-12 text-green-400" />,
          color: 'green',
          steps: [
            {
              title: 'System Configuration',
              description: 'Set up data sources, connectors, and security policies.',
              features: ['Data source integration', 'Policy configuration', 'Rule management'],
              icon: <Database className="w-8 h-8" />,
              demo: 'settings'
            },
            {
              title: 'User Management',
              description: 'Manage user accounts, roles, and access permissions.',
              features: ['Role-based access', 'User provisioning', 'Permission management'],
              icon: <Lock className="w-8 h-8" />,
              demo: 'users'
            },
            {
              title: 'Platform Monitoring',
              description: 'Monitor system health, performance, and capacity.',
              features: ['Health monitoring', 'Performance metrics', 'Capacity planning'],
              icon: <TrendingUp className="w-8 h-8" />,
              demo: 'monitoring'
            }
          ]
        };
        
      case 'Chief Information Security Officer':
        return {
          title: 'Welcome, CISO!',
          subtitle: 'Strategic security leadership',
          description: 'Get executive-level insights into your organization\'s security posture and risk management.',
          icon: <Award className="w-12 h-12 text-gold-400" />,
          color: 'yellow',
          steps: [
            {
              title: 'Executive Dashboard',
              description: 'High-level view of security metrics and organizational risk.',
              features: ['Risk scoring', 'Trend analysis', 'Compliance status'],
              icon: <Globe className="w-8 h-8" />,
              demo: 'executive'
            },
            {
              title: 'Strategic Reporting',
              description: 'Board-ready reports and security posture assessments.',
              features: ['Executive summaries', 'Risk assessments', 'Compliance reports'],
              icon: <BarChart3 className="w-8 h-8" />,
              demo: 'reports'
            },
            {
              title: 'Security Intelligence',
              description: 'AI-powered insights and recommendations for strategic decisions.',
              features: ['Threat intelligence', 'Risk predictions', 'Investment recommendations'],
              icon: <Brain className="w-8 h-8" />,
              demo: 'intelligence'
            }
          ]
        };
        
      default:
        return {
          title: 'Welcome to KARTAVYA!',
          subtitle: 'Your security operations platform',
          description: 'Discover the powerful features that will enhance your cybersecurity capabilities.',
          icon: <Sparkles className="w-12 h-12 text-blue-400" />,
          color: 'blue',
          steps: [
            {
              title: 'Security Dashboard',
              description: 'Monitor your security posture with real-time insights.',
              features: ['Real-time monitoring', 'Threat detection', 'Alert management'],
              icon: <Shield className="w-8 h-8" />,
              demo: 'dashboard'
            },
            {
              title: 'AI Assistant',
              description: 'Get intelligent support for security analysis and response.',
              features: ['Natural language queries', 'Automated analysis', 'Smart recommendations'],
              icon: <Brain className="w-8 h-8" />,
              demo: 'chat'
            },
            {
              title: 'Reporting & Analytics',
              description: 'Generate insights and reports for better decision making.',
              features: ['Custom reports', 'Analytics', 'Trend analysis'],
              icon: <BarChart3 className="w-8 h-8" />,
              demo: 'reports'
            }
          ]
        };
    }
  };

  const roleContent = getRoleBasedContent();
  const totalSteps = roleContent.steps.length + 2; // Welcome + steps + completion

  const handleNext = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      completeOnboarding();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const completeOnboarding = () => {
    localStorage.setItem('kartavya_onboarding_completed', 'true');
    showSuccess('Welcome to KARTAVYA!', 'Your onboarding is complete. Let\'s secure your organization!');
    onComplete();
  };

  const skipOnboarding = () => {
    completeOnboarding();
  };

  if (!isVisible) return null;

  const getStepContent = () => {
    if (currentStep === 0) {
      // Welcome step
      return <WelcomeStep roleContent={roleContent} user={user} />;
    } else if (currentStep === totalSteps - 1) {
      // Completion step
      return <CompletionStep roleContent={roleContent} user={user} />;
    } else {
      // Feature steps
      const stepIndex = currentStep - 1;
      return <FeatureStep step={roleContent.steps[stepIndex]} roleContent={roleContent} />;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="relative p-6 bg-gradient-to-r from-gray-800 to-gray-900 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">KARTAVYA Onboarding</h2>
                <p className="text-sm text-gray-400">Step {currentStep + 1} of {totalSteps}</p>
              </div>
            </div>
            <button
              onClick={skipOnboarding}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4 w-full bg-gray-700 rounded-full h-2 overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-600 to-purple-600 transition-all duration-500 ease-out"
              style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
            />
          </div>
        </div>

        {/* Content */}
        <div className="p-8">
          {getStepContent()}
        </div>

        {/* Footer */}
        <div className="p-6 bg-gray-800/50 border-t border-gray-700 flex items-center justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>

          <div className="flex items-center space-x-2">
            <button
              onClick={skipOnboarding}
              className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
            >
              Skip Tour
            </button>
            <button
              onClick={handleNext}
              className="flex items-center space-x-2 px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all"
            >
              <span>{currentStep === totalSteps - 1 ? 'Get Started' : 'Next'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Welcome Step Component
const WelcomeStep: React.FC<{ roleContent: any; user: any }> = ({ roleContent, user }) => (
  <div className="text-center space-y-8">
    <div className="space-y-6">
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-cyan-600/20 blur-3xl" />
        <div className="relative">{roleContent.icon}</div>
      </div>
      
      <div>
        <h1 className="text-4xl font-bold text-white mb-3">{roleContent.title}</h1>
        <p className="text-xl text-blue-400 mb-4">{roleContent.subtitle}</p>
        <p className="text-gray-300 max-w-2xl mx-auto leading-relaxed">
          {roleContent.description}
        </p>
      </div>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
      <div className="p-4 bg-gray-800/50 border border-gray-700 rounded-lg">
        <Zap className="w-8 h-8 text-yellow-400 mx-auto mb-3" />
        <h3 className="font-semibold text-white mb-2">Fast Setup</h3>
        <p className="text-sm text-gray-400">Get up and running in minutes</p>
      </div>
      <div className="p-4 bg-gray-800/50 border border-gray-700 rounded-lg">
        <Brain className="w-8 h-8 text-purple-400 mx-auto mb-3" />
        <h3 className="font-semibold text-white mb-2">AI-Powered</h3>
        <p className="text-sm text-gray-400">Intelligent threat detection</p>
      </div>
      <div className="p-4 bg-gray-800/50 border border-gray-700 rounded-lg">
        <Clock className="w-8 h-8 text-green-400 mx-auto mb-3" />
        <h3 className="font-semibold text-white mb-2">24/7 Protection</h3>
        <p className="text-sm text-gray-400">Always-on security monitoring</p>
      </div>
    </div>
  </div>
);

// Feature Step Component  
const FeatureStep: React.FC<{ step: any; roleContent: any }> = ({ step, roleContent }) => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <div className={`p-3 bg-${roleContent.color}-600/20 border border-${roleContent.color}-500/30 rounded-lg`}>
          <div className={`text-${roleContent.color}-400`}>{step.icon}</div>
        </div>
        <div>
          <h2 className="text-3xl font-bold text-white">{step.title}</h2>
        </div>
      </div>
      
      <p className="text-xl text-gray-300 leading-relaxed">
        {step.description}
      </p>
      
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-white">Key Features:</h3>
        <div className="space-y-2">
          {step.features.map((feature: string, index: number) => (
            <div key={index} className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span className="text-gray-300">{feature}</span>
            </div>
          ))}
        </div>
      </div>

      <button className="flex items-center space-x-2 px-6 py-3 bg-gray-800 border border-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
        <Play className="w-4 h-4" />
        <span>Try Interactive Demo</span>
      </button>
    </div>
    
    <div className="relative">
      <div className="aspect-square bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 rounded-2xl flex items-center justify-center">
        <FeaturePreview demo={step.demo} />
      </div>
    </div>
  </div>
);

// Completion Step Component
const CompletionStep: React.FC<{ roleContent: any; user: any }> = ({ roleContent, user }) => (
  <div className="text-center space-y-8">
    <div className="space-y-6">
      <div className="relative">
        <div className="w-20 h-20 bg-gradient-to-br from-green-600 to-blue-600 rounded-full flex items-center justify-center mx-auto">
          <CheckCircle className="w-10 h-10 text-white" />
        </div>
        <div className="absolute -inset-4 bg-green-400/20 rounded-full animate-pulse" />
      </div>
      
      <div>
        <h1 className="text-4xl font-bold text-white mb-3">You're All Set!</h1>
        <p className="text-xl text-green-400 mb-4">Welcome to the KARTAVYA Security Platform</p>
        <p className="text-gray-300 max-w-2xl mx-auto">
          You've completed the onboarding process. Your security operations center is ready to protect your organization with advanced AI-powered threat detection.
        </p>
      </div>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
      <div className="p-6 bg-gray-800/50 border border-gray-700 rounded-lg">
        <BookOpen className="w-8 h-8 text-blue-400 mx-auto mb-3" />
        <h3 className="font-semibold text-white mb-2">Documentation</h3>
        <p className="text-sm text-gray-400 mb-3">Explore comprehensive guides and tutorials</p>
        <button className="text-blue-400 hover:text-blue-300 text-sm font-medium">
          Browse Docs →
        </button>
      </div>
      
      <div className="p-6 bg-gray-800/50 border border-gray-700 rounded-lg">
        <HeadphonesIcon className="w-8 h-8 text-green-400 mx-auto mb-3" />
        <h3 className="font-semibold text-white mb-2">24/7 Support</h3>
        <p className="text-sm text-gray-400 mb-3">Get help whenever you need it</p>
        <button className="text-green-400 hover:text-green-300 text-sm font-medium">
          Contact Support →
        </button>
      </div>
    </div>

    <div className="flex items-center justify-center space-x-2 text-yellow-400">
      {[...Array(5)].map((_, i) => (
        <Star key={i} className="w-5 h-5 fill-current" />
      ))}
    </div>
    <p className="text-sm text-gray-400">Rated 5 stars by security professionals worldwide</p>
  </div>
);

// Feature Preview Component
const FeaturePreview: React.FC<{ demo: string }> = ({ demo }) => {
  const getDemoVisualization = () => {
    switch (demo) {
      case 'dashboard':
        return (
          <div className="w-full h-full p-8 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="p-4 bg-gray-700 rounded-lg">
                  <div className="w-full h-2 bg-gray-600 rounded mb-2" />
                  <div className="w-3/4 h-2 bg-blue-400 rounded" />
                </div>
              ))}
            </div>
            <div className="h-20 bg-gray-700 rounded-lg flex items-center justify-center">
              <Activity className="w-8 h-8 text-green-400 animate-pulse" />
            </div>
          </div>
        );
      case 'chat':
        return (
          <div className="w-full h-full p-8 space-y-4">
            <div className="flex justify-end">
              <div className="p-3 bg-blue-600 rounded-lg max-w-xs">
                <div className="w-20 h-2 bg-white/50 rounded" />
              </div>
            </div>
            <div className="flex justify-start">
              <div className="p-3 bg-gray-700 rounded-lg max-w-xs">
                <div className="w-24 h-2 bg-gray-400 rounded mb-1" />
                <div className="w-16 h-2 bg-gray-400 rounded" />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Brain className="w-5 h-5 text-purple-400 animate-pulse" />
              <div className="flex space-x-1">
                <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}} />
                <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}} />
              </div>
            </div>
          </div>
        );
      default:
        return (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center space-y-4">
              <Sparkles className="w-16 h-16 text-blue-400 mx-auto animate-pulse" />
              <p className="text-gray-400">Interactive Demo</p>
            </div>
          </div>
        );
    }
  };

  return getDemoVisualization();
};

export default OnboardingFlow;
