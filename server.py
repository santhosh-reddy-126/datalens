import logging
from datetime import datetime, timezone
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import products_col
from routes.auth_route import router as auth_router
from routes.product_route import router as product_router
from utils.product_utils import collect_multiple, clean_data
from database.product_db import update_product
from settings import settings


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_title)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
scheduler = AsyncIOScheduler()
app.include_router(auth_router)
app.include_router(product_router)


async def track_prices_job():
    tracked_products = list(products_col.find())
    if not tracked_products:
        logger.info("No tracked products found.")
        return
    urls = [product["url"] for product in tracked_products]
    results = await collect_multiple(urls)
    now = datetime.now(timezone.utc)
    for product, raw_result in zip(tracked_products, results):
        if not raw_result or "error" in raw_result:
            continue
        data = clean_data(raw_result)
        if not data:
            continue
        new_price = data.get("price")
        if new_price != product.get("price"):
            logger.info("Price change detected for %s", product["product_id"])
            update_product(product["product_id"], data, product["url"], now, is_new=False)

@app.on_event("startup")
async def startup_event():
    scheduler.add_job(track_prices_job, "interval", minutes=settings.scheduler_interval_minutes)
    scheduler.start()
    logger.info("Price Tracker Scheduler active")


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=settings.port,
        log_level="info"
    )