# Quick Start Guide: Implementing the Fix Plan
**For:** Development Team  
**Timeline:** 4 weeks  
**Start Date:** _[Fill in]_

---

## 🚀 Getting Started (Day 1)

### Step 1: Review the Plan
1. Read `IMPLEMENTATION_PLAN.md` - Full detailed plan
2. Read `CODEBASE_REVIEW.md` - Understand the issues
3. Review `TASK_TRACKER.md` - See all tasks

### Step 2: Set Up Your Environment
```bash
# Ensure you have the latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install any new dependencies
pip install -r requirements.txt

# Verify tests run
pytest tests/ -v
```

### Step 3: Assign Tasks
- Review tasks in `TASK_TRACKER.md`
- Assign yourself to tasks
- Update status to "In Progress"

---

## 📋 Week 1: Security (Critical - Start Here!)

### Day 1-2: Task 1.1 - Enforce JWT Authentication

**Quick Start:**
```bash
# 1. Audit current endpoints
cd src/platform/routers
grep -r "@router\." . | grep -v "get_current_user\|get_optional_user"

# 2. Start with providers.py
# Add get_current_user to all endpoints
```

**Example Change:**
```python
# BEFORE
@router.get("/{provider_id}/profile")
async def get_provider_profile(
    provider_id: UUID,
    db: Session = Depends(get_db)
):

# AFTER
@router.get("/{provider_id}/profile")
async def get_provider_profile(
    provider_id: UUID,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user)  # ADD THIS
):
```

**Test Your Changes:**
```bash
# Run auth tests
pytest tests/test_auth.py -v

# Manual test
curl http://localhost:8000/providers/123/profile
# Should return 401 Unauthorized
```

---

### Day 3-4: Task 1.2 - Implement RBAC

**Quick Start:**
```python
# 1. Enhance require_role in auth.py
# See IMPLEMENTATION_PLAN.md for full code

# 2. Apply to endpoints
@router.get("/providers/leads")
async def get_provider_leads(
    user: Dict[str, Any] = Depends(require_role("provider"))
):
    # ...
```

**Test Your Changes:**
```bash
# Test with consumer token (should fail)
pytest tests/test_rbac.py -v
```

---

### Day 5: Task 1.3 & 1.4 - Ownership & WebSocket

**Quick Start:**
```python
# 1. Add require_ownership helper
# See IMPLEMENTATION_PLAN.md

# 2. Secure WebSocket
# Update socket_io.py connect handler
```

---

## 🧪 Week 2: Testing

### Day 1-2: Task 2.1 - Unit Tests

**Quick Start:**
```bash
# 1. Check current coverage
pytest --cov=src/platform/services --cov-report=html
open htmlcov/index.html  # View coverage report

# 2. Create test files
touch tests/test_services/test_matching.py
touch tests/test_services/test_llm_gateway.py
# ... etc
```

**Example Test:**
```python
# tests/test_services/test_matching.py
import pytest
from src.platform.services.matching import MatchingService

def test_matching_algorithm():
    service = MatchingService()
    # Test matching logic
    assert service.match(...) == expected_result
```

---

### Day 3-4: Task 2.2 - Integration Tests

**Quick Start:**
```bash
# Create integration test directory
mkdir -p tests/test_integration
touch tests/test_integration/test_request_flow.py
```

**Example Test:**
```python
# See IMPLEMENTATION_PLAN.md for full example
async def test_full_request_to_booking_flow(...):
    # Test end-to-end flow
```

---

## ⚡ Week 3: Performance

### Day 1-2: Task 3.1 - Celery Migration

**Quick Start:**
```bash
# 1. Verify Celery is running
celery -A src.platform.worker worker --loglevel=info

# 2. Update chat endpoint
# See IMPLEMENTATION_PLAN.md for code changes

# 3. Test async flow
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "test"}'
# Should return task_id immediately
```

---

## 📚 Week 4: Quality

### Day 1: Task 4.2 - API Documentation

**Quick Start:**
```bash
# 1. Start server
python -m src.platform.main

# 2. Visit docs
open http://localhost:8000/api/docs
```

---

## ✅ Testing Checklist

After each task, verify:

- [ ] **Code compiles** - No syntax errors
- [ ] **Tests pass** - `pytest tests/ -v`
- [ ] **No regressions** - Existing functionality works
- [ ] **Documentation updated** - Code comments, docstrings
- [ ] **Task marked complete** - Update `TASK_TRACKER.md`

---

## 🐛 Common Issues & Solutions

### Issue: Tests failing after auth changes
**Solution:** Update test fixtures to include auth headers
```python
@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}
```

### Issue: Celery worker not starting
**Solution:** Check Redis is running
```bash
redis-cli ping  # Should return PONG
```

### Issue: Import errors
**Solution:** Ensure you're in the project root
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 📞 Getting Help

1. **Check the detailed plan** - `IMPLEMENTATION_PLAN.md`
2. **Review codebase** - Look at similar implementations
3. **Ask the team** - Use team chat/standup
4. **Document blockers** - Add to `TASK_TRACKER.md`

---

## 🎯 Success Criteria

By the end of Week 4, you should have:

- ✅ All endpoints secured with JWT
- ✅ RBAC implemented and tested
- ✅ 70%+ test coverage
- ✅ LLM calls async via Celery
- ✅ API documentation complete

---

**Ready to start?** Begin with Task 1.1 in `TASK_TRACKER.md`!
