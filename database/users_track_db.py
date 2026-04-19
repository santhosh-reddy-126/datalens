from datetime import datetime
from bson import ObjectId
from database.db import users_track_col,fix_id
from models.users_track_model import UsersTrackInDB
def create_users_track(product_id: str, email: str, now: datetime):
    users_track_doc = UsersTrackInDB(
        product_id= product_id,
        email= email,
        created_at= now
    )


    users_track_col.insert_one(users_track_doc.model_dump())

def get_users_track_by_product(product_id: str):
    docs = list(users_track_col.find({"product_id":product_id}))
    docs=fix_id(docs)
    return docs

def get_users_track_by_email(email: str):
    docs = list(users_track_col.find({"email": email}))
    docs=fix_id(docs)
    return docs

def get_mapping_between_user_and_product(product_id: str, email: str):
    doc = users_track_col.find_one({
        "email": email,
        "product_id": product_id
    })

    if not doc:
        return None

    doc["_id"] = str(doc["_id"])
    return doc

def delete_users_track(product_id: str, email: str):
    users_track_col.delete_one({
        "email": email,
        "product_id": product_id
        })