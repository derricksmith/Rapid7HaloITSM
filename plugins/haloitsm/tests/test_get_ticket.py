import sys
import os
sys.path.append(os.path.abspath('../'))

import unittest
from unittest.mock import Mock, patch
from icon_haloitsm.actions.get_ticket.action import GetTicket
from icon_haloitsm.actions.get_ticket.schema import Input, Output
from insightconnect_plugin_runtime.exceptions import PluginException


class TestGetTicket(unittest.TestCase):
    
    def setUp(self):
        self.action = GetTicket()
        self.action.connection = Mock()
        self.action.logger = Mock()
    
    def test_get_ticket_success(self):
        """Test successful ticket retrieval"""
        # Mock API response
        mock_ticket = {
            "id": 12345,
            "summary": "Test Ticket",
            "details": "Test details",
            "status": {"name": "Open"},
            "status_id": 1,
            "priority": {"name": "Medium"},
            "priority_id": 2
        }
        
        # Mock normalized response
        normalized_ticket = {
            "id": 12345,
            "summary": "Test Ticket",
            "details": "Test details",
            "status": "Open",
            "status_id": 1,
            "priority": "Medium",
            "priority_id": 2
        }
        
        self.action.connection.client.get_ticket.return_value = mock_ticket
        self.action.connection.client._normalize_ticket.return_value = normalized_ticket
        
        # Run action
        result = self.action.run({Input.TICKET_ID: 12345})
        
        # Assertions
        self.action.connection.client.get_ticket.assert_called_once_with(12345)
        self.action.connection.client._normalize_ticket.assert_called_once_with(mock_ticket)
        self.assertEqual(result[Output.TICKET], normalized_ticket)
        self.assertTrue(result[Output.SUCCESS])
    
    def test_get_ticket_missing_id(self):
        """Test error when ticket ID is missing"""
        with self.assertRaises(PluginException) as context:
            self.action.run({})
        
        self.assertIn("Missing ticket ID", str(context.exception))
    
    def test_get_ticket_invalid_id(self):
        """Test error when ticket ID is invalid"""
        with self.assertRaises(PluginException) as context:
            self.action.run({Input.TICKET_ID: "invalid"})
        
        self.assertIn("Invalid ticket ID", str(context.exception))
    
    def test_get_ticket_not_found(self):
        """Test error when ticket is not found"""
        self.action.connection.client.get_ticket.return_value = None
        
        with self.assertRaises(PluginException) as context:
            self.action.run({Input.TICKET_ID: 99999})
        
        self.assertIn("Ticket not found", str(context.exception))
    
    def test_get_ticket_api_error(self):
        """Test API error handling"""
        self.action.connection.client.get_ticket.side_effect = Exception("API Error")
        
        with self.assertRaises(PluginException) as context:
            self.action.run({Input.TICKET_ID: 12345})
        
        self.assertIn("Failed to retrieve ticket", str(context.exception))
        self.assertIn("API Error", str(context.exception))


if __name__ == "__main__":
    unittest.main()