#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock

# Import the module to test
from dailydose.main import main

class TestMain(unittest.TestCase):
    """Test cases for the main module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
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
    
    # Create a patched version of the main function where all external dependencies are mocked
    @patch('dailydose.main.initialize_mongodb')
    @patch('dailydose.main.get_random_word')
    @patch('dailydose.main.get_word_info')
    @patch('dailydose.main.display_word_info')
    def test_main_success(self, mock_display, mock_get_info, mock_get_word, mock_init_mongo):
        """Test the main function with successful word fetching."""
        # Setup mocks
        mock_init_mongo.return_value = True
        mock_get_word.return_value = "example"
        mock_get_info.return_value = self.sample_word_data
        
        # Call function
        main()
        
        # Assertions
        mock_init_mongo.assert_called_once()
        mock_get_word.assert_called_once()
        mock_get_info.assert_called_once_with("example")
        mock_display.assert_called_once_with(self.sample_word_data)
    
    @patch('dailydose.main.initialize_mongodb')
    @patch('dailydose.main.get_random_word')
    @patch('dailydose.main.get_word_info')
    @patch('dailydose.main.display_word_info')
    def test_main_retry_word(self, mock_display, mock_get_info, mock_get_word, mock_init_mongo):
        """Test the main function when the first word fails."""
        # Setup mocks
        mock_init_mongo.return_value = False
        mock_get_word.side_effect = ["unknown", "example"]
        mock_get_info.side_effect = [None, self.sample_word_data]
        
        # Call function
        main()
        
        # Assertions
        mock_init_mongo.assert_called_once()
        self.assertEqual(mock_get_word.call_count, 2)
        self.assertEqual(mock_get_info.call_count, 2)
        mock_get_info.assert_any_call("unknown")
        mock_get_info.assert_any_call("example")
        mock_display.assert_called_once_with(self.sample_word_data)


if __name__ == '__main__':
    unittest.main() 