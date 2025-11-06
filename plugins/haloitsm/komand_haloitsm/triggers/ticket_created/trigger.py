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
        This runs as a webhook receiver in InsightConnect
        """
        # Get optional filters
        filter_tickettype = params.get(Input.TICKETTYPE_ID)
        filter_priority = params.get(Input.PRIORITY_ID)
        
        self.logger.info("TicketCreated: Webhook trigger started")
        
        while True:
            try:
                # In webhook mode, this will be called by InsightConnect
                # when a webhook payload is received
                # The webhook payload will be in self.webhook_payload
                
                if hasattr(self, 'webhook_payload'):
                    ticket_data = self.webhook_payload.get('ticket', {})
                    
                    # Apply filters if specified
                    if filter_tickettype and ticket_data.get('tickettype_id') != filter_tickettype:
                        continue
                    
                    if filter_priority and ticket_data.get('priority_id') != filter_priority:
                        continue
                    
                    # Normalize ticket data
                    from komand_haloitsm.actions.create_ticket.action import CreateTicket
                    normalized_ticket = CreateTicket()._normalize_ticket(ticket_data)
                    
                    self.logger.info(f"TicketCreated: New ticket {ticket_data.get('id')} detected")
                    
                    # Send normalized ticket to workflow
                    self.send({Output.TICKET: normalized_ticket})
                
            except Exception as e:
                self.logger.error(f"TicketCreated: Error processing webhook: {str(e)}")
            
            # Webhook triggers should not sleep - they wait for incoming requests
            # If running in polling mode, add appropriate sleep
            time.sleep(0.1)