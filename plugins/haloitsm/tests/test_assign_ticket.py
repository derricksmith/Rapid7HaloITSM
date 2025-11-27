import sys
import os
sys.path.append(os.path.abspath('../'))

import unittest
from unittest.mock import Mock, patch
from icon_haloitsm.actions.assign_ticket.action import AssignTicket
from icon_haloitsm.actions.assign_ticket.schema import Input, Output
from insightconnect_plugin_runtime.exceptions import PluginException


class TestAssignTicket(unittest.TestCase):
    
    def setUp(self):
        self.action = AssignTicket()
        self.action.connection = Mock()
        self.action.logger = Mock()
    
    def test_assign_ticket_to_agent(self):
        """Test successful ticket assignment to agent"""
        # Mock API responses
        mock_update_result = {"success": True}
        mock_ticket = {
            "id": 12345,
            "agent_id": 100,
            "agent": {"name": "John Doe"}
        }
        normalized_ticket = {
            "id": 12345,
            "agent_id": 100,
            "agent": "John Doe"
        }
        
        self.action.connection.client.update_ticket.return_value = mock_update_result
        self.action.connection.client.get_ticket.return_value = mock_ticket
        self.action.connection.client._normalize_ticket.return_value = normalized_ticket
        
        # Run action
        result = self.action.run({
            Input.TICKET_ID: 12345,
            Input.AGENT_ID: 100
        })
        
        # Assertions
        expected_assignment_data = {
            "id": 12345,
            "agent_id": 100
        }
        self.action.connection.client.update_ticket.assert_called_once_with(expected_assignment_data)
        self.action.connection.client.get_ticket.assert_called_once_with(12345)
        self.assertEqual(result[Output.TICKET], normalized_ticket)
        self.assertTrue(result[Output.SUCCESS])
    
    def test_assign_ticket_to_team(self):
        """Test successful ticket assignment to team"""
        mock_update_result = {"success": True}
        mock_ticket = {
            "id": 12345,
            "team_id": 50,
            "team": {"name": "IT Support"}
        }
        normalized_ticket = {
            "id": 12345,
            "team_id": 50,
            "team": "IT Support"
        }
        
        self.action.connection.client.update_ticket.return_value = mock_update_result
        self.action.connection.client.get_ticket.return_value = mock_ticket
        self.action.connection.client._normalize_ticket.return_value = normalized_ticket
        
        # Run action
        result = self.action.run({
            Input.TICKET_ID: 12345,
            Input.TEAM_ID: 50
        })
        
        # Assertions
        expected_assignment_data = {
            "id": 12345,
            "team_id": 50
        }
        self.action.connection.client.update_ticket.assert_called_once_with(expected_assignment_data)
        self.assertTrue(result[Output.SUCCESS])
    
    def test_assign_ticket_to_both(self):
        """Test ticket assignment to both agent and team"""
        mock_update_result = {"success": True}
        mock_ticket = {
            "id": 12345,
            "agent_id": 100,
            "team_id": 50
        }
        normalized_ticket = {
            "id": 12345,
            "agent_id": 100,
            "team_id": 50
        }
        
        self.action.connection.client.update_ticket.return_value = mock_update_result
        self.action.connection.client.get_ticket.return_value = mock_ticket
        self.action.connection.client._normalize_ticket.return_value = normalized_ticket
        
        # Run action
        result = self.action.run({
            Input.TICKET_ID: 12345,
            Input.AGENT_ID: 100,
            Input.TEAM_ID: 50
        })
        
        # Check both assignments are included
        expected_assignment_data = {
            "id": 12345,
            "agent_id": 100,
            "team_id": 50
        }
        self.action.connection.client.update_ticket.assert_called_once_with(expected_assignment_data)
        self.assertTrue(result[Output.SUCCESS])
    
    def test_assign_ticket_missing_ticket_id(self):
        """Test error when ticket ID is missing"""
        with self.assertRaises(PluginException) as context:
            self.action.run({Input.AGENT_ID: 100})
        
        self.assertIn("Missing ticket ID", str(context.exception))
    
    def test_assign_ticket_missing_assignment_target(self):
        """Test error when both agent_id and team_id are missing"""
        with self.assertRaises(PluginException) as context:
            self.action.run({Input.TICKET_ID: 12345})
        
        self.assertIn("Missing assignment target", str(context.exception))
    
    def test_assign_ticket_update_failure(self):
        """Test error when ticket update fails"""
        self.action.connection.client.update_ticket.return_value = None
        
        with self.assertRaises(PluginException) as context:
            self.action.run({
                Input.TICKET_ID: 12345,
                Input.AGENT_ID: 100
            })
        
        self.assertIn("Failed to assign ticket", str(context.exception))
    
    def test_assign_ticket_api_error(self):
        """Test API error handling"""
        self.action.connection.client.update_ticket.side_effect = Exception("API Error")
        
        with self.assertRaises(PluginException) as context:
            self.action.run({
                Input.TICKET_ID: 12345,
                Input.AGENT_ID: 100
            })
        
        self.assertIn("Failed to assign ticket", str(context.exception))
        self.assertIn("API Error", str(context.exception))


if __name__ == "__main__":
    unittest.main()