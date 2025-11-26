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
        self.client_secret = client_secret_obj.get("secretKey") if client_secret_obj else None
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
        from komand_haloitsm.util.api import HaloITSMAPI
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

    def test(self) -> Dict[str, bool]:
        """
        Test the connection by attempting to authenticate and make a simple API call
        """
        try:
            self.logger.info("Connection test: Starting authentication test")
            
            # Attempt to get OAuth2 token
            token = self.client.get_access_token()
            
            if not token:
                raise ConnectionTestException(
                    cause="Failed to obtain access token",
                    assistance="OAuth2 authentication returned no token"
                )
            
            self.logger.info("Connection test: Token obtained successfully")
            
            # Test API access with a simple request (use tickettypes which is lighter than tickets)
            self.logger.info("Connection test: Testing API access")
            response = self.client.make_request(
                method="GET",
                endpoint="/tickettypes",
                params={"count": 1},
                timeout=20,
                retry_count=1
            )
            
            self.logger.info("Connection test: API call successful")
            
            return {"success": True}
            
        except ConnectionTestException:
            raise
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            raise ConnectionTestException(
                cause="Connection test failed",
                assistance=f"Unable to connect to HaloITSM API: {str(e)}",
                data=str(e)
            )