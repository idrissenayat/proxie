"use client";

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Custom hook for handling errors in components
 */
export function useErrorHandler() {
  const [error, setError] = useState(null);
  const router = useRouter();

  const handleError = useCallback((err) => {
    console.error('Error caught:', err);
    setError(err);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      setError(null);
    }, 5000);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const handleAPIError = useCallback((err) => {
    const statusCode = err?.response?.status;
    
    // Handle specific error codes
    if (statusCode === 401) {
      // Redirect to sign in
      router.push('/sign-in');
      return;
    }
    
    if (statusCode === 403) {
      // Show access denied message
      handleError(new Error('You don\'t have permission to perform this action.'));
      return;
    }
    
    if (statusCode === 404) {
      // Show not found message
      handleError(new Error('The requested resource was not found.'));
      return;
    }
    
    if (statusCode === 429) {
      // Show rate limit message
      handleError(new Error('Too many requests. Please wait a moment and try again.'));
      return;
    }
    
    // Generic error
    handleError(err);
  }, [handleError, router]);

  return {
    error,
    handleError,
    handleAPIError,
    clearError
  };
}

/**
 * Hook for async error handling
 */
export function useAsyncErrorHandler() {
  const { handleError, handleAPIError } = useErrorHandler();

  const execute = useCallback(async (asyncFn, onSuccess, onError) => {
    try {
      const result = await asyncFn();
      if (onSuccess) {
        onSuccess(result);
      }
      return result;
    } catch (err) {
      if (onError) {
        onError(err);
      } else {
        handleAPIError(err);
      }
      throw err;
    }
  }, [handleError, handleAPIError]);

  return { execute };
}
