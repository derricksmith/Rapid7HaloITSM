import insightconnect_plugin_runtime
from .schema import ConnectionSchema, Input
from insightconnect_plugin_runtime.exceptions import PluginException, ConnectionTestException
import requests
from typing import Dict, Any


class Connection(insightconnect_plugin_runtime.Connection):
    def __init__(self):
        super(self.__class__, self).__init__(input=ConnectionSchema())
        self.client = None
        self.access_token = None
        self.auth_server = None
        self.resource_server = None

    def connect(self, params: Dict[str, Any] = None) -> None:
        """
        Establish connection to HaloITSM API using OAuth2
        """
        try:
            self.logger.info("Connect: Starting connection initialization")
            self.logger.info(f"Connect: Received params type: {type(params)}")
            
            if not params:
                raise PluginException(
                    cause="No connection parameters provided",
                    assistance="Connection parameters are required"
                )
            
            # Store connection parameters
            self.logger.info("Connect: Extracting connection parameters")
            self.client_id = params.get(Input.CLIENT_ID)
            
            # Handle credential_secret_key type for client_secret
            client_secret_obj = params.get(Input.CLIENT_SECRET)
            self.logger.info(f"Connect: Client secret type: {type(client_secret_obj)}")
            
            if isinstance(client_secret_obj, dict):
                self.client_secret = client_secret_obj.get("secretKey")
            elif isinstance(client_secret_obj, str):
                # Handle case where it might be passed as a plain string
                self.client_secret = client_secret_obj
            else:
                self.client_secret = None
            
            self.auth_server = params.get(Input.AUTHORIZATION_SERVER)
            self.resource_server = params.get(Input.RESOURCE_SERVER)
            self.tenant = params.get(Input.TENANT)
            self.ssl_verify = params.get(Input.SSL_VERIFY, True)
            
            self.logger.info(f"Connect: Parameters extracted - tenant: {self.tenant}, ssl_verify: {self.ssl_verify}")
            
            # Store default values for ticket creation
            self.default_ticket_type_id = params.get(Input.DEFAULT_TICKET_TYPE_ID)
            self.default_priority_id = params.get(Input.DEFAULT_PRIORITY_ID)
            self.default_team_id = params.get(Input.DEFAULT_TEAM_ID)
            self.default_agent_id = params.get(Input.DEFAULT_AGENT_ID)
            self.default_category_id = params.get(Input.DEFAULT_CATEGORY_ID)
            
            # Validate required parameters
            if not all([self.client_id, self.client_secret, self.auth_server, self.resource_server, self.tenant]):
                raise PluginException(
                    cause="Missing required connection parameters",
                    assistance="Please provide all required connection parameters"
                )
            
            # Initialize API client helper
            from icon_haloitsm.util.api import HaloITSMAPI
            self.client = HaloITSMAPI(
                client_id=self.client_id,
                client_secret=self.client_secret,
                auth_server=self.auth_server,
                resource_server=self.resource_server,
                tenant=self.tenant,
                ssl_verify=self.ssl_verify,
                logger=self.logger
            )
            
            self.logger.info("Connect: Connection established successfully")
            
        except PluginException:
            # Re-raise PluginExceptions as-is
            raise
        except Exception as e:
            # Catch any unexpected errors during connection
            self.logger.error(f"Unexpected error during connection: {str(e)}")
            raise PluginException(
                cause="Connection initialization failed",
                assistance=f"An unexpected error occurred: {str(e)}",
                data=str(e)
            )

    def test(self) -> Dict[str, bool]:
        """
        Test the connection by making an authenticated API call
        This tests both OAuth authentication and API connectivity
        """
        try:
            self.logger.info("Connection test: Testing HaloITSM connectivity")
            
            # Verify client exists
            if not self.client:
                raise ConnectionTestException(
                    cause="API client not initialized",
                    assistance="Connection was not properly established"
                )
            
            # Test connection by making a lightweight API call
            # This tests both OAuth token acquisition AND API connectivity
            self.logger.info("Connection test: Making test API call...")
            self.client.test_connection()
            
            self.logger.info("Connection test: Connection test PASSED")
            return {"success": True}
            
        except ConnectionTestException as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            raise
        except PluginException as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            raise ConnectionTestException(
                cause=e.cause if hasattr(e, 'cause') else "Connection test failed",
                assistance=e.assistance if hasattr(e, 'assistance') else str(e),
                data=e.data if hasattr(e, 'data') else str(e)
            )
        except Exception as e:
            self.logger.error(f"Connection test failed: {type(e).__name__}: {str(e)}")
            raise ConnectionTestException(
                cause="Connection test failed",
                assistance=f"Unable to connect to HaloITSM API: {str(e)}",
                data=f"{type(e).__name__}: {str(e)}"
            )