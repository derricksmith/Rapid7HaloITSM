import sys
import os
sys.path.append(os.path.abspath('../'))

from unittest import TestCase
from icon_haloitsm.actions.create_ticket import CreateTicket
from icon_haloitsm.actions.create_ticket.schema import Input, Output
from unittest.mock import Mock, patch
import json


class TestCreateTicket(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.action = CreateTicket()
        cls.action.connection = Mock()
        cls.action.logger = Mock()
    
    @patch('icon_haloitsm.util.api.HaloITSMAPI.create_ticket')
    def test_create_ticket_success(self, mock_create):
        # Mock API response
        mock_create.return_value = {
            "id": 12345,
            "summary": "Test Ticket",
            "details": "Test Details",
            "status_id": 1,
            "tickettype_id": 1,
            "priority_id": 3,
            "datecreated": "2025-11-06T14:35:55.618Z"
        }
        
        # Test input
        input_params = {
            Input.SUMMARY: "Test Ticket",
            Input.DETAILS: "Test Details",
            Input.TICKETTYPE_ID: 1,
            Input.PRIORITY_ID: 3
        }
        
        # Mock connection client
        self.action.connection.client.create_ticket = mock_create
        
        # Run action
        result = self.action.run(input_params)
        
        # Assertions
        self.assertTrue(result[Output.SUCCESS])
        self.assertEqual(result[Output.TICKET]["id"], 12345)
        self.assertEqual(result[Output.TICKET]["summary"], "Test Ticket")
        mock_create.assert_called_once()
    
    def test_create_ticket_missing_required_field(self):
        # Test with missing required field
        input_params = {
            Input.SUMMARY: "Test Ticket",
            # Missing DETAILS and TICKETTYPE_ID
        }
        
        # Should raise exception due to validation
        # This would be caught by the InsightConnect runtime
        pass  # Placeholder for actual validation test


if __name__ == '__main__':
    import unittest
    unittest.main()