import insightconnect_plugin_runtime
from .schema import GetUserInput, GetUserOutput, Input, Output, Component
from insightconnect_plugin_runtime.exceptions import PluginException


class GetUser(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="get_user",
            description=Component.DESCRIPTION,
            input=GetUserInput(),
            output=GetUserOutput()
        )

    def run(self, params={}):
        """Get user information by ID"""
        user_id = params.get(Input.USER_ID)
        
        try:
            self.logger.info(f"GetUser: Retrieving user {user_id}")
            
            # Call HaloITSM API to get user (users endpoint, not agents)
            response = self.connection.client.make_request(
                method="GET",
                endpoint=f"/users/{user_id}"
            )
            
            if not response:
                raise PluginException(
                    cause=f"User {user_id} not found",
                    assistance="Verify the user ID exists in HaloITSM"
                )
            
            # Handle both single user and array response
            user_data = response[0] if isinstance(response, list) else response
            
            self.logger.info(f"GetUser: Successfully retrieved user {user_id}")
            
            return {
                Output.USER: user_data,
                Output.SUCCESS: True
            }
            
        except PluginException:
            raise
        except Exception as e:
            raise PluginException(
                cause=f"Failed to get user {user_id}",
                assistance=str(e)
            )
