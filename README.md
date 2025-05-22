# Daily Word

A comprehensive Python script for vocabulary learning that fetches a random English word and displays:

- Definition and part of speech
- Pronunciation (with audio link when available)
- Difficulty level classification
- Etymology information
- Synonyms and antonyms
- Usage examples in different contexts
- Memory tips based on word structure
- Practice prompts for active learning

The script also tracks your word history for spaced repetition learning.

## Requirements

- Python 3.6+
- Internet connection (to fetch words and their definitions)

## Installation

1. Clone this repository or download the `daily_word.py` file
2. Install required dependencies:

```
pip install requests
```

## Usage

Run the script from your terminal:

```
python daily_word.py
```

The script will:
1. Fetch a random English word
2. Display comprehensive information for vocabulary learning
3. Save the word to your learning history file
4. If information isn't available for a word, it will automatically try another word

## Learning Features

- **Difficulty Classification**: Words are labeled as Basic, Intermediate, or Advanced
- **Etymology Links**: Access to word origins via Etymonline
- **Mnemonic Techniques**: Memory tips based on prefixes and word structure
- **Learning History**: Words are saved to `word_history.json` for future reference and spaced repetition
- **Audio Pronunciation**: Links to audio files when available
- **Practice Prompts**: Encourages active usage to reinforce learning

## APIs Used

- Random word list from MIT (www.mit.edu/~ecprice/wordlist.10000)
- Word definitions from Free Dictionary API (dictionaryapi.dev)
- Etymology links to Etymonline (etymonline.com)

## Example Output

```
Finding a random English word for you...

======================================================================
                       📚 DAILY WORD: EXAMPLE 📚                       
======================================================================

🔊 PRONUNCIATION: /ɪɡˈzɑːmpəl/
🎧 Listen: https://api.dictionaryapi.dev/media/pronunciations/en/example-uk.mp3

📊 DIFFICULTY LEVEL: Intermediate

🔍 ETYMOLOGY: For detailed etymology, visit: https://www.etymonline.com/word/example

📖 DEFINITIONS:

  1. [noun]
     • a representative form or pattern
       Example: "I followed your example"

     • a thing characteristic of its kind or illustrating a general rule
       Example: "it's a good example of how European action can produce results"

     • an instance serving for illustration
       Example: "this patient provides a typical example of the syndrome"

🔤 SYNONYMS: model, pattern, prototype, sample, specimen

🔄 ANTONYMS: exception, anomaly, abnormality

💬 USAGE EXAMPLES:
  1. "I followed your example"
  2. "it's a good example of how European action can produce results"
  3. "People often use 'example' in casual conversation."

💡 MEMORY TIP: Try associating this word with a mental image or personal experience to better remember it.

✏️ PRACTICE: Try to use this word in a sentence of your own!

======================================================================
                Word saved to your learning history.                 
======================================================================
``` 