import logging
# No abc required
from typing import Any, List, Dict
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, before_sleep_log
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LocalFileScraper:
    def __init__(self, source_name: str):
        self._source_name = source_name
        self.client = httpx.AsyncClient(timeout=30.0)

    @property
    def source_name(self) -> str:
        return self._source_name

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def fetch_data(self, url: str) -> Any:
        if url.startswith("http://") or url.startswith("https://"):
            logger.info(f"[{self.source_name}] Fetching data from: {url}")
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        else:
            logger.info(f"[{self.source_name}] Reading local data from: {url}")
            import json
            import asyncio
            def _read_file():
                with open(url, "r", encoding="utf-8") as f:
                    return json.load(f)
            return await asyncio.to_thread(_read_file)

    @property
    def field_mapping(self) -> Dict[str, str]:
        return {
            "source_id": "product_id",
            "brand": "brand",
            "name": "model",
            "price": "price",
            "url": "product_url",
            "category": "category"
        }

    def _normalize_category(self, item: Dict[str, Any], mapping: Dict[str, str]) -> str:
        raw_cat = str(item.get(mapping.get("category", "category"), "")).lower()
        if not raw_cat or raw_cat == "none":
            raw_cat = str(item.get("metadata", {}).get("garment_type", "")).lower()
            
        name = str(item.get(mapping.get("name", "name"), "")).lower()
        
        if "belt" in raw_cat or "belt" in name:
            return "Belts"
        elif "jewel" in raw_cat or "tiffany" in name:
            return "Jewelry"
        elif "apparel" in raw_cat or "shirt" in name or "jeans" in name or "hoodie" in name:
            return "Apparel"
            
        return "General"

    async def parse_products(self, data: Any) -> List[Dict[str, Any]]:
        results = []
        mapping = self.field_mapping
        list_path = mapping.get("list_path")
        
        if list_path and isinstance(data, dict) and list_path in data:
            items = data.get(list_path, [])
        else:
            items = [data] if isinstance(data, dict) else data
            
        for item in items:
            product = {
                "source_id": str(item.get(mapping.get("source_id", "source_id"))),
                "marketplace_name": self.source_name,
                "brand": item.get(mapping.get("brand", "brand"), "Unknown"),
                "name": item.get(mapping.get("name", "name"), "Unknown"),
                "price": float(item.get(mapping.get("price", "price"), 0)),
                "url": item.get(mapping.get("url", "url"), ""),
                "category": self._normalize_category(item, mapping)
            }
            if product["source_id"] and product["price"] > 0:
                results.append(product)
        return results

    async def scrape(self, target_url: str) -> List[Dict[str, Any]]:
        try:
            logger.info(f"[{self.source_name}] Starting ingestion cycle.")
            raw_data = await self.fetch_data(target_url)
            parsed_items = await self.parse_products(raw_data)
            logger.info(f"[{self.source_name}] Successfully parsed {len(parsed_items)} items.")
            return parsed_items
        except Exception as e:
            logger.error(f"[{self.source_name}] Fatal failure during ingestion: {str(e)}")
            return []

    async def close(self):
        await self.client.aclose()
