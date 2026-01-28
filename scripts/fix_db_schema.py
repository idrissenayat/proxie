import os
from sqlalchemy import create_engine, text
from src.platform.config import settings

def migrate_db():
    print(f"Connecting to {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # Check consumers
        try:
            conn.execute(text("ALTER TABLE consumers ADD COLUMN clerk_id VARCHAR(255)"))
            conn.execute(text("CREATE UNIQUE INDEX ix_consumers_clerk_id ON consumers (clerk_id)"))
            print("Added clerk_id to consumers")
        except Exception as e:
            if "duplicate checking" in str(e) or "already exists" in str(e):
                print("clerk_id already exists in consumers")
            else:
                print(f"Error altering consumers: {e}")

        # Check providers
        try:
            conn.execute(text("ALTER TABLE providers ADD COLUMN clerk_id VARCHAR(255)"))
            conn.execute(text("CREATE UNIQUE INDEX ix_providers_clerk_id ON providers (clerk_id)"))
            print("Added clerk_id to providers")
        except Exception as e:
            if "duplicate checking" in str(e) or "already exists" in str(e):
                print("clerk_id already exists in providers")
            else:
                print(f"Error altering providers: {e}")

if __name__ == "__main__":
    migrate_db()
