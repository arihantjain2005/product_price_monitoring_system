# Product Price Monitoring System

A scalable, reliable engine for collecting, storing, and acting on marketplace price changes in real-time.

E-commerce businesses need to track competitor pricing across platforms. This system collects product data from marketplaces like Grailed, Fashionphile, and 1stdibs, deduplicates products, tracks price changes in real-time, and reliably notifies downstream systems.

## Getting Started

### Prerequisites
- Python 3.9+
- SQLite (Built-in)

### Setup & Installation
```bash
# Set up a virtual environment
python -m venv venv
# Activate the environment (Windows)
.\venv\Scripts\activate
# Activate the environment (Mac/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration
*(Configuration instructions will be added here as we implement environmental variables)*

## Usage & Features

### Features
*(List of features will be expanded as we build them out)*
- Collects and deduplicates marketplace data asynchronously.

### API Documentation
*(API Reference tables will be added as endpoints are built)*

## Development & Maintenance

### Tech Stack
- **API Framework**: FastAPI (with Pydantic for strict schema validation)
- **Database**: SQLite (Configured with WAL mode for high concurrency) / SQLAlchemy ORM
- **Async Fetching**: HTTPX and Tenacity for robust HTTP retry logic

### Running Tests
```bash
# Tests will be executed via pytest
pytest
```

### Known Limitations
*(Will be documented throughout development)*

## Architecture & Design Decisions

### How does price history scale to millions of rows?
To handle millions of price history rows efficiently without full table scans, we implemented a composite index on `(source_listing_id, timestamp.desc())` in the `PriceHistory` model. This creates O(log N) lookup times when charting price history for an individual product listing. If this system scales beyond single-node SQLite capabilities, PostgreSQL partitions by month based on `timestamp` would be the immediate next step.

### Notification Implementation
To guarantee zero event loss, we implemented the **Transactional Outbox Pattern**. When a price updates, we write the new `PriceHistory` and a `PriceChangeEvent` in the *exact same SQLite transaction*. A background dispatcher (built in Phase 4) asynchronously reads from this table and reliably delivers webhooks, independent of the scraper's execution thread.

### Extending to 100+ Data Sources
*(Detailing the abstract parser layer and ingestion engine limits will go here when we finalize Phase 3)*
