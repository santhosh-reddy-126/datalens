import logging
from datetime import datetime, timezone
import uvicorn
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from db import products_col, products_history_col
from product import ProductRequest, collect_multiple, extract_product_id, clean_data, get_clean_amazon_url
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
    clean_url = get_clean_amazon_url(str(request.url))
    if not clean_url:
        return {"status": False, "message": "unable to clean url"}
    product_id = extract_product_id(clean_url)
    if not product_id:
        raise HTTPException(status_code=400, detail="Invalid Amazon URL")
    results = await collect_multiple([clean_url])
    if not results or "error" in results[0]:
        raise HTTPException(status_code=500, detail="Scraping failed")

    data = clean_data(results[0])
    now = datetime.now(timezone.utc)
    update_db(product_id, data, clean_url, now, is_new=True)
    return {"status": True, "product_id": product_id, "data": data}

@app.get("/product", status_code=status.HTTP_200_OK)
async def list_products(tracking: Optional[bool] = None):
    
    query = {}
    
    if tracking is not None:
        query["tracking"] = tracking

    cursor = products_col.find(query)

    products = []
    for p in cursor:
        p["_id"] = str(p["_id"])
        products.append(p)
    
    return {"data": products}

@app.get("/product/{product_id}", status_code=status.HTTP_200_OK)
async def get_product(product_id: str):
    result = search_product_by_id(product_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    result["_id"] = str(result["_id"])
    return {"data": result}

@app.get("/product/search/{keyword}", status_code=status.HTTP_200_OK)
async def search_products(keyword: str):
    query = {"tracking": True, "title": {"$regex": keyword, "$options": "i"}}
    
    results = []
    for p in products_col.find(query):
        p["_id"] = str(p["_id"])
        results.append(p)

    return {"data": results}

@app.patch("/product/track/{product_id}", status_code=status.HTTP_200_OK)
async def toggle_tracking(product_id: str, active: bool):
    res = products_col.update_one(
        {"product_id": product_id},
        {"$set": {"tracking": active}}
    )

    if res.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return {"message": f"Tracking set to {active}"}


@app.get("/history/all/{product_id}", status_code=status.HTTP_200_OK)
async def get_full_product_history(product_id: str):
    docs = list(
        products_history_col.find({"product_id": product_id})
        .sort("created_at", 1)
    )

    if not docs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No history found"
        )

    for doc in docs:
        doc["_id"] = str(doc["_id"])

    return {"data": docs} 


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=settings.port,
        log_level="info"
    )