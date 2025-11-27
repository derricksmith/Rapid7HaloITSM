import sys
import os
sys.path.append(os.path.abspath('../'))

import unittest
from unittest.mock import Mock, patch
from icon_haloitsm.actions.close_ticket.action import CloseTicket
from icon_haloitsm.actions.close_ticket.schema import Input, Output
from insightconnect_plugin_runtime.exceptions import PluginException


class TestCloseTicket(unittest.TestCase):
    
    def setUp(self):
        self.action = CloseTicket()
        self.action.connection = Mock()
        self.action.logger = Mock()
    
    def test_close_ticket_success(self):
        """Test successful ticket closure"""
        # Mock API responses
        mock_update_result = {"success": True}
        mock_ticket = {
            "id": 12345,
            "status_id": 4,
            "status": {"name": "Resolved"},
            "resolution": "Issue resolved successfully"
        }
        normalized_ticket = {
            "id": 12345,
            "status_id": 4,
            "status": "Resolved",
            "resolution": "Issue resolved successfully"
        }
        
        self.action.connection.client.update_ticket.return_value = mock_update_result
        self.action.connection.client.get_ticket.return_value = mock_ticket
        self.action.connection.client._normalize_ticket.return_value = normalized_ticket
        
        # Run action
        result = self.action.run({
            Input.TICKET_ID: 12345,
            Input.RESOLUTION: "Issue resolved successfully",
            Input.STATUS_ID: 4
        })
        
        # Assertions
        expected_close_data = {
            "id": 12345,
            "status_id": 4,
            "resolution": "Issue resolved successfully",
            "details": "Ticket closed with resolution: Issue resolved successfully"
        }
        self.action.connection.client.update_ticket.assert_called_once_with(expected_close_data)
        self.action.connection.client.get_ticket.assert_called_once_with(12345)
        self.assertEqual(result[Output.TICKET], normalized_ticket)
        self.assertTrue(result[Output.SUCCESS])
    
    def test_close_ticket_minimal_params(self):
        """Test ticket closure with minimal parameters"""
        mock_update_result = {"success": True}
        mock_ticket = {
            "id": 12345,
            "status_id": 4,
            "status": {"name": "Resolved"}
        }
        normalized_ticket = {
            "id": 12345,
            "status_id": 4,
            "status": "Resolved"
        }
        
        self.action.connection.client.update_ticket.return_value = mock_update_result
        self.action.connection.client.get_ticket.return_value = mock_ticket
        self.action.connection.client._normalize_ticket.return_value = normalized_ticket
        
        # Run action with minimal parameters
        result = self.action.run({Input.TICKET_ID: 12345})
        
        # Check defaults were applied
        expected_close_data = {
            "id": 12345,
            "status_id": 4  # Default "Resolved" status
        }
        self.action.connection.client.update_ticket.assert_called_once_with(expected_close_data)
        self.assertTrue(result[Output.SUCCESS])
    
    def test_close_ticket_custom_status(self):
        """Test ticket closure with custom status"""
        mock_update_result = {"success": True}
        mock_ticket = {"id": 12345, "status_id": 5}
        normalized_ticket = {"id": 12345, "status_id": 5}
        
        self.action.connection.client.update_ticket.return_value = mock_update_result
        self.action.connection.client.get_ticket.return_value = mock_ticket
        self.action.connection.client._normalize_ticket.return_value = normalized_ticket
        
        # Run action with custom status
        result = self.action.run({
            Input.TICKET_ID: 12345,
            Input.STATUS_ID: 5  # Custom status (e.g., "Closed")
        })
        
        expected_close_data = {
            "id": 12345,
            "status_id": 5
        }
        self.action.connection.client.update_ticket.assert_called_once_with(expected_close_data)
        self.assertTrue(result[Output.SUCCESS])
    
    def test_close_ticket_missing_ticket_id(self):
        """Test error when ticket ID is missing"""
        with self.assertRaises(PluginException) as context:
            self.action.run({Input.RESOLUTION: "Fixed issue"})
        
        self.assertIn("Missing ticket ID", str(context.exception))
    
    def test_close_ticket_update_failure(self):
        """Test error when ticket update fails"""
        self.action.connection.client.update_ticket.return_value = None
        
        with self.assertRaises(PluginException) as context:
            self.action.run({Input.TICKET_ID: 12345})
        
        self.assertIn("Failed to close ticket", str(context.exception))
    
    def test_close_ticket_api_error(self):
        """Test API error handling"""
        self.action.connection.client.update_ticket.side_effect = Exception("API Error")
        
        with self.assertRaises(PluginException) as context:
            self.action.run({Input.TICKET_ID: 12345})
        
        self.assertIn("Failed to close ticket", str(context.exception))
        self.assertIn("API Error", str(context.exception))


if __name__ == "__main__":
    unittest.main()