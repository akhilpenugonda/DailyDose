#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
import sys
import datetime
from io import StringIO
import pymongo

# Import the module to test
import daily_word

class TestDailyWord(unittest.TestCase):
    """Test cases for the Daily Word application."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a test history file
        self.test_history_file = "test_word_history.json"
        if os.path.exists(self.test_history_file):
            os.remove(self.test_history_file)
        
        # Mock date for consistent testing
        self.today = "2023-01-01"
        
        # Sample word data for testing
        self.sample_word_data = {
            "word": "example",
            "phonetics": [
                {
                    "text": "/ɪɡˈzɑːmpəl/",
                    "audio": "https://api.dictionaryapi.dev/media/pronunciations/en/example-uk.mp3"
                }
            ],
            "meanings": [
                {
                    "partOfSpeech": "noun",
                    "definitions": [
                        {
                            "definition": "a representative form or pattern",
                            "example": "I followed your example",
                            "synonyms": ["model", "pattern"],
                            "antonyms": ["exception"]
                        }
                    ],
                    "synonyms": ["model", "pattern", "prototype"],
                    "antonyms": ["exception", "anomaly"]
                }
            ]
        }
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Remove test history file
        if os.path.exists(self.test_history_file):
            os.remove(self.test_history_file)
    
    @patch('requests.get')
    def test_get_random_word(self, mock_get):
        """Test fetching a random word."""
        # Mock response
        mock_response = MagicMock()
        mock_response.content = b"apple\nbanana\ncherry\ndate\neggplant"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Call function
        word = daily_word.get_random_word()
        
        # Assertions
        self.assertIn(word, ["apple", "banana", "cherry", "date", "eggplant"])
        mock_get.assert_called_once_with("https://www.mit.edu/~ecprice/wordlist.10000")
    
    @patch('requests.get')
    def test_get_word_info_success(self, mock_get):
        """Test getting word information successfully."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.sample_word_data]
        mock_get.return_value = mock_response
        
        # Call function
        result = daily_word.get_word_info("example")
        
        # Assertions
        self.assertEqual(result, self.sample_word_data)
        mock_get.assert_called_once_with("https://api.dictionaryapi.dev/api/v2/entries/en/example")
    
    @patch('requests.get')
    def test_get_word_info_failure(self, mock_get):
        """Test getting word information when API fails."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Call function
        result = daily_word.get_word_info("nonexistentword")
        
        # Assertions
        self.assertIsNone(result)
        mock_get.assert_called_once_with("https://api.dictionaryapi.dev/api/v2/entries/en/nonexistentword")
    
    def test_get_learning_difficulty(self):
        """Test difficulty level classification."""
        # Test basic word
        self.assertEqual(daily_word.get_learning_difficulty("cat"), "Basic")
        
        # Test intermediate word
        self.assertEqual(daily_word.get_learning_difficulty("example"), "Intermediate")
        
        # Test advanced word
        self.assertEqual(daily_word.get_learning_difficulty("sophisticated"), "Advanced")
    
    def test_get_memory_tip(self):
        """Test memory tip generation."""
        # Test short word
        self.assertTrue("short" in daily_word.get_memory_tip("cat").lower())
        
        # Test word with prefix
        self.assertTrue("prefix" in daily_word.get_memory_tip("unlock").lower())
        
        # Test longer word without known prefix
        self.assertTrue("mental image" in daily_word.get_memory_tip("elephant").lower())
    
    @patch('datetime.datetime')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    def test_save_to_file_new_word(self, mock_json_dump, mock_json_load, mock_file, mock_datetime):
        """Test saving a new word to file."""
        # Mock today's date
        mock_now = MagicMock()
        mock_now.strftime.return_value = self.today
        mock_datetime.now.return_value = mock_now
        
        # Set up the mock to handle file exists check
        mock_file.return_value.__enter__.return_value.read.return_value = '{}'
        
        # Mock existing history data
        mock_json_load.return_value = {"words": []}
        
        # Mock os.path.exists to return True for history file existence check
        with patch('os.path.exists', return_value=True):
            # Call function
            daily_word.save_to_file("example", self.sample_word_data)
        
        # Assertions
        mock_file.assert_called()
        mock_json_dump.assert_called_once()
        
        # Check what was written to the file
        args, kwargs = mock_json_dump.call_args
        history_data = args[0]
        self.assertEqual(len(history_data["words"]), 1, "Should have one word added")
        self.assertEqual(history_data["words"][0]["word"], "example")
        self.assertEqual(history_data["words"][0]["date_added"], self.today)
        self.assertEqual(history_data["words"][0]["review_count"], 0)
    
    @patch('datetime.datetime')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    def test_save_to_file_existing_word(self, mock_json_dump, mock_json_load, mock_file, mock_datetime):
        """Test updating an existing word in file."""
        # Mock today's date
        mock_now = MagicMock()
        mock_now.strftime.return_value = self.today
        mock_datetime.now.return_value = mock_now
        
        # Set up the mock to handle file exists check
        mock_file.return_value.__enter__.return_value.read.return_value = '{}'
        
        # Mock existing history data with the word already present
        existing_history = {
            "words": [
                {
                    "word": "example",
                    "date_added": "2022-12-01",
                    "review_count": 1,
                    "next_review": "2022-12-01"
                }
            ]
        }
        mock_json_load.return_value = existing_history
        
        # Mock os.path.exists to return True
        with patch('os.path.exists', return_value=True):
            # Call function
            daily_word.save_to_file("example", self.sample_word_data)
        
        # Assertions
        # For existing words, json.dump is NOT called because function returns early
        mock_json_dump.assert_not_called()
        
        # Verify the review count was incremented in the existing history object
        self.assertEqual(existing_history["words"][0]["review_count"], 2, 
                        "Review count should be incremented in the history object")
    
    def test_get_related_words(self):
        """Test extracting related words from the API response."""
        # Call function
        synonyms, antonyms = daily_word.get_related_words(self.sample_word_data["meanings"])
        
        # Assertions
        self.assertIn("model", synonyms)
        self.assertIn("pattern", synonyms)
        self.assertIn("prototype", synonyms)
        self.assertIn("exception", antonyms)
        self.assertIn("anomaly", antonyms)
    
    def test_get_usage_examples(self):
        """Test extracting usage examples from the API response."""
        # Call function
        examples = daily_word.get_usage_examples("example", self.sample_word_data["meanings"])
        
        # Assertions
        self.assertEqual(len(examples), 3)
        self.assertIn("I followed your example", examples)
    
    def test_get_usage_examples_insufficient(self):
        """Test extracting usage examples when insufficient examples exist."""
        # Create sample data with insufficient examples
        limited_sample_data = {
            "meanings": [
                {
                    "partOfSpeech": "noun",
                    "definitions": [
                        {
                            "definition": "a representative form or pattern"
                            # No example here
                        }
                    ]
                }
            ]
        }
        
        # Call function
        examples = daily_word.get_usage_examples("example", limited_sample_data["meanings"])
        
        # Assertions
        self.assertEqual(len(examples), 3)  # Should still generate 3 examples
        self.assertTrue(any("casual conversation" in ex for ex in examples))
        self.assertTrue(any("formal writing" in ex for ex in examples))
        self.assertTrue(any("academic context" in ex for ex in examples))
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_word_info(self, mock_stdout):
        """Test displaying word information to console."""
        # Patch save_word_history to avoid side effects
        with patch('daily_word.save_word_history', return_value=True):
            # Call function
            daily_word.display_word_info(self.sample_word_data)
            
            # Get output
            output = mock_stdout.getvalue()
            
            # Assertions
            self.assertIn("DAILY WORD: EXAMPLE", output)
            self.assertIn("PRONUNCIATION: /ɪɡˈzɑːmpəl/", output)
            self.assertIn("DIFFICULTY LEVEL: Intermediate", output)
            self.assertIn("DEFINITIONS:", output)
            self.assertIn("[noun]", output)
            self.assertIn("a representative form or pattern", output)
            self.assertIn("SYNONYMS:", output)
            self.assertIn("MEMORY TIP:", output)
            self.assertIn("PRACTICE:", output)
    
    @patch('pymongo.MongoClient')
    def test_initialize_mongodb(self, mock_client):
        """Test MongoDB initialization."""
        # Mock MongoDB environment variables
        with patch.dict('os.environ', {
            'MONGODB_URI': 'mongodb://test:test@localhost:27017/test'
        }):
            # Mock successful connection
            mock_admin = MagicMock()
            mock_client.return_value.admin = mock_admin
            
            # Call function
            result = daily_word.initialize_mongodb()
            
            # Assertions
            self.assertTrue(result)
            mock_client.assert_called_once()
            mock_admin.command.assert_called_once_with('ping')
    
    @patch('pymongo.MongoClient')
    def test_initialize_mongodb_failure(self, mock_client):
        """Test MongoDB initialization failure."""
        # Mock MongoDB environment variables
        with patch.dict('os.environ', {
            'MONGODB_URI': 'mongodb://test:test@localhost:27017/test'
        }):
            # Mock connection failure
            mock_client.side_effect = pymongo.errors.ConnectionFailure("Connection error")
            
            # Call function
            result = daily_word.initialize_mongodb()
            
            # Assertions
            self.assertFalse(result)
            mock_client.assert_called_once()
    
    @patch('pymongo.MongoClient')
    @patch('datetime.datetime')
    def test_save_to_mongodb_new_word(self, mock_datetime, mock_client):
        """Test saving new word to MongoDB."""
        # Mock today's date
        mock_now = MagicMock()
        mock_now.strftime.return_value = self.today
        mock_datetime.now.return_value = mock_now
        
        # Setup MongoDB mock
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None  # Word not found
        
        # Create MongoDB client and set global variables
        daily_word.mongo_client = mock_client
        daily_word.word_collection = mock_collection
        
        # Call function
        result = daily_word.save_to_mongodb("example", self.sample_word_data)
        
        # Assertions
        self.assertTrue(result)
        mock_collection.find_one.assert_called_once_with({"word": "example"})
        mock_collection.insert_one.assert_called_once()
        
        # Check the insert_one argument contains required fields
        insert_call_args = mock_collection.insert_one.call_args[0][0]
        self.assertEqual(insert_call_args["word"], "example")
        self.assertEqual(insert_call_args["date_added"], self.today)
        self.assertEqual(insert_call_args["last_reviewed"], self.today)
        self.assertEqual(insert_call_args["review_count"], 1)
        self.assertEqual(insert_call_args["difficulty"], "Intermediate")
    
    @patch('pymongo.MongoClient')
    @patch('datetime.datetime')
    def test_save_to_mongodb_existing_word(self, mock_datetime, mock_client):
        """Test updating existing word in MongoDB."""
        # Mock today's date
        mock_now = MagicMock()
        mock_now.strftime.return_value = self.today
        mock_datetime.now.return_value = mock_now
        
        # Setup MongoDB mock
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {
            "word": "example",
            "date_added": "2022-12-31",
            "review_count": 1
        }  # Word found
        
        # Create MongoDB client and set global variables
        daily_word.mongo_client = mock_client
        daily_word.word_collection = mock_collection
        
        # Call function
        result = daily_word.save_to_mongodb("example", self.sample_word_data)
        
        # Assertions
        self.assertTrue(result)
        mock_collection.find_one.assert_called_once_with({"word": "example"})
        mock_collection.update_one.assert_called_once()
        
        # Check update operation
        update_call_args = mock_collection.update_one.call_args
        self.assertEqual(update_call_args[0][0], {"word": "example"})
        self.assertEqual(update_call_args[0][1]["$inc"]["review_count"], 1)
        self.assertEqual(update_call_args[0][1]["$set"]["last_reviewed"], self.today)
    
    @patch('pymongo.MongoClient')
    def test_save_to_mongodb_exception(self, mock_client):
        """Test handling exceptions when saving to MongoDB."""
        # Setup MongoDB mock
        mock_collection = MagicMock()
        mock_collection.find_one.side_effect = Exception("Database error")
        
        # Create MongoDB client and set global variables
        daily_word.mongo_client = mock_client
        daily_word.word_collection = mock_collection
        
        # Call function
        result = daily_word.save_to_mongodb("example", self.sample_word_data)
        
        # Assertions
        self.assertFalse(result)
    
    @patch('daily_word.save_to_mongodb')
    @patch('daily_word.save_to_file')
    def test_save_word_history(self, mock_save_file, mock_save_mongo):
        """Test the save_word_history function."""
        # Setup mocks
        mock_save_mongo.return_value = True
        
        # Call function
        result = daily_word.save_word_history("example", self.sample_word_data)
        
        # Assertions
        self.assertTrue(result)
        mock_save_mongo.assert_called_once_with("example", self.sample_word_data)
        mock_save_file.assert_called_once_with("example", self.sample_word_data)
    
    @patch('daily_word.save_to_mongodb')
    @patch('daily_word.save_to_file')
    def test_save_word_history_mongo_fail(self, mock_save_file, mock_save_mongo):
        """Test save_word_history when MongoDB fails."""
        # Setup mocks
        mock_save_mongo.return_value = False
        
        # Call function
        result = daily_word.save_word_history("example", self.sample_word_data)
        
        # Assertions
        self.assertFalse(result)
        mock_save_mongo.assert_called_once_with("example", self.sample_word_data)
        mock_save_file.assert_called_once_with("example", self.sample_word_data)
    
    @patch('daily_word.get_random_word')
    @patch('daily_word.get_word_info')
    @patch('daily_word.display_word_info')
    @patch('daily_word.initialize_mongodb')
    def test_main_success(self, mock_init_mongo, mock_display, mock_get_info, mock_get_word):
        """Test the main function with successful word fetching."""
        # Setup mocks
        mock_init_mongo.return_value = True
        mock_get_word.return_value = "example"
        mock_get_info.return_value = self.sample_word_data
        
        # Call function
        daily_word.main()
        
        # Assertions
        mock_init_mongo.assert_called_once()
        mock_get_word.assert_called_once()
        mock_get_info.assert_called_once_with("example")
        mock_display.assert_called_once_with(self.sample_word_data)
    
    @patch('daily_word.get_random_word')
    @patch('daily_word.get_word_info')
    @patch('daily_word.display_word_info')
    @patch('daily_word.initialize_mongodb')
    def test_main_retry_word(self, mock_init_mongo, mock_display, mock_get_info, mock_get_word):
        """Test the main function when the first word fails."""
        # Setup mocks
        mock_init_mongo.return_value = False
        mock_get_word.side_effect = ["unknown", "example"]
        mock_get_info.side_effect = [None, self.sample_word_data]
        
        # Call function
        daily_word.main()
        
        # Assertions
        mock_init_mongo.assert_called_once()
        self.assertEqual(mock_get_word.call_count, 2)
        self.assertEqual(mock_get_info.call_count, 2)
        mock_get_info.assert_any_call("unknown")
        mock_get_info.assert_any_call("example")
        mock_display.assert_called_once_with(self.sample_word_data)

if __name__ == '__main__':
    unittest.main() 