import insightconnect_plugin_runtime
from .schema import SearchTicketsInput, SearchTicketsOutput, Input, Output, Component

# Custom imports below


class SearchTickets(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='search_tickets',
                description=Component.DESCRIPTION,
                input=SearchTicketsInput(),
                output=SearchTicketsOutput())

    def run(self, params={}):
        """Search for tickets in HaloITSM"""
        search = params.get(Input.SEARCH, "")
        count = params.get(Input.COUNT, 50)
        page_no = params.get(Input.PAGE_NO, 1)
        
        try:
            # Prepare search parameters
            search_params = {
                "count": count,
                "page_no": page_no
            }
            
            if search:
                search_params["search"] = search
            
            # Search for tickets via API
            tickets = self.connection.client.search_tickets(search_params)
            
            # Normalize all tickets
            normalized_tickets = []
            for ticket in tickets:
                normalized_ticket = self.connection.client._normalize_ticket(ticket)
                normalized_tickets.append(normalized_ticket)
            
            self.logger.info(f"Found {len(normalized_tickets)} tickets matching search criteria")
            
            return {
                Output.TICKETS: normalized_tickets,
                Output.SUCCESS: True,
                Output.COUNT: len(normalized_tickets)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to search tickets: {str(e)}")
            raise insightconnect_plugin_runtime.PluginException(
                cause="Failed to search tickets",
                assistance=str(e)
            )