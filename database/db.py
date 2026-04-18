from pymongo import MongoClient
from pymongo.server_api import ServerApi
from settings import settings

client = MongoClient(settings.mongo_uri, server_api=ServerApi('1'))
db = client["datalens"]
products_col = db["product"]
products_history_col = db["product_history"]
users_col = db["users"]





users_col.create_index("email", unique=True)
products_col.create_index("product_id", unique=True)

def search_product_by_id(id:str):
    return products_col.find_one({"product_id":id})
     