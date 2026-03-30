from pymongo import MongoClient
from pymongo.server_api import ServerApi
from settings import settings

client = MongoClient(settings.mongo_uri, server_api=ServerApi('1'))
db = client["datalens"]
products_col = db["product"]
products_history_col = db["product_history"]