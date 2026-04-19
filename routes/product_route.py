from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone

from database.db import products_col, products_history_col, users_track_col
from models.product_model import (
    ProductRequest,
    ProductResponse,
    ProductListResponse,
    ProductCreateResponse,
    MessageResponse,
)
from models.product_model import (
    ProductHistoryResponse,
    ProductHistoryListResponse,
)
from utils.product_utils import extract_product_id, get_clean_amazon_url, collect_multiple, clean_data
from database.product_db import create_product, search_product_by_id, delete_product_by_id
from database.users_track_db import get_mapping_between_user_and_product, create_users_track, get_users_track_by_email, delete_users_track, get_users_track_by_product
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
    now = datetime.now(timezone.utc)
    existing = search_product_by_id(product_id)
    if existing:
        email = _user["email"]
        existing_for_current_user = get_mapping_between_user_and_product(product_id, email)
        if existing_for_current_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product already exists!"
            )
        data = {'url': existing["url"], 
                'title': existing["title"], 
                'price': existing["price"], 
                'rating': existing["rating"],
                'image_url': existing["imageUrl"], 
                'final_url': existing["url"]
            }
        create_users_track(product_id,_user["email"],now)
        return ProductCreateResponse(product_id=product_id, data=data)

    results = await collect_multiple([clean_url])
    if not results or "error" in results[0]:
        raise HTTPException(status_code=500, detail="Scraping failed")

    data = clean_data(results[0])
    
    create_product(product_id, data, clean_url, now, _user["email"])
    create_users_track(product_id,_user["email"],now)
    return ProductCreateResponse(product_id=product_id, data=data)


@router.get("/product", status_code=status.HTTP_200_OK, response_model=ProductListResponse)
async def list_products(_user: dict = Depends(get_current_user)):
    docs = get_users_track_by_email(_user["email"])
    products = []
    for doc in docs:
        product_id = doc["product_id"]
        product = products_col.find_one({"product_id": product_id})
        product = _to_product_response(product)
        products.append(product)
    return ProductListResponse(data=products)


@router.get("/product/{product_id}", status_code=status.HTTP_200_OK)
async def get_product(product_id: str, _user: dict = Depends(get_current_user)):
    result = search_product_by_id(product_id)
    existing_for_current_user = get_mapping_between_user_and_product(product_id, _user["email"])

    if not result or not existing_for_current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return {"data": _to_product_response(result)}


@router.get("/product/search/{keyword}", status_code=status.HTTP_200_OK, response_model=ProductListResponse)
async def search_products(keyword: str, _user: dict = Depends(get_current_user)):
    email = _user.get("email")

    user_products = users_track_col.find(
        {"email": email},
        {"product_id": 1, "_id": 0}
    )
    product_ids = [doc["product_id"] for doc in user_products]

    if not product_ids:
        return ProductListResponse(data=[])


    query = {
        "title": {"$regex": keyword, "$options": "i"},
        "product_id": {"$in": product_ids}
    }
    results = [_to_product_response(p) for p in products_col.find(query)]
    return ProductListResponse(data=results)


@router.get("/history/all/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductHistoryListResponse)
async def get_full_product_history(product_id: str, _user: dict = Depends(get_current_user)):
    docs = list(
        products_history_col.find({"product_id": product_id})
        .sort("created_at", 1)
    )

    existing_for_current_user = get_mapping_between_user_and_product(product_id, _user["email"])

    if not docs or not existing_for_current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No history found"
        )

    return ProductHistoryListResponse(data=[_to_history_response(d) for d in docs])


@router.delete("/product/{product_id}", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def delete_product(product_id: str, _user: dict = Depends(get_current_user)):
    email = _user.get("email")

    existing = get_mapping_between_user_and_product(product_id, email)

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found for this user"
        )
    
    delete_users_track(product_id,email)

    still_user_tracks = get_users_track_by_product(product_id)

    if not still_user_tracks:
        deleted = delete_product_by_id(product_id)

        if deleted == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

    return MessageResponse(message="Product deleted successfully")
