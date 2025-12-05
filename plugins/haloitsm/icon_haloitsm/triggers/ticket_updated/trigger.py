import insightconnect_plugin_runtime
from .schema import TicketUpdatedInput, TicketUpdatedOutput, Input, Output, Component
from insightconnect_plugin_runtime.exceptions import PluginException
import time


class TicketUpdated(insightconnect_plugin_runtime.Trigger):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="ticket_updated",
            description=Component.DESCRIPTION,
            input=TicketUpdatedInput(),
            output=TicketUpdatedOutput()
        )

    def run(self, params={}):
        """
        Webhook trigger for ticket updates
        Receives HTTP POST requests from HaloITSM webhooks
        This is called once per webhook request
        """
        # Get optional filters from trigger configuration
        filter_ticket_id = params.get(Input.TICKET_ID)
        filter_status_changed = params.get(Input.STATUS_CHANGED, False)
        
        # Get webhook payload
        ticket_data = params.get('ticket', {})
        previous_status_id = params.get('previous_status_id')
        
        if not ticket_data:
            self.logger.debug("TicketUpdated: No ticket data in webhook payload")
            return
        
        # Apply filters if specified
        if filter_ticket_id and ticket_data.get('id') != filter_ticket_id:
            self.logger.debug(f"TicketUpdated: Ticket ID {ticket_data.get('id')} does not match filter {filter_ticket_id}")
            return
        
        # Check if status changed (if filter enabled)
        if filter_status_changed:
            current_status = ticket_data.get('status_id')
            if previous_status_id == current_status:
                self.logger.debug(f"TicketUpdated: Status did not change, filter enabled - skipping")
                return
        
        try:
            # Normalize ticket data
            from icon_haloitsm.actions.create_ticket.action import CreateTicket
            normalized_ticket = CreateTicket()._normalize_ticket(ticket_data)
            
            self.logger.info(f"TicketUpdated: Ticket {ticket_data.get('id')} updated")
            
            # Prepare output
            output = {Output.TICKET: normalized_ticket}
            
            # Include previous status if available
            if previous_status_id is not None:
                output[Output.PREVIOUS_STATUS_ID] = previous_status_id
            
            # Send normalized ticket to workflow
            self.send(output)
        
        except Exception as e:
            self.logger.error(f"TicketUpdated: Error processing webhook: {str(e)}")
            raise
