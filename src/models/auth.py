from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from src.models.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class ApiUser(Base):
    """
    Represents an authenticated consumer of our API.
    """
    __tablename__ = "api_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    usage_logs = relationship("ApiUsage", back_populates="user", cascade="all, delete-orphan")

class ApiUsage(Base):
    """
    Tracks usage per request as mandated by the assignment.
    """
    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, index=True)
    api_user_id = Column(Integer, ForeignKey("api_users.id"), nullable=False)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    timestamp = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("ApiUser", back_populates="usage_logs")

# Indexing usage logs by user and time for efficient rate-limiting queries
Index("ix_api_usage_user_time", ApiUsage.api_user_id, ApiUsage.timestamp.desc())
