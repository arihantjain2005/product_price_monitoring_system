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
            mock_data = [
                {"brand": "Rolex", "name": "Submariner Date", "source_id": "r-123", "marketplace_name": "Grailed", "price": 12500.0, "url": "https://grailed.com/rolex-123", "category": "Watches"},
                {"brand": "Rolex", "name": "Submariner Date", "source_id": "fp-456", "marketplace_name": "Fashionphile", "price": 13000.0, "url": "https://fashionphile.com/rolex-456", "category": "Watches"},
                {"brand": "Chanel", "name": "Classic Flap Bag", "source_id": "1d-789", "marketplace_name": "1stdibs", "price": 8500.0, "url": "https://1stdibs.com/chanel-789", "category": "Handbags"}
            ]
            process_scraped_items(db, mock_data)
            print("Successfully seeded 3 mock products (including 1 Canonical Duplicate test) via Idempotent Ingestion.")
            
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
