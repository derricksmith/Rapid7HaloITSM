import insightconnect_plugin_runtime
from .schema import GetAgentInput, GetAgentOutput, Input, Output, Component
from insightconnect_plugin_runtime.exceptions import PluginException


class GetAgent(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="get_agent",
            description=Component.DESCRIPTION,
            input=GetAgentInput(),
            output=GetAgentOutput()
        )

    def run(self, params={}):
        """Get agent information by ID"""
        agent_id = params.get(Input.AGENT_ID)
        
        try:
            self.logger.info(f"GetAgent: Retrieving agent {agent_id}")
            
            # Call HaloITSM API to get agent (agents endpoint)
            response = self.connection.client.make_request(
                method="GET",
                endpoint=f"/agent/{agent_id}"
            )
            
            if not response:
                raise PluginException(
                    cause=f"Agent {agent_id} not found",
                    assistance="Verify the agent ID exists in HaloITSM"
                )
            
            # Handle both single agent and array response
            agent_data = response[0] if isinstance(response, list) else response
            
            self.logger.info(f"GetAgent: Successfully retrieved agent {agent_id}")
            
            return {
                Output.AGENT: agent_data,
                Output.SUCCESS: True
            }
            
        except PluginException:
            raise
        except Exception as e:
            raise PluginException(
                cause=f"Failed to get agent {agent_id}",
                assistance=str(e)
            )
