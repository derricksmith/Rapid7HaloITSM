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
        try:
            if self.logger:
                self.logger.info("AddComment: Starting action")
                self.logger.info(f"AddComment: Received params: {list(params.keys()) if params else 'None'}")
            
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
        except Exception as e:
            if self.logger:
                self.logger.error(f"AddComment: Error during parameter validation: {str(e)}")
            raise
        
        try:
            if self.logger:
                self.logger.info(f"AddComment: Adding comment to ticket {ticket_id}")
            
            # Prepare the note data
            note_data = {
                "ticket_id": ticket_id,
                "note_html": note_html,
                "outcome": outcome,
                "who_can_view_id": who_can_view_id,
                "note_type_id": note_type_id
            }
            
            # Add the comment via API
            if self.logger:
                self.logger.info("AddComment: Calling API add_comment")
            result = self.connection.client.add_comment(note_data)
            
            if not result:
                raise insightconnect_plugin_runtime.PluginException(
                    cause=f"Failed to add comment to ticket {ticket_id}",
                    assistance="The comment creation operation returned no result"
                )
            
            if self.logger:
                self.logger.info(f"AddComment: Comment added, fetching updated ticket {ticket_id}")
            
            # Get the updated ticket to return current state
            try:
                updated_ticket = self.connection.client.get_ticket(ticket_id)
                normalized_ticket = self.connection.client._normalize_ticket(updated_ticket)
            except Exception as get_error:
                if self.logger:
                    self.logger.warning(f"AddComment: Could not fetch updated ticket: {str(get_error)}")
                # Return success even if we can't fetch the updated ticket
                normalized_ticket = {"id": ticket_id, "summary": "Comment added successfully"}
            
            if self.logger:
                self.logger.info(f"AddComment: Successfully completed for ticket {ticket_id}")
            
            return {
                Output.TICKET: normalized_ticket,
                Output.SUCCESS: True
            }
            
        except insightconnect_plugin_runtime.PluginException as e:
            if self.logger:
                self.logger.error(f"AddComment: PluginException: {str(e)}")
            raise
        except Exception as e:
            if self.logger:
                self.logger.error(f"AddComment: Unexpected error: {str(e)}")
            raise insightconnect_plugin_runtime.PluginException(
                cause=f"Failed to add comment to ticket {ticket_id}",
                assistance=str(e),
                data=str(e)
            )