"""
Storage operations for word data, supporting both MongoDB and local file storage.
"""
import os
import json
import datetime
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
from dotenv import load_dotenv
from .word_utils import get_learning_difficulty

# Load environment variables from .env file if it exists
load_dotenv()

# MongoDB connection settings - set to None if not using MongoDB
MONGODB_URI = os.environ.get("MONGODB_URI", None)  # Can be set via environment variable
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME", "word_learning")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION", "word_history")

# MongoDB client - will be initialized if connection string is provided
mongo_client = None
db = None
word_collection = None

def initialize_mongodb():
    """Initialize MongoDB connection if a connection string is provided"""
    global mongo_client, db, word_collection
    
    if not MONGODB_URI:
        print("MongoDB URI not provided. Using local file storage.")
        return False
    
    try:
        # Set a short timeout for the connection attempt
        mongo_client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        
        # Verify connection
        mongo_client.admin.command('ping')
        
        # Initialize database and collection
        db = mongo_client[MONGODB_DB_NAME]
        word_collection = db[MONGODB_COLLECTION]
        
        # Try to create index on word field for faster lookups
        try:
            word_collection.create_index("word")
        except OperationFailure as op_err:
            # If permission error for creating index, log it but continue
            print(f"Warning: Could not create index (permission issue): {op_err}")
            # We can still use the database without an index
        
        print("Connected to MongoDB successfully.")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"MongoDB connection failed: {e}. Using local file storage.")
        mongo_client = None
        return False

def save_to_mongodb(word, info):
    """Save word to MongoDB if connection is available"""
    if word_collection is None:
        return False
    
    try:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Check if word already exists in database
        existing_word = word_collection.find_one({"word": word})
        
        if existing_word:
            # Update existing word
            word_collection.update_one(
                {"word": word},
                {
                    "$inc": {"review_count": 1},
                    "$set": {"last_reviewed": today}
                }
            )
        else:
            # Insert new word
            word_data = {
                "word": word,
                "date_added": today,
                "last_reviewed": today,
                "review_count": 1,
                "difficulty": get_learning_difficulty(word)
            }
            
            # Add some word info for future reference
            if info:
                word_data["phonetics"] = info.get("phonetics", [])
                word_data["meanings"] = info.get("meanings", [])
            
            word_collection.insert_one(word_data)
        
        return True
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")
        return False

def save_to_file(word, info):
    """Save word to history file for spaced repetition learning"""
    history_file = "word_history.json"
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = {"words": []}
    else:
        history = {"words": []}
    
    # Add word to history
    word_entry = {
        "word": word,
        "date_added": today,
        "review_count": 0,
        "next_review": today
    }
    
    # Check if word already exists in history
    for entry in history["words"]:
        if entry["word"] == word:
            entry["review_count"] += 1
            return
    
    history["words"].append(word_entry)
    
    # Save updated history
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

def save_word_history(word, info):
    """Save word to history using available methods"""
    # Try saving to MongoDB first
    mongo_success = save_to_mongodb(word, info)
    
    # Always save to file as fallback
    save_to_file(word, info)
    
    return mongo_success 