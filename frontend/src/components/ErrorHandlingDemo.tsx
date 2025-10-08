/**
 * Error Handling Demo Component
 * Comprehensive demonstration of error handling capabilities
 */

import React, { useState } from 'react';
import { 
  AlertTriangle, 
  Wifi, 
  Server, 
  Lock, 
  Clock, 
  Bug, 
  Zap, 
  Shield,
  Play,
  RefreshCw,
  CheckCircle
} from 'lucide-react';

import { useErrorDemo, ErrorTypes, ErrorType } from '../utils/errorDemo';
import { useNotifications } from './ui/NotificationSystem';
import { LoadingButton, InlineLoading } from './ui/LoadingStates';

const ErrorHandlingDemo: React.FC = () => {
  const [isTestingAll, setIsTestingAll] = useState(false);
  const [completedTests, setCompletedTests] = useState<Set<string>>(new Set());
  const { triggerError, testAllErrors, simulateSecurityAlert } = useErrorDemo();
  const { showInfo, clearAllNotifications } = useNotifications();

  const errorCategories = [
    {
      title: 'Network Errors',
      description: 'Connection and network-related failures',
      icon: <Wifi className="w-5 h-5" />,
      color: 'text-red-400',
      errors: [
        { 
          type: ErrorTypes.NETWORK_ERROR, 
          name: 'Network Failure',
          description: 'Simulate complete network connectivity loss'
        },
        { 
          type: ErrorTypes.TIMEOUT_ERROR, 
          name: 'Request Timeout',
          description: 'Simulate request taking too long to complete'
        }
      ]
    },
    {
      title: 'API Errors',
      description: 'Server and API response errors',
      icon: <Server className="w-5 h-5" />,
      color: 'text-yellow-400',
      errors: [
        { 
          type: ErrorTypes.API_ERROR_404, 
          name: '404 Not Found',
          description: 'Simulate resource not found error'
        },
        { 
          type: ErrorTypes.API_ERROR_500, 
          name: '500 Server Error',
          description: 'Simulate internal server error'
        },
        { 
          type: ErrorTypes.API_ERROR_429, 
          name: '429 Rate Limited',
          description: 'Simulate too many requests error'
        }
      ]
    },
    {
      title: 'Authentication Errors',
      description: 'Security and authorization failures',
      icon: <Lock className="w-5 h-5" />,
      color: 'text-purple-400',
      errors: [
        { 
          type: ErrorTypes.API_ERROR_401, 
          name: '401 Unauthorized',
          description: 'Simulate session expiry or invalid credentials'
        }
      ]
    },
    {
      title: 'Component Errors',
      description: 'Frontend component and rendering errors',
      icon: <Bug className="w-5 h-5" />,
      color: 'text-orange-400',
      errors: [
        { 
          type: ErrorTypes.COMPONENT_ERROR, 
          name: 'Component Crash',
          description: 'Simulate React component render failure'
        },
        { 
          type: ErrorTypes.ASYNC_ERROR, 
          name: 'Async Operation',
          description: 'Simulate async operation failure'
        }
      ]
    }
  ];

  const securityAlerts = [
    { severity: 'critical' as const, name: 'Critical Alert', color: 'bg-red-600' },
    { severity: 'high' as const, name: 'High Alert', color: 'bg-orange-600' },
    { severity: 'medium' as const, name: 'Medium Alert', color: 'bg-yellow-600' },
    { severity: 'low' as const, name: 'Low Alert', color: 'bg-blue-600' }
  ];

  const handleTriggerError = async (errorType: ErrorType, errorName: string) => {
    try {
      showInfo('Testing Error', `Triggering ${errorName}...`);
      await triggerError(errorType);
      setCompletedTests(prev => new Set([...prev, errorType]));
    } catch (error) {
      console.log(`Error ${errorName} triggered successfully`);
      setCompletedTests(prev => new Set([...prev, errorType]));
    }
  };

  const handleTestAllErrors = async () => {
    setIsTestingAll(true);
    try {
      await testAllErrors();
      setCompletedTests(new Set(Object.values(ErrorTypes)));
    } catch (error) {
      console.error('Error during bulk testing:', error);
    } finally {
      setIsTestingAll(false);
    }
  };

  const handleClearNotifications = () => {
    clearAllNotifications();
    setCompletedTests(new Set());
    showInfo('Cleared', 'All notifications and test results cleared');
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-3 mb-4">
          <Shield className="w-8 h-8 text-blue-400" />
          <h1 className="text-3xl font-bold text-white">SIEM Error Handling Demo</h1>
        </div>
        <p className="text-gray-300 max-w-2xl mx-auto">
          Comprehensive demonstration of error boundaries, user-friendly notifications, 
          loading states, and recovery mechanisms in the SIEM application.
        </p>
      </div>

      {/* Control Panel */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Zap className="w-5 h-5 text-yellow-400" />
          <span>Test Controls</span>
        </h2>
        
        <div className="flex flex-wrap gap-4">
          <LoadingButton
            loading={isTestingAll}
            onClick={handleTestAllErrors}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Play className="w-4 h-4" />
            Test All Errors
          </LoadingButton>
          
          <button
            onClick={handleClearNotifications}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Clear All</span>
          </button>

          <div className="flex items-center space-x-2 text-gray-300">
            <CheckCircle className="w-4 h-4 text-green-400" />
            <span>Completed: {completedTests.size} / {Object.keys(ErrorTypes).length}</span>
          </div>
        </div>

        {isTestingAll && (
          <div className="mt-4">
            <InlineLoading text="Running comprehensive error tests..." />
          </div>
        )}
      </div>

      {/* Error Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {errorCategories.map((category, categoryIndex) => (
          <div key={categoryIndex} className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className={`${category.color}`}>
                {category.icon}
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">{category.title}</h3>
                <p className="text-sm text-gray-400">{category.description}</p>
              </div>
            </div>

            <div className="space-y-3">
              {category.errors.map((error, errorIndex) => (
                <div key={errorIndex} className="bg-gray-900 border border-gray-600 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-white flex items-center space-x-2">
                      <span>{error.name}</span>
                      {completedTests.has(error.type) && (
                        <CheckCircle className="w-4 h-4 text-green-400" />
                      )}
                    </h4>
                    <button
                      onClick={() => handleTriggerError(error.type, error.name)}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-md transition-colors"
                      disabled={isTestingAll}
                    >
                      Test
                    </button>
                  </div>
                  <p className="text-sm text-gray-400">{error.description}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Security Alerts Demo */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-red-400" />
          <span>Security Alert Simulation</span>
        </h2>
        
        <p className="text-gray-400 mb-4">
          Test security-specific notifications with different severity levels
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {securityAlerts.map((alert, index) => (
            <button
              key={index}
              onClick={() => simulateSecurityAlert(alert.severity)}
              className={`${alert.color} hover:opacity-80 text-white p-4 rounded-lg transition-all transform hover:scale-105`}
            >
              <div className="text-center">
                <AlertTriangle className="w-6 h-6 mx-auto mb-2" />
                <span className="font-medium">{alert.name}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Features Overview */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Error Handling Features</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-gray-900 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-400 mb-2">Error Boundaries</h3>
            <p className="text-sm text-gray-300">
              Catch component errors and display user-friendly fallback UI
            </p>
          </div>
          
          <div className="bg-gray-900 p-4 rounded-lg">
            <h3 className="font-semibold text-green-400 mb-2">Toast Notifications</h3>
            <p className="text-sm text-gray-300">
              Contextual error messages with actions and automatic dismissal
            </p>
          </div>
          
          <div className="bg-gray-900 p-4 rounded-lg">
            <h3 className="font-semibold text-purple-400 mb-2">Retry Logic</h3>
            <p className="text-sm text-gray-300">
              Automatic retry with exponential backoff for recoverable errors
            </p>
          </div>
          
          <div className="bg-gray-900 p-4 rounded-lg">
            <h3 className="font-semibold text-yellow-400 mb-2">Loading States</h3>
            <p className="text-sm text-gray-300">
              Skeleton screens and spinners during data loading
            </p>
          </div>
          
          <div className="bg-gray-900 p-4 rounded-lg">
            <h3 className="font-semibold text-red-400 mb-2">Connection Monitoring</h3>
            <p className="text-sm text-gray-300">
              Real-time network status with offline handling
            </p>
          </div>
          
          <div className="bg-gray-900 p-4 rounded-lg">
            <h3 className="font-semibold text-orange-400 mb-2">Error Recovery</h3>
            <p className="text-sm text-gray-300">
              Multiple recovery options and graceful degradation
            </p>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Testing Instructions</h2>
        <ol className="text-gray-300 space-y-2">
          <li className="flex items-start space-x-2">
            <span className="text-blue-400 font-bold">1.</span>
            <span>Click individual "Test" buttons to trigger specific error scenarios</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-400 font-bold">2.</span>
            <span>Use "Test All Errors" to run a comprehensive error simulation</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-400 font-bold">3.</span>
            <span>Try the security alert buttons to see specialized notifications</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-400 font-bold">4.</span>
            <span>Observe the toast notifications in the top-right corner</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-400 font-bold">5.</span>
            <span>Check the browser console for detailed error logging</span>
          </li>
        </ol>
      </div>
    </div>
  );
};

export default ErrorHandlingDemo;
