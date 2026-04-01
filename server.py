import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from db import products_col, products_history_col
from product import ProductRequest, collect_multiple, extract_product_id, clean_data
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

async def get_latest_history(product_id: str):
    doc = products_history_col.find_one({"product_id": product_id}, sort=[("created_at", -1)])
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

def update_db(product_id, data, url, now, is_new=False):
    payload = {
        "price": data.get("price"),
        "updated_at": now
    }
    if is_new:
        payload.update({
            "url": url,
            "title": data.get("title"),
            "imageUrl": data.get("image_url"),
            "rating": data.get("rating"),
            "tracking": True
        })
    products_col.update_one({"product_id": product_id}, {"$set": payload}, upsert=True)
    if not is_new:
        products_history_col.insert_one({
            "product_id": product_id,
            "price": data.get("price"),
            "created_at": now
        })

async def track_prices_job():
    tracked_products = list(products_col.find({"tracking": True}))
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
            update_db(product["product_id"], data, product["url"], now, is_new=False)

@app.on_event("startup")
async def startup_event():
    scheduler.add_job(track_prices_job, "interval", minutes=settings.scheduler_interval_minutes)
    scheduler.start()
    logger.info("Price Tracker Scheduler active")

@app.post("/product", status_code=status.HTTP_201_CREATED)
async def add_new_product(request: ProductRequest):
    product_id = extract_product_id(request.url)
    if not product_id:
        raise HTTPException(status_code=400, detail="Invalid Amazon URL")
    results = await collect_multiple([request.url])
    if not results or "error" in results[0]:
        raise HTTPException(status_code=500, detail="Scraping failed")
    data = clean_data(results[0])
    now = datetime.now(timezone.utc)
    update_db(product_id, data, request.url, now, is_new=True)
    return {"status": "success", "product_id": product_id, "data": data}

@app.get("/product")
async def list_tracked_products():
    cursor = products_col.find({"tracking": True})
    return {"status": True, "data": [dict(p, _id=str(p["_id"])) for p in cursor]}

@app.get("/product/search/{keyword}")
async def search_products(keyword: str):
    query = {"tracking": True, "title": {"$regex": keyword, "$options": "i"}}
    results = [dict(p, _id=str(p["_id"])) for p in products_col.find(query)]
    return {"status": True, "data": results}

@app.patch("/product/track/{product_id}")
async def toggle_tracking(product_id: str, active: bool):
    res = products_col.update_one({"product_id": product_id}, {"$set": {"tracking": active}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": True, "message": f"Tracking set to {active}"}

@app.get("/history/all/{product_id}")
async def get_full_product_history(product_id: str):
    docs = list(products_history_col.find({"product_id": product_id}).sort("created_at", 1))
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return {"status": True, "data": docs}


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=settings.port,
        log_level="info"
    )