import insightconnect_plugin_runtime
from .schema import AddCommentInput, AddCommentOutput, Input, Output, Component

# Custom imports below


class AddComment(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='add_comment',
                description=Component.DESCRIPTION,
                input=AddCommentInput(),
                output=AddCommentOutput())

    def run(self, params={}):
        """Add a comment/note to a HaloITSM ticket"""
        ticket_id = params.get(Input.TICKET_ID)
        note_html = params.get(Input.NOTE_HTML)
        outcome = params.get(Input.OUTCOME, "")
        who_can_view_id = params.get(Input.WHO_CAN_VIEW_ID, 1)  # Default to public
        note_type_id = params.get(Input.NOTE_TYPE_ID, 1)  # Default to standard note
        
        if not ticket_id:
            raise insightconnect_plugin_runtime.PluginException(
                cause="Missing ticket ID",
                assistance="Please provide a valid ticket ID"
            )
            
        if not note_html:
            raise insightconnect_plugin_runtime.PluginException(
                cause="Missing note content",
                assistance="Please provide note content in note_html parameter"
            )
        
        try:
            # Prepare the note data
            note_data = {
                "ticket_id": ticket_id,
                "note_html": note_html,
                "outcome": outcome,
                "who_can_view_id": who_can_view_id,
                "note_type_id": note_type_id
            }
            
            # Add the comment via API
            result = self.connection.client.add_comment(note_data)
            
            if not result:
                raise insightconnect_plugin_runtime.PluginException(
                    cause=f"Failed to add comment to ticket {ticket_id}",
                    assistance="The comment creation operation returned no result"
                )
            
            # Get the updated ticket to return current state
            updated_ticket = self.connection.client.get_ticket(ticket_id)
            normalized_ticket = self.connection.client._normalize_ticket(updated_ticket)
            
            self.logger.info(f"Successfully added comment to ticket {ticket_id}")
            
            return {
                Output.TICKET: normalized_ticket,
                Output.SUCCESS: True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to add comment to ticket {ticket_id}: {str(e)}")
            raise insightconnect_plugin_runtime.PluginException(
                cause=f"Failed to add comment to ticket {ticket_id}",
                assistance=str(e)
            )