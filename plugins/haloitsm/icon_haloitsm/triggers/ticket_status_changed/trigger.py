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
        Polling trigger for ticket status changes
        Continuously checks for status changes
        """
        # Get optional filters from trigger configuration
        filter_ticket_id = params.get(Input.TICKET_ID)
        filter_new_status = params.get(Input.NEW_STATUS_ID)
        
        self.logger.info("TicketStatusChanged: Polling trigger started")
        
        # Polling triggers run continuously
        while True:
            # The workflow engine will populate params with webhook body on each request
            ticket_data = params.get('ticket', {})
            old_status_id = params.get('old_status_id')
            new_status_id = ticket_data.get('status_id') if ticket_data else None
            
            if ticket_data:
                # Apply filters if specified
                if filter_ticket_id and ticket_data.get('id') != filter_ticket_id:
                    time.sleep(0.1)
                    continue
                
                if filter_new_status and new_status_id != filter_new_status:
                    time.sleep(0.1)
                    continue
                
                # Only trigger if status actually changed
                if old_status_id is not None and old_status_id == new_status_id:
                    time.sleep(0.1)
                    continue
                
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
                    self.logger.error(f"TicketStatusChanged: Error processing ticket: {str(e)}")
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.1)
