"""
Main entry point for the Daily Word application.
"""
from dailydose.core.word_utils import get_random_word, get_word_info
from dailydose.core.display import display_word_info
from dailydose.core.storage import initialize_mongodb

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