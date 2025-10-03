"""
Unit tests for NLP parser functionality.
"""

import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp_parser.parser import NLPParser
from nlp_parser.utils import clean_query, extract_keywords, validate_ip_address


class TestNLPParser(unittest.TestCase):
    """Test cases for NLP parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = NLPParser()
    
    def test_intent_extraction(self):
        """Test intent extraction from queries."""
        test_cases = [
            ("show me failed login attempts", "search_logs"),
            ("how many alerts today", "count_events"),
            ("analyze this threat", "analyze_threat"),
            ("get statistics for last week", "get_stats")
        ]
        
        for query, expected_intent in test_cases:
            result = self.parser.parse_query(query)
            self.assertEqual(result['intent'], expected_intent)
    
    def test_entity_extraction(self):
        """Test entity extraction from queries."""
        query = "show traffic from IP 192.168.1.100 to user john@example.com"
        result = self.parser.parse_query(query)
        
        self.assertIn('ip_address', result['entities'])
        self.assertIn('email', result['entities'])
        self.assertIn('192.168.1.100', result['entities']['ip_address'])
        self.assertIn('john@example.com', result['entities']['email'])
    
    def test_temporal_extraction(self):
        """Test temporal information extraction."""
        test_cases = [
            "last 24 hours",
            "past 2 weeks",
            "today",
            "yesterday"
        ]
        
        for temporal_phrase in test_cases:
            query = f"show logs from {temporal_phrase}"
            result = self.parser.parse_query(query)
            self.assertIsNotNone(result['temporal'])
    
    def test_clean_query(self):
        """Test query cleaning functionality."""
        dirty_query = "  show   me   logs  from  src  ip  "
        clean = clean_query(dirty_query)
        self.assertEqual(clean, "show me logs from source ip")
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        query = "malware attack from suspicious domain"
        keywords = extract_keywords(query)
        self.assertIn("malware", keywords)
        self.assertIn("attack", keywords)
        self.assertIn("suspicious", keywords)
    
    def test_validate_ip_address(self):
        """Test IP address validation."""
        valid_ips = ["192.168.1.1", "10.0.0.1", "172.16.1.100"]
        invalid_ips = ["256.256.256.256", "192.168.1", "not.an.ip"]
        
        for ip in valid_ips:
            self.assertTrue(validate_ip_address(ip))
        
        for ip in invalid_ips:
            self.assertFalse(validate_ip_address(ip))


class TestQueryGeneration(unittest.TestCase):
    """Test query generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = NLPParser()
    
    def test_filter_extraction(self):
        """Test filter extraction from queries."""
        query = "show logs where source ip is 192.168.1.100 and port is 80"
        result = self.parser.parse_query(query)
        
        filters = result['filters']
        self.assertEqual(filters.get('source_ip'), '192.168.1.100')
        self.assertEqual(filters.get('port'), '80')
    
    def test_query_suggestions(self):
        """Test query suggestion generation."""
        suggestions = self.parser.generate_query_suggestions("login")
        self.assertIsInstance(suggestions, list)
        self.assertTrue(len(suggestions) > 0)
        
        # Check if suggestions contain relevant terms
        suggestion_text = ' '.join(suggestions).lower()
        self.assertIn('login', suggestion_text)


if __name__ == '__main__':
    unittest.main()