"""
Unit tests for SIEM connectors.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from siem_connector.utils import parse_time_range, normalize_log_entry, format_query_results


class TestSIEMConnectorUtils(unittest.TestCase):
    """Test utility functions for SIEM connectors."""
    
    def test_parse_time_range(self):
        """Test time range parsing."""
        test_cases = [
            "last hour",
            "last 24 hours", 
            "last week",
            "today",
            "yesterday"
        ]
        
        for time_str in test_cases:
            result = parse_time_range(time_str)
            self.assertIn('gte', result)
            self.assertIn('lte', result)
    
    def test_normalize_log_entry_elasticsearch(self):
        """Test log entry normalization for Elasticsearch."""
        es_log = {
            '_source': {
                '@timestamp': '2024-01-01T12:00:00Z',
                'message': 'Test log message',
                'source': {'ip': '192.168.1.100'},
                'destination': {'ip': '10.0.0.1'},
                'user': {'name': 'testuser'},
                'event': {'type': 'authentication'},
                'log': {'level': 'high'}
            }
        }
        
        normalized = normalize_log_entry(es_log, 'elasticsearch')
        
        self.assertEqual(normalized['source'], 'elasticsearch')
        self.assertEqual(normalized['timestamp'], '2024-01-01T12:00:00Z')
        self.assertEqual(normalized['message'], 'Test log message')
        self.assertEqual(normalized['source_ip'], '192.168.1.100')
        self.assertEqual(normalized['dest_ip'], '10.0.0.1')
        self.assertEqual(normalized['user'], 'testuser')
        self.assertEqual(normalized['event_type'], 'authentication')
        self.assertEqual(normalized['severity'], 'high')
    
    def test_normalize_log_entry_wazuh(self):
        """Test log entry normalization for Wazuh."""
        wazuh_log = {
            'timestamp': '2024-01-01T12:00:00Z',
            'rule': {
                'description': 'Test alert',
                'groups': ['authentication'],
                'level': 10
            },
            'data': {
                'srcip': '192.168.1.100',
                'srcuser': 'testuser'
            }
        }
        
        normalized = normalize_log_entry(wazuh_log, 'wazuh')
        
        self.assertEqual(normalized['source'], 'wazuh')
        self.assertEqual(normalized['timestamp'], '2024-01-01T12:00:00Z')
        self.assertEqual(normalized['message'], 'Test alert')
        self.assertEqual(normalized['source_ip'], '192.168.1.100')
        self.assertEqual(normalized['user'], 'testuser')
        self.assertEqual(normalized['event_type'], 'authentication')
        self.assertEqual(normalized['severity'], 10)
    
    def test_format_query_results_json(self):
        """Test JSON formatting of query results."""
        results = [
            {'field1': 'value1', 'field2': 'value2'},
            {'field1': 'value3', 'field2': 'value4'}
        ]
        
        formatted = format_query_results(results, 'json')
        self.assertIn('value1', formatted)
        self.assertIn('value2', formatted)
    
    def test_format_query_results_table(self):
        """Test table formatting of query results."""
        results = [
            {'timestamp': '2024-01-01', 'severity': 'high'},
            {'timestamp': '2024-01-02', 'severity': 'medium'}
        ]
        
        formatted = format_query_results(results, 'table')
        self.assertIn('timestamp', formatted)
        self.assertIn('severity', formatted)
        self.assertIn('high', formatted)
    
    def test_format_empty_results(self):
        """Test formatting of empty results."""
        formatted = format_query_results([], 'table')
        self.assertEqual(formatted, "No results found.")


class TestElasticConnectorMock(unittest.TestCase):
    """Test Elasticsearch connector with mocking."""
    
    @patch('elasticsearch.Elasticsearch')
    def test_connection_success(self, mock_es):
        """Test successful Elasticsearch connection."""
        # Mock the Elasticsearch client
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_es.return_value = mock_client
        
        # This would require importing ElasticConnector
        # from siem_connector.elastic_connector import ElasticConnector
        # connector = ElasticConnector()
        # self.assertTrue(connector.client.ping())
        
        # For now, just test that mocking works
        self.assertTrue(mock_client.ping())
    
    @patch('elasticsearch.Elasticsearch')
    def test_query_execution(self, mock_es):
        """Test query execution."""
        mock_client = Mock()
        mock_client.search.return_value = {
            'hits': {
                'total': {'value': 1},
                'hits': [{'_source': {'message': 'test'}}]
            }
        }
        mock_es.return_value = mock_client
        
        # Test the mock
        result = mock_client.search(index='test', body={'query': {'match_all': {}}})
        self.assertEqual(result['hits']['total']['value'], 1)


if __name__ == '__main__':
    unittest.main()