# Sprint 8 Implementation Plan
**Date**: 2026-01-25
**Status**: Planning

## Overview
This implementation plan breaks down the Sprint 8 PRD into actionable development phases.

---

## Phase 1: Backend Infrastructure (Days 1-2)

### 1.1 Media Storage System
**Files to create:**
- `src/platform/services/media.py` - Media storage service
- `src/platform/routers/media.py` - Media upload endpoints
- `src/platform/schemas/media.py` - Media schemas

**Tasks:**
- [ ] Create media upload endpoint (`POST /media/upload`)
- [ ] Implement file validation (size, type, dimensions)
- [ ] Store media files to `uploads/` directory
- [ ] Generate unique URLs for media access
- [ ] Create media cleanup job (24-hour expiry)

### 1.2 Enhanced Chat Schema
**Files to modify:**
- `src/platform/schemas/chat.py`

**Tasks:**
- [ ] Add `media` field (array of attachments)
- [ ] Add `action` field (approve/edit/cancel)
- [ ] Add `draft` response field
- [ ] Add `awaiting_approval` response field

### 1.3 Draft Request Storage
**Files to modify:**
- `src/platform/services/chat.py`

**Tasks:**
- [ ] Add draft storage to session context
- [ ] Implement draft creation/update logic
- [ ] Handle approve/edit/cancel actions
- [ ] Create request on approval

---

## Phase 2: Multi-Modal Chat Service (Days 3-4)

### 2.1 Gemini Vision Integration
**Files to modify:**
- `src/platform/services/chat.py`

**Tasks:**
- [ ] Update chat service to accept media in messages
- [ ] Convert base64 images to Gemini format
- [ ] Send images inline with text to Gemini
- [ ] Handle video frame extraction
- [ ] Update system prompt for visual analysis

### 2.2 Updated Chat Router
**Files to modify:**
- `src/platform/routers/chat.py`

**Tasks:**
- [ ] Accept media attachments in request
- [ ] Validate media (count, size, type)
- [ ] Pass media to chat service
- [ ] Return draft and approval status

---

## Phase 3: Specialist Agent System (Days 5-6)

### 3.1 Specialist Agent Framework
**Files to create:**
- `src/platform/services/specialists/__init__.py`
- `src/platform/services/specialists/base.py` - Base specialist class
- `src/platform/services/specialists/haircut.py` - Haircut specialist

**Tasks:**
- [ ] Create `SpecialistAgent` base class
- [ ] Define specialist interface (analyze, validate, enrich)
- [ ] Create specialist registry
- [ ] Implement specialist selection logic

### 3.2 Haircut Specialist Implementation
**Files to create:**
- `src/platform/services/specialists/haircut.py`

**Tasks:**
- [ ] Create Haircut Specialist agent
- [ ] Implement hair type analysis (with Gemini vision)
- [ ] Create terminology mapping
- [ ] Implement validation rules
- [ ] Generate enriched request data
- [ ] Identify missing information

### 3.3 Integrate Specialists into Chat
**Files to modify:**
- `src/platform/services/chat.py`

**Tasks:**
- [ ] Detect service category from conversation
- [ ] Consult appropriate specialist
- [ ] Incorporate specialist feedback
- [ ] Ask for missing information
- [ ] Enrich draft with specialist data

---

## Phase 4: Draft & Approval Workflow (Day 7)

### 4.1 Draft Generation
**Files to modify:**
- `src/platform/services/chat.py`

**Tasks:**
- [ ] Detect when all required info is gathered
- [ ] Generate structured draft object
- [ ] Include media references in draft
- [ ] Include specialist notes (internal)
- [ ] Set `awaiting_approval: true`

### 4.2 Draft Actions
**Tasks:**
- [ ] Handle `action: "approve_request"`
  - Create service request in database
  - Attach media to request
  - Trigger matching engine
  - Return success message
- [ ] Handle `action: "edit_request"`
  - Clear draft
  - Ask what to change
  - Continue conversation
- [ ] Handle `action: "cancel_request"`
  - Clear draft and session
  - Confirm cancellation

---

## Phase 5: Frontend - Media Input (Days 8-10)

### 5.1 Attachment Menu
**Files to modify:**
- `web/src/pages/ChatPage.jsx`

**Tasks:**
- [ ] Create attachment popup menu
- [ ] Add "Take Photo" option
- [ ] Add "Choose Photo" option
- [ ] Add "Choose Video" option
- [ ] Add "Live Camera" option
- [ ] Style menu with dark theme

### 5.2 Photo Picker
**Tasks:**
- [ ] Implement file input for images
- [ ] Support multiple selection (up to 5)
- [ ] Validate file size (max 5MB)
- [ ] Show thumbnail previews
- [ ] Allow removal before sending

### 5.3 Camera Capture
**Files to create:**
- `web/src/components/CameraCapture.jsx`

**Tasks:**
- [ ] Create camera component using getUserMedia
- [ ] Show live preview
- [ ] Add capture button
- [ ] Add close button
- [ ] Return captured image to chat
- [ ] Handle camera permission errors

### 5.4 Video Picker
**Tasks:**
- [ ] Implement file input for videos
- [ ] Validate file size (max 10MB)
- [ ] Validate duration (max 30 seconds)
- [ ] Show video thumbnail

### 5.5 Live Camera View
**Files to create:**
- `web/src/components/LiveCamera.jsx`

**Tasks:**
- [ ] Create fullscreen camera overlay
- [ ] Show live preview
- [ ] Add capture button (takes frame)
- [ ] Add close button
- [ ] Show instruction text

### 5.6 Media Preview Strip
**Tasks:**
- [ ] Create thumbnail strip component
- [ ] Show above input when media selected
- [ ] Add X button on each thumbnail
- [ ] Show count indicator

---

## Phase 6: Frontend - Draft Card & Actions (Day 11)

### 6.1 Draft Request Card Component
**Files to create:**
- `web/src/components/DraftRequestCard.jsx`

**Tasks:**
- [ ] Create card layout (zinc-800 background)
- [ ] Display service type
- [ ] Display details list
- [ ] Display location, budget, timing
- [ ] Display attached media thumbnails
- [ ] Add "Post Request" button (primary/blue)
- [ ] Add "Edit" button (secondary/gray)
- [ ] Add "Cancel" button (secondary/gray)

### 6.2 Integrate Draft Card in Chat
**Files to modify:**
- `web/src/pages/ChatPage.jsx`

**Tasks:**
- [ ] Detect `draft` in response
- [ ] Render DraftRequestCard in chat
- [ ] Handle button clicks
- [ ] Send action to backend
- [ ] Update UI after action

---

## Phase 7: Media in Messages (Day 12)

### 7.1 Send Media with Message
**Files to modify:**
- `web/src/pages/ChatPage.jsx`

**Tasks:**
- [ ] Convert selected media to base64
- [ ] Include in request payload
- [ ] Clear media after sending
- [ ] Show loading state during upload

### 7.2 Display Media in User Messages
**Tasks:**
- [ ] Show media thumbnails in user bubble
- [ ] Make thumbnails clickable for full view
- [ ] Style for dark theme

### 7.3 Media Viewer Modal
**Files to create:**
- `web/src/components/MediaViewer.jsx`

**Tasks:**
- [ ] Create fullscreen media viewer
- [ ] Support images and videos
- [ ] Add close button
- [ ] Support swipe/navigation for multiple

---

## Phase 8: Testing & Polish (Days 13-14)

### 8.1 Backend Tests
- [ ] Test media upload endpoint
- [ ] Test vision analysis
- [ ] Test specialist consultation
- [ ] Test draft workflow
- [ ] Test request creation

### 8.2 Frontend Tests
- [ ] Test photo upload flow
- [ ] Test camera capture flow
- [ ] Test video upload flow
- [ ] Test live camera
- [ ] Test draft approval/edit/cancel

### 8.3 Integration Tests
- [ ] Full haircut with photo flow
- [ ] Multiple photos flow
- [ ] Edit draft flow
- [ ] Cancel draft flow

### 8.4 Mobile Testing
- [ ] Test on iOS Safari
- [ ] Test on Android Chrome
- [ ] Test camera permissions
- [ ] Test file picker

---

## File Summary

### New Files (Backend)
```
src/platform/
├── services/
│   ├── media.py
│   └── specialists/
│       ├── __init__.py
│       ├── base.py
│       └── haircut.py
├── routers/
│   └── media.py
└── schemas/
    └── media.py
```

### New Files (Frontend)
```
web/src/
├── components/
│   ├── CameraCapture.jsx
│   ├── LiveCamera.jsx
│   ├── DraftRequestCard.jsx
│   └── MediaViewer.jsx
```

### Modified Files
```
Backend:
- src/platform/schemas/chat.py
- src/platform/services/chat.py
- src/platform/routers/chat.py
- src/platform/main.py

Frontend:
- web/src/pages/ChatPage.jsx
```

---

## Dependencies

### Backend
- No new dependencies (Gemini already supports vision)

### Frontend
- No new dependencies (using native browser APIs)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Camera not working on all browsers | Provide fallback to file upload |
| Large media files slow down chat | Compress images before upload |
| Gemini rate limits with images | Implement retry with backoff |
| Video analysis might be slow | Process first frame only if needed |

---

## Success Metrics

- [ ] Photo upload → Agent describes what it sees
- [ ] Camera capture → Works on mobile and desktop
- [ ] Video upload → Agent understands content
- [ ] Live camera → Can capture frames
- [ ] Haircut specialist → Enriches requests with terminology
- [ ] Draft preview → Shows all gathered info
- [ ] Approve/Edit/Cancel → All actions work correctly
- [ ] Request created → Stored in database with media
