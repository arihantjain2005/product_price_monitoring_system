from typing import Any, Dict, List
from src.services.scraper_base import MarketplaceScraper

class GrailedScraper(MarketplaceScraper):
    @property
    def source_name(self) -> str:
        return "Grailed"

    @property
    def field_mapping(self) -> Dict[str, str]:
        return {
            "list_path": "data",
            "source_id": "id",
            "brand": "designer",
            "name": "title",
            "price": "price",
            "url": "url",
            "category": "category"
        }

class FashionphileScraper(MarketplaceScraper):
    @property
    def source_name(self) -> str:
        return "Fashionphile"

    @property
    def field_mapping(self) -> Dict[str, str]:
        return {
            "list_path": "results",
            "source_id": "sku",
            "brand": "brand",
            "name": "product_name",
            "price": "current_price",
            "url": "product_url",
            "category": "category"
        }

class FirstDibsScraper(MarketplaceScraper):
    @property
    def source_name(self) -> str:
        return "1stdibs"

    @property
    def field_mapping(self) -> Dict[str, str]:
        return {
            "list_path": "items",
            "source_id": "item_id",
            "brand": "maker",
            "name": "title",
            "price": "price_usd",
            "url": "url",
            "category": "category"
        }
