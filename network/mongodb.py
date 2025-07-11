from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    uri = os.getenv("MONGODB_URI")
    dbname = os.getenv("MONGODB_DB")
    collection = os.getenv("MONGODB_COLLECTION")

    client = MongoClient(uri)
    db = client[dbname]
    return db[collection]
