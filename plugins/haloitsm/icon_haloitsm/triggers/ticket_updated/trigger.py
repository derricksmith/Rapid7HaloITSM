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
        This runs as a webhook receiver in InsightConnect
        """
        # Get optional filters
        filter_ticket_id = params.get(Input.TICKET_ID)
        filter_status_changed = params.get(Input.STATUS_CHANGED, False)
        
        self.logger.info("TicketUpdated: Webhook trigger started")
        
        while True:
            try:
                # In webhook mode, this will be called by InsightConnect
                # when a webhook payload is received
                # The webhook payload will be in self.webhook_payload
                
                if hasattr(self, 'webhook_payload'):
                    ticket_data = self.webhook_payload.get('ticket', {})
                    
                    # Apply filters if specified
                    if filter_ticket_id and ticket_data.get('id') != filter_ticket_id:
                        continue
                    
                    # Check if status changed (if filter enabled)
                    previous_status = self.webhook_payload.get('previous_status_id')
                    current_status = ticket_data.get('status_id')
                    
                    if filter_status_changed and previous_status == current_status:
                        # Skip if status didn't change and filter is enabled
                        continue
                    
                    # Normalize ticket data
                    from icon_haloitsm.actions.create_ticket.action import CreateTicket
                    normalized_ticket = CreateTicket()._normalize_ticket(ticket_data)
                    
                    self.logger.info(f"TicketUpdated: Ticket {ticket_data.get('id')} updated")
                    
                    # Prepare output
                    output = {Output.TICKET: normalized_ticket}
                    
                    # Include previous status if available
                    if previous_status is not None:
                        output[Output.PREVIOUS_STATUS_ID] = previous_status
                    
                    # Send normalized ticket to workflow
                    self.send(output)
                
            except Exception as e:
                self.logger.error(f"TicketUpdated: Error processing webhook: {str(e)}")
            
            # Webhook triggers should not sleep - they wait for incoming requests
            # If running in polling mode, add appropriate sleep
            time.sleep(0.1)
