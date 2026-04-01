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
*(Detailing our indexing design and data partitioning strategies will go here after schema implementation)*

### Notification Implementation
*(Detailing the Transactional Outbox pattern design will go here after building the Event architecture)*

### Extending to 100+ Data Sources
*(Detailing the abstract parser layer and ingestion engine limits will go here when we finalize Phase 3)*
