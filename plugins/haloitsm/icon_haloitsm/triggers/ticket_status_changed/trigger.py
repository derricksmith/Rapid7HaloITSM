import insightconnect_plugin_runtime
from .schema import TicketStatusChangedInput, TicketStatusChangedOutput, Input, Output, Component
from insightconnect_plugin_runtime.exceptions import PluginException
import time


class TicketStatusChanged(insightconnect_plugin_runtime.Trigger):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="ticket_status_changed",
            description=Component.DESCRIPTION,
            input=TicketStatusChangedInput(),
            output=TicketStatusChangedOutput()
        )

    def run(self, params={}):
        """
        Webhook trigger for ticket status changes
        Receives HTTP POST requests from HaloITSM webhooks
        This is called once per webhook request
        """
        # Get optional filters from trigger configuration
        filter_ticket_id = params.get(Input.TICKET_ID)
        filter_new_status = params.get(Input.NEW_STATUS_ID)
        
        # Get webhook payload
        ticket_data = params.get('ticket', {})
        old_status_id = params.get('old_status_id')
        new_status_id = ticket_data.get('status_id') if ticket_data else None
        
        if not ticket_data:
            self.logger.debug("TicketStatusChanged: No ticket data in webhook payload")
            return
        
        # Apply filters if specified
        if filter_ticket_id and ticket_data.get('id') != filter_ticket_id:
            self.logger.debug(f"TicketStatusChanged: Ticket ID {ticket_data.get('id')} does not match filter {filter_ticket_id}")
            return
        
        if filter_new_status and new_status_id != filter_new_status:
            self.logger.debug(f"TicketStatusChanged: New status {new_status_id} does not match filter {filter_new_status}")
            return
        
        # Only trigger if status actually changed
        if old_status_id is not None and old_status_id == new_status_id:
            self.logger.debug(f"TicketStatusChanged: Status did not change ({new_status_id}) - skipping")
            return
        
        try:
            # Normalize ticket data
            from icon_haloitsm.actions.create_ticket.action import CreateTicket
            normalized_ticket = CreateTicket()._normalize_ticket(ticket_data)
            
            self.logger.info(f"TicketStatusChanged: Ticket {ticket_data.get('id')} status changed from {old_status_id} to {new_status_id}")
            
            # Send normalized ticket to workflow with status info
            self.send({
                Output.TICKET: normalized_ticket,
                Output.OLD_STATUS_ID: old_status_id if old_status_id is not None else 0,
                Output.NEW_STATUS_ID: new_status_id if new_status_id is not None else 0
            })
        
        except Exception as e:
            self.logger.error(f"TicketStatusChanged: Error processing webhook: {str(e)}")
            raise
