from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from src.models.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class PriceChangeEvent(Base):
    """
    Implements the Transactional Outbox Pattern.
    When a price changes, we write the new PriceHistory AND a PriceChangeEvent 
    in the exact same database transaction. A separate background worker reads 
    from this table to notify webhooks, guaranteeing zero event loss.
    """
    __tablename__ = "price_change_events"

    id = Column(Integer, primary_key=True, index=True)
    price_history_id = Column(Integer, ForeignKey("price_history.id"), nullable=False)
    # Status can be: 'pending', 'processing', 'completed', 'failed'
    status = Column(String, default="pending", index=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    processed_at = Column(DateTime, nullable=True)

    price_history = relationship("PriceHistory")
