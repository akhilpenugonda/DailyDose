#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
import datetime
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure

# Import the module to test
from dailydose.core import storage

class TestStorage(unittest.TestCase):
    """Test cases for the storage module."""
    
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
            result = storage.initialize_mongodb()
            
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
            result = storage.initialize_mongodb()
            
            # Assertions
            self.assertFalse(result)
            mock_client.assert_called_once()
    
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
            storage.save_to_file("example", self.sample_word_data)
        
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
            storage.save_to_file("example", self.sample_word_data)
        
        # Assertions
        # For existing words, json.dump is NOT called because function returns early
        mock_json_dump.assert_not_called()
        
        # Verify the review count was incremented in the existing history object
        self.assertEqual(existing_history["words"][0]["review_count"], 2, 
                        "Review count should be incremented in the history object")
    
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
        storage.mongo_client = mock_client
        storage.word_collection = mock_collection
        
        # Call function
        result = storage.save_to_mongodb("example", self.sample_word_data)
        
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
        storage.mongo_client = mock_client
        storage.word_collection = mock_collection
        
        # Call function
        result = storage.save_to_mongodb("example", self.sample_word_data)
        
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
        storage.mongo_client = mock_client
        storage.word_collection = mock_collection
        
        # Call function
        result = storage.save_to_mongodb("example", self.sample_word_data)
        
        # Assertions
        self.assertFalse(result)
    
    @patch('dailydose.core.storage.save_to_mongodb')
    @patch('dailydose.core.storage.save_to_file')
    def test_save_word_history(self, mock_save_file, mock_save_mongo):
        """Test the save_word_history function."""
        # Setup mocks
        mock_save_mongo.return_value = True
        
        # Call function
        result = storage.save_word_history("example", self.sample_word_data)
        
        # Assertions
        self.assertTrue(result)
        mock_save_mongo.assert_called_once_with("example", self.sample_word_data)
        mock_save_file.assert_called_once_with("example", self.sample_word_data)
    
    @patch('dailydose.core.storage.save_to_mongodb')
    @patch('dailydose.core.storage.save_to_file')
    def test_save_word_history_mongo_fail(self, mock_save_file, mock_save_mongo):
        """Test save_word_history when MongoDB fails."""
        # Setup mocks
        mock_save_mongo.return_value = False
        
        # Call function
        result = storage.save_word_history("example", self.sample_word_data)
        
        # Assertions
        self.assertFalse(result)
        mock_save_mongo.assert_called_once_with("example", self.sample_word_data)
        mock_save_file.assert_called_once_with("example", self.sample_word_data)


if __name__ == '__main__':
    unittest.main() 