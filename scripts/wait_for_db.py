import time
import psycopg2
import sys
import os

# Add src to path just in case, though we parse raw URL here or use env
sys.path.append(os.getcwd())

from src.platform.config import settings

def wait_for_db():
    print(f"Waiting for database at {settings.DATABASE_URL}...")
    retries = 60
    while retries > 0:
        try:
            conn = psycopg2.connect(settings.DATABASE_URL)
            conn.close()
            print("✅ Database is ready!")
            return
        except psycopg2.OperationalError:
            retries -= 1
            print(f"Database not ready yet, retrying... ({retries} left)")
            time.sleep(2)
        except Exception as e:
            print(f"Unexpected error: {e}")
            retries -= 1
            time.sleep(2)
    
    print("❌ Could not connect to database.")
    sys.exit(1)

if __name__ == "__main__":
    wait_for_db()
