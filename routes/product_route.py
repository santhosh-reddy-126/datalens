from fastapi import APIRouter, HTTPException, status
from typing import Optional
from datetime import datetime, timezone


from database.db import products_col, products_history_col
from models.product_model import ProductRequest
from utils.product_utils import extract_product_id, get_clean_amazon_url, collect_multiple, clean_data
from database.product_db import update_product,search_product_by_id










router = APIRouter(prefix="", tags=["product"])


@router.post("/product", status_code=status.HTTP_201_CREATED)
async def add_new_product(request: ProductRequest):
    clean_url = get_clean_amazon_url(str(request.url))
    product_id = extract_product_id(clean_url)

    existing = search_product_by_id(product_id)
    if existing:
        
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product already exists!"
        )

    results = await collect_multiple([clean_url])
    if not results or "error" in results[0]:
        print(results)
        raise HTTPException(status_code=500, detail="Scraping failed")

    data = clean_data(results[0])
    now = datetime.now(timezone.utc)

    update_product(product_id, data, clean_url, now, is_new=True)
    return {
        "product_id": product_id,
        "data": data
    }

@router.get("/product", status_code=status.HTTP_200_OK)
async def list_products():
    
    cursor = products_col.find()

    products = []
    for p in cursor:
        p["_id"] = str(p["_id"])
        products.append(p)
    
    return {"data": products}

@router.get("/product/{product_id}", status_code=status.HTTP_200_OK)
async def get_product(product_id: str):
    result = search_product_by_id(product_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    result["_id"] = str(result["_id"])
    return {"data": result}

@router.get("/product/search/{keyword}", status_code=status.HTTP_200_OK)
async def search_products(keyword: str):
    query = {"title": {"$regex": keyword, "$options": "i"}}
    
    results = []
    for p in products_col.find(query):
        p["_id"] = str(p["_id"])
        results.append(p)

    return {"data": results}


@router.get("/history/all/{product_id}", status_code=status.HTTP_200_OK)
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


@router.delete("/product/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: str):
    
    res = products_col.delete_one({"product_id": product_id})

    if res.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    products_history_col.delete_many({"product_id": product_id})

    return {
        "message": "Product deleted successfully"
    }
