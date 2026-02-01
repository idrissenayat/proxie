"use client";

import { useEffect } from 'react';
import { ErrorFallback } from '@/components/ErrorBoundary';

/**
 * Global error page for Next.js App Router
 * This catches errors that escape ErrorBoundary
 */
export default function Error({ error, reset }) {
  useEffect(() => {
    // Log error to error reporting service
    console.error('Global error caught:', error);
    
    // Send to Sentry error reporting service
    if (typeof window !== 'undefined') {
      import('@sentry/nextjs').then((Sentry) => {
        Sentry.captureException(error, {
          tags: {
            errorPage: true,
          },
        });
      }).catch((sentryError) => {
        // Silently fail if Sentry is not available
        console.warn('Failed to send error to Sentry:', sentryError);
      });
    }
  }, [error]);

  return (
    <ErrorFallback 
      error={error} 
      onReset={reset}
      showDetails={process.env.NODE_ENV === 'development'}
    />
  );
}
