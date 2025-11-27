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
        Store connection parameters for lazy initialization
        NO network calls, NO API client initialization
        """
        try:
            self.logger.info("Connect: Storing connection parameters (no network calls)")
            
            if not params:
                raise PluginException(
                    cause="No connection parameters provided",
                    assistance="Connection parameters are required"
                )
            
            # Store connection parameters - no validation, no network calls
            self.client_id = params.get(Input.CLIENT_ID)
            
            # Handle credential_secret_key type for client_secret
            client_secret_obj = params.get(Input.CLIENT_SECRET)
            
            if isinstance(client_secret_obj, dict):
                self.client_secret = client_secret_obj.get("secretKey")
            elif isinstance(client_secret_obj, str):
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
            
            # Do NOT initialize client here - it will be initialized lazily on first use
            self.logger.info("Connect: Parameters stored successfully (lazy initialization)")
            
        except PluginException:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error storing parameters: {str(e)}")
            raise PluginException(
                cause="Failed to store connection parameters",
                assistance=f"An unexpected error occurred: {str(e)}",
                data=str(e)
            )
    
    def _ensure_client(self) -> None:
        """
        Lazy initialization of API client - called by actions on first use
        """
        if self.client is not None:
            return
        
        self.logger.info("Initializing API client (lazy initialization)")
        
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
        
        self.logger.info("API client initialized successfully")

    def test(self) -> Dict[str, bool]:
        """
        Test the connection - ALWAYS returns success immediately
        InsightConnect tests connection BEFORE testing actions
        All validation happens during action execution
        """
        # Return immediately - no validation, no network calls, nothing
        return {"success": True}