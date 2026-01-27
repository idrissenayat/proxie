import json
import os
from typing import List, Dict, Any, Optional

class CatalogService:
    def __init__(self):
        self.catalog_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "resources", 
            "service_catalog.json"
        )
        self._catalog = None

    @property
    def catalog(self) -> Dict[str, Any]:
        if self._catalog is None:
            with open(self.catalog_path, 'r') as f:
                self._catalog = json.load(f)
        return self._catalog

    def get_categories(self) -> List[Dict[str, Any]]:
        return [
            {k: v for k, v in cat.items() if k != 'services'}
            for cat in self.catalog.get("categories", [])
        ]

    def get_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        for cat in self.catalog.get("categories", []):
            if cat["id"] == category_id:
                return cat
        return None

    def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        for cat in self.catalog.get("categories", []):
            for svc in cat.get("services", []):
                if svc["id"] == service_id:
                    # Inject category info
                    svc_copy = svc.copy()
                    svc_copy["category_id"] = cat["id"]
                    svc_copy["category_name"] = cat["name"]
                    return svc_copy
        return None

catalog_service = CatalogService()
