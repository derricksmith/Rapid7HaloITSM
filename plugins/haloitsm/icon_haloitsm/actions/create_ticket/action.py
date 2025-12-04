import insightconnect_plugin_runtime
from .schema import CreateTicketInput, CreateTicketOutput, Input, Output, Component
from insightconnect_plugin_runtime.exceptions import PluginException


class CreateTicket(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="create_ticket",
            description=Component.DESCRIPTION,
            input=CreateTicketInput(),
            output=CreateTicketOutput()
        )

    def run(self, params={}):
        """
        Create a new ticket in HaloITSM
        """
        # Ensure API client is initialized (lazy initialization)
        self.connection._ensure_client()
        
        self.logger.info("CreateTicket: Starting ticket creation")
        
        # Build ticket data from input parameters
        ticket_data = {
            "summary": params.get(Input.SUMMARY),
            "details": params.get(Input.DETAILS),
            "actioncode": 0  # 0 = New ticket
        }
        
        # Use provided ticket type or fall back to connection default
        ticket_type_id = params.get(Input.TICKETTYPE_ID) or self.connection.default_ticket_type_id
        if not ticket_type_id:
            raise PluginException(
                cause="Missing ticket type ID",
                assistance="Please provide tickettype_id in action parameters or set default_ticket_type_id in connection configuration"
            )
        ticket_data["tickettype_id"] = ticket_type_id
        
        # Add optional fields with connection defaults as fallbacks
        field_defaults = [
            (Input.PRIORITY_ID, "priority_id", self.connection.default_priority_id),
            (Input.STATUS_ID, "status_id", None),  # No default for status, use HaloITSM default
            (Input.CATEGORY_ID, "category_id", self.connection.default_category_id),
            (Input.AGENT_ID, "agent_id", self.connection.default_agent_id),
            (Input.TEAM_ID, "team_id", self.connection.default_team_id),
            (Input.SITE_ID, "site_id", None),
            (Input.USER_ID, "user_id", None)
        ]
        
        for input_field, api_field, default_value in field_defaults:
            value = params.get(input_field) or default_value
            if value is not None:
                ticket_data[api_field] = value
        
        # Add custom fields if provided
        custom_fields = params.get(Input.CUSTOMFIELDS, [])
        if custom_fields:
            ticket_data["customfields"] = custom_fields
        
        try:
            # Create ticket using API client
            result = self.connection.client.create_ticket(ticket_data)
            
            self.logger.info(f"CreateTicket v2.0.17: Ticket created successfully with ID {result.get('id')}")
            self.logger.info(f"CreateTicket: Raw response from HaloITSM: {result}")
            
            # Build output
            return {
                Output.TICKET: self._normalize_ticket(result),
                Output.SUCCESS: True
            }
            
        except PluginException:
            # Re-raise PluginExceptions without modification
            raise
        except Exception as e:
            self.logger.error(f"CreateTicket: Unexpected error: {type(e).__name__}: {str(e)}")
            raise PluginException(
                cause="Failed to create ticket",
                assistance=f"{type(e).__name__}: {str(e)[:200]}"
            )
    
    def _normalize_ticket(self, ticket_data):
        """
        Normalize ticket data to match output schema
        Only return fields defined in the schema, convert None to empty strings
        """
        self.logger.info(f"Normalizing ticket data: {ticket_data}")
        
        # Extract nested name values safely - MUST return empty string, never None
        status_name = ""
        if isinstance(ticket_data.get("status"), dict):
            status_name = ticket_data.get("status", {}).get("name", "")
        
        agent_name = ""
        agent_email = ""
        if isinstance(ticket_data.get("agent"), dict):
            agent_name = ticket_data.get("agent", {}).get("name", "")
            agent_email = ticket_data.get("agent", {}).get("emailaddress", "")
        
        result = {
            "id": ticket_data.get("id"),
            "summary": ticket_data.get("summary", ""),
            "details": ticket_data.get("details", ""),
            "status_id": ticket_data.get("status_id"),
            "status_name": status_name if status_name is not None else "",
            "priority_id": ticket_data.get("priority_id"),
            "agent_id": ticket_data.get("agent_id"),
            "agent_name": agent_name if agent_name is not None else "",
            "agent_email": agent_email if agent_email is not None else "",
            "datecreated": ticket_data.get("datecreated", ""),
            "url": ticket_data.get("url", "")
        }
        
        self.logger.info(f"Normalized result: {result}")
        return result