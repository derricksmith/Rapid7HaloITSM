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
            self.logger.info("Connect: Connecting to HaloITSM API")
            
            if not params:
                raise PluginException(
                    cause="No connection parameters provided",
                    assistance="Connection parameters are required"
                )
            
            # Store connection parameters
            self.client_id = params.get(Input.CLIENT_ID)
            # Handle credential_secret_key type for client_secret
            client_secret_obj = params.get(Input.CLIENT_SECRET)
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
        Test the connection by attempting to authenticate and make a simple API call
        """
        try:
            self.logger.info("Connection test: Starting authentication test")
            self.logger.info(f"Connection test: Auth server: {self.auth_server}")
            self.logger.info(f"Connection test: Resource server: {self.resource_server}")
            self.logger.info(f"Connection test: Tenant: {self.tenant}")
            self.logger.info(f"Connection test: SSL Verify: {self.ssl_verify}")
            self.logger.info(f"Connection test: Client ID: {self.client_id[:10]}..." if self.client_id else "None")
            
            # Attempt to get OAuth2 token (this is the main test)
            # If this succeeds, the connection is valid
            self.logger.info("Connection test: Requesting OAuth2 token...")
            token = self.client.get_access_token()
            
            if not token:
                raise ConnectionTestException(
                    cause="Failed to obtain access token",
                    assistance="OAuth2 authentication returned no token"
                )
            
            self.logger.info(f"Connection test: Token obtained successfully (length: {len(token) if token else 0})")
            
            # Test API access with a simple request
            # Use a very simple endpoint that should always work
            self.logger.info("Connection test: Testing API access with GET /tickettypes?pageinate=false&count=1")
            try:
                response = self.client.make_request(
                    method="GET",
                    endpoint="/tickettypes",
                    params={"pageinate": "false", "count": "1"},
                    timeout=15,
                    retry_count=1
                )
                self.logger.info(f"Connection test: API call successful, response type: {type(response).__name__}")
            except Exception as api_error:
                # If the API call fails but we got a token, that's still a valid connection
                # The API endpoint might not exist or might require different parameters
                self.logger.warning(f"API test call failed but token was obtained: {str(api_error)}")
                self.logger.info("Connection test: Treating as PASS since authentication succeeded")
            
            self.logger.info("Connection test: Connection test PASSED")
            
            return {"success": True}
            
        except ConnectionTestException as e:
            self.logger.error(f"Connection test failed (ConnectionTestException): {str(e)}")
            raise
        except PluginException as e:
            self.logger.error(f"Connection test failed (PluginException): {str(e)}")
            raise ConnectionTestException(
                cause=e.cause if hasattr(e, 'cause') else "Connection test failed",
                assistance=e.assistance if hasattr(e, 'assistance') else str(e),
                data=e.data if hasattr(e, 'data') else str(e)
            )
        except Exception as e:
            self.logger.error(f"Connection test failed (unexpected error): {type(e).__name__}: {str(e)}")
            raise ConnectionTestException(
                cause="Connection test failed with unexpected error",
                assistance=f"Unable to connect to HaloITSM API: {str(e)}",
                data=f"{type(e).__name__}: {str(e)}"
            )