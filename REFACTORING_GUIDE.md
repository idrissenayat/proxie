# Refactoring Guide: Using Common Utilities

This guide shows how to use the new utility functions to reduce code duplication.

---

## Database Helpers

### Before (Repeated Pattern)
```python
provider = db.query(Provider).filter(Provider.id == provider_id).first()
if not provider:
    raise HTTPException(status_code=404, detail="Provider not found")
```

### After (Using Utility)
```python
from src.platform.utils.db_helpers import get_or_404

provider = get_or_404(db, Provider, provider_id, "Provider")
```

**Benefits:**
- ✅ Consistent error messages
- ✅ Less boilerplate
- ✅ Type-safe

---

## Exception Helpers

### Before (Repeated Pattern)
```python
raise HTTPException(status_code=404, detail="Provider not found")
raise HTTPException(status_code=403, detail="Not authorized")
raise HTTPException(status_code=400, detail="Invalid input")
```

### After (Using Utility)
```python
from src.platform.utils.exceptions import (
    raise_not_found,
    raise_forbidden,
    raise_bad_request
)

raise raise_not_found("Provider", provider_id)
raise raise_forbidden("Not authorized to edit this profile")
raise raise_bad_request("Invalid input data")
```

**Benefits:**
- ✅ Consistent error format
- ✅ Less code
- ✅ Easier to maintain

---

## Response Formatting

### Before (Inconsistent)
```python
return {"success": True, "data": {...}}
return {"message": "Created", "id": "123"}
return JSONResponse(status_code=201, content={...})
```

### After (Using Utility)
```python
from src.platform.utils.responses import success_response, paginated_response

return success_response(data={"id": "123"}, message="Created successfully")
return paginated_response(items, total=100, page=1, per_page=20)
```

**Benefits:**
- ✅ Consistent API responses
- ✅ Standardized format
- ✅ Better client experience

---

## Migration Examples

### Example 1: Provider Router

**Before:**
```python
@router.get("/{provider_id}", response_model=ProviderResponse)
def get_provider(provider_id: UUID, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider
```

**After:**
```python
from src.platform.utils.db_helpers import get_or_404

@router.get("/{provider_id}", response_model=ProviderResponse)
def get_provider(provider_id: UUID, db: Session = Depends(get_db)):
    provider = get_or_404(db, Provider, provider_id, "Provider")
    return provider
```

---

### Example 2: Request Router

**Before:**
```python
@router.get("/{request_id}", response_model=ServiceRequestResponse)
def get_request(request_id: UUID, db: Session = Depends(get_db)):
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req
```

**After:**
```python
from src.platform.utils.db_helpers import get_or_404

@router.get("/{request_id}", response_model=ServiceRequestResponse)
def get_request(request_id: UUID, db: Session = Depends(get_db)):
    req = get_or_404(db, ServiceRequest, request_id, "Request")
    return req
```

---

### Example 3: Authorization Check

**Before:**
```python
if provider.clerk_id != user.get("sub") and user.get("public_metadata", {}).get("role") != "admin":
    raise HTTPException(status_code=403, detail="Not authorized to edit this profile")
```

**After:**
```python
from src.platform.utils.exceptions import raise_forbidden

if provider.clerk_id != user.get("sub") and user.get("public_metadata", {}).get("role") != "admin":
    raise raise_forbidden("Not authorized to edit this profile")
```

---

## Available Utilities

### Database Helpers (`src/platform/utils/db_helpers.py`)
- `get_or_404(db, model, id, name)` - Get resource or raise 404
- `get_or_none(db, model, id)` - Get resource or return None
- `get_by_field_or_404(db, model, field, value, name)` - Get by field or raise 404
- `exists(db, model, id)` - Check if resource exists

### Exception Helpers (`src/platform/utils/exceptions.py`)
- `raise_not_found(resource_type, id)` - Raise 404
- `raise_forbidden(message)` - Raise 403
- `raise_bad_request(message)` - Raise 400
- `raise_conflict(message)` - Raise 409

### Response Helpers (`src/platform/utils/responses.py`)
- `success_response(data, message, status_code)` - Standard success response
- `error_response(error, details, status_code)` - Standard error response
- `paginated_response(items, total, page, per_page)` - Paginated response

---

## Migration Checklist

- [ ] Replace `db.query(...).filter(...).first()` + `if not:` with `get_or_404()`
- [ ] Replace `raise HTTPException(status_code=404, ...)` with `raise raise_not_found()`
- [ ] Replace `raise HTTPException(status_code=403, ...)` with `raise raise_forbidden()`
- [ ] Replace `raise HTTPException(status_code=400, ...)` with `raise raise_bad_request()`
- [ ] Standardize response formats using `success_response()` and `error_response()`
- [ ] Use `paginated_response()` for list endpoints

---

## Benefits

1. **Consistency** - All endpoints use same patterns
2. **Maintainability** - Changes in one place affect all endpoints
3. **Readability** - Less boilerplate, clearer intent
4. **Type Safety** - Better IDE support and type checking
5. **Testing** - Easier to mock and test utilities
