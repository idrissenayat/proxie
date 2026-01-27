# Sprint 9 Implementation Plan: Provider Experience & Provider Agent

**Date**: 2026-01-25
**Status**: Completed ✅

## Phase 1: Data Model & Suggestion Engine (Backend)

### 1.1 Model Updates
- [x] Add `offer_templates` (JSON) to `Provider` model.
- [x] Create `ProviderLeadView` model (provider_id, request_id, viewed_at) to track notifications.
- [x] Update `ProviderSchema` to include these new fields.

### 1.2 Offer Suggestion Service
- [x] Create `src/platform/services/suggestions.py`.
- [x] Implement logic to:
    - Parse `specialist_analysis` from a lead.
    - Compare with provider's `base_price`.
    - Apply market heuristics (standard/complex).
    - Suggest `recommended_price` and `message`.

---

## Phase 2: Provider Agent & Tools (Backend)

### 2.1 Tool Implementation
- [x] `get_my_leads`: Extended version of `get_matching_requests` with "New" status.
- [x] `get_lead_details`: Fetches full metadata, media URLs, and mark as viewed.
- [x] `suggest_offer`: Integrates with the Suggestion Service.
- [x] `draft_offer`: Prepares an offer object for UI confirmation.

### 2.2 Provider Personality
- [x] Create `PROVIDER_SYSTEM_PROMPT` in `chat.py`.
- [x] Update `ChatService.handle_chat` to switch prompts based on roles.
- [x] Ensure provider agent can "see" consumer media descriptions in context.

---

## Phase 3: Rich Lead Experience (Frontend)

### 3.1 Enhanced Dashboard
- [x] Update `ProviderDashboardPage.jsx` (Summary Cards).
- [x] Add `LeadCard` component with:
    - Media thumbnails.
    - "New" badge logic.
    - Budget spotlight.

### 3.2 Lead Detail Gallery
- [x] Create `LeadDetailView` modal/page.
- [x] Implement image gallery (swipeable).
- [x] Display **Specialist Analysis** section (Technical specs for pros).

---

## Phase 4: Quick Offer Flow (Frontend)

### 4.1 Make Offer UI
- [x] Build "Make Offer" screen with:
    - Smart price suggestions toggle.
    - Time slot selection (easy-tap buttons).
    - Message template selection.

### 4.2 Offer Templates
- [x] UI for managing templates in Provider Profile.
- [x] Integration of "Quick Offer" templates in Lead Cards.

### 4.3 My Offers Section
- [x] Screen to track status of all submitted offers (Pending/Accepted).

---

## Phase 5: Provider Agent Chat (Frontend)
- [x] Add Chat sidebar/modal for providers.
- [x] Implement "Draft Offer" card rendering (similar to Consumer Draft).
- [x] Enable "Contextual Ask" (Ask agent about a specific lead).

---

## Success Metrics
- [x] Lead Cards show thumbnails.
- [x] Provider Agent suggests pricing based on visuals.
- [x] Offer submitted in < 60 seconds using templates.
- [x] "New" badge disappears after viewing details.
