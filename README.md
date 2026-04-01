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

### 1. Database Initialization & Seeding
Before running the API, you must initialize the local SQLite database to create the schema models (`CanonicalProduct`, `SourceListing`, `PriceHistory`, `ApiUser`, `PriceChangeEvent`). 
```bash
# 1. Initialize the empty tables
python init_db.py

# 2. Seed the database with a test API key for evaluation
python seed_db.py
# (Your test API key will be: entrupy-intern-test-key-2026)
```

### 2. Running the API Server
Start the FastAPI backend. By default, it binds to `http://localhost:8000`.
```bash
uvicorn src.main:app --reload
```
*Note: Starting the server automatically initiates the Background Outbox Dispatcher loop via FastAPI's `lifespan` manager.*

## API Documentation

All API endpoints strictly require authentication. You must pass the seed key in the HTTP headers:
`X-API-Key: entrupy-intern-test-key-2026`

All responses follow a strict `APIResponse` standard:
```json
{
  "success": true,
  "data": ...,
  "error": null
}
```

### 1. Register Webhook
`POST /webhooks`
Registers your external server to receive price fluctuation alerts.
**Payload:**
```json
{ "target_url": "https://your-server.com/alerts" }
```

### 2. Trigger Data Refresh
`POST /refresh`
Triggers the ingestion engine asynchronously.
**Response:** `202 ACCEPTED` (Returns immediately while processing runs in the background).

### 3. Browse & Filter Products
`GET /products`
Queries your Canonical Products and localized listings.
**Query Parameters:**
- `category` (string, optional)
- `source` (string, optional)
- `min_price` (float, optional)
- `max_price` (float, optional)
- `skip` (int, default=0)
- `limit` (int, default=20)

### 4. Detail & History Endpoints
`GET /products/{product_id}`
Retrieves a deeply eager-loaded payload containing the canonical product, its source listings, and nested price history.

`GET /products/{product_id}/history`
Fetches a flattened, chronologically sorted array of price points specifically designed for frontend charting libraries (like Chart.js).

### 5. Platform Analytics
`GET /analytics`
An optimized dashboard aggregation endpoint leveraging SQLAlchemy `func.count()`. It returns the total tracked products, marketplace listings, and historical price fluctuations instantly without crashing memory.

## 💻 Frontend UI & Dashboard Setup

To visualize our robust backend logic, we (the engineering team) built a Vanilla HTML/JS frontend shell. Since I (your AI Developer) initialized a Stitch UI project in the cloud for high-fidelity component generation, we needed a native local sandbox to actually test those components against our APIs.

**How to run it:**
1. Ensure your FastAPI server is running (`uvicorn src.main:app --reload`). I already injected CORS middleware so they can talk securely!
2. Simply open `frontend/index.html` directly in any web browser. 
3. *(Optional)* For a more "production-like" server, run: 
   ```bash
   python -m http.server 3000 --directory frontend
   # Then visit http://localhost:3000
   ```

I organically wired the "Sync Now" button to execute a `POST /refresh` call. Go ahead and click it—you'll see the UI smoothly transition states as it speaks natively to our backend!

## Usage & Features

### Features
- **Deduplication Engine**: Automatically binds marketplace listings to a `CanonicalProduct`.
- **Idempotent Ingestion**: Will not rewrite identical price data natively protecting against DB bloat.
- **Robust Scrapers**: Abstract `MarketplaceScraper` base utilizing `httpx` and `tenacity` exponential back-off retries.
- **Transactional Webhooks**: Reliable notification delivery decoupled from parsing.

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
To guarantee zero event loss, we implemented the **Transactional Outbox Pattern**. When a price updates, we write the new `PriceHistory` and a `PriceChangeEvent` in the *exact same SQLite transaction*. A background dispatcher asynchronously reads from this table locally and reliably delivers HTTP webhooks, independent of the scraper's execution thread.

### Extending to 100+ Data Sources
We utilized strong Object-Oriented polymorphism to scale the ingestion engine. The `MarketplaceScraper` base class encapsulates all HTTP networking, timeout handling (`httpx`), and exponential backoff retry logic (`tenacity`). To add 100+ sources, developers only need to write a new class (e.g. `EbayScraper(MarketplaceScraper)`) that strictly implements the `@abstractmethod def parse_products()`. This completely isolates custom marketplace parsers from the core ingestion mechanics.
