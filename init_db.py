import logging
from src.database import init_db

# We MUST import all models here so that SQLAlchemy's Base.metadata knows about them
# before we call create_all()
from src.models.product import CanonicalProduct, SourceListing, PriceHistory
from src.models.auth import ApiUser, ApiUsage
from src.models.event import PriceChangeEvent
from src.models.webhook import WebhookSubscription

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing SQLite database 'prices.db'...")
    try:
        # This function safely creates tables if they don't exist
        init_db()
        logger.info("Database tables created successfully! Check the project root for 'prices.db'.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

if __name__ == "__main__":
    main()
