from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String
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
        
        # 2. Filter by City
        # Use the ->> operator to extract text value from JSON
        query = query.filter(
            Provider.location.op("->>")("city") == request_data.location.city
        )
        
        # Execute
        providers = query.all()
        
        return [p.id for p in providers]
