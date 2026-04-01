# Product Price Monitoring System

> A scalable, production-grade engine for collecting, deduplicating, and acting on marketplace price changes in real-time — built for the Entrupy engineering assignment.

E-commerce businesses live or die by pricing intelligence. This system solves a real problem: tracking the same product across multiple resale platforms (Grailed, Fashionphile, 1stdibs), detecting when prices shift, and notifying downstream consumers reliably — even if the app crashes mid-delivery.

---

## 📁 Project Structure

```
product_price_monitoring_system/
├── src/
│   ├── api/              # FastAPI routers (one file per resource)
│   │   ├── dependencies.py   # Auth + rate-limiting
│   │   ├── webhooks.py
│   │   ├── refresh.py
│   │   ├── products.py
│   │   └── analytics.py
│   ├── models/           # SQLAlchemy ORM models
│   │   ├── product.py        # CanonicalProduct, SourceListing, PriceHistory
│   │   ├── auth.py           # ApiUser, ApiUsage
│   │   ├── event.py          # PriceChangeEvent (Outbox Pattern)
│   │   └── webhook.py        # WebhookSubscription
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/         # Business logic layer
│   │   ├── scraper_base.py   # Abstract HTTPX + Tenacity base class
│   │   ├── scrapers.py       # Grailed, Fashionphile, 1stdibs implementations
│   │   ├── ingestion.py      # Idempotent upsert + Outbox logging
│   │   └── dispatcher.py     # Background webhook delivery worker
│   ├── utils/
│   │   └── logger.py         # Structured logging utility
│   ├── database.py       # SQLAlchemy engine + session factory
│   └── main.py           # FastAPI app + CORS + lifespan hooks
├── frontend/
│   ├── index.html            # HTML shell
│   ├── styles/               # Modular CSS (one file per concern)
│   │   ├── base.css          # Design tokens + global reset
│   │   ├── sidebar.css
│   │   ├── dashboard.css
│   │   ├── products.css
│   │   └── components.css    # Shared buttons, loaders, toasts
│   └── js/                   # Modular JavaScript (SRP architecture)
│       ├── config.js         # All runtime constants
│       ├── api.js            # All backend HTTP calls
│       ├── components.js     # Pure render functions
│       ├── router.js         # Client-side navigation
│       ├── views/
│       │   ├── dashboard.js
│       │   └── products.js
│       └── app.js            # Bootstrap entry point
├── init_db.py            # Creates all database tables
├── seed_db.py            # Seeds test API key + mock products
└── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip (comes with Python)
- A terminal (PowerShell on Windows works great)

### 1. Clone & Setup

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Initialize the Database

This creates all the SQLite tables from scratch — no SQL files needed, SQLAlchemy handles it.

```bash
python init_db.py
```

You'll see: `Database tables created successfully!`

### 3. Seed Test Data

This does two things: injects a test API key so you can actually hit the endpoints, and populates 3 sample products (including a deliberate duplicate to prove the deduplication engine works).

```bash
python seed_db.py
```

Output you should see:
```
Successfully created test ApiUser with key: 'entrupy-intern-test-key-2026'
Successfully seeded 3 mock products (including 1 Canonical Duplicate test) via Idempotent Ingestion.
```

> 💡 **Your API Key is:** `entrupy-intern-test-key-2026` — use this in all request headers.

### 4. Run the API Server

```bash
uvicorn src.main:app --reload
```

The API is now live at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

> The server automatically starts the **Background Outbox Dispatcher** loop on boot — no extra process needed.

### 5. Launch the Frontend Dashboard

With the API running, open a second terminal:

```bash
python -m http.server 3000 --directory frontend
```

Then visit `http://localhost:3000` in your browser.  
You'll see a dark-mode executive dashboard that immediately pulls live stats from your running API. The **"Sync Now"** button triggers a real `POST /refresh` call with animated state transitions.

#### What you'll see on the Dashboard (Step 16)
When the page loads, the **Dashboard View** instantly fires a `GET /analytics` call to your running backend and populates three live metric cards:

- **Canonical Products** — how many unique products are being tracked
- **Tracked Listings** — total marketplace listings across all sources  
- **Price Fluctuations** — total recorded price change events

Click "Products Hub" in the sidebar to switch to the filterable product grid. The sidebar navigation is fully wired — each click transitions cleanly to the corresponding view.

#### Frontend Architecture: Modular SRP Design

We deliberately avoided writing a monolithic `app.js` file. Instead, every JS file has exactly one job:

| File | What it does (and only this) |
|---|---|
| `js/config.js` | Stores `API_BASE_URL` and `API_KEY` constants — frozen, immutable |
| `js/api.js` | All `fetch()` calls with timeout handling and error propagation |
| `js/components.js` | Pure render functions — returns HTML strings, no API calls |
| `js/router.js` | Maps nav clicks to view renders, manages active states |
| `js/views/dashboard.js` | Dashboard screen only: renders skeleton, fetches analytics, populates cards |
| `js/views/products.js` | Products screen only: filter bar, product grid, error states |
| `js/app.js` | Bootstrap entry point — initializes router, API health check, global events |

CSS follows the same discipline under `styles/`:
- `base.css` — design tokens and global reset only
- `sidebar.css`, `dashboard.css`, `products.css` — one file per screen
- `components.css` — shared reusable elements (buttons, loaders, toast notifications)

This means adding a new screen in the future requires creating two files (`views/newscreen.js` + `styles/newscreen.css`) and a single route entry — nothing else needs to change.

---

## 🔌 API Documentation

All endpoints require the `X-API-Key` header:

```
X-API-Key: entrupy-intern-test-key-2026
```

Every response follows a consistent envelope:

```json
{ "success": true, "data": ..., "error": null }
```

### Health Check
```
GET /health
```
No auth required. Returns `{"success": true, "message": "API is healthy"}`. Great for checking if the server is up.

### Trigger Data Refresh
```
POST /refresh
```
Fires the scraping + ingestion pipeline in the background. Returns **202 immediately** — your client doesn't wait for scraping to finish.

### Browse & Filter Products
```
GET /products
```
| Parameter | Type | Default | Description |
|---|---|---|---|
| `category` | string | — | Filter by category name |
| `source` | string | — | Filter by marketplace (e.g. `Grailed`) |
| `min_price` | float | — | Minimum price filter |
| `max_price` | float | — | Maximum price filter |
| `skip` | int | 0 | Pagination offset |
| `limit` | int | 20 | Page size (max 100) |

### Product Detail
```
GET /products/{id}
```
Returns the full canonical product with all source listings and nested price history. Uses SQLAlchemy `joinedload` to avoid N+1 queries.

### Price History (Chart-Ready)
```
GET /products/{id}/history
```  
Returns a flat, chronologically sorted array of price points — designed to feed directly into charting libraries like Chart.js.

```json
[
  { "marketplace": "Grailed",      "price": 12500.0, "timestamp": "2026-04-01T..." },
  { "marketplace": "Fashionphile", "price": 13000.0, "timestamp": "2026-04-01T..." }
]
```

### Platform Analytics
```
GET /analytics  
```
Returns aggregated system-wide stats in a single fast query (uses `func.count()` — no Python-side aggregation).

```json
{
  "summary": {
    "total_canonical_products": 2,
    "total_tracked_listings": 3,
    "total_recorded_price_fluctuations": 3
  },
  "by_category": { "Watches": 1, "Handbags": 1 },
  "by_marketplace": { "Grailed": 1, "Fashionphile": 1, "1stdibs": 1 }
}
```

### Register Webhook
```
POST /webhooks
```
```json
{ "target_url": "https://your-server.com/price-alerts" }
```
Once registered, your server receives a POST payload whenever any tracked product's price changes.

---

## 🧠 Architecture & Design Decisions

### Deduplication: The CanonicalProduct Model

The Rolex Submariner listed on Grailed and the same watch on Fashionphile are the *same product* — your analytics should reflect that. We solve this with a `CanonicalProduct` layer. The ingestion engine looks up (or creates) a single canonical record per `brand + name` pair, then attaches each marketplace's listing beneath it. This makes cross-platform price comparison a first-class citizen of the data model.

### Zero-Loss Notifications: The Transactional Outbox Pattern

Here's the tricky part of reliable webhook delivery: if we send the HTTP notification in the same thread as ingestion and the request fails — or the app crashes — we never know if the downstream system got the update.

We solved this with the **Transactional Outbox Pattern**: when a price change is detected, we write both the new `PriceHistory` row *and* a `PriceChangeEvent` record in the **exact same SQL transaction**. A separate background loop (started automatically on server boot) polls the `price_change_events` table every 5 seconds and delivers the webhook. If delivery fails, the event stays in the table for retry. Zero events can fall through the cracks.

### Scaling Price History to Millions of Rows

We put a composite index on `(source_listing_id, timestamp DESC)` on the `PriceHistory` table. This gives O(log N) lookup time for any product's price trend — instead of a full table scan. When this grows beyond SQLite's comfortable limits, partitioning by month in PostgreSQL is the obvious next migration.

### Idempotent Ingestion

If you scrape the same product 50 times in an hour and the price hasn't changed, the database stays clean — no duplicate rows. We only write a new `PriceHistory` entry when the price *actually* differs from the most recent one. This makes the ingestion engine safe to run as frequently as you want.

### Extending to 100+ Sources

The `MarketplaceScraper` abstract class handles all the networking complexity — HTTP timeouts, exponential backoff retries via Tenacity, structured logging. To add a new marketplace, you write one class that inherits from it and implements a single method: `parse_products()`. The rest wires up automatically.

### Frontend Architecture (Modular SRP)

The frontend follows Single Responsibility Principle as strictly as the backend:
- `config.js` — constants only
- `api.js` — all HTTP calls, nothing else
- `components.js` — pure render functions, zero API calls
- `views/` — per-screen orchestration
- `router.js` — navigation mapping only
- `app.js` — bootstrap entry point only

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI + Pydantic v2 |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (WAL mode) |
| HTTP Client | HTTPX (async) |
| Retry Logic | Tenacity |
| Frontend | Vanilla HTML / CSS / JS |

---

## 🧪 Running Tests

```bash
pytest
```

*(Integration tests covering idempotency, authentication, and price detection are written in Phase 7.)*
