import logging
from abc import ABC, abstractmethod
from typing import Any, List, Dict
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, before_sleep_log
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MarketplaceScraper(ABC):
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    @property
    @abstractmethod
    def source_name(self) -> str:
        pass

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def fetch_data(self, url: str) -> Any:
        logger.info(f"[{self.source_name}] Fetching data from: {url}")
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    @abstractmethod
    async def parse_products(self, data: Any) -> List[Dict[str, Any]]:
        pass

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
