# Proxie Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.12.0] - 2026-01-27

### Added - Architecture 2.0 & Hardening
- **Infrastructure**
  - Migrated primary UI to **Next.js 14** (web-next)
  - Integrated **Clerk Authentication** for enterprise-grade security
  - Moved session management to **Redis Cluster**
  - Added **Socket.io** for real-time, low-latency communication
  - Implemented **Health & Readiness** probes for GKE orchestration
- **Observability**
  - Integrated **Sentry** for error tracking
  - Added **OpenTelemetry** tracing and **Grafana/Loki** log collection
  - Switched to **Structlog** for production-grade structured logging
- **AI Layer**
  - Implemented **LiteLLM Gateway** for model fallback and caching
  - Added **Agent-Native Profile Sync** (Automatic captue of user data)
- **Frontend**
  - New **Onboarding Hero** and premium landing pages
  - **Live Profile Cards** in-chat for real-time visual feedback

---

## [0.11.0] - 2026-01-27

### Added - Request Details & Provider Profiles

#### Backend
- **Request Lifecycle Management**
  - `GET /requests/{id}` - Get detailed request with status history
  - `PATCH /requests/{id}` - Edit request (only if status='matching' and no offers)
  - `POST /requests/{id}/cancel` - Cancel request (only if status in ['matching', 'pending'])
  - Added `status_history` JSONB field to `service_requests` table
  - Auto-initialization of status_history for existing requests
  
- **Provider Profile System**
  - `GET /providers/{id}/profile` - Public provider profile (consumer view)
  - `PATCH /providers/{id}/profile` - Update own profile (provider self-edit)
  - Extended `providers` table with: `business_name`, `bio`, `profile_photo_url`, `years_experience`, `jobs_completed`, `response_rate`, `average_response_time_hours`
  
- **Portfolio Management**
  - `GET /providers/{id}/portfolio` - Get portfolio photos
  - `POST /providers/{id}/portfolio` - Add portfolio photo
  - `PATCH /providers/{id}/portfolio/{photo_id}` - Update photo caption/order
  - `DELETE /providers/{id}/portfolio/{photo_id}` - Remove photo
  - Created `provider_portfolio_photos` table with indexes
  
- **Service Management** (Extended)
  - `POST /providers/{id}/services` - Add service
  - `PATCH /providers/{id}/services/{service_id}` - Update service
  - `DELETE /providers/{id}/services/{service_id}` - Delete service

#### Frontend
- **Consumer Experience**
  - `RequestDetailView.jsx` - Full request detail page with timeline
  - `StatusTimeline.jsx` - Chronological status history component
  - `MediaGallery.jsx` - Reusable image/video grid component
  - `PublicProviderProfile.jsx` - Consumer-facing provider profile
  - `ReviewsList.jsx` - Provider reviews display component
  - Clickable request cards in dashboard → navigate to detail view
  - Edit Request flow → opens chat with pre-filled context
  - Cancel Request flow → premium confirmation modal
  
- **Provider Experience**
  - `ProviderProfilePage.jsx` - Tabbed self-management interface
    - **Info Tab**: Display and edit profile details
    - **Services Tab**: Manage offered services
    - **Portfolio Tab**: Manage portfolio photos
    - **Reviews Tab**: View received reviews
  - `EditProfileModal.jsx` - Profile editing modal with glassmorphic design
  - `PortfolioManager.jsx` - Portfolio photo CRUD interface
  - `ServiceManager.jsx` - Service offering management
  - "View Public Profile" button to preview consumer-facing view
  
- **Navigation & Integration**
  - Added routes: `/request/:id`, `/providers/:id`, `/provider/profile`
  - Provider names in offers page → clickable to profile
  - Request cards in dashboard → clickable to details
  - Chat integration for edit/booking contexts

#### Database
- **Migration Script**: `migrations/sprint_10_profiles_and_requests.sql`
  - Safe alterations with `IF NOT EXISTS` checks
  - Data preservation for existing records
  - Index creation for performance optimization
  - Verification queries included

### Changed
- **CORS Configuration** - Added `PATCH` method to allowed methods
- **API Client** - Added 8 new functions for profile and request management
- **Dashboard Components** - Enhanced with hover effects and navigation

### Fixed
- Request cancellation now properly updates status_history
- Provider profile endpoints now return all new fields
- Portfolio ordering works correctly with display_order

---

## [0.1.0] - 2026-01-26

### Added - Provider Enrollment & Verification System

#### Backend
- **Enrollment API** (`/enrollment/*`)
  - `POST /enrollment/start` - Initialize enrollment session
  - `GET /enrollment/{id}` - Retrieve enrollment data
  - `PATCH /enrollment/{id}` - Update enrollment data with proper JSON mutation handling
  - `POST /enrollment/{id}/submit` - Submit for verification
- **Service Catalog API** (`/services/*`)
  - `GET /services/catalog/full` - Get categories with nested services
  - `GET /services/catalog/{category_id}` - Get category details
  - `GET /services/services/{service_id}` - Get service metadata
- **Database Models**
  - `ProviderEnrollment` - Tracks enrollment lifecycle (draft → pending → verified)
  - `ProviderLeadView` - Analytics for provider lead engagement
- **Verification Service**
  - Auto-verification for basic services (haircut, cleaning, etc.)
  - Manual review queue for licensed services (plumbing, electrical)
  - Completeness validation (name, services, location, availability)
  - Provider record creation upon verification
- **Service Catalog**
  - JSON-based catalog with 5 categories
  - 6+ services with pricing ranges and requirements
  - License requirements and photo minimums
  - Specializations and metadata

#### AI Agent
- **Enrollment Agent Role**
  - Specialized system prompt for provider onboarding
  - Conversational data collection
  - Friendly, encouraging tone
- **Enrollment Tools**
  - `get_service_catalog` - Show service options
  - `update_enrollment` - Save data incrementally
  - `request_portfolio` - Trigger photo upload UI
  - `get_enrollment_summary` - Generate review card
  - `submit_enrollment` - Finalize and verify

#### Frontend
- **Enrollment Components**
  - `ServiceSelector` - Category grid → Service checklist with pricing
  - `PortfolioUploader` - Multi-photo upload with camera support
  - `EnrollmentSummaryCard` - Review card before submission
- **Dashboard Updates**
  - "Become a Provider" CTA card on Get Leads tab
  - Enrollment status detection
  - Provider ID persistence in localStorage
- **Chat Integration**
  - Enrollment session handling
  - Service catalog rendering
  - Portfolio uploader trigger
  - Summary card display

#### Documentation
- **API Documentation** (`docs/api/README.md`) - Complete endpoint reference
- **Testing Guide** (`docs/testing/README.md`) - End-to-end test procedures
- **Deployment Guide** (`docs/deployment/README.md`) - Setup and production deployment
- **Enrollment Quick Reference** (`docs/guides/enrollment_quick_reference.md`) - User guide
- **Sprint 9C Summary** (`docs/project/sprint_9c_summary.md`) - Technical overview

### Fixed
- **JSON Field Mutation** - Used `flag_modified()` to ensure SQLAlchemy detects changes
- **Service Catalog** - Returns full categories with services, not just headers
- **Chat Endpoint** - Added trailing slash to prevent 307 redirects
- **ServiceSelector** - Added optional chaining to prevent crashes on undefined data

### Changed
- **ChatRequest Schema** - Added `submit_enrollment` and `submit_offer` to action literals
- **API Client** - Updated `getServiceCatalog()` to use `/services/catalog/full`
- **Chat Endpoint** - Now uses `/chat/` with trailing slash

---

## [0.0.9] - 2026-01-20

### Added - Consumer Dashboard & Request Management

#### Backend
- `GET /consumers/{id}/requests` - Get consumer's requests grouped by status
- Request status tracking (open, pending, upcoming, completed)

#### Frontend
- **My Requests Page** - Consumer dashboard with request tracking
- Request cards with status badges
- Grouped views (Open, Pending, Upcoming, Completed)
- Request counts and summaries

---

## [0.0.8] - 2026-01-18

### Added - Provider Dashboard & Leads View

#### Backend
- `GET /requests` - List service requests with filters
- `PUT /requests/{id}/view` - Mark lead as viewed
- Provider lead matching

#### Frontend
- **Provider Dashboard** - Leads view with filtering
- Lead cards with request details
- "Make Offer" workflow
- Lead analytics (view tracking)

---

## [0.0.7] - 2026-01-15

### Added - Multi-Modal Agent & Specialist Framework

#### Backend
- Media upload endpoint (`POST /media/upload`)
- Multi-modal chat support (images, videos)
- Specialist system (Hair Specialist with vision capabilities)

#### Frontend
- Photo/video upload in chat
- Camera capture integration
- Media preview in messages
- Voice input/output

---

## [0.0.6] - 2026-01-12

### Added - Security Hardening

#### Backend
- CORS middleware with configurable origins
- Security headers (X-Frame-Options, CSP, etc.)
- Rate limiting (future)
- Input validation via Pydantic

---

## [0.0.5] - 2026-01-10

### Changed - Gemini Migration

#### Backend
- Migrated from Claude to Google Gemini API
- Updated agent prompts for Gemini
- Tool calling format changes

---

## [0.0.4] - 2026-01-08

### Added - AI Chatbot Interface

#### Frontend
- Dark mode dashboard
- Conversational input bar
- Voice input (Web Speech API)
- Text-to-speech output
- Premium UI with glassmorphism

---

## [0.0.3] - 2026-01-05

### Added - MCP Server & Interface

#### Backend
- MCP server implementation
- Authentication layer
- Tool definitions for Claude Desktop

---

## [0.0.2] - 2026-01-03

### Added - Core Platform

#### Backend
- Service request ingestion
- Matching engine
- Offer aggregation
- Booking confirmation

#### Frontend
- Mobile app (Expo) - now archived
- Web app (Vite + React)

---

## [0.0.1] - 2026-01-01

### Added - Foundation

#### Backend
- PostgreSQL database setup
- Provider registration
- Database models (Provider, ServiceRequest, Offer, Booking, Review)
- FastAPI application structure

---

## Upcoming

### [0.2.0] - Planned
- [ ] Admin dashboard for manual verification
- [ ] ID verification for licensed services
- [ ] Background checks integration
- [ ] Email notifications
- [ ] SMS verification
- [ ] Provider profile editing
- [ ] Service pricing updates
- [ ] Portfolio management

### [0.3.0] - Planned
- [ ] Payment processing
- [ ] Booking calendar integration
- [ ] Review system
- [ ] Rating algorithm
- [ ] Trust score
- [ ] Dispute resolution

### [1.0.0] - Planned
- [ ] Multi-city support
- [ ] Additional service categories
- [ ] Mobile app (React Native)
- [ ] Real-time notifications
- [ ] Analytics dashboard
- [ ] Business intelligence

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.11.0 | 2026-01-27 | Request Details & Provider Profiles |
| 0.1.0 | 2026-01-26 | Provider Enrollment & Verification |
| 0.0.9 | 2026-01-20 | Consumer Dashboard |
| 0.0.8 | 2026-01-18 | Provider Dashboard |
| 0.0.7 | 2026-01-15 | Multi-Modal Agent |
| 0.0.6 | 2026-01-12 | Security Hardening |
| 0.0.5 | 2026-01-10 | Gemini Migration |
| 0.0.4 | 2026-01-08 | AI Chatbot Interface |
| 0.0.3 | 2026-01-05 | MCP Server |
| 0.0.2 | 2026-01-03 | Core Platform |
| 0.0.1 | 2026-01-01 | Foundation |

---

## Breaking Changes

### 0.1.0
- Chat endpoint now requires trailing slash: `/chat/` not `/chat`
- Service catalog endpoint changed: use `/services/catalog/full` for UI components

---

## Migration Guide

### Upgrading to 0.1.0

#### Backend
```bash
# Run new migrations
python scripts/migrate.py

# Restart server
python src/platform/main.py
```

#### Frontend
```bash
# Update dependencies (if needed)
npm install

# Clear localStorage (optional, for clean state)
localStorage.clear()

# Restart dev server
npm run dev
```

#### Database
No manual migrations required. `migrate.py` handles:
- Creating `provider_enrollments` table
- Creating `provider_lead_views` table
- Adding new indexes

---

## Contributors

- Idrisse Nayat - Lead Developer

---

**Note:** This is an MVP project. Version numbers reflect development milestones, not production releases.
