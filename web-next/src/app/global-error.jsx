"use client";

import { ErrorFallback } from '@/components/ErrorBoundary';

/**
 * Global error handler for root layout errors
 * This is a fallback for errors in the root layout itself
 */
export default function GlobalError({ error, reset }) {
  return (
    <html lang="en">
      <body className="bg-black antialiased text-white">
        <ErrorFallback 
          error={error} 
          onReset={reset}
          showDetails={process.env.NODE_ENV === 'development'}
        />
      </body>
    </html>
  );
}
