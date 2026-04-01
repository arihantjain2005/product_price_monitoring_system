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

async def dispatch_webhooks(client: httpx.AsyncClient, event: PriceChangeEvent, webhooks: list[WebhookSubscription]):
    history = event.price_history
    listing = history.listing
    product = listing.canonical_product

    payload = {
        "event_id": event.id,
        "product_id": product.id,
        "brand": product.brand,
        "name": product.name,
        "marketplace": listing.marketplace_name,
        "new_price": history.price,
        "timestamp": history.timestamp.isoformat()
    }

    for hook in webhooks:
        try:
            response = await client.post(hook.target_url, json=payload, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Delivered event {event.id} to {hook.target_url}")
        except Exception as e:
            logger.error(f"Failed to deliver event {event.id} to {hook.target_url}: {e}")

async def process_outbox():
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
            return

        active_webhooks = db.query(WebhookSubscription).filter(
            WebhookSubscription.is_active == True
        ).all()

        if not active_webhooks:
            for event in pending_events:
                event.status = "processed"
                event.processed_at = datetime.now(timezone.utc)
            db.commit()
            return

        async with httpx.AsyncClient() as client:
            for event in pending_events:
                event.status = "processing"
            db.commit()

            for event in pending_events:
                await dispatch_webhooks(client, event, active_webhooks)
                event.status = "processed"
                event.processed_at = datetime.now(timezone.utc)
            db.commit()

    except Exception as e:
        logger.error(f"Outbox processor failed: {e}")
        db.rollback()
    finally:
        db.close()
