from typing import Any, Dict, List
from src.services.scraper_base import MarketplaceScraper

class GrailedScraper(MarketplaceScraper):
    @property
    def source_name(self) -> str:
        return "Grailed"

    async def parse_products(self, data: Any) -> List[Dict[str, Any]]:
        results = []
        items = data.get("data", [])
        for item in items:
            product = {
                "source_id": str(item.get("id")),
                "marketplace_name": self.source_name,
                "brand": item.get("designer", "Unknown"),
                "name": item.get("title", "Unknown"),
                "price": float(item.get("price", 0)),
                "url": item.get("url", ""),
                "category": item.get("category", "General")
            }
            if product["source_id"] and product["price"] > 0:
                results.append(product)
        return results

class FashionphileScraper(MarketplaceScraper):
    @property
    def source_name(self) -> str:
        return "Fashionphile"

    async def parse_products(self, data: Any) -> List[Dict[str, Any]]:
        results = []
        items = data.get("results", [])
        for item in items:
            product = {
                "source_id": str(item.get("sku")),
                "marketplace_name": self.source_name,
                "brand": item.get("brand", "Unknown"),
                "name": item.get("product_name", "Unknown"),
                "price": float(item.get("current_price", 0)),
                "url": item.get("product_url", ""),
                "category": item.get("category", "General")
            }
            if product["source_id"] and product["price"] > 0:
                results.append(product)
        return results

class FirstDibsScraper(MarketplaceScraper):
    @property
    def source_name(self) -> str:
        return "1stdibs"

    async def parse_products(self, data: Any) -> List[Dict[str, Any]]:
        results = []
        items = data.get("items", [])
        for item in items:
            product = {
                "source_id": str(item.get("item_id")),
                "marketplace_name": self.source_name,
                "brand": item.get("maker", "Unknown"),
                "name": item.get("title", "Unknown"),
                "price": float(item.get("price_usd", 0)),
                "url": item.get("url", ""),
                "category": item.get("category", "General")
            }
            if product["source_id"] and product["price"] > 0:
                results.append(product)
        return results
