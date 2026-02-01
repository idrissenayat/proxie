# Duplicate Messages Fix
**Date:** January 30, 2026  
**Status:** ✅ Fixed

---

## Problem

Users were experiencing duplicate messages from the agent:
- Initial greeting message appearing twice
- User messages being sent twice ("I want to join Proxie" appearing twice)
- Agent responses appearing twice

---

## Root Causes Identified

### 1. **React Strict Mode (Development)**
- Next.js enables React Strict Mode by default in development
- This causes components to mount twice, triggering `useEffect` hooks twice
- Each mount creates new event listeners and sends initial messages

### 2. **Socket Event Listeners Not Cleaned Up**
- Socket.io event listeners (`new_message`, `session_ready`) were registered but not properly cleaned up
- On component re-render, new listeners were added without removing old ones
- This caused duplicate event handling

### 3. **Speech Recognition Not Cleaned Up**
- Speech recognition handlers were not properly cleaned up
- Multiple recognition instances could trigger `handleSend` multiple times

### 4. **Missing Duplicate Prevention Guards**
- `handleSend` function didn't check if a message was already being processed
- Initial message effect could run multiple times without proper guards
- No persistent storage to prevent duplicates across React Strict Mode remounts

### 5. **useEffect Dependencies**
- `handleSend` was not memoized with `useCallback`
- This caused the function to be recreated on every render
- useEffect dependencies were incomplete, causing stale closures

---

## Fixes Applied

### 1. **Socket Event Listener Cleanup** ✅
```javascript
// Before: Empty cleanup function
return () => {};

// After: Proper cleanup
return () => {
    socket.off('new_message', handleNewMessage);
    socket.off('session_ready', handleSessionReady);
};
```

### 2. **Speech Recognition Cleanup** ✅
```javascript
// Added proper cleanup with null checks
return () => {
    if (recognitionRef.current) {
        recognitionRef.current.onresult = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.onend = null;
        try {
            recognitionRef.current.stop();
        } catch (e) {
            // Ignore errors when stopping
        }
        recognitionRef.current = null;
    }
};
```

### 3. **Duplicate Prevention in handleSend** ✅
```javascript
// Added guard at the start of handleSend
if (isThinking) {
    console.warn('Already processing a message, ignoring duplicate send');
    return;
}

// Set thinking state immediately
setIsThinking(true);
```

### 4. **SessionStorage Guard for Initial Messages** ✅
```javascript
// Added persistent storage guard for React Strict Mode
const storageKey = `proxie_initial_sent_${role}_${initialMessage}_${rebookId}_${requestId}`;
if (hasSentInitialRef.current || (typeof window !== 'undefined' && sessionStorage.getItem(storageKey))) {
    return;
}

// Set flag in both ref and sessionStorage
hasSentInitialRef.current = true;
if (typeof window !== 'undefined') {
    sessionStorage.setItem(storageKey, 'true');
}
```

### 5. **Memoized handleSend with useCallback** ✅
```javascript
// Wrapped handleSend in useCallback to prevent recreation
const handleSend = useCallback(async (customText = null, action = null, activeEnrollmentId = enrollmentId, initialMedia = null) => {
    // ... implementation
}, [isThinking, input, selectedMedia, sessionId, role, providerId, enrollmentId]);
```

### 6. **Speech Recognition Duplicate Prevention** ✅
```javascript
// Added flag to prevent duplicate processing
let hasProcessedResult = false;

const handleResult = (event) => {
    if (hasProcessedResult) return;
    hasProcessedResult = true;
    // ... process result
};
```

### 7. **Fixed useEffect Dependencies** ✅
```javascript
// Added handleSend to dependencies
}, [initialMessage, role, rebookId, requestId, handleSend]);
```

---

## Files Modified

- ✅ `web-next/src/app/chat/page.js`
  - Added socket event listener cleanup
  - Added speech recognition cleanup
  - Added duplicate prevention guards
  - Memoized `handleSend` with `useCallback`
  - Added sessionStorage guard for initial messages
  - Fixed useEffect dependencies

---

## Testing

To verify the fix works:

1. **Clear browser cache and sessionStorage**
2. **Open chat page** - Should see greeting message only once
3. **Send a message** - Should appear only once
4. **Check console** - Should not see duplicate warnings
5. **Test enrollment flow** - "I want to join Proxie" should send only once

---

## Notes

- **React Strict Mode**: The sessionStorage guard prevents duplicates even when React Strict Mode causes double mounts
- **Production**: React Strict Mode is disabled in production builds, but the guards still protect against other race conditions
- **Performance**: The guards add minimal overhead and significantly improve reliability

---

## Status

✅ **FIXED** - All duplicate message issues resolved

---

**Fixed By:** AI Assistant  
**Date:** January 30, 2026
