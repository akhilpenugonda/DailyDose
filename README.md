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

The script tracks your word history for spaced repetition learning using either MongoDB (if available) or local file storage.

## Requirements

- Python 3.6+
- Internet connection (to fetch words and their definitions)
- MongoDB (optional) for enhanced data storage

## Installation

### Quick Setup (Recommended)

Use the provided setup script to create a virtual environment and install dependencies:

```bash
# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

This will:
1. Create a Python virtual environment
2. Install all required dependencies
3. Create a `.env` file from the template if it doesn't exist

### Manual Installation

1. Clone this repository or download the `daily_word.py` file
2. Install required dependencies:

```bash
pip install requests pymongo python-dotenv
```

## Usage

### Basic Usage

Run the script from your terminal:

```bash
python daily_word.py
```

The script will:
1. Fetch a random English word
2. Display comprehensive information for vocabulary learning
3. Save the word to your learning history (file or database)
4. If information isn't available for a word, it will automatically try another word

### MongoDB Configuration (Optional)

The script can store word history in MongoDB for enhanced functionality. You have two options to configure it:

#### Option 1: Using a .env file (Recommended)

1. Create a `.env` file in the same directory as the script (or use the setup script to create it)
2. Add your MongoDB connection details to the file:

```
MONGODB_URI=mongodb://username:password@host:port/database
MONGODB_DB_NAME=word_learning
MONGODB_COLLECTION=word_history
```

3. Edit the `.env` file with your actual connection details.

#### Option 2: Using environment variables

Set the MongoDB connection string using environment variables:

```bash
# Unix/Linux/macOS
export MONGODB_URI="mongodb://username:password@host:port/database"

# Windows
set MONGODB_URI=mongodb://username:password@host:port/database
```

Optional database configuration:

```bash
export MONGODB_DB_NAME="your_database_name"
export MONGODB_COLLECTION="your_collection_name"
```

#### MongoDB Permissions

The script will work with limited MongoDB permissions. If your MongoDB user does not have permissions to create indexes, the script will display a warning but continue to function normally.

If MongoDB connection fails or is not configured, the script will automatically fall back to local file storage.

## Learning Features

- **Difficulty Classification**: Words are labeled as Basic, Intermediate, or Advanced
- **Etymology Links**: Access to word origins via Etymonline
- **Mnemonic Techniques**: Memory tips based on prefixes and word structure
- **Learning History**: Words are saved to MongoDB (if available) or `word_history.json` for future reference
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
            Word saved to MongoDB and local file storage.            
======================================================================
```

## Troubleshooting

### MongoDB Connection Issues

If you encounter MongoDB connection issues:

1. Verify your connection string in the `.env` file
2. Ensure your MongoDB user has appropriate permissions
3. Check if your MongoDB server is running and accessible

If issues persist, the script will use local file storage as a fallback. 