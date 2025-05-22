"""
Display operations for word data.
"""
from .word_utils import (
    get_learning_difficulty,
    get_etymology,
    get_memory_tip,
    get_related_words,
    get_usage_examples
)
from .storage import save_word_history

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