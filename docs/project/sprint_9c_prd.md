# Sprint 9C: Provider Enrollment & Verification System - PRD

**Product Owner**: Idriss  
**Date**: January 26, 2026  
**Sprint Goal**: Enable service providers to enroll on the Proxie platform through a conversational agent that collects required information, verifies their services, and activates their Provider Agent to accept leads.

---

## 1. Executive Summary
Currently, providers are manually seeded. This PRD replaces manual onboarding with a structured, agent-led **Provider Enrollment System**. Providers will converse with an Enrollment Agent to set up their profiles, select services from a catalog, and upload portfolios. Once verified, their specialized Provider Agent is activated to begin receiving leads.

## 2. User Stories

### 2.1 Starting Enrollment
- **US-1: Access Enrollment**: New providers tapping "Get Leads" see a "Become a Provider" CTA.
- **US-2: Agent Introduction**: Enrollment Agent explains the 5-minute process and data requirements.

### 2.2 Collecting Information
- **US-3: Personal Info**: Collect name, business name, phone, email, and profile photo.
- **US-4: Service Selection**: Provider picks categories (Hair, Cleaning, etc.) and specific services.
- **US-5: Service Details**: Collect pricing ranges, duration, and specializations for each service.
- **US-6: Location**: Define service radius and whether they travel or have a shop.
- **US-7: Availability**: Set general weekly working hours.

### 2.3 Portfolio & Bio
- **US-8: Portfolio Upload**: Upload 3-10 photos. Agent confirms content and relevance.
- **US-9: Credentials**: Collect years of experience, training, and licenses for regulated services.
- **US-10: Bio Generation**: Agent helps draft a professional bio based on the conversation.

### 2.4 Review & Activation
- **US-11: Enrollment Summary**: Review all data in a structured card before submission.
- **US-12: Submission**: Agent explains the verification timeline.
- **US-13: Auto-Verification**: Instant activation for complete, non-regulated profiles.
- **US-14: Manual Verification**: Queue for licensed/regulated industries (Plumbing, Electrical).
- **US-15: Activation**: Notification "You're approved! 🎉" and activation of the Provider Agent.

---

## 3. Service Catalog (MVP)

| Category | Typical Services | Verification |
|----------|------------------|--------------|
| **Hair & Beauty** | Haircut, Color, Barber | Basic (Portfolio 3+) |
| **Cleaning** | Standard, Deep, Move-out | Basic |
| **Plumbing** | Leak Repair, Water Heater | Licensed (License #) |
| **Electrical** | Lighting, Panel, Wiring | Licensed (License #) |
| **Photography** | Portrait, Wedding, Event | Basic (Portfolio 5+) |

---

## 4. Technical Requirements

### 4.1 Data Models
- **ProviderEnrollment**: Document-style storage for the multi-step onboarding data.
- **ServiceCatalog**: JSON-based reference for valid services and price ranges.

### 4.2 Enrollment Agent (LLM)
- **Role**: `enrollment`.
- **System Prompt**: Guidance on conversational data collection and tool usage.
- **Tools**: `update_profile`, `add_service`, `set_availability`, `add_portfolio_photo`, `submit_enrollment`.

### 4.3 Verification Engine
- Logic to check profile completeness (Name, 3+ Photos, Pricing, Hours).
- Flag licensed services for manual review.

---

## 5. UI Design (MVP)

- **Entry State**: A premium "Start Earning" card on the Get Leads tab.
- **Conversation UI**: Uses the existing Dark Mode chat theme with tailored cards for service selection and summary.
- **Action Cards**: Inline checklists for services and multi-photo upload grids.
- **Status Screens**: "Verification in Progress" state with progress steps.

---

## 6. Success Criteria
- ✅ Any new user can complete enrollment via chat.
- ✅ Services are mapped to structured DB types.
- ✅ Portfolio photos are stored and linked to the provider.
- ✅ Auto-verification activates the Provider Agent for compliant profiles.
