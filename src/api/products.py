from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from src.database import get_db
from src.models.product import CanonicalProduct, SourceListing, PriceHistory
from src.schemas.product import ProductResponse
from src.schemas.base import APIResponse
from src.api.dependencies import verify_api_key

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", response_model=APIResponse[List[ProductResponse]])
def get_products(
    category: Optional[str] = None,
    source: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(verify_api_key)
):
    query = db.query(CanonicalProduct).outerjoin(CanonicalProduct.listings).outerjoin(SourceListing.price_history)

    if category:
        query = query.filter(CanonicalProduct.category == category)
    if source:
        query = query.filter(SourceListing.marketplace_name == source)
    if min_price is not None:
        query = query.filter(PriceHistory.price >= min_price)
    if max_price is not None:
        query = query.filter(PriceHistory.price <= max_price)

    products = query.group_by(CanonicalProduct.id).offset(skip).limit(limit).all()

    return APIResponse(success=True, data=products)

@router.get("/{product_id}", response_model=APIResponse[ProductResponse])
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_api_key)
):
    product = db.query(CanonicalProduct).options(
        joinedload(CanonicalProduct.listings).joinedload(SourceListing.price_history)
    ).filter(CanonicalProduct.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return APIResponse(success=True, data=product)

@router.get("/{product_id}/history", response_model=APIResponse[list[dict]])
def get_product_history(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_api_key)
):
    product = db.query(CanonicalProduct).options(
        joinedload(CanonicalProduct.listings).joinedload(SourceListing.price_history)
    ).filter(CanonicalProduct.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    history_flat = []
    for listing in product.listings:
        for history in listing.price_history:
            history_flat.append({
                "marketplace": listing.marketplace_name,
                "price": history.price,
                "timestamp": history.timestamp.isoformat()
            })
            
    history_flat.sort(key=lambda x: x["timestamp"])
    return APIResponse(success=True, data=history_flat)
