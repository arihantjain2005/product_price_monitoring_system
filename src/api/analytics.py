from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database import get_db
from src.models.product import CanonicalProduct, SourceListing, PriceHistory
from src.schemas.base import APIResponse
from src.api.dependencies import verify_api_key

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("", response_model=APIResponse[dict])
def get_analytics(
    db: Session = Depends(get_db),
    user=Depends(verify_api_key)
):
    total_products = db.query(CanonicalProduct).count()
    total_listings = db.query(SourceListing).count()
    total_price_changes = db.query(PriceHistory).count()
    
    # Breakdown by underlying Category
    category_counts = db.query(
        CanonicalProduct.category, 
        func.count(CanonicalProduct.id)
    ).group_by(CanonicalProduct.category).all()
    
    # Breakdown by underlying Marketplace source
    marketplace_counts = db.query(
        SourceListing.marketplace_name, 
        func.count(SourceListing.id)
    ).group_by(SourceListing.marketplace_name).all()

    data = {
        "summary": {
            "total_canonical_products": total_products,
            "total_tracked_listings": total_listings,
            "total_recorded_price_fluctuations": total_price_changes
        },
        "by_category": {cat or "Unknown": count for cat, count in category_counts},
        "by_marketplace": {market: count for market, count in marketplace_counts}
    }

    return APIResponse(success=True, data=data)

from typing import Optional
from sqlalchemy.orm import joinedload
from fastapi import Query

@router.get("/recent-changes", response_model=APIResponse[list[dict]])
def get_recent_changes(
    after_id: int = Query(0, description="Get changes after this PriceHistory ID"),
    db: Session = Depends(get_db),
    user=Depends(verify_api_key)
):
    query = db.query(PriceHistory).options(
        joinedload(PriceHistory.listing).joinedload(SourceListing.canonical_product)
    ).order_by(PriceHistory.id.desc())

    if after_id == 0:
        # Just return the very last ID so frontend can initialize its cursor
        latest = query.first()
        return APIResponse(success=True, data=[{
             "history_id": latest.id if latest else 0,
             "brand": "", "name": "", "marketplace": "", "new_price": 0
        }] if latest else [])
    
    changes = query.filter(PriceHistory.id > after_id).limit(20).all()
    
    results = []
    for c in changes:
        # Reverse to chronological since we queried descending
        p = c.listing.canonical_product
        results.insert(0, {
            "history_id": c.id,
            "brand": p.brand,
            "name": p.name,
            "marketplace": c.listing.marketplace_name,
            "new_price": c.price
        })

    return APIResponse(success=True, data=results)
