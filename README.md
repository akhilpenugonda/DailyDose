# Daily Word

A simple Python script that fetches a random English word and displays its:
- Definition
- Pronunciation
- Part of speech
- Example usage
- Synonyms (when available)

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
2. Display comprehensive information about the word
3. If information isn't available for a word, it will automatically try another word

## APIs Used

- Random word list from MIT (www.mit.edu/~ecprice/wordlist.10000)
- Word definitions from Free Dictionary API (dictionaryapi.dev)

## Example Output

```
Finding a random English word for you...

============================================================
                  📚 DAILY WORD: EXAMPLE 📚                  
============================================================

🔊 PRONUNCIATION: /ɪɡˈzɑːmpəl/

📖 DEFINITIONS:

  1. [noun]
     • a representative form or pattern
       Example: "I followed your example"
       Synonyms: model, pattern, prototype, sample, specimen

     • a thing characteristic of its kind or illustrating a general rule
       Example: "it's a good example of how European action can produce results"

     • an instance serving for illustration
       Example: "this patient provides a typical example of the syndrome"

============================================================
``` 