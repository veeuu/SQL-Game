from pymongo import MongoClient
from datetime import datetime
import os

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
DB_NAME = "sql-challenges"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
users_collection = db["users"]
progress_collection = db["progress"]
challenges_collection = db["challenges"]
level_completions_collection = db["level_completions"]
rooms_collection = db["rooms"]
daily_activity_collection = db["daily_activity"]

# Create indexes
users_collection.create_index("username", unique=True)
users_collection.create_index("email", unique=True)
progress_collection.create_index("user_id")
level_completions_collection.create_index([("user_id", 1), ("level", 1)])
daily_activity_collection.create_index([("user_id", 1), ("date", 1)], unique=True)

def init_challenges():
    """Initialize challenges in MongoDB if not exists"""
    if challenges_collection.count_documents({}) == 0:
        from challenges import CHALLENGES
        challenges_collection.insert_many(CHALLENGES)
        print("✅ Challenges initialized in MongoDB")

# Initialize on import
init_challenges()
