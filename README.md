# Product Price Monitoring System

A scalable, reliable engine for collecting, storing, and acting on marketplace price changes in real-time.

E-commerce businesses need to track competitor pricing across platforms. This system collects product data from marketplaces like Grailed, Fashionphile, and 1stdibs, deduplicates products, tracks price changes in real-time, and reliably notifies downstream systems.

## Getting Started

### Prerequisites
- Python 3.9+
- SQLite (Built-in)

### Setup & Installation
```bash
# Set up a virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize the SQLite Database
python init_db.py

# Run the API server
uvicorn src.main:app --reload
```

### Configuration
*(Configuration instructions will be added here as we implement environmental variables)*

## System Operations: Step-by-Step Guide

### 1. Database Initialization
Before running the API, you must initialize the local SQLite database. This creates the foundational models: `CanonicalProduct` (for deduplication), `SourceListing`, `PriceHistory`, `ApiUser` (for access control), and `PriceChangeEvent` (for reliable notifications).
```bash
python init_db.py
```

### 2. Running the API Server
Start the FastAPI server. By default, it runs on `http://localhost:8000`.
```bash
uvicorn src.main:app --reload
```
*Note: Starting the server automatically initiates the Background Outbox Dispatcher loop.*

### 3. API Authentication & Webhooks
All core endpoints require an `X-API-Key` header. Requests are strictly tracked in the `api_usage` table. 
To receive updates, clients POST their callback URL to `/webhooks`.

### 4. Background Webhook Delivery
The system uses a **Transactional Outbox Pattern**. When the ingestion engine detects a price variation, it writes the new price and an event flag to the DB within an atomic transaction. A separate async loop polls this table every 5 seconds and dispatches HTTP POST payloads to all active webhooks, ensuring zero event loss.

## Usage & Features

### Features
- **Deduplication Engine**: Automatically binds marketplace listings to a `CanonicalProduct`.
- **Idempotent Ingestion**: Will not rewrite identical price data natively protecting against DB bloat.
- **Robust Scrapers**: Abstract `MarketplaceScraper` base utilizing `httpx` and `tenacity` exponential back-off retries.
- **Transactional Webhooks**: Reliable notification delivery decoupled from parsing.

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
We utilized strong Object-Oriented polymorphism to scale the ingestion engine. The `MarketplaceScraper` base class encapsulates all HTTP networking, timeout handling, and exponential backoff retry logic. To add 100+ sources, developers only need to write a new class (e.g. `EbayScraper(MarketplaceScraper)`) that strictly implements the `@abstractmethod def parse_products()`. This completely isolates custom marketplace parsers from the core ingestion mechanics.
