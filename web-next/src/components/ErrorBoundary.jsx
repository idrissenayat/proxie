"use client";

import React from 'react';
import { AlertTriangle, RefreshCw, Home, Bug, ChevronLeft } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null,
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to console and error reporting service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });

    // Send to Sentry error reporting service
    if (typeof window !== 'undefined') {
      import('@sentry/nextjs').then((Sentry) => {
        Sentry.captureException(error, {
          contexts: {
            react: {
              componentStack: errorInfo?.componentStack,
            },
          },
          tags: {
            errorBoundary: true,
          },
        });
      }).catch((sentryError) => {
        // Silently fail if Sentry is not available
        console.warn('Failed to send error to Sentry:', sentryError);
      });
    }
  }

  handleReset = () => {
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null 
    });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleReset);
      }

      // Default fallback UI
      return (
        <ErrorFallback 
          error={this.state.error} 
          onReset={this.handleReset}
          showDetails={this.props.showDetails || false}
        />
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

/**
 * Default error fallback component
 */
export function ErrorFallback({ error, onReset, showDetails = false }) {
  const isDevelopment = process.env.NODE_ENV === 'development';

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center p-8 text-center">
      <div className="max-w-md w-full">
        <div className="mb-6 flex justify-center">
          <div className="p-4 bg-red-500/10 rounded-full">
            <AlertTriangle size={48} className="text-red-500" />
          </div>
        </div>
        
        <h1 className="text-2xl font-black text-white mb-2">
          Something went wrong
        </h1>
        
        <p className="text-zinc-400 mb-6">
          We're sorry, but something unexpected happened. Please try refreshing the page.
        </p>

        {showDetails && error && (
          <div className="mb-6 p-4 bg-zinc-900 rounded-lg text-left">
            <p className="text-sm text-red-400 font-mono mb-2">
              {error.toString()}
            </p>
            {isDevelopment && error.stack && (
              <pre className="text-xs text-zinc-500 overflow-auto max-h-40">
                {error.stack}
              </pre>
            )}
          </div>
        )}

        <div className="flex flex-col gap-3">
          <button
            onClick={onReset}
            className="px-6 py-3 bg-zinc-900 hover:bg-zinc-800 rounded-2xl font-bold text-white cursor-pointer flex items-center justify-center gap-2 transition-colors"
          >
            <RefreshCw size={20} />
            Try Again
          </button>
          
          <button
            onClick={() => {
              if (typeof window !== 'undefined') {
                window.location.href = '/';
              }
            }}
            className="px-6 py-3 bg-zinc-800 hover:bg-zinc-700 rounded-2xl font-bold text-white cursor-pointer flex items-center justify-center gap-2 transition-colors"
          >
            <Home size={20} />
            Go Home
          </button>

          {isDevelopment && (
            <button
              onClick={() => {
                if (typeof window !== 'undefined') {
                  console.error('Full error details:', error);
                  alert('Error details logged to console');
                }
              }}
              className="px-6 py-2 text-sm text-zinc-500 hover:text-zinc-400 flex items-center justify-center gap-2"
            >
              <Bug size={16} />
              Show Error Details (Dev)
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * API Error Fallback Component
 */
export function APIErrorFallback({ error, onRetry, onGoBack }) {
  const errorMessage = error?.response?.data?.detail || error?.message || 'An error occurred';
  const statusCode = error?.response?.status;

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center p-8 text-center">
      <div className="max-w-md w-full">
        <div className="mb-6 flex justify-center">
          <div className="p-4 bg-red-500/10 rounded-full">
            <AlertTriangle size={48} className="text-red-500" />
          </div>
        </div>
        
        <h1 className="text-2xl font-black text-white mb-2">
          {statusCode === 404 ? 'Not Found' : 
           statusCode === 403 ? 'Access Denied' :
           statusCode === 401 ? 'Authentication Required' :
           statusCode === 429 ? 'Too Many Requests' :
           'Request Failed'}
        </h1>
        
        <p className="text-zinc-400 mb-6">
          {statusCode === 404 ? 'The resource you\'re looking for doesn\'t exist.' :
           statusCode === 403 ? 'You don\'t have permission to access this resource.' :
           statusCode === 401 ? 'Please sign in to continue.' :
           statusCode === 429 ? 'Too many requests. Please wait a moment and try again.' :
           errorMessage}
        </p>

        <div className="flex flex-col gap-3">
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-6 py-3 bg-zinc-900 hover:bg-zinc-800 rounded-2xl font-bold text-white cursor-pointer flex items-center justify-center gap-2 transition-colors"
            >
              <RefreshCw size={20} />
              Retry
            </button>
          )}
          
          {onGoBack && (
            <button
              onClick={onGoBack}
              className="px-6 py-3 bg-zinc-800 hover:bg-zinc-700 rounded-2xl font-bold text-white cursor-pointer flex items-center justify-center gap-2 transition-colors"
            >
              <ChevronLeft size={20} />
              Go Back
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
