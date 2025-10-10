/**
 * KARTAVYA SIEM - Guided Tour Component
 * Step-by-step interactive tutorial for new users showcasing all features
 */

import React, { useState } from 'react';
import { 
  ArrowRight, ArrowLeft, Play, CheckCircle, BookOpen, 
  MessageSquare, Brain, Shield, BarChart3, Globe, Target,
  Eye, Zap, AlertTriangle
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import SimpleDashboard from '../SimpleDashboard/SimpleDashboard';
import EntityRecognitionDemo from '../EntityRecognitionDemo/EntityRecognitionDemo';

interface TourStep {
  id: string;
  title: string;
  description: string;
  content: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const GuidedTour: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const navigate = useNavigate();

  const markStepComplete = (stepId: string) => {
    if (!completedSteps.includes(stepId)) {
      setCompletedSteps([...completedSteps, stepId]);
    }
  };

  const tourSteps: TourStep[] = [
    {
      id: 'welcome',
      title: '🚀 Welcome to KARTAVYA SIEM',
      description: 'Your intelligent security information and event management platform',
      content: (
        <div className="text-center py-12">
          <div className="mb-8">
            <div className="w-24 h-24 bg-gradient-to-r from-blue-600 to-blue-500 rounded-2xl mx-auto flex items-center justify-center shadow-xl">
              <Shield className="w-12 h-12 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-white mb-4">Welcome to KARTAVYA</h2>
          <p className="text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
            KARTAVYA is an advanced conversational SIEM platform that combines AI-powered chat interfaces 
            with intelligent threat detection, entity recognition, and automated security analysis.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <MessageSquare className="w-8 h-8 text-blue-400 mx-auto mb-3" />
              <h3 className="font-semibold text-white mb-2">Conversational Interface</h3>
              <p className="text-sm text-gray-400">Chat naturally about security events and get intelligent responses</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <Brain className="w-8 h-8 text-green-400 mx-auto mb-3" />
              <h3 className="font-semibold text-white mb-2">AI Entity Recognition</h3>
              <p className="text-sm text-gray-400">Automatically detect and analyze security entities like IPs, domains, CVEs</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <Shield className="w-8 h-8 text-purple-400 mx-auto mb-3" />
              <h3 className="font-semibold text-white mb-2">Threat Intelligence</h3>
              <p className="text-sm text-gray-400">Real-time threat intelligence integration for enhanced context</p>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'dashboard_overview',
      title: '📊 Feature Dashboard Overview',
      description: 'Explore all the advanced visualization and analysis components',
      content: (
        <div className="h-[600px] overflow-y-auto rounded-lg border border-gray-700">
          <SimpleDashboard />
        </div>
      ),
      action: {
        label: 'Try Live Entity Test',
        onClick: () => {
          // This will be handled by the dashboard component
          console.log('Scrolling to entity test section');
        }
      }
    },
    {
      id: 'entity_recognition',
      title: '🧠 Advanced Entity Recognition',
      description: 'See how KARTAVYA automatically detects and analyzes security entities',
      content: (
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <Brain className="w-6 h-6 text-green-400 mr-2" />
              What is Entity Recognition?
            </h3>
            <p className="text-gray-300 mb-4">
              Entity Recognition automatically identifies and extracts security-relevant entities from text, such as:
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { icon: Globe, label: 'IP Addresses', color: 'text-blue-400' },
                { icon: Globe, label: 'Domains', color: 'text-green-400' },
                { icon: AlertTriangle, label: 'CVE IDs', color: 'text-red-400' },
                { icon: Target, label: 'MITRE Techniques', color: 'text-yellow-400' },
                { icon: Shield, label: 'File Hashes', color: 'text-purple-400' },
                { icon: Eye, label: 'Email Addresses', color: 'text-cyan-400' },
                { icon: BarChart3, label: 'Process Names', color: 'text-orange-400' },
                { icon: Zap, label: 'Registry Keys', color: 'text-pink-400' }
              ].map((item, index) => (
                <div key={index} className="bg-gray-900/50 rounded-lg p-3 text-center">
                  <item.icon className={`w-6 h-6 mx-auto mb-2 ${item.color}`} />
                  <div className="text-xs text-gray-300">{item.label}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-6">
            <h4 className="font-semibold text-blue-300 mb-3">✨ Enhanced with Threat Intelligence</h4>
            <p className="text-gray-300 text-sm">
              Each detected entity is automatically enriched with real-time threat intelligence data including:
            </p>
            <ul className="list-disc list-inside text-gray-300 text-sm mt-2 space-y-1">
              <li>Reputation scoring (Malicious/Suspicious/Clean/Unknown)</li>
              <li>Geo-location data and ISP information</li>
              <li>Malware family associations and campaign attribution</li>
              <li>First/last seen timestamps and confidence scores</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      id: 'entity_demo',
      title: '🧪 Interactive Entity Testing',
      description: 'Test entity recognition with real examples and see threat intelligence in action',
      content: (
        <div className="h-[600px] overflow-y-auto rounded-lg border border-gray-700">
          <EntityRecognitionDemo />
        </div>
      ),
      action: {
        label: 'Test a Demo Query',
        onClick: () => {
          console.log('Try testing one of the demo queries');
        }
      }
    },
    {
      id: 'chat_interface',
      title: '💬 Conversational SIEM Interface',
      description: 'Learn about the main chat interface where all the magic happens',
      content: (
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <MessageSquare className="w-6 h-6 text-blue-400 mr-2" />
              Main Chat Interface Features
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-white mb-3">🎯 Smart Conversations</h4>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li className="flex items-start">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                    Natural language queries about security events
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                    Automatic entity detection in responses
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                    Context-aware smart actions for investigation
                  </li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-3">⚡ Enhanced Intelligence</h4>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li className="flex items-start">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                    Real-time threat intelligence enrichment
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                    Interactive entity cards with detailed info
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                    Progressive investigation workflow
                  </li>
                </ul>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h4 className="font-semibold text-white mb-3">🏗️ Three-Column Layout</h4>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-900/50 rounded p-4 text-center">
                <div className="font-medium text-blue-400 mb-2">Left Sidebar</div>
                <div className="text-xs text-gray-400">Quick actions & recent investigations</div>
              </div>
              <div className="bg-gray-900/50 rounded p-4 text-center">
                <div className="font-medium text-green-400 mb-2">Chat Console</div>
                <div className="text-xs text-gray-400">Main conversation interface</div>
              </div>
              <div className="bg-gray-900/50 rounded p-4 text-center">
                <div className="font-medium text-purple-400 mb-2">Context Panel</div>
                <div className="text-xs text-gray-400">Query preview & investigation context</div>
              </div>
            </div>
          </div>

          <div className="bg-green-900/20 border border-green-700/50 rounded-lg p-6">
            <h4 className="font-semibold text-green-300 mb-3">🚀 Ready to Get Started?</h4>
            <p className="text-gray-300 text-sm mb-4">
              The main chat interface integrates all the features you've seen in this tour. Try asking questions like:
            </p>
            <div className="space-y-2">
              {[
                "Show me failed logins from 192.168.1.100",
                "Any malware activity in the last 24 hours?", 
                "Check for CVE-2024-1234 exploitation attempts",
                "Analyze traffic to suspicious-domain.com"
              ].map((query, index) => (
                <div key={index} className="bg-gray-800/50 rounded px-3 py-2 font-mono text-sm text-gray-300">
                  "{query}"
                </div>
              ))}
            </div>
          </div>
        </div>
      ),
      action: {
        label: 'Go to Chat Interface',
        onClick: () => navigate('/console')
      }
    },
    {
      id: 'complete',
      title: '🎉 Tour Complete!',
      description: 'You\'re ready to use KARTAVYA SIEM like a pro',
      content: (
        <div className="text-center py-12">
          <div className="mb-8">
            <div className="w-24 h-24 bg-gradient-to-r from-green-600 to-green-500 rounded-2xl mx-auto flex items-center justify-center shadow-xl">
              <CheckCircle className="w-12 h-12 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-white mb-4">Congratulations! 🎉</h2>
          <p className="text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
            You've completed the KARTAVYA SIEM guided tour! You now know how to use advanced entity recognition, 
            threat intelligence, and conversational security analysis.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto mb-8">
            <button
              onClick={() => navigate('/console')}
              className="bg-blue-600 hover:bg-blue-700 text-white p-6 rounded-lg transition-colors"
            >
              <MessageSquare className="w-8 h-8 mx-auto mb-3" />
              <h3 className="font-semibold mb-2">Start Investigating</h3>
              <p className="text-sm text-blue-100">Jump into the main chat interface</p>
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-purple-600 hover:bg-purple-700 text-white p-6 rounded-lg transition-colors"
            >
              <Play className="w-8 h-8 mx-auto mb-3" />
              <h3 className="font-semibold mb-2">Explore Features</h3>
              <p className="text-sm text-purple-100">Return to the feature dashboard</p>
            </button>
          </div>

          <div className="text-sm text-gray-400">
            💡 Tip: You can always return to this guided tour from the sidebar navigation
          </div>
        </div>
      )
    }
  ];

  const nextStep = () => {
    markStepComplete(tourSteps[currentStep].id);
    if (currentStep < tourSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const goToStep = (stepIndex: number) => {
    setCurrentStep(stepIndex);
  };

  const currentTourStep = tourSteps[currentStep];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="flex h-screen">
        {/* Tour Sidebar */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col">
          <div className="p-6 border-b border-gray-700">
            <h1 className="text-xl font-bold text-white flex items-center">
              <BookOpen className="w-6 h-6 text-blue-400 mr-2" />
              Guided Tour
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              Step {currentStep + 1} of {tourSteps.length}
            </p>
          </div>
          
          {/* Progress Steps */}
          <div className="flex-1 p-6 overflow-y-auto">
            <div className="space-y-3">
              {tourSteps.map((step, index) => {
                const isCompleted = completedSteps.includes(step.id);
                const isCurrent = currentStep === index;
                const isAccessible = index <= currentStep;
                
                return (
                  <button
                    key={step.id}
                    onClick={() => isAccessible && goToStep(index)}
                    disabled={!isAccessible}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      isCurrent 
                        ? 'bg-blue-600 text-white border border-blue-500' 
                        : isCompleted
                        ? 'bg-green-900/30 text-green-300 border border-green-700/30 hover:bg-green-900/40'
                        : isAccessible
                        ? 'bg-gray-700 text-gray-300 hover:bg-gray-600 border border-gray-600'
                        : 'bg-gray-800 text-gray-500 border border-gray-700 cursor-not-allowed'
                    }`}
                  >
                    <div className="flex items-center">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center mr-3 ${
                        isCompleted 
                          ? 'bg-green-600 text-white' 
                          : isCurrent 
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-600 text-gray-400'
                      }`}>
                        {isCompleted ? (
                          <CheckCircle className="w-4 h-4" />
                        ) : (
                          <span className="text-xs font-medium">{index + 1}</span>
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-sm">{step.title}</div>
                        <div className="text-xs mt-1 opacity-80">{step.description}</div>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
          
          {/* Navigation Buttons */}
          <div className="p-6 border-t border-gray-700">
            <div className="flex space-x-3">
              <button
                onClick={prevStep}
                disabled={currentStep === 0}
                className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-500 text-white text-sm rounded transition-colors flex items-center justify-center"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Previous
              </button>
              <button
                onClick={nextStep}
                disabled={currentStep === tourSteps.length - 1}
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-800 disabled:text-gray-500 text-white text-sm rounded transition-colors flex items-center justify-center"
              >
                Next
                <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </div>
            
            {currentTourStep.action && (
              <button
                onClick={currentTourStep.action.onClick}
                className="w-full mt-3 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
              >
                {currentTourStep.action.label}
              </button>
            )}
          </div>
        </div>

        {/* Tour Content */}
        <div className="flex-1 overflow-hidden">
          <div className="h-full overflow-y-auto p-8">
            <div className="max-w-6xl mx-auto">
              <div className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">
                  {currentTourStep.title}
                </h1>
                <p className="text-gray-400 text-lg">
                  {currentTourStep.description}
                </p>
              </div>
              
              <div className="bg-gray-900 rounded-lg border border-gray-700">
                {currentTourStep.content}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GuidedTour;
