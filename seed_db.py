from src.database import SessionLocal
from src.models.auth import ApiUser
from src.models.product import CanonicalProduct
from src.services.ingestion import process_scraped_items

def seed_database():
    db = SessionLocal()
    try:
        exists = db.query(ApiUser).filter(ApiUser.username == "test_developer").first()
        if not exists:
            dev_user = ApiUser(
                username="test_developer",
                api_key="entrupy-intern-test-key-2026"
            )
            db.add(dev_user)
            db.commit()
            print("Successfully created test ApiUser with key: 'entrupy-intern-test-key-2026'")
        else:
            print("Test user already exists.")
            
        if db.query(CanonicalProduct).count() == 0:
            print("Database initialized clean. Waiting for ingestion pipeline.")
            
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
