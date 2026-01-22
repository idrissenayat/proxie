"""
Database migration script.

For MVP, we use simple create_all. 
For production, use Alembic for proper migrations.
"""

import sys
sys.path.insert(0, '.')

from src.platform.database import engine, Base
from src.platform.models import *  # Import all models


def migrate():
    """Create all database tables."""
    print("🔄 Running migrations...")
    
    Base.metadata.create_all(bind=engine)
    
    print("✅ Migrations complete")


if __name__ == "__main__":
    migrate()
