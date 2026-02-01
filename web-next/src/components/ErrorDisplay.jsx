"use client";

import React from 'react';
import { AlertTriangle, X, RefreshCw } from 'lucide-react';

/**
 * Inline error display component for API errors
 */
export function ErrorDisplay({ error, onDismiss, onRetry, className = "" }) {
  if (!error) return null;

  const errorMessage = error?.response?.data?.detail || error?.message || 'An error occurred';
  const statusCode = error?.response?.status;

  return (
    <div className={`p-4 bg-red-500/10 border border-red-500/20 rounded-lg ${className}`}>
      <div className="flex items-start gap-3">
        <AlertTriangle size={20} className="text-red-500 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-red-400 text-sm font-medium mb-1">
            {statusCode === 404 ? 'Not Found' :
             statusCode === 403 ? 'Access Denied' :
             statusCode === 401 ? 'Authentication Required' :
             statusCode === 429 ? 'Rate Limit Exceeded' :
             'Error'}
          </p>
          <p className="text-zinc-400 text-sm">
            {errorMessage}
          </p>
        </div>
        <div className="flex gap-2">
          {onRetry && (
            <button
              onClick={onRetry}
              className="p-1 hover:bg-red-500/20 rounded transition-colors"
              title="Retry"
            >
              <RefreshCw size={16} className="text-red-400" />
            </button>
          )}
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="p-1 hover:bg-red-500/20 rounded transition-colors"
              title="Dismiss"
            >
              <X size={16} className="text-red-400" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Loading error component for failed data fetching
 */
export function LoadingError({ error, onRetry, title = "Failed to Load" }) {
  return (
    <div className="min-h-[400px] flex flex-col items-center justify-center p-8 text-center">
      <AlertTriangle size={48} className="text-red-500 mb-4" />
      <h2 className="text-xl font-black text-white mb-2">{title}</h2>
      <p className="text-zinc-500 mb-6">
        {error?.response?.data?.detail || error?.message || 'An error occurred while loading data.'}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-6 py-3 bg-zinc-900 hover:bg-zinc-800 rounded-2xl font-bold text-white cursor-pointer flex items-center gap-2 transition-colors"
        >
          <RefreshCw size={20} />
          Try Again
        </button>
      )}
    </div>
  );
}

/**
 * Network error component
 */
export function NetworkError({ onRetry }) {
  return (
    <div className="min-h-[400px] flex flex-col items-center justify-center p-8 text-center">
      <AlertTriangle size={48} className="text-yellow-500 mb-4" />
      <h2 className="text-xl font-black text-white mb-2">Connection Problem</h2>
      <p className="text-zinc-500 mb-6">
        Unable to connect to the server. Please check your internet connection.
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-6 py-3 bg-zinc-900 hover:bg-zinc-800 rounded-2xl font-bold text-white cursor-pointer flex items-center gap-2 transition-colors"
        >
          <RefreshCw size={20} />
          Retry Connection
        </button>
      )}
    </div>
  );
}
