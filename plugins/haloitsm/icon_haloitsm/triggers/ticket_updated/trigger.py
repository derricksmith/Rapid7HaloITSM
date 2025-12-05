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
        Polling trigger for ticket updates
        Continuously checks for ticket updates
        """
        # Get optional filters from trigger configuration
        filter_ticket_id = params.get(Input.TICKET_ID)
        filter_status_changed = params.get(Input.STATUS_CHANGED, False)
        
        self.logger.info("TicketUpdated: Polling trigger started")
        
        # Polling triggers run continuously
        while True:
            # The workflow engine will populate params with webhook body on each request
            ticket_data = params.get('ticket', {})
            previous_status_id = params.get('previous_status_id')
            
            if ticket_data:
                # Apply filters if specified
                if filter_ticket_id and ticket_data.get('id') != filter_ticket_id:
                    time.sleep(0.1)
                    continue
                
                # Check if status changed (if filter enabled)
                if filter_status_changed:
                    current_status = ticket_data.get('status_id')
                    if previous_status_id == current_status:
                        # Skip if status didn't change and filter is enabled
                        time.sleep(0.1)
                        continue
                
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
                    self.logger.error(f"TicketUpdated: Error processing ticket: {str(e)}")
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.1)
