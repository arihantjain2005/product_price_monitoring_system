import asyncio
import httpx
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from src.database import SessionLocal
from src.models.event import PriceChangeEvent
from src.models.product import PriceHistory, SourceListing
from src.models.webhook import WebhookSubscription
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def dispatch_webhooks(client: httpx.AsyncClient, event_id: int, payload: dict, webhook_urls: list[str]):
    for url in webhook_urls:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Delivered event {event_id} to {url}")
        except Exception as e:
            logger.error(f"Failed to deliver event {event_id} to {url}: {e}")

def _fetch_and_prepare_events():
    db: Session = SessionLocal()
    try:
        pending_events = db.query(PriceChangeEvent).options(
            joinedload(PriceChangeEvent.price_history)
            .joinedload(PriceHistory.listing)
            .joinedload(SourceListing.canonical_product)
        ).filter(
            PriceChangeEvent.status == "pending"
        ).limit(50).all()

        if not pending_events:
            db.close()
            return [], [], []

        active_webhooks = db.query(WebhookSubscription).filter(
            WebhookSubscription.is_active == True
        ).all()

        if not active_webhooks:
            for event in pending_events:
                event.status = "processed"
                event.processed_at = datetime.now(timezone.utc)
            db.commit()
            db.close()
            return [], [], []

        events_data = []
        event_ids = []
        for event in pending_events:
            event.status = "processing"
            history = event.price_history
            listing = history.listing
            product = listing.canonical_product
            events_data.append((event.id, {
                "event_id": event.id,
                "product_id": product.id,
                "brand": product.brand,
                "name": product.name,
                "marketplace": listing.marketplace_name,
                "new_price": history.price,
                "timestamp": history.timestamp.isoformat()
            }))
            event_ids.append(event.id)
        db.commit()

        # Extract target_url as plain strings BEFORE closing the session
        # to avoid DetachedInstanceError when used across async threads
        webhook_urls = [hook.target_url for hook in active_webhooks]
        db.close()

        return events_data, webhook_urls, event_ids

    except Exception as e:
        logger.error(f"Outbox fetch failed: {e}")
        db.rollback()
        db.close()
        return [], [], []

def _mark_events_processed(event_ids: list[int]):
    if not event_ids:
        return
    db: Session = SessionLocal()
    try:
        events = db.query(PriceChangeEvent).filter(PriceChangeEvent.id.in_(event_ids)).all()
        for event in events:
            event.status = "processed"
            event.processed_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as e:
        logger.error(f"Outbox completion mark failed: {e}")
        db.rollback()
    finally:
        db.close()

async def process_outbox():
    events_data, webhook_urls, event_ids = await asyncio.to_thread(_fetch_and_prepare_events)
    
    if not events_data:
        return

    async with httpx.AsyncClient() as client:
        for event_id, payload in events_data:
            await dispatch_webhooks(client, event_id, payload, webhook_urls)
            
    await asyncio.to_thread(_mark_events_processed, event_ids)
