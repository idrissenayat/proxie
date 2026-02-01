# Sentry Integration Setup Guide

**Status:** ✅ Implemented  
**Date:** January 30, 2026

---

## Overview

Sentry error tracking has been integrated into the Proxie Next.js frontend. This provides comprehensive error monitoring, performance tracking, and session replay capabilities.

---

## What's Implemented

### ✅ Configuration Files
- `sentry.client.config.js` - Client-side error tracking
- `sentry.server.config.js` - Server-side error tracking  
- `sentry.edge.config.js` - Edge runtime error tracking
- `next.config.mjs` - Sentry webpack plugin integration

### ✅ Error Tracking
- **Error Boundaries** - React component errors captured
- **Global Error Page** - Next.js error page errors captured
- **API Errors** - 5xx and unexpected errors from API calls captured

### ✅ Features Enabled
- Browser tracing for performance monitoring
- Session replay for debugging user sessions
- Source map upload for readable stack traces
- Automatic error filtering (development mode)

---

## Setup Instructions

### 1. Get Sentry DSN

1. Sign up at [sentry.io](https://sentry.io)
2. Create a new project (select "Next.js")
3. Copy your DSN from project settings

### 2. Configure Environment Variables

Add to your `.env.local` file:

```bash
# Sentry DSN (required)
NEXT_PUBLIC_SENTRY_DSN=https://your-key@sentry.io/your-project-id

# Optional: Enable Sentry in development
NEXT_PUBLIC_SENTRY_DEBUG=false

# Optional: For source map uploads during build
SENTRY_ORG=your-org-slug
SENTRY_PROJECT=your-project-slug

# Optional: Auth token for source maps (get from Sentry settings)
SENTRY_AUTH_TOKEN=your-auth-token
```

### 3. Build and Deploy

```bash
# Install dependencies (if not already done)
npm install

# Build the application
npm run build

# Source maps will be uploaded automatically if SENTRY_ORG and SENTRY_PROJECT are set
```

---

## How It Works

### Error Boundaries
When a React component throws an error, `ErrorBoundary.jsx` catches it and:
1. Displays a user-friendly error UI
2. Sends error details to Sentry with React context
3. Includes component stack trace

### Global Error Page
When Next.js encounters an unhandled error, `error.js`:
1. Displays the error fallback UI
2. Sends error to Sentry
3. Provides reset functionality

### API Error Tracking
The Axios interceptor in `api.js`:
1. Catches API errors (5xx and unexpected errors)
2. Sends to Sentry with request context
3. Includes URL, method, and response data

---

## Configuration Details

### Client Configuration (`sentry.client.config.js`)
- **Traces Sample Rate:** 10% in production, 100% in development
- **Session Replay:** Enabled with text masking and media blocking
- **Debug Mode:** Enabled in development (if `NEXT_PUBLIC_SENTRY_DEBUG=true`)

### Server Configuration (`sentry.server.config.js`)
- **Traces Sample Rate:** 10% in production, 100% in development
- **Error Filtering:** Development errors filtered unless debug mode enabled

### Edge Configuration (`sentry.edge.config.js`)
- Same as server configuration
- Used for middleware and edge routes

---

## Testing

### Test Error Boundary
1. Create a test component that throws an error
2. Verify error is caught and displayed
3. Check Sentry dashboard for error report

### Test API Errors
1. Make an API call that returns 500 error
2. Verify error is logged to console
3. Check Sentry dashboard for error report

### Test in Development
By default, Sentry is disabled in development. To enable:
```bash
NEXT_PUBLIC_SENTRY_DEBUG=true npm run dev
```

---

## Monitoring

### Sentry Dashboard
- **Issues:** View all errors grouped by type
- **Performance:** Monitor API response times
- **Replays:** Watch user sessions that led to errors
- **Releases:** Track deployments and error rates

### Key Metrics
- Error rate by endpoint
- Error rate by user
- Performance by route
- Session replay for debugging

---

## Best Practices

### 1. Don't Send Sensitive Data
- Sentry automatically filters common sensitive fields
- Review `beforeSend` hooks if needed
- Use `tags` and `extra` for non-sensitive context

### 2. Use Tags for Filtering
Errors are tagged with:
- `errorBoundary: true` - React component errors
- `errorPage: true` - Next.js error page errors
- `apiError: true` - API errors
- `statusCode: <code>` - HTTP status codes

### 3. Monitor Production Only
- Development errors are filtered by default
- Set `NEXT_PUBLIC_SENTRY_DEBUG=true` only when testing
- Use separate Sentry projects for staging/production

---

## Troubleshooting

### Errors Not Appearing in Sentry

1. **Check DSN:** Verify `NEXT_PUBLIC_SENTRY_DSN` is set correctly
2. **Check Environment:** Errors are filtered in development by default
3. **Check Console:** Look for Sentry initialization errors
4. **Check Network:** Verify Sentry API is accessible

### Source Maps Not Working

1. **Check Build:** Source maps must be generated during build
2. **Check Auth:** Verify `SENTRY_AUTH_TOKEN` is set
3. **Check Org/Project:** Verify `SENTRY_ORG` and `SENTRY_PROJECT` match Sentry dashboard

### Performance Issues

1. **Reduce Sample Rate:** Lower `tracesSampleRate` if needed
2. **Disable Replay:** Set `replaysSessionSampleRate: 0` if not needed
3. **Filter Events:** Use `beforeSend` to filter unnecessary events

---

## Files Modified

```
web-next/
├── sentry.client.config.js      ✅ New
├── sentry.server.config.js      ✅ New
├── sentry.edge.config.js        ✅ New
├── next.config.mjs              ✅ Updated
├── src/
│   ├── components/
│   │   └── ErrorBoundary.jsx    ✅ Updated
│   ├── app/
│   │   └── error.js             ✅ Updated
│   └── lib/
│       └── api.js                ✅ Updated
└── package.json                  ✅ Updated (@sentry/nextjs added)
```

---

## Next Steps

1. **Set up Sentry account** and get DSN
2. **Configure environment variables** in `.env.local`
3. **Test error tracking** by triggering test errors
4. **Set up alerts** in Sentry dashboard for critical errors
5. **Monitor error rates** and performance metrics

---

## References

- [Sentry Next.js Documentation](https://docs.sentry.io/platforms/javascript/guides/nextjs/)
- [Sentry React Error Boundaries](https://docs.sentry.io/platforms/javascript/guides/react/components/errorboundary/)
- [Sentry Session Replay](https://docs.sentry.io/platforms/javascript/session-replay/)

---

**Status:** ✅ **IMPLEMENTATION COMPLETE**
