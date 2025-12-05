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
        This is called once per webhook request
        """
        # Get optional filters from trigger configuration
        filter_tickettype = params.get(Input.TICKETTYPE_ID)
        filter_priority = params.get(Input.PRIORITY_ID)
        
        # Get webhook payload
        ticket_data = params.get('ticket', {})
        
        if not ticket_data:
            self.logger.debug("TicketCreated: No ticket data in webhook payload")
            return
        
        # Apply filters if specified
        if filter_tickettype and ticket_data.get('tickettype_id') != filter_tickettype:
            self.logger.debug(f"TicketCreated: Ticket type {ticket_data.get('tickettype_id')} does not match filter {filter_tickettype}")
            return
        
        if filter_priority and ticket_data.get('priority_id') != filter_priority:
            self.logger.debug(f"TicketCreated: Priority {ticket_data.get('priority_id')} does not match filter {filter_priority}")
            return
        
        try:
            # Normalize ticket data
            from icon_haloitsm.actions.create_ticket.action import CreateTicket
            normalized_ticket = CreateTicket()._normalize_ticket(ticket_data)
            
            self.logger.info(f"TicketCreated: Processing new ticket {ticket_data.get('id')}")
            
            # Send normalized ticket to workflow
            self.send({Output.TICKET: normalized_ticket})
            
        except Exception as e:
            self.logger.error(f"TicketCreated: Error processing webhook: {str(e)}")
            raise