#!/usr/bin/env python3
import requests
import random
import json
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

def display_word_info(word_data):
    """Display information about the word in a nicely formatted way"""
    if not word_data:
        print("Sorry, couldn't find information for this word.")
        return
    
    word = word_data.get("word", "")
    
    print("\n" + "="*60)
    print(f"📚 DAILY WORD: {word.upper()} 📚".center(60))
    print("="*60)
    
    # Phonetics
    phonetics = word_data.get("phonetics", [])
    if phonetics:
        for p in phonetics:
            if "text" in p:
                print(f"\n🔊 PRONUNCIATION: {p['text']}")
                break
    
    # Meanings
    meanings = word_data.get("meanings", [])
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
                
                # Synonyms
                synonyms = definition.get("synonyms", [])
                if synonyms and len(synonyms) > 0:
                    print(f"       Synonyms: {', '.join(synonyms[:5])}")  # Limit to 5 synonyms
    
    print("\n" + "="*60 + "\n")

def main():
    print("Finding a random English word for you...\n")
    
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