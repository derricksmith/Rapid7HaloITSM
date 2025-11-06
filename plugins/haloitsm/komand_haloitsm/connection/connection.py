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
        
        # Store connection parameters
        self.client_id = params.get(Input.CLIENT_ID, {}).get("secretKey")
        self.client_secret = params.get(Input.CLIENT_SECRET, {}).get("secretKey")
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
            # Attempt to get OAuth2 token
            self.client.get_access_token()
            
            # Test API access with a simple request
            response = self.client.make_request(
                method="GET",
                endpoint="/tickets",
                params={"count": 1}
            )
            
            return {"success": True}
            
        except Exception as e:
            raise ConnectionTestException(
                cause="Connection test failed",
                assistance=f"Unable to connect to HaloITSM API: {str(e)}",
                data=str(e)
            )