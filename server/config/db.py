import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from config.logger import get_logger

load_dotenv()

logger = get_logger("config.db")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

logger.info("Connecting to MongoDB | db=%s", DB_NAME)
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    logger.info("MongoDB connection established | db=%s", DB_NAME)
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    logger.error("MongoDB connection failed: %s", e)
    raise

db = client[DB_NAME]
users_collection = db["users"]
documents_collection = db["documents"]
