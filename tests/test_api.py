from datetime import datetime
import pytest
from src.models.product import CanonicalProduct, SourceListing, PriceHistory

def test_api_auth_failure(client):
    # Missing API Key
    response = client.get("/products")
    assert response.status_code == 401
    assert "Missing X-API-Key" in response.json()["error"]
    
    # Invalid API Key
    response = client.get("/products", headers={"X-API-Key": "invalid_key"})
    assert response.status_code == 401
    assert "Invalid API Key" in response.json()["error"]

def test_api_products_list_and_filter(client, db_session):
    # Setup dummy data
    p1 = CanonicalProduct(brand="Chanel", name="Belt", category="Belts")
    p2 = CanonicalProduct(brand="Tiffany", name="Ring", category="Jewelry")
    db_session.add_all([p1, p2])
    db_session.commit()
    
    l1 = SourceListing(canonical_product_id=p1.id, marketplace_name="1stdibs", source_id="1", url="http://test")
    l2 = SourceListing(canonical_product_id=p2.id, marketplace_name="Fashionphile", source_id="2", url="http://test2")
    db_session.add_all([l1, l2])
    db_session.commit()
    
    h1 = PriceHistory(source_listing_id=l1.id, price=100.0)
    h2 = PriceHistory(source_listing_id=l2.id, price=50.0)
    db_session.add_all([h1, h2])
    db_session.commit()
    
    headers = {"X-API-Key": "test_api_key"}
    
    # List all
    response = client.get("/products", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    
    # Filter by category
    response = client.get("/products?category=Jewelry", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["brand"] == "Tiffany"
    
    # Filter by source
    response = client.get("/products?source=1stdibs", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    
    # Filter by price range
    response = client.get("/products?min_price=60&max_price=200", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["brand"] == "Chanel"

def test_api_product_detail_and_history(client, db_session):
    p1 = CanonicalProduct(brand="Amiri", name="Jeans", category="Apparel")
    db_session.add(p1)
    db_session.commit()
    
    l1 = SourceListing(canonical_product_id=p1.id, marketplace_name="Grailed", source_id="1", url="http")
    db_session.add(l1)
    db_session.commit()
    
    h1 = PriceHistory(source_listing_id=l1.id, price=300.0)
    h2 = PriceHistory(source_listing_id=l1.id, price=250.0)
    db_session.add_all([h1, h2])
    db_session.commit()
    
    headers = {"X-API-Key": "test_api_key"}
    
    # Detail
    response = client.get(f"/products/{p1.id}", headers=headers)
    assert response.status_code == 200
    product = response.json()["data"]
    assert product["brand"] == "Amiri"
    assert len(product["listings"]) == 1
    assert len(product["listings"][0]["price_history"]) == 2
    
    # History
    response = client.get(f"/products/{p1.id}/history", headers=headers)
    assert response.status_code == 200
    history = response.json()["data"]
    assert len(history) == 2
    # Ensure sorted by time
    assert history[0]["price"] == 300.0 or history[1]["price"] == 300.0

def test_api_analytics(client, db_session):
    p1 = CanonicalProduct(brand="Gucci", name="Bag", category="Bags")
    db_session.add(p1)
    db_session.commit()
    
    l1 = SourceListing(canonical_product_id=p1.id, marketplace_name="Grailed", source_id="1", url="http")
    db_session.add(l1)
    db_session.commit()
    
    h1 = PriceHistory(source_listing_id=l1.id, price=1000.0)
    db_session.add(h1)
    db_session.commit()
    
    headers = {"X-API-Key": "test_api_key"}
    response = client.get("/analytics", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["summary"]["total_canonical_products"] == 1
    assert data["summary"]["total_tracked_listings"] == 1
    assert "Grailed" in data["by_marketplace"]
    assert data["by_marketplace"]["Grailed"] == 1
