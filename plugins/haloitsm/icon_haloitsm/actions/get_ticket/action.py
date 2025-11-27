import insightconnect_plugin_runtime
from .schema import GetTicketInput, GetTicketOutput, Input, Output, Component

# Custom imports below


class GetTicket(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='get_ticket',
                description=Component.DESCRIPTION,
                input=GetTicketInput(),
                output=GetTicketOutput())

    def run(self, params={}):
        """Get a specific ticket by ID"""
        ticket_id = params.get(Input.TICKET_ID)
        
        if not ticket_id:
            raise insightconnect_plugin_runtime.PluginException(
                cause="Missing ticket ID",
                assistance="Please provide a valid ticket ID"
            )
        
        # Validate ticket ID is a number
        if not isinstance(ticket_id, int) or ticket_id <= 0:
            raise insightconnect_plugin_runtime.PluginException(
                cause="Invalid ticket ID",
                assistance="Ticket ID must be a positive integer"
            )
        
        try:
            # Get ticket from HaloITSM API
            ticket = self.connection.client.get_ticket(ticket_id)
            
            if not ticket:
                raise insightconnect_plugin_runtime.PluginException(
                    cause=f"Ticket {ticket_id} not found",
                    assistance="Please verify the ticket ID exists in HaloITSM"
                )
            
            # Normalize the ticket data
            normalized_ticket = self.connection.client._normalize_ticket(ticket)
            
            self.logger.info(f"Successfully retrieved ticket {ticket_id}")
            
            return {
                Output.TICKET: normalized_ticket,
                Output.SUCCESS: True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get ticket {ticket_id}: {str(e)}")
            raise insightconnect_plugin_runtime.PluginException(
                cause=f"Failed to retrieve ticket {ticket_id}",
                assistance=str(e)
            )