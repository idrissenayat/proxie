# Sprint 9 PRD: Provider Experience & Provider Agent

**Status**: Approved ✅
**Date**: 2026-01-25

## 1. Executive Summary
Sprint 8 delivered a sophisticated Consumer Agent. Now we need to complete the other side of the marketplace — the Provider Experience. This sprint transforms the provider side with Rich Lead Cards (visuals), a Provider Agent (AI assistant), Smart Offer Suggestions, and a Quick Response Flow.

## 2. User Stories

### 2.1 Rich Lead Display
- **US-1: View Lead with Media**: Providers see photos/videos attached to requests.
- **US-2: Lead Detail View**: Full details including media gallery, consumer notes, and specialist analysis.
- **US-3: Filter and Sort Leads**: Focus on relevant opportunities by service type, budget, and timing.

### 2.2 Provider Agent
- **US-4: Chat with Provider Agent**: Conversational assistant for managing leads.
- **US-5: Ask About a Lead**: Summarizes request details and provides insights.
- **US-6: Get Offer Suggestions**: Suggests pricing and timing based on request complexity and market rates.
- **US-7: Draft Offer via Agent**: Gathers info and creates a draft offer for review and approval.

### 2.3 Quick Offer Flow
- **US-8: One-Tap Offer Templates**: Use saved templates (price, duration, message) for faster responses.
- **US-9: Smart Time Slot Suggestions**: Suggests slots based on provider's calendar.
- **US-10: Offer Confirmation**: Clear confirmation after submission.

### 2.4 Provider Dashboard Enhancements
- **US-11: Dashboard Overview**: Activity cards for New Leads, Pending Offers, Upcoming Bookings.
- **US-12: Lead Notifications**: Badge indicator for unviewed leads.
- **US-13: My Offers Section**: Track status of all submitted offers.

## 3. UI Requirements
- **Dashboard Layout**: Activity cards at top, filterable lead list below.
- **Lead Card**: Dark background (zinc-800), thumbnails, budget spotlight.
- **Lead Detail**: Swipeable gallery, metadata section, specialist insights, "Make Offer" CTA.
- **Make Offer Screen**: Suggested price, time slot picker, template selection.

## 4. Backend Requirements
- **Endpoints**:
    - `GET /requests` (Provider context with viewed status).
    - `PUT /requests/{id}/view`.
    - `GET /providers/{id}` (inc. templates/availability).
    - `POST /providers/{id}/templates`.
    - `GET /providers/{id}/available-slots`.
- **Provider Agent Tools**: `get_my_leads`, `get_lead_details`, `suggest_offer`, `draft_offer`, `submit_offer`.
- **Offer Suggestions Service**: Logic for complexity analysis and competitive pricing.
