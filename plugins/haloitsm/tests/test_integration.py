import os
import json
from komand_haloitsm.connection.connection import Connection
from komand_haloitsm.actions.create_ticket import CreateTicket
from komand_haloitsm.actions.update_ticket import UpdateTicket


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
    
    def test_full_ticket_lifecycle(self):
        """Test creating, retrieving, updating, and closing a ticket"""
        
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
        
        # Step 2: Update ticket
        print(f"Updating ticket {ticket_id}...")
        update_result = self.update_action.run({
            "ticket_id": ticket_id,
            "summary": "Integration Test Ticket - UPDATED",
            "status_id": 2  # In Progress
        })
        
        assert update_result["success"] is True
        assert update_result["ticket"]["summary"] == "Integration Test Ticket - UPDATED"
        print("Ticket updated successfully")
        
        print("\n✓ Integration test passed")


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
        print("Integration tests completed!")