import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from contextlib import contextmanager

from src.main import app
from src.database import Base, get_db
from src.models.auth import ApiUser

# Setup an SQLite database for testing (not in-memory per thread)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_session():
    # Import all models to ensure they are registered with Base.metadata
    import src.models.auth
    import src.models.product
    import src.models.event
    import src.models.webhook
    # Create tables before each test
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    # Drop tables after each test to ensure isolation
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    # Setup test user for auth
    test_user = ApiUser(username="test_user", api_key="test_api_key")
    db_session.add(test_user)
    db_session.commit()
    
    with TestClient(app) as test_client:
        yield test_client
