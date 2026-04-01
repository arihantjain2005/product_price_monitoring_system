import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.base import Base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./prices.db")

# WAL mode improves concurrency in SQLite, avoiding "database is locked" errors
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

if DATABASE_URL.startswith("sqlite"):
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA journal_mode=WAL;")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
