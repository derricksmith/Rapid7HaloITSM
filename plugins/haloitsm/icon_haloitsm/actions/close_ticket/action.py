import insightconnect_plugin_runtime
from .schema import CloseTicketInput, CloseTicketOutput, Input, Output, Component

# Custom imports below


class CloseTicket(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='close_ticket',
                description=Component.DESCRIPTION,
                input=CloseTicketInput(),
                output=CloseTicketOutput())

    def run(self, params={}):
        """Close a HaloITSM ticket with resolution details"""
        ticket_id = params.get(Input.TICKET_ID)
        resolution = params.get(Input.RESOLUTION, "")
        status_id = params.get(Input.STATUS_ID, 4)  # Default to "Resolved" status
        
        if not ticket_id:
            raise insightconnect_plugin_runtime.PluginException(
                cause="Missing ticket ID",
                assistance="Please provide a valid ticket ID"
            )
        
        try:
            # Prepare the update payload to close the ticket
            close_data = {
                "id": ticket_id,
                "status_id": status_id
            }
            
            # Add resolution if provided
            if resolution:
                close_data["resolution"] = resolution
                # Also update the details to include resolution
                close_data["details"] = f"Ticket closed with resolution: {resolution}"
            
            # Update the ticket to close it
            self.logger.info(f"CloseTicket: Updating ticket {ticket_id} with status {status_id}")
            try:
                result = self.connection.client.update_ticket(close_data)
            except insightconnect_plugin_runtime.PluginException:
                # Re-raise PluginExceptions as-is
                raise
            except Exception as api_error:
                self.logger.error(f"CloseTicket: Unexpected API error: {type(api_error).__name__}: {str(api_error)}")
                raise insightconnect_plugin_runtime.PluginException(
                    cause=f"Failed to close ticket {ticket_id}",
                    assistance=f"{type(api_error).__name__}: {str(api_error)[:200]}"
                )
            
            if not result:
                raise insightconnect_plugin_runtime.PluginException(
                    cause=f"Failed to close ticket {ticket_id}",
                    assistance="The ticket update operation returned no result"
                )
            
            # Get the updated ticket to return current state
            self.logger.info(f"CloseTicket: Fetching updated ticket {ticket_id}")
            try:
                updated_ticket = self.connection.client.get_ticket(ticket_id)
                normalized_ticket = self.connection.client._normalize_ticket(updated_ticket)
            except Exception as get_error:
                self.logger.warning(f"CloseTicket: Could not fetch updated ticket: {str(get_error)}")
                # Return minimal ticket data - close was successful even if we can't fetch updated state
                normalized_ticket = {
                    "id": ticket_id,
                    "summary": "Ticket closed successfully",
                    "status_id": status_id
                }
            
            self.logger.info(f"CloseTicket: Successfully closed ticket {ticket_id}")
            
            return {
                Output.TICKET: normalized_ticket,
                Output.SUCCESS: True
            }
            
        except insightconnect_plugin_runtime.PluginException:
            # Re-raise PluginExceptions without modification
            raise
        except Exception as e:
            self.logger.error(f"CloseTicket: Unexpected error: {type(e).__name__}: {str(e)}")
            raise insightconnect_plugin_runtime.PluginException(
                cause=f"Failed to close ticket",
                assistance=f"{type(e).__name__}: {str(e)[:200]}"
            )