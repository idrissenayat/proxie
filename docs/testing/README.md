# Proxie Testing Guide

## Quick Start

### Prerequisites
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:5173`
- PostgreSQL database initialized

### Test the Complete Flow

## 1. Provider Enrollment (New!)

### Via UI
1. Navigate to `http://localhost:5173`
2. Click **"Get Leads"** tab
3. Click **"Become a Provider"** button
4. Chat with the enrollment agent:
   - Provide name, business name, phone, email
   - Select services from the catalog (e.g., Hair & Beauty → Haircut)
   - Set pricing and duration
   - Add location and service radius
   - Upload portfolio photos (optional)
   - Provide bio
5. Review summary and click **"Submit Enrollment"**
6. Verify you see "Verified" status or "Pending Verification"

### Via API
```bash
# 1. Start enrollment
ENROLLMENT_ID=$(curl -s -X POST http://localhost:8000/enrollment/start | jq -r '.enrollment_id')

# 2. Add enrollment data
curl -X PATCH "http://localhost:8000/enrollment/$ENROLLMENT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Doe",
    "business_name": "Janes Salon",
    "email": "jane@salon.com",
    "phone": "555-5678",
    "services": [{"id": "haircut", "name": "Haircut", "price": 40, "duration": 30}],
    "location": {"city": "Brooklyn", "address": "456 Oak St"},
    "service_radius_miles": 10,
    "availability": {"monday": ["9:00-17:00"], "tuesday": ["9:00-17:00"]},
    "bio": "15 years experience in modern cuts"
  }'

# 3. Submit for verification
curl -X POST "http://localhost:8000/enrollment/$ENROLLMENT_ID/submit"

# 4. Check status
curl "http://localhost:8000/enrollment/$ENROLLMENT_ID" | jq '.status, .provider_id'
```

**Expected Results:**
- Status: `verified` (for basic services like haircut)
- Provider ID: UUID of created provider
- Provider record created with `status: active` and `verified: true`

---

## 2. Consumer Request Flow

### Via UI
1. Go to **"Find Services"** tab
2. Type: `"I need a haircut for curly hair in Brooklyn this weekend"`
3. Review the draft request
4. Approve and post
5. Wait for offers from providers
6. Accept an offer
7. Confirm booking

### Via API
```bash
# 1. Create consumer ID
CONSUMER_ID=$(uuidgen)

# 2. Create request
REQUEST_ID=$(curl -s -X POST http://localhost:8000/requests \
  -H "Content-Type: application/json" \
  -d "{
    \"consumer_id\": \"$CONSUMER_ID\",
    \"service_category\": \"hair\",
    \"service_type\": \"Haircut\",
    \"raw_input\": \"I need a haircut for curly hair\",
    \"location\": {\"city\": \"Brooklyn\"},
    \"budget\": {\"min\": 50, \"max\": 100}
  }" | jq -r '.id')

# 3. Check for offers
curl "http://localhost:8000/requests/$REQUEST_ID/offers"
```

---

## 3. Provider Offer Flow

### Via UI
1. Go to **"Get Leads"** tab (as enrolled provider)
2. View available leads
3. Click on a lead
4. Use AI agent to draft an offer
5. Submit offer

### Via API
```bash
# 1. Submit offer
OFFER_ID=$(curl -s -X POST http://localhost:8000/offers \
  -H "Content-Type: application/json" \
  -d "{
    \"request_id\": \"$REQUEST_ID\",
    \"provider_id\": \"$PROVIDER_ID\",
    \"price\": 75,
    \"message\": \"I specialize in curly hair cuts\",
    \"proposed_slots\": [
      {\"date\": \"2026-01-28\", \"start_time\": \"14:00\", \"end_time\": \"15:00\"}
    ]
  }" | jq -r '.id')

# 2. Consumer accepts offer
curl -X PUT "http://localhost:8000/offers/$OFFER_ID/accept" \
  -H "Content-Type: application/json" \
  -d '{
    "selected_slot": {
      "date": "2026-01-28",
      "start_time": "14:00"
    }
  }'
```

---

## 4. Service Catalog

### Test Catalog Endpoints
```bash
# Get full catalog with services
curl http://localhost:8000/services/catalog/full | jq '.[0]'

# Get specific category
curl http://localhost:8000/services/catalog/hair_beauty | jq '.services'

# Get specific service
curl http://localhost:8000/services/services/haircut | jq
```

**Expected:**
- Categories include: Hair & Beauty, Cleaning, Plumbing, Electrical, Photography
- Each category has nested services array
- Services include pricing ranges and specializations

---

## 5. Chat Agent

### Test Enrollment Agent
```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"I want to be a barber\",
    \"role\": \"enrollment\",
    \"enrollment_id\": \"$ENROLLMENT_ID\"
  }" | jq '.message'
```

### Test Consumer Agent
```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"I need a haircut in Brooklyn\",
    \"role\": \"consumer\",
    \"consumer_id\": \"$CONSUMER_ID\"
  }" | jq '.message'
```

### Test Provider Agent
```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Show me my leads\",
    \"role\": \"provider\",
    \"provider_id\": \"$PROVIDER_ID\"
  }" | jq '.message, .data'
```

---

## Common Issues & Solutions

### Issue: Enrollment stays "pending"
**Cause:** Missing required fields
**Solution:** Check verification response for missing fields
```bash
curl -X POST "http://localhost:8000/enrollment/$ENROLLMENT_ID/submit" | jq '.message'
```

### Issue: Service Selector shows no services
**Cause:** Using wrong catalog endpoint
**Solution:** Use `/services/catalog/full` not `/services/catalog`

### Issue: Chat returns 307 redirect
**Cause:** Missing trailing slash
**Solution:** Use `/chat/` not `/chat`

### Issue: JSON field not updating
**Cause:** SQLAlchemy not detecting mutation
**Solution:** Already fixed with `flag_modified()` in PATCH endpoint

---

## Test Data

### Sample Provider
```json
{
  "full_name": "Maria Garcia",
  "business_name": "Maria's Hair Studio",
  "email": "maria@hairstudio.com",
  "phone": "555-0123",
  "services": [
    {"id": "haircut", "name": "Haircut", "price": 45, "duration": 45},
    {"id": "hair_color", "name": "Hair Color", "price": 150, "duration": 120}
  ],
  "location": {"city": "Brooklyn", "address": "789 Park Ave"},
  "service_radius_miles": 8,
  "availability": {
    "monday": ["10:00-18:00"],
    "tuesday": ["10:00-18:00"],
    "wednesday": ["10:00-18:00"],
    "thursday": ["10:00-18:00"],
    "friday": ["10:00-20:00"],
    "saturday": ["9:00-17:00"]
  },
  "bio": "20 years experience. Certified colorist. Specializing in balayage and curly cuts."
}
```

### Sample Consumer Request
```json
{
  "service_category": "hair",
  "service_type": "Haircut",
  "raw_input": "I need a haircut for my curly hair, preferably someone who knows type 3C curls",
  "location": {"city": "Brooklyn", "neighborhood": "Williamsburg"},
  "budget": {"min": 60, "max": 100},
  "timing": {"urgency": "this_week", "preference": "weekend"}
}
```

---

## Performance Benchmarks

| Operation | Target | Current |
|-----------|--------|---------|
| Enrollment submission | < 2s | ~1.5s |
| Service catalog load | < 500ms | ~200ms |
| Chat response (no AI) | < 1s | ~500ms |
| Chat response (with AI) | < 5s | ~3s |
| Request creation | < 1s | ~600ms |

---

## Automated Tests

### Run Backend Tests
```bash
cd /Users/idrissenayat/Project\ Proxie
source venv/bin/activate
pytest tests/ -v
```

### Run Frontend Tests
```bash
cd web
npm test
```

---

## Manual UI Testing Checklist

### Enrollment Flow
- [ ] "Become a Provider" button visible on Get Leads tab
- [ ] Enrollment chat opens with specialized greeting
- [ ] Service Selector shows categories
- [ ] Clicking category shows services (Haircut, Hair Color, etc.)
- [ ] Selected services show checkmark
- [ ] Portfolio Uploader appears when requested
- [ ] Summary card shows all collected data
- [ ] Submit button triggers verification
- [ ] Success message appears on verification
- [ ] Dashboard updates to show provider view

### Consumer Flow
- [ ] Chat input accepts natural language
- [ ] Draft request card appears
- [ ] Approve button posts request
- [ ] Offers appear in chat
- [ ] Accept offer creates booking
- [ ] Booking confirmation shown

### Provider Flow
- [ ] Leads view shows available requests
- [ ] Click lead opens details
- [ ] Make offer button works
- [ ] Offer draft appears
- [ ] Submit offer succeeds

---

## Debugging Tips

### Enable Verbose Logging
```bash
# Backend
export LOG_LEVEL=DEBUG
python src/platform/main.py

# Frontend
# Open browser DevTools → Console
```

### Check Database State
```bash
# Connect to PostgreSQL
psql -U postgres -d proxie

# Check enrollments
SELECT id, status, created_at FROM provider_enrollments ORDER BY created_at DESC LIMIT 5;

# Check providers
SELECT id, name, email, status, verified FROM providers ORDER BY created_at DESC LIMIT 5;
```

### API Health Check
```bash
curl http://localhost:8000/docs
# Should return Swagger UI
```

---

## Next Steps

After successful testing:
1. ✅ Provider Enrollment works end-to-end
2. ✅ Service Catalog loads correctly
3. ✅ Chat agents respond appropriately
4. ⏭️ Ready for pilot with real users
