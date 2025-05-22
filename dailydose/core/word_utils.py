"""
Utility functions for word processing and analysis.
"""
import requests
import random
import sys

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