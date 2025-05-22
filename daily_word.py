#!/usr/bin/env python3
import requests
import random
import json
import sys
import os
import datetime
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

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
        
        # Create index on word field for faster lookups
        word_collection.create_index("word")
        
        print("Connected to MongoDB successfully.")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"MongoDB connection failed: {e}. Using local file storage.")
        mongo_client = None
        return False

def get_random_word():
    """Fetch a random word from a list of common English words"""
    try:
        # Get a list of words
        word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
        response = requests.get(word_site)
        words = response.content.decode('utf-8').splitlines()
        
        # Filter out very short words
        words = [word for word in words if len(word) > 3]
        
        # Pick a random word
        return random.choice(words)
    except Exception as e:
        print(f"Error fetching random word: {e}")
        sys.exit(1)

def get_word_info(word):
    """Get detailed information about a word using Free Dictionary API"""
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()[0]
        else:
            return None
    except Exception as e:
        print(f"Error fetching word information: {e}")
        return None

def get_etymology(word):
    """Get etymology information about a word using Etymonline API"""
    try:
        # This is a simplified approach - in a real implementation,
        # you would want to use a proper etymology API or database
        url = f"https://www.etymonline.com/word/{word}"
        return f"For detailed etymology, visit: {url}"
    except Exception as e:
        return "Etymology information not available."

def get_learning_difficulty(word):
    """Estimate the learning difficulty of a word based on various factors"""
    length = len(word)
    
    if length <= 5:
        return "Basic"
    elif length <= 8:
        return "Intermediate"
    else:
        return "Advanced"

def get_memory_tip(word):
    """Generate a simple memory tip for the word"""
    if len(word) <= 4:
        return "Short words are often foundational vocabulary - practice using it in everyday conversation."
    
    # Check if word contains common prefixes
    prefixes = {
        "un": "The prefix 'un-' often means 'not' or indicates a reversal of action.",
        "re": "The prefix 're-' often means 'again' or 'back'.",
        "pre": "The prefix 'pre-' often means 'before'.",
        "post": "The prefix 'post-' often means 'after'.",
        "in": "The prefix 'in-' can mean 'not' or 'into'.",
        "dis": "The prefix 'dis-' often means 'not' or 'apart'.",
        "en": "The prefix 'en-' often means 'cause to be'.",
        "em": "The prefix 'em-' often means 'cause to be'.",
        "anti": "The prefix 'anti-' means 'against' or 'opposite'.",
        "auto": "The prefix 'auto-' means 'self' or 'same'.",
        "bi": "The prefix 'bi-' means 'two'.",
        "co": "The prefix 'co-' means 'together'."
    }
    
    for prefix, meaning in prefixes.items():
        if word.startswith(prefix):
            return meaning
    
    # Simple association tip
    return f"Try associating this word with a mental image or personal experience to better remember it."

def save_to_mongodb(word, info):
    """Save word to MongoDB if connection is available"""
    if not word_collection:
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

def get_usage_examples(word, definitions):
    """Get additional usage examples beyond those provided in definitions"""
    examples = []
    
    # Extract examples from definitions
    for meaning in definitions:
        for definition in meaning.get("definitions", []):
            if "example" in definition:
                examples.append(definition["example"])
    
    # If we have fewer than 3 examples, add some generic ones
    if len(examples) < 3:
        contexts = ["casual conversation", "formal writing", "academic context"]
        generic_examples = [
            f"People often use '{word}' in {contexts[0]}.",
            f"In {contexts[1]}, '{word}' appears frequently.",
            f"Students learn about '{word}' in {contexts[2]}."
        ]
        
        examples.extend(generic_examples[:3-len(examples)])
    
    return examples[:3]  # Return up to 3 examples

def get_related_words(meanings):
    """Extract related words (antonyms, synonyms) from meanings data"""
    synonyms = []
    antonyms = []
    
    for meaning in meanings:
        # Get synonyms and antonyms from definitions
        for definition in meaning.get("definitions", []):
            synonyms.extend(definition.get("synonyms", []))
            antonyms.extend(definition.get("antonyms", []))
        
        # Also check for synonyms/antonyms at the meaning level
        synonyms.extend(meaning.get("synonyms", []))
        antonyms.extend(meaning.get("antonyms", []))
    
    # Remove duplicates and limit length
    synonyms = list(dict.fromkeys(synonyms))[:5]
    antonyms = list(dict.fromkeys(antonyms))[:5]
    
    return synonyms, antonyms

def display_word_info(word_data):
    """Display information about the word in a nicely formatted way"""
    if not word_data:
        print("Sorry, couldn't find information for this word.")
        return
    
    word = word_data.get("word", "")
    meanings = word_data.get("meanings", [])
    
    # Save this word to history
    db_status = save_word_history(word, word_data)
    
    print("\n" + "="*70)
    print(f"📚 DAILY WORD: {word.upper()} 📚".center(70))
    print("="*70)
    
    # Phonetics
    phonetics = word_data.get("phonetics", [])
    if phonetics:
        for p in phonetics:
            if "text" in p:
                print(f"\n🔊 PRONUNCIATION: {p['text']}")
                if "audio" in p and p["audio"]:
                    print(f"🎧 Listen: {p['audio']}")
                break
    
    # Word difficulty
    difficulty = get_learning_difficulty(word)
    print(f"\n📊 DIFFICULTY LEVEL: {difficulty}")
    
    # Etymology
    print(f"\n🔍 ETYMOLOGY: {get_etymology(word)}")
    
    # Meanings
    if meanings:
        print("\n📖 DEFINITIONS:")
        
        for i, meaning in enumerate(meanings, 1):
            part_of_speech = meaning.get("partOfSpeech", "")
            definitions = meaning.get("definitions", [])
            
            print(f"\n  {i}. [{part_of_speech}]")
            
            for j, definition in enumerate(definitions[:3], 1):  # Limit to 3 definitions per part of speech
                print(f"     • {definition.get('definition', '')}")
                
                # Example
                if "example" in definition:
                    print(f"       Example: \"{definition['example']}\"")
    
    # Get synonyms and antonyms
    synonyms, antonyms = get_related_words(meanings)
    
    # Display synonyms
    if synonyms:
        print(f"\n🔤 SYNONYMS: {', '.join(synonyms)}")
    
    # Display antonyms
    if antonyms:
        print(f"\n🔄 ANTONYMS: {', '.join(antonyms)}")
    
    # Usage examples
    examples = get_usage_examples(word, meanings)
    if examples:
        print("\n💬 USAGE EXAMPLES:")
        for i, example in enumerate(examples, 1):
            print(f"  {i}. \"{example}\"")
    
    # Learning tips
    print(f"\n💡 MEMORY TIP: {get_memory_tip(word)}")
    
    # Practice prompt
    print("\n✏️ PRACTICE: Try to use this word in a sentence of your own!")
    
    print("\n" + "="*70)
    storage_msg = "Word saved to MongoDB and local file storage." if db_status else "Word saved to local file storage."
    print(f"{storage_msg}".center(70))
    print("="*70 + "\n")

def main():
    """Main function that runs the program"""
    print("Finding a random English word for you...\n")
    
    # Try to initialize MongoDB connection
    initialize_mongodb()
    
    while True:
        word = get_random_word()
        word_info = get_word_info(word)
        
        if word_info:
            display_word_info(word_info)
            break
        else:
            print(f"Couldn't find information for '{word}'. Trying another word...")

if __name__ == "__main__":
    main() 