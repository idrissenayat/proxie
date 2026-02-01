# Proxie Agent Architecture v2: Specification & Implementation Plan

**Document Type:** Technical Specification + Implementation Plan  
**Prepared For:** AntiGravity Engineering Team  
**Date:** January 28, 2026  
**Priority:** High - Core Platform Capability  
**Estimated Total Effort:** 4-6 weeks

---

## Executive Summary

This document specifies the complete agent ecosystem for Proxie, transforming it from a single-agent chatbot into a true multi-agent marketplace where personalized AI agents represent both consumers and providers, coordinated by a platform orchestrator and supported by domain specialists.

### Vision

> Every user gets their own AI agent that learns their preferences and advocates for their interests. These agents communicate with each other through the platform to negotiate and complete transactions seamlessly.

---

## Part 1: Agent Architecture Specification

### 1.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROXIE AGENT ARCHITECTURE v2                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAYER 1: USER-FACING AGENTS (Conversational Interface)                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  CONSUMER SIDE                      PROVIDER SIDE                   │   │
│  │  ┌─────────────┐ ┌─────────────┐   ┌─────────────┐ ┌─────────────┐ │   │
│  │  │   GUEST     │ │  PERSONAL   │   │ ENROLLMENT  │ │  PERSONAL   │ │   │
│  │  │   AGENT     │ │  CONSUMER   │   │   AGENT     │ │  PROVIDER   │ │   │
│  │  │             │ │   AGENT     │   │             │ │   AGENT     │ │   │
│  │  │ • Welcome   │ │             │   │ • Onboard   │ │             │ │   │
│  │  │ • Qualify   │ │ • Remember  │   │ • Collect   │ │ • Leads     │ │   │
│  │  │ • Convert   │ │ • Suggest   │   │ • Verify    │ │ • Insights  │ │   │
│  │  │             │ │ • Advocate  │   │             │ │ • Optimize  │ │   │
│  │  └──────┬──────┘ └──────┬──────┘   └──────┬──────┘ └──────┬──────┘ │   │
│  │         │               │                 │               │         │   │
│  │         └───────┬───────┘                 └───────┬───────┘         │   │
│  │                 │                                 │                  │   │
│  └─────────────────┼─────────────────────────────────┼──────────────────┘   │
│                    │                                 │                      │
│                    ▼                                 ▼                      │
│  LAYER 2: PLATFORM ORCHESTRATOR                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │                      ORCHESTRATOR                                   │   │
│  │                                                                      │   │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │   │
│  │   │   ROUTER     │  │   HANDOFF    │  │    A2A       │             │   │
│  │   │              │  │   MANAGER    │  │  PROTOCOL    │             │   │
│  │   │ • Intent     │  │              │  │              │             │   │
│  │   │   detection  │  │ • Guest →    │  │ • Request    │             │   │
│  │   │ • Agent      │  │   Personal   │  │   quotes     │             │   │
│  │   │   selection  │  │ • Enrollment │  │ • Negotiate  │             │   │
│  │   │ • Context    │  │   → Personal │  │ • Confirm    │             │   │
│  │   │   injection  │  │ • Context    │  │   bookings   │             │   │
│  │   │              │  │   transfer   │  │              │             │   │
│  │   └──────────────┘  └──────────────┘  └──────────────┘             │   │
│  │                                                                      │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  LAYER 3: SPECIALIST CONSULTANTS (Domain Expertise - Non-conversational)   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐           │   │
│  │  │  HAIRCUT  │ │ CLEANING  │ │ PLUMBING  │ │   PHOTO   │  • • •    │   │
│  │  │ SPECIALIST│ │ SPECIALIST│ │ SPECIALIST│ │ SPECIALIST│           │   │
│  │  │           │ │           │ │           │ │           │           │   │
│  │  │ • Analyze │ │ • Estimate│ │ • Diagnose│ │ • Assess  │           │   │
│  │  │ • Price   │ │ • Price   │ │ • Price   │ │ • Price   │           │   │
│  │  │ • Advise  │ │ • Advise  │ │ • Advise  │ │ • Advise  │           │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘           │   │
│  │                                                                      │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  LAYER 4: MEMORY & LEARNING LAYER                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐              │   │
│  │  │   CONSUMER    │ │   PROVIDER    │ │  SPECIALIST   │              │   │
│  │  │    MEMORY     │ │    MEMORY     │ │  KNOWLEDGE    │              │   │
│  │  │               │ │               │ │     BASE      │              │   │
│  │  │ • Preferences │ │ • Performance │ │               │              │   │
│  │  │ • History     │ │ • Pricing     │ │ • Domain data │              │   │
│  │  │ • Style       │ │ • Patterns    │ │ • Benchmarks  │              │   │
│  │  │ • Favorites   │ │ • Feedback    │ │ • Best practs │              │   │
│  │  └───────────────┘ └───────────────┘ └───────────────┘              │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 Agent Definitions

#### 1.2.1 Guest Agent (Consumer Side)

**Purpose:** Welcome new visitors, understand their needs, and convert them to registered users.

**Characteristics:**
| Attribute | Value |
|-----------|-------|
| Memory | Session-only (Redis, 24hr TTL) |
| Personalization | None - generic helpful persona |
| Primary Goal | Qualify need → Demonstrate value → Convert to signup |
| Tools | `create_service_request`, `search_providers`, `show_signup_prompt` |

**System Prompt Core:**
```
You are Proxie, a friendly AI concierge helping someone find a service provider.
This is a guest user - you don't know anything about them yet.

Your goals:
1. Understand what service they need
2. Show them how easy Proxie makes finding providers
3. Encourage them to create an account to save their preferences

Be warm, efficient, and demonstrate value quickly. After helping them create 
their first request, suggest signing up to track it and get personalized 
recommendations in the future.
```

**Transition Trigger:** User completes Clerk signup → Hand off to Personal Consumer Agent

---

#### 1.2.2 Personal Consumer Agent

**Purpose:** Serve as the user's dedicated AI assistant that learns their preferences and advocates for their interests.

**Characteristics:**
| Attribute | Value |
|-----------|-------|
| Memory | Persistent (PostgreSQL + Vector embeddings) |
| Personalization | High - learns from every interaction |
| Primary Goal | Maximize user satisfaction and booking success |
| Tools | All consumer tools + `recall_preferences`, `update_preferences`, `get_booking_history`, `suggest_providers` |

**System Prompt Core:**
```
You are {user_name}'s personal Proxie assistant. You remember their preferences
and past experiences to provide increasingly personalized service.

What you know about {user_name}:
{memory_context}

Your goals:
1. Use their history to make better recommendations
2. Remember details they've shared (budget, style preferences, schedule)
3. Proactively suggest services based on patterns
4. Advocate for them when reviewing offers

Be proactive: "I noticed you usually book haircuts every 6 weeks - would you 
like me to find availability for next week?"
```

**Memory Schema:**
```python
class ConsumerMemory(BaseModel):
    user_id: UUID
    
    # Explicit preferences (user stated)
    preferred_budget_range: Optional[dict]  # {"min": 50, "max": 150}
    preferred_timing: Optional[str]  # "weekends", "evenings", "flexible"
    communication_style: Optional[str]  # "brief", "detailed", "friendly"
    
    # Learned preferences (inferred from behavior)
    favorite_providers: List[UUID]
    service_frequency: dict  # {"haircut": "6 weeks", "cleaning": "2 weeks"}
    quality_vs_price: str  # "quality_focused", "price_sensitive", "balanced"
    
    # Interaction history
    total_bookings: int
    total_requests: int
    avg_rating_given: float
    last_interaction: datetime
    
    # Embeddings for semantic matching
    preference_embedding: List[float]  # 1536-dim vector
```

---

#### 1.2.3 Enrollment Agent (Provider Side)

**Purpose:** Guide new providers through the onboarding process conversationally.

**Characteristics:**
| Attribute | Value |
|-----------|-------|
| Memory | Session + Enrollment record |
| Personalization | Adapts to provider's service category |
| Primary Goal | Complete enrollment with high-quality data |
| Tools | `get_service_catalog`, `update_enrollment`, `validate_enrollment`, `submit_enrollment` |

**Current State:** ✅ Fully implemented

**Transition Trigger:** Enrollment verified → Create Personal Provider Agent instance

---

#### 1.2.4 Personal Provider Agent

**Purpose:** Help providers manage their business, optimize pricing, and deliver better service.

**Characteristics:**
| Attribute | Value |
|-----------|-------|
| Memory | Persistent (PostgreSQL + Analytics) |
| Personalization | High - learns business patterns |
| Primary Goal | Maximize provider success (bookings, ratings, revenue) |
| Tools | `get_leads`, `suggest_offer`, `analyze_performance`, `optimize_schedule`, `get_market_insights` |

**System Prompt Core:**
```
You are the business assistant for {provider_name}, a {service_type} provider on Proxie.

Business snapshot:
- Jobs completed: {jobs_completed}
- Average rating: {avg_rating}
- Response rate: {response_rate}
- This week's leads: {lead_count}

Your goals:
1. Help them respond to leads quickly and effectively
2. Suggest competitive but profitable pricing
3. Identify patterns that affect their success
4. Proactively alert them to opportunities

Be a trusted business advisor: "Your response time has improved to 2 hours - 
that's helping your conversion rate. I noticed 3 new leads in your area today."
```

**Memory Schema:**
```python
class ProviderMemory(BaseModel):
    provider_id: UUID
    
    # Performance metrics
    total_leads_received: int
    total_offers_sent: int
    total_bookings: int
    conversion_rate: float  # offers → bookings
    avg_response_time_hours: float
    
    # Pricing intelligence
    pricing_history: List[dict]  # [{"service": "haircut", "price": 75, "won": True}]
    market_position: str  # "premium", "mid-market", "budget"
    price_sensitivity: float  # How much price affects their win rate
    
    # Schedule patterns
    busiest_days: List[str]
    preferred_hours: dict
    avg_job_duration: dict  # by service type
    
    # Customer feedback themes
    positive_themes: List[str]  # ["punctual", "skilled", "friendly"]
    improvement_areas: List[str]  # ["communication", "cleanup"]
    
    # Business goals (provider-stated)
    weekly_booking_target: Optional[int]
    revenue_target: Optional[float]
```

---

#### 1.2.5 Specialist Agents

**Purpose:** Provide deep domain expertise that other agents consult for analysis, pricing, and quality assessment.

**Characteristics:**
| Attribute | Value |
|-----------|-------|
| Memory | Knowledge base (not conversational memory) |
| Interface | Consultation API (not direct user chat) |
| Primary Goal | Provide accurate domain-specific analysis |
| Consumers | Personal agents, Orchestrator |

**Specialist Interface:**
```python
class SpecialistConsultation(BaseModel):
    """Request format for specialist consultation"""
    query_type: str  # "analyze", "price", "validate", "recommend"
    service_category: str
    context: dict  # Request details, photos, preferences
    requestor: str  # "consumer_agent", "provider_agent", "orchestrator"

class SpecialistResponse(BaseModel):
    """Response format from specialist"""
    analysis: Optional[dict]  # Domain-specific analysis
    price_range: Optional[dict]  # {"min": X, "max": Y, "recommended": Z}
    recommendations: List[str]
    warnings: List[str]  # Red flags or concerns
    confidence: float  # 0-1 confidence in analysis
    follow_up_questions: List[str]  # Questions to ask user
```

**Haircut Specialist Knowledge Base:**
```yaml
haircut_specialist:
  capabilities:
    - Identify hair type from photos (1A-4C curl patterns)
    - Assess hair health (porosity, damage, thickness)
    - Recommend appropriate services
    - Estimate pricing by complexity
    - Flag quality concerns in provider portfolios
  
  pricing_factors:
    - hair_length: [short: 1.0, medium: 1.2, long: 1.5]
    - curl_pattern: [straight: 1.0, wavy: 1.1, curly: 1.3, coily: 1.4]
    - service_type: [trim: 0.8, full_cut: 1.0, color: 1.5, treatment: 1.3]
    - provider_experience: [junior: 0.8, mid: 1.0, senior: 1.3, master: 1.6]
  
  quality_indicators:
    positive:
      - Even, clean lines in portfolio photos
      - Diverse hair types in portfolio
      - Before/after consistency
    negative:
      - Blurry or poorly lit photos
      - Limited portfolio variety
      - No curl-specific examples for curl services
```

---

### 1.3 Platform Orchestrator

**Purpose:** Route conversations, manage agent handoffs, and coordinate agent-to-agent communication.

#### 1.3.1 Router Component

```python
class AgentRouter:
    """Determines which agent should handle the current interaction"""
    
    async def route(self, session: Session, message: Message) -> AgentType:
        # Check user authentication status
        if not session.user_id:
            return AgentType.GUEST_CONSUMER
        
        # Check user role
        user = await get_user(session.user_id)
        
        if user.role == "consumer":
            return AgentType.PERSONAL_CONSUMER
        
        if user.role == "provider":
            # Check if enrolled
            if user.provider.is_verified:
                return AgentType.PERSONAL_PROVIDER
            else:
                return AgentType.ENROLLMENT
        
        # Check for explicit routing hints
        if session.context.get("force_agent"):
            return session.context["force_agent"]
        
        return AgentType.GUEST_CONSUMER
```

#### 1.3.2 Handoff Manager

```python
class HandoffManager:
    """Manages transitions between agents with context preservation"""
    
    async def handoff(
        self, 
        from_agent: AgentType, 
        to_agent: AgentType, 
        session: Session,
        reason: str
    ) -> HandoffResult:
        
        # 1. Extract transferable context from source agent
        context = await self.extract_context(from_agent, session)
        
        # 2. Generate handoff summary for destination agent
        summary = await self.generate_summary(context, reason)
        
        # 3. Initialize destination agent with context
        new_session = await self.initialize_agent(to_agent, session.user_id, summary)
        
        # 4. Archive source session
        await self.archive_session(session)
        
        # 5. Send transition message to user
        transition_message = self.get_transition_message(from_agent, to_agent, reason)
        
        return HandoffResult(
            new_session=new_session,
            transition_message=transition_message
        )
    
    def get_transition_message(self, from_agent, to_agent, reason) -> str:
        templates = {
            (AgentType.GUEST_CONSUMER, AgentType.PERSONAL_CONSUMER): 
                "Welcome back, {name}! I've got your preferences loaded and ready to help.",
            (AgentType.ENROLLMENT, AgentType.PERSONAL_PROVIDER):
                "Congratulations on joining Proxie! I'm now your dedicated business assistant.",
        }
        return templates.get((from_agent, to_agent), "I'm here to help!")
```

#### 1.3.3 Agent-to-Agent Protocol

```python
class A2AProtocol:
    """Handles communication between consumer and provider agents"""
    
    class MessageType(Enum):
        REQUEST_QUOTE = "request_quote"
        QUOTE_RESPONSE = "quote_response"
        NEGOTIATE = "negotiate"
        ACCEPT = "accept"
        DECLINE = "decline"
        CONFIRM_BOOKING = "confirm_booking"
    
    async def request_quote(
        self,
        consumer_agent: PersonalConsumerAgent,
        provider_ids: List[UUID],
        request: ServiceRequest
    ) -> List[QuoteResponse]:
        """Consumer agent requests quotes from multiple provider agents"""
        
        quotes = []
        for provider_id in provider_ids:
            provider_agent = await self.get_provider_agent(provider_id)
            
            # Prepare request context
            quote_request = QuoteRequest(
                service_type=request.service_type,
                description=request.description,
                location=request.location,
                timing=request.timing_flexibility,
                budget_hint=request.budget_max,  # Optional hint
                consumer_preferences=consumer_agent.get_relevant_preferences()
            )
            
            # Provider agent generates quote
            quote = await provider_agent.generate_quote(quote_request)
            quotes.append(quote)
        
        return quotes
    
    async def negotiate(
        self,
        consumer_agent: PersonalConsumerAgent,
        provider_agent: PersonalProviderAgent,
        offer_id: UUID,
        counter_proposal: dict
    ) -> NegotiationResult:
        """Facilitate negotiation between agents"""
        
        # Consumer agent's position
        consumer_position = consumer_agent.evaluate_counter_position(counter_proposal)
        
        # Provider agent's response
        provider_response = await provider_agent.respond_to_negotiation(
            offer_id=offer_id,
            counter_proposal=counter_proposal,
            consumer_context=consumer_position
        )
        
        return NegotiationResult(
            status=provider_response.status,  # "accepted", "countered", "declined"
            updated_offer=provider_response.updated_offer,
            message=provider_response.message
        )
```

---

### 1.4 Memory Layer Specification

#### 1.4.1 Database Schema Additions

```sql
-- Consumer Memory Table
CREATE TABLE consumer_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id UUID NOT NULL REFERENCES consumers(id) ON DELETE CASCADE,
    
    -- Explicit preferences
    preferred_budget_min DECIMAL(10,2),
    preferred_budget_max DECIMAL(10,2),
    preferred_timing VARCHAR(50),
    communication_style VARCHAR(50),
    
    -- Learned preferences (JSON for flexibility)
    learned_preferences JSONB DEFAULT '{}'::jsonb,
    
    -- Interaction stats
    total_bookings INTEGER DEFAULT 0,
    total_requests INTEGER DEFAULT 0,
    avg_rating_given DECIMAL(3,2),
    
    -- Embeddings
    preference_embedding VECTOR(1536),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_consumer_memory_embedding 
ON consumer_memories USING ivfflat(preference_embedding vector_cosine_ops);

-- Provider Memory Table  
CREATE TABLE provider_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    
    -- Performance metrics
    total_leads_received INTEGER DEFAULT 0,
    total_offers_sent INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,4) DEFAULT 0,
    avg_response_time_hours DECIMAL(6,2),
    
    -- Pricing intelligence
    pricing_history JSONB DEFAULT '[]'::jsonb,
    market_position VARCHAR(50),
    
    -- Schedule patterns
    schedule_patterns JSONB DEFAULT '{}'::jsonb,
    
    -- Feedback analysis
    feedback_themes JSONB DEFAULT '{}'::jsonb,
    
    -- Goals
    weekly_booking_target INTEGER,
    revenue_target DECIMAL(10,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Specialist Knowledge Base Table
CREATE TABLE specialist_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specialist_type VARCHAR(100) NOT NULL,  -- 'haircut', 'cleaning', etc.
    
    -- Knowledge content
    pricing_rules JSONB NOT NULL,
    quality_indicators JSONB NOT NULL,
    domain_vocabulary JSONB DEFAULT '{}'::jsonb,
    
    -- Learned patterns
    successful_patterns JSONB DEFAULT '[]'::jsonb,
    regional_adjustments JSONB DEFAULT '{}'::jsonb,
    
    -- Versioning
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent Interaction Log (for learning)
CREATE TABLE agent_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    user_id UUID,
    
    -- Interaction details
    interaction_type VARCHAR(50),  -- 'request', 'offer', 'booking', 'feedback'
    input_summary TEXT,
    output_summary TEXT,
    tools_used JSONB DEFAULT '[]'::jsonb,
    
    -- Outcome tracking
    outcome VARCHAR(50),  -- 'success', 'abandoned', 'error'
    user_satisfaction INTEGER,  -- 1-5 if feedback given
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_interactions_user ON agent_interactions(user_id);
CREATE INDEX idx_interactions_type ON agent_interactions(agent_type, interaction_type);
```

#### 1.4.2 Memory Service

```python
class MemoryService:
    """Unified interface for agent memory operations"""
    
    async def get_consumer_context(self, consumer_id: UUID) -> ConsumerContext:
        """Retrieve full context for Personal Consumer Agent"""
        
        memory = await self.db.get_consumer_memory(consumer_id)
        recent_bookings = await self.db.get_recent_bookings(consumer_id, limit=5)
        recent_requests = await self.db.get_recent_requests(consumer_id, limit=5)
        favorite_providers = await self.db.get_favorite_providers(consumer_id)
        
        return ConsumerContext(
            memory=memory,
            recent_bookings=recent_bookings,
            recent_requests=recent_requests,
            favorites=favorite_providers,
            summary=self._generate_context_summary(memory, recent_bookings)
        )
    
    async def update_consumer_memory(
        self, 
        consumer_id: UUID, 
        interaction: AgentInteraction
    ):
        """Update consumer memory based on interaction"""
        
        memory = await self.db.get_consumer_memory(consumer_id)
        
        # Update stats
        if interaction.outcome == "booking":
            memory.total_bookings += 1
        
        # Learn preferences from behavior
        if interaction.tools_used:
            self._infer_preferences(memory, interaction)
        
        # Update embedding if preferences changed significantly
        if self._should_update_embedding(memory):
            memory.preference_embedding = await self._compute_embedding(memory)
        
        await self.db.save_consumer_memory(memory)
    
    async def get_provider_context(self, provider_id: UUID) -> ProviderContext:
        """Retrieve full context for Personal Provider Agent"""
        
        memory = await self.db.get_provider_memory(provider_id)
        recent_leads = await self.db.get_recent_leads(provider_id, limit=10)
        performance = await self._compute_performance_metrics(provider_id)
        market_data = await self._get_market_comparison(provider_id)
        
        return ProviderContext(
            memory=memory,
            recent_leads=recent_leads,
            performance=performance,
            market_position=market_data,
            insights=self._generate_insights(memory, performance)
        )
    
    async def consult_specialist(
        self,
        specialist_type: str,
        consultation: SpecialistConsultation
    ) -> SpecialistResponse:
        """Query specialist knowledge base"""
        
        knowledge = await self.db.get_specialist_knowledge(specialist_type)
        
        # Apply domain-specific analysis
        if consultation.query_type == "analyze":
            return await self._specialist_analyze(knowledge, consultation)
        elif consultation.query_type == "price":
            return await self._specialist_price(knowledge, consultation)
        elif consultation.query_type == "validate":
            return await self._specialist_validate(knowledge, consultation)
        
        raise ValueError(f"Unknown query type: {consultation.query_type}")
```

---

## Part 2: Implementation Plan

### 2.1 Phase Overview

| Phase | Focus | Duration | Dependencies |
|-------|-------|----------|--------------|
| **Phase 1** | Memory Layer Foundation | 1 week | None |
| **Phase 2** | Personal Consumer Agent | 1 week | Phase 1 |
| **Phase 3** | Personal Provider Agent | 1 week | Phase 1 |
| **Phase 4** | Orchestrator Enhancements | 1 week | Phases 2, 3 |
| **Phase 5** | Additional Specialists | 1-2 weeks | Phase 4 |
| **Phase 6** | Agent-to-Agent Protocol | 1 week | Phase 4 |

---

### 2.2 Phase 1: Memory Layer Foundation (Week 1)

**Goal:** Build the data infrastructure that enables agents to learn and remember.

#### Tasks

| ID | Task | Effort | Owner |
|----|------|--------|-------|
| M1-1 | Create database migration for memory tables | 0.5d | Backend |
| M1-2 | Implement `ConsumerMemory` model and repository | 1d | Backend |
| M1-3 | Implement `ProviderMemory` model and repository | 1d | Backend |
| M1-4 | Implement `SpecialistKnowledge` model and repository | 0.5d | Backend |
| M1-5 | Create `MemoryService` with CRUD operations | 1d | Backend |
| M1-6 | Add embedding generation for preferences | 0.5d | AI |
| M1-7 | Write unit tests for memory layer | 0.5d | Backend |

#### Deliverables
- [ ] Database tables created and migrated
- [ ] Memory service with full CRUD
- [ ] Embedding generation working
- [ ] 80%+ test coverage on memory layer

#### Acceptance Criteria
```python
# Should be able to:
memory = await memory_service.get_consumer_context(consumer_id)
assert memory.recent_bookings is not None
assert memory.preference_embedding is not None

await memory_service.update_consumer_memory(consumer_id, interaction)
updated = await memory_service.get_consumer_context(consumer_id)
assert updated.total_bookings == memory.total_bookings + 1
```

---

### 2.3 Phase 2: Personal Consumer Agent (Week 2)

**Goal:** Transform the generic consumer agent into a personalized assistant.

#### Tasks

| ID | Task | Effort | Owner |
|----|------|--------|-------|
| C1-1 | Define Personal Consumer Agent system prompt template | 0.5d | AI |
| C1-2 | Implement `recall_preferences` tool | 0.5d | Backend |
| C1-3 | Implement `update_preferences` tool | 0.5d | Backend |
| C1-4 | Implement `get_booking_history` tool | 0.5d | Backend |
| C1-5 | Implement `suggest_providers` tool (uses embeddings) | 1d | AI |
| C1-6 | Update ChatService to inject memory context | 1d | Backend |
| C1-7 | Implement proactive suggestion logic | 1d | AI |
| C1-8 | Write integration tests | 0.5d | QA |

#### Deliverables
- [ ] Personal Consumer Agent with memory access
- [ ] Proactive suggestions based on history
- [ ] Preference learning from interactions

#### Acceptance Criteria
```gherkin
Scenario: Agent remembers user preferences
  Given I am a registered user with 3 past haircut bookings
  When I say "I need a haircut"
  Then the agent should mention my usual preferences
  And suggest providers I've used before or similar ones

Scenario: Agent learns from interactions
  Given I consistently book weekend appointments
  When I create a new request
  Then the agent should default to weekend timing
```

---

### 2.4 Phase 3: Personal Provider Agent (Week 3)

**Goal:** Create a business assistant that helps providers succeed.

#### Tasks

| ID | Task | Effort | Owner |
|----|------|--------|-------|
| P1-1 | Define Personal Provider Agent system prompt template | 0.5d | AI |
| P1-2 | Implement `analyze_performance` tool | 1d | Backend |
| P1-3 | Implement `get_market_insights` tool | 1d | Backend |
| P1-4 | Implement `optimize_schedule` tool | 1d | Backend |
| P1-5 | Implement `suggest_pricing` tool (uses market data) | 1d | AI |
| P1-6 | Update ChatService for provider context injection | 0.5d | Backend |
| P1-7 | Implement proactive business alerts | 1d | AI |
| P1-8 | Write integration tests | 0.5d | QA |

#### Deliverables
- [ ] Personal Provider Agent with business insights
- [ ] Performance analytics accessible via chat
- [ ] Pricing suggestions based on market data

#### Acceptance Criteria
```gherkin
Scenario: Agent provides business insights
  Given I am a verified provider with 10+ completed jobs
  When I ask "How am I doing?"
  Then the agent should show my conversion rate
  And compare my response time to successful providers
  And suggest improvements if applicable

Scenario: Agent suggests competitive pricing
  Given there is a new lead in my area
  When I ask the agent for pricing advice
  Then it should analyze similar recent bookings
  And suggest a price range with reasoning
```

---

### 2.5 Phase 4: Orchestrator Enhancements (Week 4)

**Goal:** Upgrade the orchestrator to handle handoffs and multi-agent coordination.

#### Tasks

| ID | Task | Effort | Owner |
|----|------|--------|-------|
| O1-1 | Implement `HandoffManager` class | 1d | Backend |
| O1-2 | Add Guest → Personal Consumer handoff | 0.5d | Backend |
| O1-3 | Add Enrollment → Personal Provider handoff | 0.5d | Backend |
| O1-4 | Implement context extraction and summarization | 1d | AI |
| O1-5 | Update LangGraph routing logic | 1d | Backend |
| O1-6 | Add handoff events to WebSocket | 0.5d | Backend |
| O1-7 | Update frontend for agent transitions | 0.5d | Frontend |
| O1-8 | Write E2E tests for handoffs | 0.5d | QA |

#### Deliverables
- [ ] Seamless handoffs between agent types
- [ ] Context preserved across transitions
- [ ] User notified of agent changes

#### Acceptance Criteria
```gherkin
Scenario: Guest to Personal Consumer handoff
  Given I am chatting as a guest
  And I have described my service need
  When I complete Clerk signup
  Then I should be greeted by my personal agent
  And my request should still be in context
  And the agent should know my name
```

---

### 2.6 Phase 5: Additional Specialists (Weeks 5-6)

**Goal:** Expand domain expertise beyond haircuts.

#### Tasks (per specialist)

| ID | Task | Effort | Owner |
|----|------|--------|-------|
| S1-1 | Research domain (pricing, terminology, quality indicators) | 0.5d | Product |
| S1-2 | Create knowledge base JSON/YAML | 0.5d | Product |
| S1-3 | Implement specialist consultation logic | 1d | AI |
| S1-4 | Train/tune analysis prompts | 1d | AI |
| S1-5 | Add to service catalog | 0.5d | Backend |
| S1-6 | Write specialist tests | 0.5d | QA |

**Specialists to build:**
1. **Cleaning Specialist** (Week 5)
2. **Plumbing Specialist** (Week 5)
3. **Photography Specialist** (Week 6)

#### Deliverables
- [ ] 3 new specialists operational
- [ ] Knowledge bases documented
- [ ] Consultation API working for all

---

### 2.7 Phase 6: Agent-to-Agent Protocol (Week 6-7)

**Goal:** Enable consumer and provider agents to communicate directly for negotiation.

#### Tasks

| ID | Task | Effort | Owner |
|----|------|--------|-------|
| A1-1 | Define A2A message types and schemas | 0.5d | Backend |
| A1-2 | Implement `A2AProtocol` class | 1d | Backend |
| A1-3 | Implement `request_quote` flow | 1d | Backend |
| A1-4 | Implement `negotiate` flow | 1d | Backend |
| A1-5 | Implement `confirm_booking` flow | 0.5d | Backend |
| A1-6 | Add A2A events to activity log | 0.5d | Backend |
| A1-7 | Update UI to show agent negotiation status | 1d | Frontend |
| A1-8 | Write E2E tests for full flow | 1d | QA |

#### Deliverables
- [ ] Consumer agent can request quotes from multiple providers
- [ ] Provider agents respond with personalized offers
- [ ] Negotiation possible through agents
- [ ] Full booking flow via agent communication

#### Acceptance Criteria
```gherkin
Scenario: Agent-to-agent quote request
  Given I have created a haircut request
  And 3 providers match my criteria
  When my agent requests quotes
  Then each provider's agent should generate a personalized offer
  And I should see all 3 offers with reasoning

Scenario: Agent-assisted negotiation
  Given I received an offer for $100
  When I say "That's a bit high, can we do $80?"
  Then my agent should negotiate with the provider's agent
  And return with a counter-offer or acceptance
```

---

### 2.8 Implementation Timeline

```
Week 1  ████████████████████████████████████████  Memory Layer
Week 2  ████████████████████████████████████████  Personal Consumer Agent
Week 3  ████████████████████████████████████████  Personal Provider Agent
Week 4  ████████████████████████████████████████  Orchestrator Enhancements
Week 5  ████████████████████████████████████████  Cleaning + Plumbing Specialists
Week 6  ████████████████████████████████████████  Photography Specialist + A2A Protocol
Week 7  ████████████████████████████████████████  A2A Protocol + Integration Testing
```

---

## Part 3: Files to Update

### 3.1 Documentation Updates

| File | Changes Required |
|------|------------------|
| `proxie_architecture_main.md` | Add Agent Architecture v2 section, update AI Layer diagram |
| `proxie_architecture_appendices.md` | Add Appendix I: Agent Specifications, Add memory schema to Appendix A |
| `product_backlog.md` | Add new backlog items for each phase |
| `roadmap.md` | Add Phase 3.5: Agent Ecosystem |
| `overview.md` | Update "How It Works" with agent details |

### 3.2 New Files to Create

| File | Purpose |
|------|---------|
| `src/platform/agents/guest_agent.py` | Guest Agent implementation |
| `src/platform/agents/personal_consumer_agent.py` | Personal Consumer Agent |
| `src/platform/agents/personal_provider_agent.py` | Personal Provider Agent |
| `src/platform/agents/specialists/haircut.py` | Haircut Specialist |
| `src/platform/agents/specialists/cleaning.py` | Cleaning Specialist |
| `src/platform/agents/specialists/plumbing.py` | Plumbing Specialist |
| `src/platform/agents/specialists/photography.py` | Photography Specialist |
| `src/platform/services/memory_service.py` | Memory Layer service |
| `src/platform/services/orchestrator.py` | Enhanced orchestrator |
| `src/platform/services/a2a_protocol.py` | Agent-to-Agent protocol |
| `src/platform/models/memory.py` | Memory models |
| `migrations/agent_memory_tables.sql` | Database migration |

### 3.3 Files to Modify

| File | Changes |
|------|---------|
| `src/platform/services/chat.py` | Integrate memory service, update agent routing |
| `src/platform/models/__init__.py` | Export new models |
| `src/platform/main.py` | Register new routers if needed |
| `web/src/pages/ChatPage.jsx` | Handle agent transition UI |
| `web/src/components/Chat/AgentIndicator.jsx` | New component showing which agent is active |

---

## Part 4: Success Metrics

### 4.1 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Memory retrieval latency | <100ms | p95 response time |
| Agent handoff success rate | >99% | Handoffs without context loss |
| Specialist consultation accuracy | >90% | Validated against expert review |
| A2A protocol completion rate | >95% | Quote requests that complete |

### 4.2 Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Guest → Signup conversion | +20% | Compare before/after |
| Repeat booking rate | +15% | Users with 2+ bookings |
| Provider response time | -30% | Average time to first offer |
| User satisfaction (NPS) | +10 points | Post-booking survey |

---

## Part 5: Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Memory bloat over time | Medium | High | Implement memory summarization, TTL on old interactions |
| Specialist accuracy issues | Medium | Medium | Human-in-the-loop validation for first 100 consultations |
| A2A negotiation loops | Low | High | Implement max negotiation rounds, timeout |
| Handoff context loss | Medium | High | Extensive E2E testing, fallback to full context |
| LLM cost increase | High | Medium | Cache specialist responses, optimize prompts |

---

## Appendix: Prompt Templates

### A.1 Guest Agent Prompt

```
You are Proxie, a friendly AI concierge for a service marketplace.

This user is a guest (not logged in). Your goals:
1. Help them find what they need quickly
2. Demonstrate Proxie's value
3. Encourage signup to save preferences

Guidelines:
- Be warm and efficient
- Don't ask for personal details beyond service needs
- After creating a request, mention benefits of signing up
- If they seem ready to book, prompt for account creation

Available tools: {tools}
```

### A.2 Personal Consumer Agent Prompt

```
You are {user_name}'s personal Proxie assistant.

## What you know about {user_name}:
{memory_summary}

## Recent activity:
{recent_bookings_summary}

## Your goals:
1. Use their history to personalize recommendations
2. Remember their preferences without asking repeatedly
3. Proactively suggest services based on patterns
4. Advocate for them when evaluating offers

## Guidelines:
- Greet them by name
- Reference past experiences when relevant
- If suggesting providers, prioritize their favorites
- Be proactive: "Based on your usual schedule, should I look for availability next week?"

Available tools: {tools}
```

### A.3 Personal Provider Agent Prompt

```
You are the business assistant for {provider_name}, a {service_types} provider.

## Business Snapshot:
- Jobs completed: {jobs_completed}
- Rating: {avg_rating} ({review_count} reviews)
- Response rate: {response_rate}%
- Conversion rate: {conversion_rate}%
- Active leads: {active_lead_count}

## Performance Insights:
{performance_insights}

## Your goals:
1. Help them respond to leads quickly
2. Suggest competitive pricing
3. Identify opportunities and risks
4. Provide actionable business advice

## Guidelines:
- Be a trusted business advisor
- Lead with actionable insights
- When showing leads, highlight best matches
- Suggest improvements constructively

Available tools: {tools}
```

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-28 | Architecture Team | Initial specification |

**Next Review:** After Phase 1 completion
