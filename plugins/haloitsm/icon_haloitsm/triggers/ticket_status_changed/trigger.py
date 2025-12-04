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
        This runs as a webhook receiver in InsightConnect
        """
        # Get optional filters
        filter_ticket_id = params.get(Input.TICKET_ID)
        filter_new_status = params.get(Input.NEW_STATUS_ID)
        
        self.logger.info("TicketStatusChanged: Webhook trigger started")
        
        while True:
            try:
                # In webhook mode, this will be called by InsightConnect
                # when a webhook payload is received
                # The webhook payload will be in self.webhook_payload
                
                if hasattr(self, 'webhook_payload'):
                    ticket_data = self.webhook_payload.get('ticket', {})
                    old_status = self.webhook_payload.get('old_status_id')
                    new_status = ticket_data.get('status_id')
                    
                    # Apply filters if specified
                    if filter_ticket_id and ticket_data.get('id') != filter_ticket_id:
                        continue
                    
                    if filter_new_status and new_status != filter_new_status:
                        continue
                    
                    # Only trigger if status actually changed
                    if old_status is not None and old_status == new_status:
                        continue
                    
                    # Normalize ticket data
                    from icon_haloitsm.actions.create_ticket.action import CreateTicket
                    normalized_ticket = CreateTicket()._normalize_ticket(ticket_data)
                    
                    self.logger.info(f"TicketStatusChanged: Ticket {ticket_data.get('id')} status changed from {old_status} to {new_status}")
                    
                    # Send normalized ticket to workflow with status info
                    self.send({
                        Output.TICKET: normalized_ticket,
                        Output.OLD_STATUS_ID: old_status if old_status is not None else 0,
                        Output.NEW_STATUS_ID: new_status if new_status is not None else 0
                    })
                
            except Exception as e:
                self.logger.error(f"TicketStatusChanged: Error processing webhook: {str(e)}")
            
            # Webhook triggers should not sleep - they wait for incoming requests
            # If running in polling mode, add appropriate sleep
            time.sleep(0.1)
