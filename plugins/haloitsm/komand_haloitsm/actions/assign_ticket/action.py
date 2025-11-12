import insightconnect_plugin_runtime
from .schema import AssignTicketInput, AssignTicketOutput, Input, Output, Component

# Custom imports below


class AssignTicket(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='assign_ticket',
                description=Component.DESCRIPTION,
                input=AssignTicketInput(),
                output=AssignTicketOutput())

    def run(self, params={}):
        """Assign a HaloITSM ticket to an agent or team"""
        ticket_id = params.get(Input.TICKET_ID)
        agent_id = params.get(Input.AGENT_ID)
        team_id = params.get(Input.TEAM_ID)
        
        if not ticket_id:
            raise insightconnect_plugin_runtime.PluginException(
                cause="Missing ticket ID",
                assistance="Please provide a valid ticket ID"
            )
            
        if not agent_id and not team_id:
            raise insightconnect_plugin_runtime.PluginException(
                cause="Missing assignment target",
                assistance="Please provide either agent_id or team_id for assignment"
            )
        
        try:
            # Prepare the assignment data
            assignment_data = {
                "id": ticket_id
            }
            
            # Add agent assignment if provided
            if agent_id:
                assignment_data["agent_id"] = agent_id
            
            # Add team assignment if provided
            if team_id:
                assignment_data["team_id"] = team_id
            
            # Update the ticket with new assignment
            result = self.connection.client.update_ticket(assignment_data)
            
            if not result:
                raise insightconnect_plugin_runtime.PluginException(
                    cause=f"Failed to assign ticket {ticket_id}",
                    assistance="The ticket assignment operation returned no result"
                )
            
            # Get the updated ticket to return current state
            updated_ticket = self.connection.client.get_ticket(ticket_id)
            normalized_ticket = self.connection.client._normalize_ticket(updated_ticket)
            
            assignment_info = []
            if agent_id:
                assignment_info.append(f"agent {agent_id}")
            if team_id:
                assignment_info.append(f"team {team_id}")
            
            self.logger.info(f"Successfully assigned ticket {ticket_id} to {', '.join(assignment_info)}")
            
            return {
                Output.TICKET: normalized_ticket,
                Output.SUCCESS: True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to assign ticket {ticket_id}: {str(e)}")
            raise insightconnect_plugin_runtime.PluginException(
                cause=f"Failed to assign ticket {ticket_id}",
                assistance=str(e)
            )