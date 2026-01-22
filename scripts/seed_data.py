"""
Seed the database with sample data for development.
"""

import sys
sys.path.insert(0, '.')

from src.platform.database import SessionLocal, engine, Base
from src.platform.models import Provider, Service


def seed_providers():
    """Create sample providers."""
    
    providers = [
        {
            "name": "Maya Johnson",
            "email": "maya@example.com",
            "bio": "Curly hair specialist with 8 years of experience.",
            "location": {
                "city": "Brooklyn",
                "neighborhood": "Bed-Stuy",
                "service_radius_km": 5
            },
            "specializations": ["curly hair", "natural hair", "dry cutting"],
            "rating": 4.9,
            "review_count": 47,
            "status": "active"
        },
        {
            "name": "Dion Williams",
            "email": "dion@example.com",
            "bio": "Mobile stylist specializing in curly cutting techniques.",
            "location": {
                "city": "Brooklyn",
                "neighborhood": "Crown Heights",
                "service_radius_km": 10
            },
            "specializations": ["curly hair", "mobile service"],
            "rating": 4.7,
            "review_count": 28,
            "status": "active"
        },
    ]
    
    db = SessionLocal()
    try:
        for provider_data in providers:
            provider = Provider(**provider_data)
            db.add(provider)
        db.commit()
        print(f"✅ Created {len(providers)} sample providers")
    finally:
        db.close()


def main():
    """Run all seed functions."""
    print("🌱 Seeding database...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    # Seed data
    seed_providers()
    
    print("✅ Database seeded successfully")


if __name__ == "__main__":
    main()
