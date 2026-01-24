from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.platform.models.provider import Provider
from src.platform.models.service import Service
from src.platform.schemas.request import ServiceRequestCreate

class MatchingService:
    def __init__(self, db: Session):
        self.db = db

    def find_providers(self, request_data: ServiceRequestCreate) -> List[UUID]:
        """
        Find providers matching the service request criteria.
        Matching logic:
        1. Service Type matching (via Service table)
        2. Location matching (City)
        """
        
        # Start with all providers
        query = self.db.query(Provider)
        
        # 1. Join with Services to find providers offering the requested service type
        # We use a case-insensitive match on the service name
        query = query.join(Service).filter(
            Service.name.ilike(f"%{request_data.service_type}%")
        )
        
        # 2. Filter by City (assuming location stored in JSON has a 'city' field)
        # Note: JSON querying details depend on DB, but for now we'll do a basic check
        # This is a bit complex in pure SQLA with generic JSON, but specific to PG:
        # Provider.location['city'].astext == request_data.location.city
        
        # For simplicity in MVP without complex JSON operators setup:
        # We will fetch candidates and filter in python if the set is small, 
        # OR use the JSON operator if feasible. Let's try to refine the query with JSON.
        
        # Assuming postgres:
        query = query.filter(Provider.location['city'].astext == request_data.location.city)
        
        # Execute
        providers = query.all()
        
        return [p.id for p in providers]
