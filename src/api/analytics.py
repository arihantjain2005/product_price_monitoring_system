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
