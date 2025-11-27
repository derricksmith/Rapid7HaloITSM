import sys
import os
sys.path.append(os.path.abspath('../'))

import unittest
from unittest.mock import Mock, patch
from icon_haloitsm.actions.search_tickets.action import SearchTickets
from icon_haloitsm.actions.search_tickets.schema import Input, Output
from insightconnect_plugin_runtime.exceptions import PluginException


class TestSearchTickets(unittest.TestCase):
    
    def setUp(self):
        self.action = SearchTickets()
        self.action.connection = Mock()
        self.action.logger = Mock()
    
    def test_search_tickets_success(self):
        """Test successful ticket search"""
        # Mock API response
        mock_tickets = [
            {
                "id": 12345,
                "summary": "Test Ticket 1",
                "details": "First test ticket",
                "status": {"name": "Open"},
                "status_id": 1
            },
            {
                "id": 12346,
                "summary": "Test Ticket 2", 
                "details": "Second test ticket",
                "status": {"name": "In Progress"},
                "status_id": 2
            }
        ]
        
        # Mock normalized responses
        normalized_tickets = [
            {
                "id": 12345,
                "summary": "Test Ticket 1",
                "details": "First test ticket", 
                "status": "Open",
                "status_id": 1
            },
            {
                "id": 12346,
                "summary": "Test Ticket 2",
                "details": "Second test ticket",
                "status": "In Progress", 
                "status_id": 2
            }
        ]
        
        self.action.connection.client.search_tickets.return_value = mock_tickets
        self.action.connection.client._normalize_ticket.side_effect = normalized_tickets
        
        # Run action
        result = self.action.run({
            Input.SEARCH: "Test Ticket",
            Input.COUNT: 10,
            Input.PAGE_NO: 1
        })
        
        # Assertions
        expected_params = {
            "count": 10,
            "page_no": 1,
            "search": "Test Ticket"
        }
        self.action.connection.client.search_tickets.assert_called_once_with(expected_params)
        self.assertEqual(len(result[Output.TICKETS]), 2)
        self.assertTrue(result[Output.SUCCESS])
        self.assertEqual(result[Output.COUNT], 2)
    
    def test_search_tickets_minimal_params(self):
        """Test search with minimal parameters"""
        mock_tickets = [{"id": 123, "summary": "Ticket"}]
        normalized_ticket = {"id": 123, "summary": "Ticket"}
        
        self.action.connection.client.search_tickets.return_value = mock_tickets
        self.action.connection.client._normalize_ticket.return_value = normalized_ticket
        
        # Run action with minimal parameters
        result = self.action.run({})
        
        # Check defaults were applied
        expected_params = {
            "count": 50,  # Default count
            "page_no": 1  # Default page
        }
        self.action.connection.client.search_tickets.assert_called_once_with(expected_params)
        self.assertTrue(result[Output.SUCCESS])
    
    def test_search_tickets_with_search_string(self):
        """Test search with search string"""
        mock_tickets = []
        self.action.connection.client.search_tickets.return_value = mock_tickets
        
        result = self.action.run({Input.SEARCH: "specific query"})
        
        expected_params = {
            "count": 50,
            "page_no": 1,
            "search": "specific query"
        }
        self.action.connection.client.search_tickets.assert_called_once_with(expected_params)
        self.assertEqual(len(result[Output.TICKETS]), 0)
        self.assertEqual(result[Output.COUNT], 0)
    
    def test_search_tickets_empty_results(self):
        """Test search returning empty results"""
        self.action.connection.client.search_tickets.return_value = []
        
        result = self.action.run({Input.SEARCH: "nonexistent"})
        
        self.assertEqual(len(result[Output.TICKETS]), 0)
        self.assertTrue(result[Output.SUCCESS])
        self.assertEqual(result[Output.COUNT], 0)
    
    def test_search_tickets_api_error(self):
        """Test API error handling"""
        self.action.connection.client.search_tickets.side_effect = Exception("API Error")
        
        with self.assertRaises(PluginException) as context:
            self.action.run({Input.SEARCH: "test"})
        
        self.assertIn("Failed to search tickets", str(context.exception))
        self.assertIn("API Error", str(context.exception))


if __name__ == "__main__":
    unittest.main()