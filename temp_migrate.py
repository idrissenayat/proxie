from sqlalchemy import text
from src.platform.database import engine

def migrate():
    with engine.connect() as conn:
        print("Adding category column to services table if not exists...")
        conn.execute(text("ALTER TABLE services ADD COLUMN IF NOT EXISTS category VARCHAR(100);"))
        conn.commit()
        print("Done.")

if __name__ == "__main__":
    migrate()
