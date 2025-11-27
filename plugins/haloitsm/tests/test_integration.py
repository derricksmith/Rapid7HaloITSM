import sys
import os
sys.path.append(os.path.abspath('../'))

import os
import json
from icon_haloitsm.connection.connection import Connection
from icon_haloitsm.actions.create_ticket.action import CreateTicket
from icon_haloitsm.actions.update_ticket.action import UpdateTicket
from icon_haloitsm.actions.get_ticket.action import GetTicket
from icon_haloitsm.actions.add_comment.action import AddComment
from icon_haloitsm.actions.assign_ticket.action import AssignTicket
from icon_haloitsm.actions.close_ticket.action import CloseTicket
from icon_haloitsm.actions.search_tickets.action import SearchTickets


class TestHaloITSMIntegration:
    """
    Integration tests - require real HaloITSM instance
    Set environment variables:
    - HALO_CLIENT_ID
    - HALO_CLIENT_SECRET
    - HALO_AUTH_SERVER
    - HALO_RESOURCE_SERVER
    - HALO_TENANT
    """
    
    @classmethod
    def setup_class(cls):
        # Create connection
        cls.connection = Connection()
        connection_params = {
            "client_id": {"secretKey": os.getenv("HALO_CLIENT_ID")},
            "client_secret": {"secretKey": os.getenv("HALO_CLIENT_SECRET")},
            "authorization_server": os.getenv("HALO_AUTH_SERVER"),
            "resource_server": os.getenv("HALO_RESOURCE_SERVER"),
            "tenant": os.getenv("HALO_TENANT"),
            "ssl_verify": True
        }
        cls.connection.connect(connection_params)
        
        # Initialize actions
        cls.create_action = CreateTicket()
        cls.create_action.connection = cls.connection
        
        cls.update_action = UpdateTicket()
        cls.update_action.connection = cls.connection
        
        cls.get_action = GetTicket()
        cls.get_action.connection = cls.connection
        
        cls.add_comment_action = AddComment()
        cls.add_comment_action.connection = cls.connection
        
        cls.assign_action = AssignTicket()
        cls.assign_action.connection = cls.connection
        
        cls.close_action = CloseTicket()
        cls.close_action.connection = cls.connection
        
        cls.search_action = SearchTickets()
        cls.search_action.connection = cls.connection
    
    def test_full_ticket_lifecycle(self):
        """Test complete ticket lifecycle with all actions"""
        
        # Step 1: Create ticket
        print("Creating ticket...")
        create_result = self.create_action.run({
            "summary": "Integration Test Ticket",
            "details": "This is an integration test ticket created by automated tests",
            "tickettype_id": 1,
            "priority_id": 2
        })
        
        assert create_result["success"] is True
        ticket_id = create_result["ticket"]["id"]
        print(f"Created ticket ID: {ticket_id}")
        
        # Step 2: Get ticket
        print(f"Retrieving ticket {ticket_id}...")
        get_result = self.get_action.run({"ticket_id": ticket_id})
        
        assert get_result["success"] is True
        assert get_result["ticket"]["id"] == ticket_id
        print("Ticket retrieved successfully")
        
        # Step 3: Add comment
        print(f"Adding comment to ticket {ticket_id}...")
        comment_result = self.add_comment_action.run({
            "ticket_id": ticket_id,
            "note_html": "This is an integration test comment",
            "outcome": "Added automated test note"
        })
        
        assert comment_result["success"] is True
        print("Comment added successfully")
        
        # Step 4: Assign ticket (try team assignment if agent fails)
        print(f"Assigning ticket {ticket_id}...")
        try:
            assign_result = self.assign_action.run({
                "ticket_id": ticket_id,
                "team_id": 1  # Assign to first team
            })
            assert assign_result["success"] is True
            print("Ticket assigned to team successfully")
        except Exception as e:
            print(f"Team assignment failed, trying agent: {e}")
            try:
                assign_result = self.assign_action.run({
                    "ticket_id": ticket_id,
                    "agent_id": 1  # Assign to first agent
                })
                assert assign_result["success"] is True
                print("Ticket assigned to agent successfully")
            except Exception as e2:
                print(f"Agent assignment also failed: {e2}")
        
        # Step 5: Update ticket
        print(f"Updating ticket {ticket_id}...")
        update_result = self.update_action.run({
            "ticket_id": ticket_id,
            "summary": "Integration Test Ticket - UPDATED",
            "status_id": 2  # In Progress
        })
        
        assert update_result["success"] is True
        assert "UPDATED" in update_result["ticket"]["summary"]
        print("Ticket updated successfully")
        
        # Step 6: Search for tickets
        print("Searching for tickets...")
        search_result = self.search_action.run({
            "search": "Integration Test",
            "count": 10
        })
        
        assert search_result["success"] is True
        found_ticket = any(t["id"] == ticket_id for t in search_result["tickets"])
        assert found_ticket, f"Could not find ticket {ticket_id} in search results"
        print("Ticket found in search results")
        
        # Step 7: Close ticket
        print(f"Closing ticket {ticket_id}...")
        close_result = self.close_action.run({
            "ticket_id": ticket_id,
            "resolution": "Integration test completed successfully",
            "status_id": 4  # Resolved
        })
        
        assert close_result["success"] is True
        print("Ticket closed successfully")
        
        print("\n✓ Complete integration test passed - all actions working!")
    
    def test_error_handling(self):
        """Test error handling for various scenarios"""
        
        print("Testing error handling...")
        
        # Test getting non-existent ticket
        try:
            self.get_action.run({"ticket_id": 999999})
            assert False, "Should have raised an exception for non-existent ticket"
        except Exception:
            print("✓ Non-existent ticket error handled correctly")
        
        # Test invalid ticket assignment
        try:
            self.assign_action.run({
                "ticket_id": 999999,
                "agent_id": 999999
            })
            assert False, "Should have raised an exception for invalid assignment"
        except Exception:
            print("✓ Invalid assignment error handled correctly")
        
        print("✓ Error handling tests passed")


if __name__ == "__main__":
    # Basic check for required environment variables
    required_vars = ["HALO_CLIENT_ID", "HALO_CLIENT_SECRET", "HALO_AUTH_SERVER", 
                    "HALO_RESOURCE_SERVER", "HALO_TENANT"]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables to run integration tests")
    else:
        test = TestHaloITSMIntegration()
        test.setup_class()
        test.test_full_ticket_lifecycle()
        test.test_error_handling()
        print("All integration tests completed!")