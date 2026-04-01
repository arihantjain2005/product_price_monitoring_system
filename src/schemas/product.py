from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class PriceHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    price: float
    timestamp: datetime

class SourceListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    marketplace_name: str
    source_id: str
    url: str
    current_price: Optional[float] = None
    price_history: List[PriceHistoryResponse] = []

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str
    name: str
    category: str
    created_at: datetime
    listings: List[SourceListingResponse] = []
