#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

# Import the module to test
from dailydose.core import display

class TestDisplay(unittest.TestCase):
    """Test cases for the display module."""
    
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
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_word_info(self, mock_stdout):
        """Test displaying word information to console."""
        # Patch save_word_history to avoid side effects
        with patch('dailydose.core.storage.save_word_history', return_value=True):
            # Call function
            display.display_word_info(self.sample_word_data)
            
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
            self.assertIn("Word saved to", output)


if __name__ == '__main__':
    unittest.main() 