import os
from sqlalchemy import create_engine, text
from src.platform.config import settings

def migrate_db():
    print(f"Connecting to {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # 0. Enable pgvector extension
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            print("Enabled pgvector extension")
        except Exception as e:
            print(f"Could not enable pgvector (might not have superuser or already enabled): {e}")

        # Helper to add column if not exists
        def add_column_if_missing(table, column, type_str):
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {type_str}"))
                print(f"Added {column} to {table}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"{column} already exists in {table}")
                else:
                    print(f"Error adding {column} to {table}: {e}")

        # 1. Update consumers
        add_column_if_missing("consumers", "clerk_id", "VARCHAR(255)")
        try:
            conn.execute(text("CREATE UNIQUE INDEX ix_consumers_clerk_id ON consumers (clerk_id)"))
        except: pass

        # 2. Update providers
        add_column_if_missing("providers", "clerk_id", "VARCHAR(255)")
        try:
            conn.execute(text("CREATE UNIQUE INDEX ix_providers_clerk_id ON providers (clerk_id)"))
        except: pass
        
        # Add embedding and Sprint 10 columns
        add_column_if_missing("providers", "embedding", "vector(3072)")
        add_column_if_missing("providers", "jobs_completed", "INTEGER DEFAULT 0")
        add_column_if_missing("providers", "response_rate", "FLOAT DEFAULT 0.0")
        add_column_if_missing("providers", "average_response_time_hours", "FLOAT")
        add_column_if_missing("providers", "offer_templates", "JSONB DEFAULT '[]'::jsonb")

if __name__ == "__main__":
    migrate_db()
