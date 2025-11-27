import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.abspath('../'))

from icon_haloitsm.actions.create_ticket.action import CreateTicket
from icon_haloitsm.actions.create_ticket.schema import Input, Output


class TestCreateTicketWithDefaults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.action = CreateTicket()
        
        # Mock connection with defaults
        cls.action.connection = Mock()
        cls.action.connection.default_ticket_type_id = 1
        cls.action.connection.default_priority_id = 3
        cls.action.connection.default_team_id = 15
        cls.action.connection.default_agent_id = 42
        cls.action.connection.default_category_id = 8
        
        cls.action.logger = Mock()

    @patch('icon_haloitsm.util.api.HaloITSMAPI.create_ticket')
    def test_create_ticket_with_connection_defaults(self, mock_create):
        """Test ticket creation using connection defaults"""
        # Mock API response
        mock_create.return_value = {
            "id": 12345,
            "summary": "Test Ticket with Defaults",
            "details": "Test Details",
            "status_id": 1,
            "tickettype_id": 1,
            "priority_id": 3,
            "team_id": 15,
            "agent_id": 42,
            "category_id": 8,
            "datecreated": "2025-11-06T14:35:55.618Z"
        }
        
        # Test input - only required fields
        input_params = {
            Input.SUMMARY: "Test Ticket with Defaults",
            Input.DETAILS: "Test Details"
            # No other fields - should use connection defaults
        }
        
        # Mock connection client
        self.action.connection.client.create_ticket = mock_create
        
        # Run action
        result = self.action.run(input_params)
        
        # Verify API was called with connection defaults
        expected_ticket_data = {
            "summary": "Test Ticket with Defaults",
            "details": "Test Details",
            "actioncode": 0,
            "tickettype_id": 1,
            "priority_id": 3,
            "team_id": 15,
            "agent_id": 42,
            "category_id": 8
        }
        
        mock_create.assert_called_once_with(expected_ticket_data)
        
        # Verify results
        self.assertTrue(result[Output.SUCCESS])
        self.assertEqual(result[Output.TICKET]["id"], 12345)
    
    @patch('icon_haloitsm.util.api.HaloITSMAPI.create_ticket')
    def test_create_ticket_override_defaults(self, mock_create):
        """Test ticket creation with overridden defaults"""
        # Mock API response
        mock_create.return_value = {
            "id": 12346,
            "summary": "Override Test Ticket",
            "details": "Override Details",
            "status_id": 1,
            "tickettype_id": 2,  # Overridden
            "priority_id": 4,    # Overridden
            "team_id": 20,       # Overridden
            "agent_id": 42,      # From connection default
            "category_id": 8,    # From connection default
            "datecreated": "2025-11-06T14:35:55.618Z"
        }
        
        # Test input - override some defaults
        input_params = {
            Input.SUMMARY: "Override Test Ticket",
            Input.DETAILS: "Override Details",
            Input.TICKETTYPE_ID: 2,  # Override default
            Input.PRIORITY_ID: 4,    # Override default  
            Input.TEAM_ID: 20        # Override default
            # agent_id and category_id should use connection defaults
        }
        
        # Mock connection client
        self.action.connection.client.create_ticket = mock_create
        
        # Run action
        result = self.action.run(input_params)
        
        # Verify API was called with mixed values
        expected_ticket_data = {
            "summary": "Override Test Ticket",
            "details": "Override Details", 
            "actioncode": 0,
            "tickettype_id": 2,   # Overridden
            "priority_id": 4,     # Overridden
            "team_id": 20,        # Overridden
            "agent_id": 42,       # Connection default
            "category_id": 8      # Connection default
        }
        
        mock_create.assert_called_once_with(expected_ticket_data)
        
        # Verify results
        self.assertTrue(result[Output.SUCCESS])
        self.assertEqual(result[Output.TICKET]["id"], 12346)

    def test_create_ticket_no_defaults_fails(self):
        """Test that missing ticket type with no default fails"""
        # Clear connection defaults
        self.action.connection.default_ticket_type_id = None
        
        input_params = {
            Input.SUMMARY: "Test Ticket",
            Input.DETAILS: "Test Details"
            # No tickettype_id and no default
        }
        
        # Should raise PluginException
        with self.assertRaises(Exception) as context:
            self.action.run(input_params)
        
        # Verify error message mentions missing ticket type
        self.assertIn("ticket type", str(context.exception).lower())


if __name__ == '__main__':
    unittest.main()