from pymongo import MongoClient
from .core.config import settings

client: MongoClient = None
db = None

def connect_to_mongo():
    global client, db
    client = MongoClient(settings.DATABASE_URL)
    db = client.get_database(settings.DATABASE_NAME) # Specify database name

def close_mongo_connection():
    global client
    if client:
        client.close()

def get_mongo_db():
    return db