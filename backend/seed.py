import sys
import os

# Add backend directory to sys.path so 'app' can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.utils.synthetic_data import seed_database

def run_seed():
    db = SessionLocal()
    try:
        print("Starting seed...")
        seed_database(db)
        print("Database seeding completed successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
