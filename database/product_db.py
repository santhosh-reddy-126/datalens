from datetime import datetime

from database.db import products_col, products_history_col
from models.product_model import ProductInDB
from models.product_model import ProductHistoryInDB
from models.users_track_model import UsersTrackInDB


def create_product(product_id: str, data: dict, url: str, now: datetime, email: str) -> None:
    """Insert a brand-new product and its first history entry."""
    product = ProductInDB(
        product_id=product_id,
        url=url,
        title=data.get("title"),
        imageUrl=data.get("image_url"),
        rating=data.get("rating"),
        price=data.get("price"),
        updated_at=now,
    )
    products_col.update_one(
        {"product_id": product_id},
        {"$set": product.model_dump()},
        upsert=True,
    )

    history = ProductHistoryInDB(
        product_id=product_id,
        price=data.get("price"),
        created_at=now,
    )
    products_history_col.insert_one(history.model_dump())


def update_product_price(product_id: str, data: dict, now: datetime) -> None:
    """Update only the price and timestamp for an existing product."""
    products_col.update_one(
        {"product_id": product_id},
        {"$set": {"price": data.get("price"), "updated_at": now}},
    )

    history = ProductHistoryInDB(
        product_id=product_id,
        price=data.get("price"),
        created_at=now,
    )
    products_history_col.insert_one(history.model_dump())


def search_product_by_id(product_id: str) -> dict | None:
    """Find a single product by its product_id."""
    return products_col.find_one({"product_id": product_id})


def delete_product_by_id(product_id: str) -> int:
    """Delete a product and all its history. Returns deleted count."""
    res = products_col.delete_one({"product_id": product_id})
    if res.deleted_count > 0:
        products_history_col.delete_many({"product_id": product_id})
    return res.deleted_count