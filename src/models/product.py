from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from src.models.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class CanonicalProduct(Base):
    __tablename__ = "canonical_products"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    listings = relationship("SourceListing", back_populates="canonical_product", cascade="all, delete-orphan")

class SourceListing(Base):
    __tablename__ = "source_listings"

    id = Column(Integer, primary_key=True, index=True)
    canonical_product_id = Column(Integer, ForeignKey("canonical_products.id"), nullable=False)
    marketplace_name = Column(String, index=True, nullable=False)
    source_id = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    canonical_product = relationship("CanonicalProduct", back_populates="listings")
    price_history = relationship("PriceHistory", back_populates="listing", cascade="all, delete-orphan")

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    source_listing_id = Column(Integer, ForeignKey("source_listings.id"), nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=utc_now, nullable=False)

    listing = relationship("SourceListing", back_populates="price_history")

# The assignment specifies we must scale to millions of price rows. 
# Indexing by listing and time provides O(log N) lookup instead of a full table scan.
Index("ix_price_history_listing_time", PriceHistory.source_listing_id, PriceHistory.timestamp.desc())
