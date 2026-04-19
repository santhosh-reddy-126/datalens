from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone

from database.db import products_col, products_history_col
from models.product_model import (
    ProductRequest,
    ProductResponse,
    ProductListResponse,
    ProductCreateResponse,
    MessageResponse,
)
from models.product_history_model import (
    ProductHistoryResponse,
    ProductHistoryListResponse,
)
from utils.product_utils import extract_product_id, get_clean_amazon_url, collect_multiple, clean_data
from database.product_db import create_product, search_product_by_id, delete_product_by_id
from utils.auth_utils import get_current_user


router = APIRouter(prefix="", tags=["product"])


def _to_product_response(doc: dict) -> ProductResponse:
    """Convert a MongoDB product document to a ProductResponse."""
    return ProductResponse(
        id=str(doc["_id"]),
        product_id=doc["product_id"],
        url=doc.get("url", ""),
        title=doc.get("title"),
        imageUrl=doc.get("imageUrl"),
        rating=doc.get("rating"),
        price=doc.get("price"),
        updated_at=doc.get("updated_at"),
    )


def _to_history_response(doc: dict) -> ProductHistoryResponse:
    """Convert a MongoDB history document to a ProductHistoryResponse."""
    return ProductHistoryResponse(
        id=str(doc["_id"]),
        product_id=doc["product_id"],
        price=doc.get("price"),
        created_at=doc["created_at"],
    )


@router.post("/product", status_code=status.HTTP_201_CREATED, response_model=ProductCreateResponse)
async def add_new_product(request: ProductRequest, _user: dict = Depends(get_current_user)):
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
        raise HTTPException(status_code=500, detail="Scraping failed")

    data = clean_data(results[0])
    now = datetime.now(timezone.utc)

    create_product(product_id, data, clean_url, now)
    return ProductCreateResponse(product_id=product_id, data=data)


@router.get("/product", status_code=status.HTTP_200_OK, response_model=ProductListResponse)
async def list_products(_user: dict = Depends(get_current_user)):
    cursor = products_col.find()
    products = [_to_product_response(p) for p in cursor]
    return ProductListResponse(data=products)


@router.get("/product/{product_id}", status_code=status.HTTP_200_OK)
async def get_product(product_id: str, _user: dict = Depends(get_current_user)):
    result = search_product_by_id(product_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return {"data": _to_product_response(result)}


@router.get("/product/search/{keyword}", status_code=status.HTTP_200_OK, response_model=ProductListResponse)
async def search_products(keyword: str, _user: dict = Depends(get_current_user)):
    query = {"title": {"$regex": keyword, "$options": "i"}}
    results = [_to_product_response(p) for p in products_col.find(query)]
    return ProductListResponse(data=results)


@router.get("/history/all/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductHistoryListResponse)
async def get_full_product_history(product_id: str, _user: dict = Depends(get_current_user)):
    docs = list(
        products_history_col.find({"product_id": product_id})
        .sort("created_at", 1)
    )

    if not docs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No history found"
        )

    return ProductHistoryListResponse(data=[_to_history_response(d) for d in docs])


@router.delete("/product/{product_id}", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def delete_product(product_id: str, _user: dict = Depends(get_current_user)):
    deleted = delete_product_by_id(product_id)

    if deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return MessageResponse(message="Product deleted successfully")
