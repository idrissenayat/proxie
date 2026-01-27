# Sprint 8: Multi-Modal Consumer Agent with Specialist Agents

## Product Requirements Document

**Product Owner**: Idriss  
**Date**: January 25, 2026  
**Sprint Goal**: Enable the Consumer Agent to accept photos, videos, and live camera input, consult domain specialists, and present requests for user approval before posting.

---

## 1. Executive Summary

Currently, users can only interact with the Proxie agent via text and voice. This sprint enhances the Consumer Agent to understand visual input (photos, videos, live camera) and consult specialized agents for domain-specific validation before posting service requests.

**Key Outcome**: Users can show the agent what they need (e.g., their hair, a plumbing leak, a dirty room) and the agent understands, asks smart questions, validates with a specialist, and confirms before posting.

---

## 2. User Stories

### 2.1 Multi-Modal Input

#### US-1: Photo Upload

> As a consumer, I want to upload photos so the agent can see what I need help with.

**Acceptance Criteria:**
- User can tap a button to select photos from their device
- User can select multiple photos (up to 5)
- Photos appear as thumbnails before sending
- User can remove a photo before sending
- Agent acknowledges seeing the photos and describes what it sees
- Photos are attached to the service request

#### US-2: Take Photo

> As a consumer, I want to take a photo with my camera so I can quickly show the agent my current situation.

**Acceptance Criteria:**
- User can tap a button to open the camera
- Camera shows a live preview
- User can capture a photo
- Captured photo appears in the chat ready to send
- Works on mobile and desktop (with webcam)

#### US-3: Video Upload

> As a consumer, I want to upload a short video so the agent can better understand my needs.

**Acceptance Criteria:**
- User can select a video file from their device
- Video is limited to 30 seconds / 10MB (show error if exceeded)
- Agent can analyze the video content
- Video thumbnail appears in chat

#### US-4: Live Camera

> As a consumer, I want to show the agent a live camera feed so it can see my situation in real-time.

**Acceptance Criteria:**
- User can open a live camera view
- Agent can see the live feed (via periodic frame captures)
- User can capture a frame to attach to the request
- User can close the camera and return to chat
- Clear indication that camera is active

### 2.2 Agent Understanding

#### US-5: Visual Analysis

> As a consumer, when I share photos or videos, I want the agent to describe what it sees so I know it understands my needs.

**Acceptance Criteria:**
- When user shares a photo of their hair, agent says something like "I can see you have curly, shoulder-length hair with some highlights"
- When user shares a photo of a plumbing issue, agent describes the visible problem
- Agent uses visual information to ask relevant follow-up questions
- Agent does not hallucinate details not visible in the image

#### US-6: Context from Media

> As a consumer, I want the agent to use visual information to reduce the questions it needs to ask me.

**Acceptance Criteria:**
- If agent can see hair type from photo, it doesn't ask "What's your hair type?"
- If agent can see location context from photo, it may ask to confirm rather than ask from scratch
- Agent combines visual info with conversation context

### 2.3 Specialist Consultation

#### US-7: Haircut Specialist

> As a consumer requesting a haircut, I want the agent to consult a hair expert so my request uses the right terminology and captures all relevant details.

**Acceptance Criteria:**
- When service type is haircut/hair-related, agent consults the Haircut Specialist
- Specialist analyzes any hair photos shared
- Specialist identifies hair type (e.g., "Type 3B curly")
- Specialist enriches request with professional terminology
- Specialist flags if anything is missing
- User does not see the specialist consultation directly (it happens behind the scenes)

#### US-8: Specialist Suggestions

> As a consumer, I want the agent to ask me for additional information if the specialist says something is missing.

**Acceptance Criteria:**
- If specialist says "need to see the back of the hair," agent asks user for that
- If specialist says "budget seems low for this service," agent gently asks user to confirm
- Agent incorporates specialist feedback naturally into conversation

### 2.4 Request Approval Workflow

#### US-9: Draft Preview

> As a consumer, I want to see a summary of my request before it's posted so I can make sure everything is correct.

**Acceptance Criteria:**
- When agent has gathered all information, it shows a formatted draft
- Draft clearly displays: service type, details, location, budget, timing
- Draft shows attached photos/videos
- Draft appears as a card in the chat
- User can read and review all details

#### US-10: Approve Request

> As a consumer, I want to approve my request with a single tap so it gets posted to providers.

**Acceptance Criteria:**
- Draft card has a clear "Post Request" button
- Tapping "Post Request" submits the request to the platform
- Agent confirms "Your request has been posted!"
- Request appears in the system with status "matching"
- User cannot accidentally post without seeing the draft first

#### US-11: Edit Request

> As a consumer, I want to edit my request before posting if something is wrong.

**Acceptance Criteria:**
- Draft card has an "Edit" button
- Tapping "Edit" clears the draft and lets user make changes
- Agent asks "What would you like to change?"
- User can update details through conversation
- Agent shows a new draft after changes

#### US-12: Cancel Request

> As a consumer, I want to cancel and start over if I change my mind.

**Acceptance Criteria:**
- Draft card has a "Cancel" button
- Tapping "Cancel" discards the draft
- Agent confirms "Request cancelled. Is there something else I can help with?"
- User can start a completely new request

---

## 3. User Interface Requirements

### 3.1 Input Bar Enhancement

Current input bar:
```
[+] [        Ask anything          🎤 (◯)]
```

The [+] button should open an attachment menu with options:
- 📷 **Take Photo** — Opens camera to capture
- 🖼️ **Choose Photo** — Opens file picker for images
- 📁 **Choose Video** — Opens file picker for videos
- 📹 **Live Camera** — Opens live camera view

### 3.2 Media Preview

When user has selected media but not yet sent:
- Show thumbnail strip above the input bar
- Each thumbnail has an X button to remove
- Thumbnails are small (about 60x60 pixels)
- Show count if multiple items

### 3.3 Live Camera View

Full-screen overlay with:
- Live camera preview (full screen)
- "Capture" button at bottom center (large, white circle)
- "Close" button at top right (X icon)
- Brief instruction text: "Show what you need help with"
- Dark background for controls area

### 3.4 Draft Request Card

Appears in chat when agent has prepared a draft:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 SERVICE REQUEST DRAFT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Service: Curly Bob Haircut

Details:
- Style: Curly bob, chin-length
- Hair type: 3B curly, shoulder-length
- Goal: Shorter while maintaining curls

📍 Brooklyn, NY
💰 $70-90
📅 This weekend

📷 2 photos attached
[thumbnail] [thumbnail]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[✓ Post Request] [✏️ Edit] [✗ Cancel]
```

**Style notes:**
- Dark card background (zinc-800)
- Clear section headers
- Photo thumbnails if media attached
- Three action buttons at bottom
- "Post Request" is primary (blue)
- "Edit" and "Cancel" are secondary (gray)

### 3.5 User Message with Media

When user sends a message with attached media:
- Show media thumbnails above the message text
- Thumbnails are clickable to view full size
- Message bubble is slightly larger to accommodate

---

## 4. Conversation Flow Requirements

### 4.1 Happy Path: Haircut with Photo

```
Agent: Hi! I'm Proxie, your personal service concierge. What can I help you find today?

User: I need a haircut

Agent: I'd love to help you find a great stylist! Could you show me your current hair? 
       You can take a photo or upload one.

User: [Uploads photo of their hair]

Agent: Beautiful! I can see you have curly hair, looks like it's about shoulder-length 
       with some natural highlights. What kind of cut are you thinking?

User: Something shorter, maybe a bob but I want to keep my curls

Agent: A curly bob is a great choice! It'll really show off your curl pattern.
       Where are you located?

User: Brooklyn

Agent: And what's your budget for this haircut?

User: Around 80 dollars

Agent: Perfect! When do you need this done?

User: This weekend if possible

Agent: Got it! Let me put together your request...

       [Shows Draft Request Card]

User: [Taps "Post Request"]

Agent: Done! ✅ Your request is now live.
       
       I'll notify you as soon as stylists respond. Based on your criteria, 
       you should hear back within a few hours!
```

### 4.2 Flow with Edit

```
[After agent shows draft]

User: [Taps "Edit"]

Agent: No problem! What would you like to change?

User: Actually my budget is more like 60-70

Agent: Got it, I'll update the budget to $60-70.

       [Shows updated Draft Request Card with new budget]

User: [Taps "Post Request"]

Agent: Done! ✅ Your request is now live.
```

### 4.3 Flow with Multiple Photos

```
User: I need a haircut [attaches 3 photos: front, side, back]

Agent: Thanks for sharing those photos! I can see:
       - Front: Curly hair framing your face nicely
       - Side: About shoulder-length with good volume  
       - Back: Some layers already, healthy-looking ends
       
       What style are you going for?
```

### 4.4 Flow with Missing Information

```
Agent: [After analyzing request internally with specialist]
       
       Before I finalize your request, could you also show me the back of your hair? 
       This helps stylists understand your current layers and length better.

User: [Takes photo of back of head]

Agent: Perfect, that's really helpful! Now I have everything I need.

       [Shows Draft Request Card]
```

---

## 5. Backend Requirements

### 5.1 Chat API Enhancement

The `POST /chat/` endpoint must accept:
- `message` — Text message (optional if media present)
- `session_id` — Session identifier
- `role` — "consumer" or "provider"
- `media` — Array of media attachments (optional)
  - Each attachment has: `type` (image/video), `data` (base64), `mime_type`
- `action` — Workflow action: "approve_request", "edit_request", "cancel_request" (optional)

Response must include:
- `session_id` — Session identifier
- `message` — Agent's text response
- `draft` — Draft request object when awaiting approval (optional)
- `awaiting_approval` — Boolean indicating if waiting for user action

### 5.2 Media Storage

- Store uploaded media files on the server
- Generate URLs that can be accessed by the frontend
- Associate media with the session
- Include media URLs in the final service request
- Clean up media for abandoned sessions (after 24 hours)

### 5.3 Specialist Agent System

Create a system where:
- Multiple specialist agents can be registered (haircut, cleaning, plumbing, etc.)
- Consumer agent can consult the appropriate specialist based on service type
- Specialist receives: gathered information, any media shared
- Specialist returns: validation result, enriched data, missing info, suggestions
- Consumer agent uses specialist feedback to improve the request

**For Sprint 8, implement only the Haircut Specialist.** Others will be added in future sprints.

### 5.4 Haircut Specialist Requirements

The Haircut Specialist should:
- Analyze hair photos to identify hair type (straight/wavy/curly/coily and subtypes)
- Understand haircut terminology (bob, pixie, layers, fade, etc.)
- Understand color terminology (highlights, balayage, ombre, etc.)
- Identify if the request is for cut, color, treatment, or styling
- Enrich vague descriptions with professional terms
- Flag if important information is missing
- Estimate service duration and complexity
- Suggest additional photos if helpful

### 5.5 Draft Request Storage

- Store draft requests in the session
- Draft should include all gathered information
- Draft should reference attached media
- Draft should include specialist notes (not shown to user)
- Draft is cleared after approval, edit, or cancel

### 5.6 Request Creation

When user approves:
- Create the service request in the database
- Include all details from the draft
- Attach media URLs to the request
- Set status to "matching"
- Trigger the matching engine
- Return success to the user

---

## 6. Technical Constraints

### 6.1 Media Limits

- Maximum 5 media items per message
- Images: max 5MB each, formats: JPEG, PNG, WebP, GIF
- Videos: max 10MB, max 30 seconds, formats: MP4, WebM, MOV
- Live camera: capture at 720p resolution

### 6.2 Gemini API

- Use Gemini's multi-modal capabilities for image/video understanding
- Gemini 1.5 Flash or 2.0 Flash both support vision
- Send images inline with the conversation
- Handle rate limits gracefully

### 6.3 Browser Compatibility

- Camera access requires HTTPS (except localhost)
- Use `getUserMedia` API for camera
- Provide fallback message if camera not available
- Test on: Chrome, Safari, Firefox (desktop and mobile)

---

## 7. Out of Scope

The following are **NOT** part of this sprint:

- Provider-side multi-modal input (future sprint)
- Specialist agents other than Haircut (future sprint)
- Video recording from camera (only photo capture)
- Real-time streaming to agent (using frame captures instead)
- Persistent conversation history across sessions
- Voice output reading of draft requests

---

## 8. Success Criteria

Sprint is complete when:

- ✅ User can upload photos and agent describes what it sees
- ✅ User can take a photo with camera and send it
- ✅ User can upload a short video and agent understands it
- ✅ User can open live camera and capture frames
- ✅ Agent consults Haircut Specialist for hair-related requests
- ✅ Agent shows draft request card before posting
- ✅ User can approve, edit, or cancel the draft
- ✅ Approved requests are created in the database with media attached
- ✅ All existing text/voice functionality continues to work
- ✅ Works on mobile browsers (Chrome, Safari)

---

## 9. Test Scenarios

### Scenario 1: Photo Upload Flow
1. Open chat
2. Type "I need a haircut"
3. Tap [+] → Choose Photo
4. Select a photo
5. See thumbnail preview
6. Send message
7. Verify agent describes the photo
8. Complete the flow to draft
9. Approve
10. Verify request created with photo

### Scenario 2: Camera Capture Flow
1. Open chat
2. Type "I need a haircut"
3. Tap [+] → Take Photo
4. See camera preview
5. Capture photo
6. See thumbnail in chat
7. Send
8. Verify agent sees photo

### Scenario 3: Edit Draft Flow
1. Complete flow to draft
2. Tap "Edit"
3. Say "Change budget to 100 dollars"
4. See updated draft
5. Approve
6. Verify request has updated budget

### Scenario 4: Cancel Draft Flow
1. Complete flow to draft
2. Tap "Cancel"
3. Verify draft is cleared
4. Start new request
5. Verify can complete new flow

### Scenario 5: Multiple Photos
1. Say "I need a haircut"
2. Upload 3 photos at once
3. Verify all thumbnails shown
4. Send
5. Verify agent acknowledges all photos

### Scenario 6: Video Upload
1. Say "I need a haircut"
2. Upload short video of hair
3. Send
4. Verify agent understands video content

---

## 10. Appendix: Haircut Specialist Knowledge Base

The Haircut Specialist should understand:

### Hair Types (Andre Walker System)
- **Type 1: Straight** (1A fine, 1B medium, 1C coarse)
- **Type 2: Wavy** (2A loose S-waves, 2B defined S-waves, 2C strong waves)
- **Type 3: Curly** (3A loose curls, 3B springy curls, 3C tight curls)
- **Type 4: Coily** (4A soft coils, 4B Z-pattern, 4C tight Z-pattern)

### Haircut Styles
- **Bob** (classic, A-line, inverted, lob)
- **Pixie** (classic, long pixie, undercut pixie)
- **Layers** (long layers, short layers, face-framing)
- **Bangs** (curtain, side-swept, blunt, wispy)
- **Fades** (low, mid, high, skin fade)
- Undercut, shag, wolf cut, mullet, etc.

### Color Services
- Highlights (foil, balayage, babylights)
- Lowlights
- Single process (all-over color)
- Root touch-up
- Color correction
- Toner/gloss

### Treatments
- Keratin treatment
- Deep conditioning
- Scalp treatment
- Bond repair (Olaplex, K18)
