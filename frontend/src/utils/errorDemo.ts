/**
 * Error Demo Utilities
 * For testing error handling capabilities
 */

import { useState, useCallback } from 'react';

export enum ErrorTypes {
  API_ERROR = 'api_error',
  NETWORK_ERROR = 'network_error',
  VALIDATION_ERROR = 'validation_error',
  AUTHENTICATION_ERROR = 'authentication_error',
  PERMISSION_ERROR = 'permission_error',
  TIMEOUT_ERROR = 'timeout_error',
  GENERIC_ERROR = 'generic_error'
}

export interface ErrorDemoState {
  isLoading: boolean;
  error: string | null;
  successCount: number;
  errorCount: number;
}

export const useErrorDemo = () => {
  const [state, setState] = useState<ErrorDemoState>({
    isLoading: false,
    error: null,
    successCount: 0,
    errorCount: 0
  });

  const simulateError = useCallback(async (errorType: ErrorTypes) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    const errorMessages = {
      [ErrorTypes.API_ERROR]: 'API endpoint returned an unexpected error',
      [ErrorTypes.NETWORK_ERROR]: 'Network connection failed',
      [ErrorTypes.VALIDATION_ERROR]: 'Input validation failed',
      [ErrorTypes.AUTHENTICATION_ERROR]: 'Authentication token expired',
      [ErrorTypes.PERMISSION_ERROR]: 'Insufficient permissions to access resource',
      [ErrorTypes.TIMEOUT_ERROR]: 'Request timed out after 30 seconds',
      [ErrorTypes.GENERIC_ERROR]: 'An unexpected error occurred'
    };

    setState(prev => ({
      ...prev,
      isLoading: false,
      error: errorMessages[errorType],
      errorCount: prev.errorCount + 1
    }));
  }, []);

  const simulateSuccess = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 800));

    setState(prev => ({
      ...prev,
      isLoading: false,
      successCount: prev.successCount + 1
    }));
  }, []);

  const clearState = useCallback(() => {
    setState({
      isLoading: false,
      error: null,
      successCount: 0,
      errorCount: 0
    });
  }, []);

  return {
    ...state,
    simulateError,
    simulateSuccess,
    clearState
  };
};
