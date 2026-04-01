from fastapi import APIRouter, Depends, BackgroundTasks, status
from src.database import SessionLocal
from src.schemas.base import APIResponse
from src.api.dependencies import verify_api_key
from src.services.scrapers import GrailedScraper, FashionphileScraper, FirstDibsScraper
from src.services.ingestion import process_scraped_items
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/refresh", tags=["refresh"])

async def execute_refresh():
    db = SessionLocal()
    try:
        scrapers = [
            (GrailedScraper(), "https://example.com/api/grailed_mock"),
            (FashionphileScraper(), "https://example.com/api/fashionphile_mock"),
            (FirstDibsScraper(), "https://example.com/api/1stdibs_mock")
        ]
        
        all_results = []
        for scraper, url in scrapers:
            results = await scraper.scrape(url)
            all_results.extend(results)
            await scraper.close()
            
        process_scraped_items(db, all_results)
        logger.info(f"Background refresh complete. Ingested {len(all_results)} items.")
    except Exception as e:
        logger.error(f"Background refresh failed: {e}")
    finally:
        db.close()

@router.post("", response_model=APIResponse[str], status_code=status.HTTP_202_ACCEPTED)
async def trigger_refresh(
    background_tasks: BackgroundTasks,
    user=Depends(verify_api_key)
):
    background_tasks.add_task(execute_refresh)
    return APIResponse(success=True, data="Data refresh triggered in the background.")
