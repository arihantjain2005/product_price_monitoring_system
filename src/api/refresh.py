from fastapi import APIRouter, Depends, BackgroundTasks, status
from src.database import SessionLocal
from src.schemas.base import APIResponse
from src.api.dependencies import verify_api_key
# Redundant scraper module removed
from src.services.ingestion import process_scraped_items
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/refresh", tags=["refresh"])

async def execute_refresh():
    import os
    import asyncio
    from src.services.scraper_base import LocalFileScraper
    db = SessionLocal()
    try:
        scrapers = {
            "grailed": LocalFileScraper("Grailed"),
            "fashionphile": LocalFileScraper("Fashionphile"),
            "1stdibs": LocalFileScraper("1stdibs")
        }
        
        base_dir = "sample_products/sample_products"
        all_results = []
        
        if os.path.exists(base_dir):
            for filename in os.listdir(base_dir):
                if not filename.endswith(".json"):
                    continue
                file_path = os.path.join(base_dir, filename)
                
                # Identify marketplace mapping
                for prefix, scraper in scrapers.items():
                    if filename.startswith(prefix):
                        results = await scraper.scrape(file_path)
                        all_results.extend(results)
                        break
                
        for scraper in scrapers.values():
            await scraper.close()
            
        await asyncio.to_thread(process_scraped_items, db, all_results)
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
