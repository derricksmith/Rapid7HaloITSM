import insightconnect_plugin_runtime
from .schema import TicketCreatedInput, TicketCreatedOutput, Input, Output, Component
from insightconnect_plugin_runtime.exceptions import PluginException
import time


class TicketCreated(insightconnect_plugin_runtime.Trigger):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="ticket_created",
            description=Component.DESCRIPTION,
            input=TicketCreatedInput(),
            output=TicketCreatedOutput()
        )

    def run(self, params={}):
        """
        Webhook trigger for new ticket creation
        Receives HTTP POST requests from HaloITSM webhooks
        """
        # Get optional filters from trigger configuration
        filter_tickettype = params.get(Input.TICKETTYPE_ID)
        filter_priority = params.get(Input.PRIORITY_ID)
        
        self.logger.info("TicketCreated: Webhook trigger ready to receive events")
        
        # Webhook triggers run continuously waiting for webhook POST requests
        while True:
            # The workflow engine will populate params with webhook body on each request
            ticket_data = params.get('ticket', {})
            
            if ticket_data:
                # Apply filters if specified
                if filter_tickettype and ticket_data.get('tickettype_id') != filter_tickettype:
                    continue
                
                if filter_priority and ticket_data.get('priority_id') != filter_priority:
                    continue
                
                try:
                    # Normalize ticket data
                    from icon_haloitsm.actions.create_ticket.action import CreateTicket
                    normalized_ticket = CreateTicket()._normalize_ticket(ticket_data)
                    
                    self.logger.info(f"TicketCreated: Processing new ticket {ticket_data.get('id')}")
                    
                    # Send normalized ticket to workflow
                    self.send({Output.TICKET: normalized_ticket})
                    
                except Exception as e:
                    self.logger.error(f"TicketCreated: Error processing webhook: {str(e)}")
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.1)