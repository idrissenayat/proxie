from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from src.platform.services.catalog import catalog_service

router = APIRouter(
    prefix="/services",
    tags=["services"],
)

@router.get("/catalog", response_model=List[Dict[str, Any]])
def get_categories():
    """Get all service categories (headers only)."""
    return catalog_service.get_categories()

@router.get("/catalog/full", response_model=List[Dict[str, Any]])
def get_full_catalog():
    """Get all service categories with their services for UI selectors."""
    return catalog_service.catalog.get("categories", [])

@router.get("/catalog/{category_id}")
def get_category_details(category_id: str):
    """Get details for a specific category including its services."""
    cat = catalog_service.get_category(category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat

@router.get("/services/{service_id}")
def get_service_details(service_id: str):
    """Get details for a specific service."""
    svc = catalog_service.get_service(service_id)
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    return svc
