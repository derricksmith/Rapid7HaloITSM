import insightconnect_plugin_runtime
from .schema import UpdateTicketInput, UpdateTicketOutput, Input, Output, Component
from insightconnect_plugin_runtime.exceptions import PluginException


class UpdateTicket(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="update_ticket",
            description=Component.DESCRIPTION,
            input=UpdateTicketInput(),
            output=UpdateTicketOutput()
        )

    def run(self, params={}):
        """
        Update an existing ticket in HaloITSM
        """
        # Ensure API client is initialized (lazy initialization)
        self.connection._ensure_client()
        
        ticket_id = params.get(Input.TICKET_ID)
        self.logger.info(f"UpdateTicket: Updating ticket {ticket_id}")
        
        # Build update data - only include fields that were provided
        ticket_data = {
            "id": ticket_id,
            "actioncode": 1  # 1 = Update ticket
        }
        
        # Add provided fields to update
        field_mapping = {
            Input.SUMMARY: "summary",
            Input.DETAILS: "details",
            Input.STATUS_ID: "status_id",
            Input.PRIORITY_ID: "priority_id",
            Input.AGENT_ID: "agent_id"
        }
        
        for input_field, api_field in field_mapping.items():
            value = params.get(input_field)
            if value is not None:
                ticket_data[api_field] = value
        
        # Handle custom fields
        custom_fields = params.get(Input.CUSTOMFIELDS, [])
        if custom_fields:
            ticket_data["customfields"] = custom_fields
        
        try:
            # Update ticket using API client
            result = self.connection.client.update_ticket(ticket_data)
            
            self.logger.info(f"UpdateTicket: Ticket {ticket_id} updated successfully")
            
            # Build output (reuse normalize method from create_ticket)
            from icon_haloitsm.actions.create_ticket.action import CreateTicket
            normalized_ticket = CreateTicket()._normalize_ticket(result)
            
            return {
                Output.TICKET: normalized_ticket,
                Output.SUCCESS: True
            }
            
        except PluginException:
            # Re-raise PluginExceptions without modification
            raise
        except Exception as e:
            self.logger.error(f"UpdateTicket: Unexpected error: {type(e).__name__}: {str(e)}")
            raise PluginException(
                cause="Failed to update ticket",
                assistance=f"{type(e).__name__}: {str(e)[:200]}"
            )