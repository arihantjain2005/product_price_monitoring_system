from typing import Any, Dict, List
from sqlalchemy.orm import Session
from src.models.product import CanonicalProduct, SourceListing, PriceHistory
from src.models.event import PriceChangeEvent

def process_scraped_items(db: Session, items: List[Dict[str, Any]]):
    for item in items:
        brand = item.get("brand")
        name = item.get("name")
        source_id = item.get("source_id")
        marketplace = item.get("marketplace_name")
        price = item.get("price")
        url = item.get("url")
        category = item.get("category")

        if not all([brand, name, source_id, marketplace, price]):
            continue

        canonical = db.query(CanonicalProduct).filter(
            CanonicalProduct.brand == brand,
            CanonicalProduct.name == name
        ).first()

        if not canonical:
            canonical = CanonicalProduct(brand=brand, name=name, category=category)
            db.add(canonical)
            db.flush()

        listing = db.query(SourceListing).filter(
            SourceListing.marketplace_name == marketplace,
            SourceListing.source_id == source_id
        ).first()

        if not listing:
            listing = SourceListing(
                canonical_product_id=canonical.id,
                marketplace_name=marketplace,
                source_id=source_id,
                url=url
            )
            db.add(listing)
            db.flush()

        last_price_record = db.query(PriceHistory).filter(
            PriceHistory.source_listing_id == listing.id
        ).order_by(PriceHistory.timestamp.desc()).first()

        if not last_price_record or last_price_record.price != price:
            new_price_entry = PriceHistory(
                source_listing_id=listing.id,
                price=price
            )
            db.add(new_price_entry)
            db.flush()

            outbox_event = PriceChangeEvent(
                price_history_id=new_price_entry.id,
                status="pending"
            )
            db.add(outbox_event)

    db.commit()
