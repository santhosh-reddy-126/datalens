from database.db import products_col, products_history_col

def update_product(product_id, data, url, now, is_new=False):
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



def search_product_by_id(id:str):
    return products_col.find_one({"product_id":id})