import pytest
import asyncio
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from src.services.ingestion import process_scraped_items
from src.models.product import CanonicalProduct, SourceListing, PriceHistory
from src.models.event import PriceChangeEvent
from src.services.dispatcher import _fetch_and_prepare_events

@pytest.mark.asyncio
async def test_ingestion_creates_canonical_and_listings(db_session: Session):
    data = [{"source_id": "1", "marketplace_name": "1stdibs", "brand": "Gucci", "name": "Bag", "price": 1000.0, "url": "http://1", "category": "Bags"}]
    process_scraped_items(db_session, data)
    
    products = db_session.query(CanonicalProduct).all()
    assert len(products) == 1
    assert products[0].brand == "Gucci"
    
    listings = db_session.query(SourceListing).all()
    assert len(listings) == 1
    assert listings[0].marketplace_name == "1stdibs"
    
    history = db_session.query(PriceHistory).all()
    assert len(history) == 1
    assert history[0].price == 1000.0

@pytest.mark.asyncio
async def test_ingestion_updates_existing_listing(db_session: Session):
    data1 = [{"source_id": "2", "marketplace_name": "Grailed", "brand": "Amiri", "name": "Shirt", "price": 500.0, "url": "http://g", "category": "Apparel"}]
    process_scraped_items(db_session, data1)
    
    listings = db_session.query(SourceListing).all()
    assert len(listings) == 1
    
    data2 = [{"source_id": "2", "marketplace_name": "Grailed", "brand": "Amiri", "name": "Shirt", "price": 450.0, "url": "http://g", "category": "Apparel"}]
    process_scraped_items(db_session, data2)
        
    listings = db_session.query(SourceListing).all()
    assert len(listings) == 1
    
    history = db_session.query(PriceHistory).all()
    assert len(history) == 2
    prices = [h.price for h in history]
    assert 500.0 in prices
    assert 450.0 in prices

@pytest.mark.asyncio
async def test_outbox_creates_events_on_price_change(db_session: Session):
    data1 = [{"source_id": "3", "marketplace_name": "Fashionphile", "brand": "Tiffany", "name": "Ring", "price": 100.0, "url": "http", "category": "Jewelry"}]
    process_scraped_items(db_session, data1)
        
    events = db_session.query(PriceChangeEvent).all()
    # The first ingestion ALSO creates an event for the initial price record.
    assert len(events) == 1
    assert events[0].price_history.price == 100.0
    
    data2 = [{"source_id": "3", "marketplace_name": "Fashionphile", "brand": "Tiffany", "name": "Ring", "price": 90.0, "url": "http", "category": "Jewelry"}]
    process_scraped_items(db_session, data2)
        
    events = db_session.query(PriceChangeEvent).all()
    assert len(events) == 2
    assert events[-1].status == "pending"
    assert events[-1].price_history.price == 90.0

@pytest.mark.asyncio
async def test_webhook_delivery_failure_recovery(db_session: Session):
    from src.models.webhook import WebhookSubscription
    from src.services.dispatcher import dispatch_webhooks
    import httpx
    
    sub = WebhookSubscription(target_url="http://fail.com", is_active=True)
    db_session.add(sub)
    db_session.commit()
    
    payload = {"event": "test"}
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = Exception("Connection Failed")
        async with httpx.AsyncClient() as client:
            try:
                await dispatch_webhooks(client, 1, payload, [sub])
                raised = False
            except:
                raised = True
            assert not raised
