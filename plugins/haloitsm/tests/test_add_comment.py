import unittest
from unittest.mock import Mock, patch
from komand_haloitsm.actions.add_comment.action import AddComment
from komand_haloitsm.actions.add_comment.schema import Input, Output
from insightconnect_plugin_runtime.exceptions import PluginException


class TestAddComment(unittest.TestCase):
    
    def setUp(self):
        self.action = AddComment()
        self.action.connection = Mock()
        self.action.logger = Mock()
    
    def test_add_comment_success(self):
        """Test successful comment addition"""
        # Mock API responses
        mock_comment_result = {"id": 123, "ticket_id": 12345}
        mock_ticket = {
            "id": 12345,
            "summary": "Test Ticket",
            "details": "Updated with comment"
        }
        normalized_ticket = {
            "id": 12345,
            "summary": "Test Ticket",
            "details": "Updated with comment"
        }
        
        self.action.connection.client.add_comment.return_value = mock_comment_result
        self.action.connection.client.get_ticket.return_value = mock_ticket
        self.action.connection.client._normalize_ticket.return_value = normalized_ticket
        
        # Run action
        result = self.action.run({
            Input.TICKET_ID: 12345,
            Input.NOTE_HTML: "This is a test comment",
            Input.OUTCOME: "Updated status",
            Input.WHO_CAN_VIEW_ID: 1,
            Input.NOTE_TYPE_ID: 1
        })
        
        # Assertions
        expected_note_data = {
            "ticket_id": 12345,
            "note_html": "This is a test comment",
            "outcome": "Updated status",
            "who_can_view_id": 1,
            "note_type_id": 1
        }
        self.action.connection.client.add_comment.assert_called_once_with(expected_note_data)
        self.action.connection.client.get_ticket.assert_called_once_with(12345)
        self.assertEqual(result[Output.TICKET], normalized_ticket)
        self.assertTrue(result[Output.SUCCESS])
    
    def test_add_comment_minimal_params(self):
        """Test comment addition with minimal parameters"""
        mock_comment_result = {"id": 123, "ticket_id": 12345}
        mock_ticket = {"id": 12345, "summary": "Test"}
        normalized_ticket = {"id": 12345, "summary": "Test"}
        
        self.action.connection.client.add_comment.return_value = mock_comment_result
        self.action.connection.client.get_ticket.return_value = mock_ticket
        self.action.connection.client._normalize_ticket.return_value = normalized_ticket
        
        # Run action with minimal parameters
        result = self.action.run({
            Input.TICKET_ID: 12345,
            Input.NOTE_HTML: "Minimal comment"
        })
        
        # Check defaults were applied
        expected_note_data = {
            "ticket_id": 12345,
            "note_html": "Minimal comment",
            "outcome": "",
            "who_can_view_id": 1,  # Default public
            "note_type_id": 1      # Default standard note
        }
        self.action.connection.client.add_comment.assert_called_once_with(expected_note_data)
        self.assertTrue(result[Output.SUCCESS])
    
    def test_add_comment_missing_ticket_id(self):
        """Test error when ticket ID is missing"""
        with self.assertRaises(PluginException) as context:
            self.action.run({Input.NOTE_HTML: "Comment without ticket ID"})
        
        self.assertIn("Missing ticket ID", str(context.exception))
    
    def test_add_comment_missing_content(self):
        """Test error when note content is missing"""
        with self.assertRaises(PluginException) as context:
            self.action.run({Input.TICKET_ID: 12345})
        
        self.assertIn("Missing note content", str(context.exception))
    
    def test_add_comment_api_failure(self):
        """Test error when comment addition fails"""
        self.action.connection.client.add_comment.return_value = None
        
        with self.assertRaises(PluginException) as context:
            self.action.run({
                Input.TICKET_ID: 12345,
                Input.NOTE_HTML: "Test comment"
            })
        
        self.assertIn("Failed to add comment", str(context.exception))
    
    def test_add_comment_api_error(self):
        """Test API error handling"""
        self.action.connection.client.add_comment.side_effect = Exception("API Error")
        
        with self.assertRaises(PluginException) as context:
            self.action.run({
                Input.TICKET_ID: 12345,
                Input.NOTE_HTML: "Test comment"
            })
        
        self.assertIn("Failed to add comment", str(context.exception))
        self.assertIn("API Error", str(context.exception))


if __name__ == "__main__":
    unittest.main()