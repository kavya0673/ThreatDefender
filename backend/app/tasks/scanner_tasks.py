from celery import Celery
from app.core.config import settings
from app.scanner.engine import ScannerEngine
from app.db.session import SessionLocal
import asyncio
import logging

logger = logging.getLogger(__name__)

celery_app = Celery("ares_tasks", broker=settings.get_redis_url, backend=settings.get_redis_url)

@celery_app.task(name="run_scan")
def run_scan(scan_id: int, target_url: str):
    """
    Celery task to run a website security scan.
    """
    logger.info(f"Task received: scan_id={scan_id}, target_url={target_url}")
    
    # We create a new DB session for the worker process
    db = SessionLocal()
    try:
        engine = ScannerEngine(db, scan_id)
        # run the async engine in the sync celery task
        asyncio.run(engine.run())
    except Exception as e:
        logger.error(f"Task failed for scan {scan_id}: {e}")
    finally:
        db.close()
    
    return {"scan_id": scan_id, "status": "processed"}
