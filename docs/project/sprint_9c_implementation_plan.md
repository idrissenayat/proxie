# Sprint 9C Implementation Plan: Provider Enrollment System

**Date**: 2026-01-26
**Status**: Planning

## Phase 1: Data Model & Service Catalog (Backend)

### 1.1 Service Catalog Infrastructure
- [ ] Define `src/platform/resources/service_catalog.json` with categories, services, and verification rules.
- [ ] Create `CatalogService` to query available services and categories.
- [ ] Add `GET /services/catalog` and `GET /services/catalog/{category}` endpoints.

### 1.2 Enrollment State Management
- [ ] Create `ProviderEnrollment` model in `src/platform/models/provider.py`:
    - `id`, `provider_id` (optional until activated), `status` (draft, pending_verification, verified).
    - `data` (JSONB) to hold temporary enrollment state.
- [ ] Add `enrollment_id` to session context in `ChatService`.

---

## Phase 2: Enrollment Agent & Chat Integration (AI Layer)

### 2.1 Enrollment Tools
- [ ] Implement tools in `src/platform/services/chat.py` (or specialized handler):
    - `get_service_catalog`: Show categories/services.
    - `update_enrollment_data`: Generic tool for the agent to save profile/location/pricing info.
    - `save_portfolio`: Link uploaded media to the enrollment record.
    - `submit_enrollment`: Finalize and trigger verification.

### 2.2 System Prompting
- [ ] Create `ENROLLMENT_SYSTEM_PROMPT` emphasizing conversational guidance, price suggestion, and bio drafting.
- [ ] Logic in `ChatService` to route to `role="enrollment"` and load the appropriate context.

---

## Phase 3: Verification & Activation Logic (Backend Service)

### 3.1 Verification Service
- [ ] Create `src/platform/services/verification.py`.
- [ ] Implement `check_completeness(enrollment_id)`:
    - 3+ Photos?
    - Pricing for all services?
    - Address/Radius set?
    - Hours defined?
- [ ] Implement `activate_provider(enrollment_id)`:
    - Create/Update `Provider` record.
    - Transfer media to permanent storage.
    - Set `is_active=True`.

---

## Phase 4: Frontend Enrollment Experience (Frontend)

### 4.1 Enrollment Landing
- [ ] Update `DashboardPage.jsx` (Supply tab):
    - If provider is not enrolled, show "Become a Provider" landing card.
    - If enrollment is pending, show "Verification in Progress" state.

### 4.2 Interactive Enrollment Components
- [ ] Create `ServiceSelector.jsx`: Multi-select grid for services.
- [ ] Create `PortfolioUploader.jsx`: Drag-and-drop / Camera grid for work photos.
- [ ] Create `EnrollmentSummaryCard.jsx`: Final review display.

### 4.3 Chat Flow Integration
- [ ] Update `ChatPage.jsx` to support the `enrollment` role.
- [ ] Handle rendering of the new interactive components within the message stream.

---

## Success Metrics
- [ ] Enrollment completes in < 10 agent turns.
- [ ] 100% of "Hair & Beauty" providers auto-verified if photos >= 3.
- [ ] All bio generation matches the master barber style defined in PRD.
