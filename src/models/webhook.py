from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from src.models.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
