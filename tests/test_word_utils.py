#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock
import requests

# Import the module to test
from dailydose.core import word_utils

class TestWordUtils(unittest.TestCase):
    """Test cases for the word_utils module."""
    
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
    
    @patch('requests.get')
    def test_get_random_word(self, mock_get):
        """Test fetching a random word."""
        # Mock response
        mock_response = MagicMock()
        mock_response.content = b"apple\nbanana\ncherry\ndate\neggplant"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Call function
        word = word_utils.get_random_word()
        
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
        result = word_utils.get_word_info("example")
        
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
        result = word_utils.get_word_info("nonexistentword")
        
        # Assertions
        self.assertIsNone(result)
        mock_get.assert_called_once_with("https://api.dictionaryapi.dev/api/v2/entries/en/nonexistentword")
    
    def test_get_learning_difficulty(self):
        """Test difficulty level classification."""
        # Test basic word
        self.assertEqual(word_utils.get_learning_difficulty("cat"), "Basic")
        
        # Test intermediate word
        self.assertEqual(word_utils.get_learning_difficulty("example"), "Intermediate")
        
        # Test advanced word
        self.assertEqual(word_utils.get_learning_difficulty("sophisticated"), "Advanced")
    
    def test_get_memory_tip(self):
        """Test memory tip generation."""
        # Test short word
        self.assertTrue("short" in word_utils.get_memory_tip("cat").lower())
        
        # Test word with prefix
        self.assertTrue("prefix" in word_utils.get_memory_tip("unlock").lower())
        
        # Test longer word without known prefix
        self.assertTrue("mental image" in word_utils.get_memory_tip("elephant").lower())
    
    def test_get_related_words(self):
        """Test extracting related words from the API response."""
        # Call function
        synonyms, antonyms = word_utils.get_related_words(self.sample_word_data["meanings"])
        
        # Assertions
        self.assertIn("model", synonyms)
        self.assertIn("pattern", synonyms)
        self.assertIn("prototype", synonyms)
        self.assertIn("exception", antonyms)
        self.assertIn("anomaly", antonyms)
    
    def test_get_usage_examples(self):
        """Test extracting usage examples from the API response."""
        # Call function
        examples = word_utils.get_usage_examples("example", self.sample_word_data["meanings"])
        
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
        examples = word_utils.get_usage_examples("example", limited_sample_data["meanings"])
        
        # Assertions
        self.assertEqual(len(examples), 3)  # Should still generate 3 examples
        self.assertTrue(any("casual conversation" in ex for ex in examples))
        self.assertTrue(any("formal writing" in ex for ex in examples))
        self.assertTrue(any("academic context" in ex for ex in examples))


if __name__ == '__main__':
    unittest.main() 