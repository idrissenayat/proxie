# Provider Enrollment Quick Reference

## Overview
The Provider Enrollment system enables professionals to self-onboard through a conversational AI experience, with automatic verification for basic services.

---

## User Journey

```
Dashboard → "Become a Provider" → Chat with Agent → Complete Profile → Auto-Verify → Start Receiving Leads
```

**Time to Complete:** 5-10 minutes  
**Verification:** Instant for basic services (haircut, cleaning, etc.)

---

## Enrollment Steps

### 1. Basic Information
**Agent asks for:**
- Full name
- Business name (optional)
- Phone number
- Email address

**Example:**
```
Agent: "What's your full name?"
User: "Maria Garcia"
Agent: "Great! What's your business name?"
User: "Maria's Hair Studio"
```

### 2. Service Selection
**Agent shows Service Selector UI with:**
- Categories (Hair & Beauty, Cleaning, Plumbing, etc.)
- Services within each category
- Typical price ranges

**User actions:**
- Click category → View services
- Select services (checkboxes)
- Click "Done with [Category]"

### 3. Pricing & Duration
**Agent collects for each service:**
- Your price
- Service duration

**Example:**
```
Agent: "What do you charge for a haircut?"
User: "$45 for 45 minutes"
```

### 4. Location & Radius
**Agent asks:**
- Your location (city/address)
- Service radius (miles)

**Example:**
```
Agent: "Where are you located?"
User: "123 Main St, Brooklyn, NY"
Agent: "How far will you travel?"
User: "10 miles"
```

### 5. Availability
**Agent collects:**
- Days of the week
- Hours available

**Example:**
```
Agent: "When are you available?"
User: "Monday to Friday, 9am to 6pm. Saturdays 10am to 4pm"
```

### 6. Portfolio (Optional)
**Agent triggers Portfolio Uploader:**
- Add 3-10 photos of your work
- Camera or gallery upload
- Agent uses vision to describe your work

**Recommended:** At least 3 photos for better matching

### 7. Bio
**Agent helps draft:**
- Years of experience
- Specializations
- Unique selling points

**Example:**
```
Agent: "Tell me about your experience"
User: "I've been cutting hair for 15 years, specializing in curly cuts and balayage"
Agent: "Perfect! Here's a draft bio: [shows draft]"
```

### 8. Review & Submit
**Agent shows Enrollment Summary Card:**
- All collected information
- Edit or Submit buttons

**Click Submit** → Verification runs → Provider activated!

---

## Verification Rules

### Auto-Verified (Instant)
✅ Services with `requires_license: false`
- Haircut
- Hair Color
- Standard Cleaning
- Portrait Photography

**Result:** Provider created immediately, can receive leads

### Manual Review (24-48 hours)
⏳ Services with `requires_license: true`
- Plumbing
- Electrical
- Licensed trades

**Result:** Status = "Pending Verification", admin review required

---

## Data Collected

| Field | Required | Type |
|-------|----------|------|
| Full Name | ✅ | String |
| Business Name | ❌ | String |
| Email | ✅ | String |
| Phone | ✅ | String |
| Services | ✅ | Array |
| Pricing | ✅ | Per service |
| Location | ✅ | Object |
| Service Radius | ✅ | Number (miles) |
| Availability | ✅ | Object |
| Portfolio | ❌ | Array of images |
| Bio | ✅ | String |

---

## Service Catalog Structure

```json
{
  "categories": [
    {
      "id": "hair_beauty",
      "name": "Hair & Beauty",
      "icon": "Scissors",
      "verification_level": "basic",
      "services": [
        {
          "id": "haircut",
          "name": "Haircut",
          "typical_price_range": {"min": 30, "max": 100},
          "requires_license": false,
          "min_photos": 3,
          "specializations": ["Men's cuts", "Women's cuts", "Curly hair"]
        }
      ]
    }
  ]
}
```

---

## Agent Tools

The enrollment agent has access to:

| Tool | Purpose |
|------|---------|
| `get_service_catalog` | Show service categories and options |
| `update_enrollment` | Save collected data incrementally |
| `request_portfolio` | Trigger photo upload UI |
| `get_enrollment_summary` | Generate review card |
| `submit_enrollment` | Finalize and verify |

---

## UI Components

### ServiceSelector
- **Location:** Chat message bubble
- **Interaction:** Click category → Select services → Done
- **State:** Selected services show checkmark

### PortfolioUploader
- **Location:** Chat message bubble
- **Actions:** Add Photo, Take Photo, Remove
- **Limit:** 10 photos max

### EnrollmentSummaryCard
- **Location:** Chat message bubble
- **Content:** All enrollment data formatted
- **Actions:** Edit (back to chat), Submit (verify)

---

## Error Handling

### Incomplete Submission
**Error:** "Enrollment incomplete. Missing: [fields]"
**Solution:** Agent guides user to provide missing info

### Duplicate Email
**Behavior:** Links to existing provider record
**Message:** "Welcome back! Updating your profile..."

### Invalid Data
**Validation:** Pydantic schemas catch issues
**Response:** Agent asks for correction

---

## Post-Enrollment

### If Auto-Verified
1. Provider record created
2. Status = `active`, Verified = `true`
3. Dashboard shows "Get Leads" view
4. Can immediately receive and respond to requests

### If Manual Review
1. Enrollment status = `pending_verification`
2. Dashboard shows "Verification Pending" message
3. Email notification sent (future)
4. Admin reviews within 24-48 hours

---

## Testing Checklist

- [ ] Start enrollment from dashboard
- [ ] Complete all steps with agent
- [ ] Service selector shows services
- [ ] Portfolio uploader appears
- [ ] Summary card displays correctly
- [ ] Submit triggers verification
- [ ] Auto-verify creates provider
- [ ] Dashboard updates to provider view

---

## Common Questions

**Q: Can I edit my profile after enrollment?**  
A: Yes, through the provider dashboard (future feature)

**Q: How long does verification take?**  
A: Instant for basic services, 24-48 hours for licensed services

**Q: Can I offer multiple services?**  
A: Yes, select as many as you want from the catalog

**Q: What if my service isn't listed?**  
A: Contact support to add new services (future feature)

**Q: Do I need a business name?**  
A: No, you can operate under your personal name

**Q: Can I change my pricing later?**  
A: Yes, through the provider dashboard (future feature)

---

## Technical Details

### Database Tables
- `provider_enrollments` - Tracks enrollment state
- `providers` - Permanent provider records
- `provider_lead_views` - Analytics on lead engagement

### API Endpoints
- `POST /enrollment/start` - Create session
- `PATCH /enrollment/{id}` - Update data
- `POST /enrollment/{id}/submit` - Verify
- `GET /enrollment/{id}` - Check status

### Frontend State
- `enrollment_id` - Stored in localStorage
- `provider_id` - Stored after verification
- Chat session maintains enrollment context

---

## Future Enhancements

- [ ] ID verification for licensed services
- [ ] Background checks integration
- [ ] Video portfolio support
- [ ] Multi-language support
- [ ] SMS verification
- [ ] Social proof (reviews from other platforms)
- [ ] Skill assessments
- [ ] Onboarding analytics dashboard

---

**Need Help?** See [Testing Guide](../testing/README.md) or [API Documentation](../api/README.md)
