import requests
import time
from typing import Dict, Any, Optional
from insightconnect_plugin_runtime.exceptions import PluginException


class HaloITSMAPI:
    """
    Helper class for HaloITSM API operations
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        auth_server: str,
        resource_server: str,
        tenant: str,
        ssl_verify: bool = True,
        logger=None
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_server = auth_server.rstrip('/')
        self.resource_server = resource_server.rstrip('/')
        self.tenant = tenant
        self.ssl_verify = ssl_verify
        self.logger = logger
        
        self.access_token = None
        self.token_expires_at = 0
    
    def get_access_token(self) -> str:
        """
        Get OAuth2 access token, refreshing if necessary
        """
        current_time = time.time()
        
        # Return cached token if still valid (with 60 second buffer)
        if self.access_token and current_time < (self.token_expires_at - 60):
            return self.access_token
        
        # Request new token
        token_url = f"{self.auth_server}/token"
        
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "all"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            response = requests.post(
                token_url,
                data=payload,
                headers=headers,
                verify=self.ssl_verify,
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = current_time + expires_in
            
            if self.logger:
                self.logger.info(f"OAuth2 token obtained, expires in {expires_in} seconds")
            
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            raise PluginException(
                cause="Failed to obtain OAuth2 token",
                assistance="Check your client credentials and authorization server URL",
                data=str(e)
            )
    
    def make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Any] = None,
        retry_count: int = 3,
        timeout: int = 30
    ) -> Any:
        """
        Make an authenticated request to HaloITSM API
        """
        token = self.get_access_token()
        url = f"{self.resource_server}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        if self.logger:
            self.logger.info(f"Making {method} request to {url}")
        
        for attempt in range(retry_count):
            try:
                if self.logger:
                    self.logger.info(f"Request attempt {attempt + 1}/{retry_count}")
                
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    verify=self.ssl_verify,
                    timeout=timeout
                )
                
                # Handle 401 - token may have expired
                if response.status_code == 401 and attempt < retry_count - 1:
                    if self.logger:
                        self.logger.info("Token expired, refreshing...")
                    self.access_token = None  # Force token refresh
                    token = self.get_access_token()
                    headers["Authorization"] = f"Bearer {token}"
                    continue
                
                response.raise_for_status()
                
                # Return JSON if available, otherwise return text
                try:
                    return response.json()
                except ValueError:
                    return response.text
                    
            except requests.exceptions.Timeout as e:
                if self.logger:
                    self.logger.warning(f"Request timeout on attempt {attempt + 1}/{retry_count}")
                if attempt == retry_count - 1:
                    raise PluginException(
                        cause="Request timeout",
                        assistance=f"HaloITSM API did not respond within {timeout} seconds. Check network connectivity and server URL.",
                        data=str(e)
                    )
            except requests.exceptions.HTTPError as e:
                if self.logger:
                    self.logger.warning(f"HTTP error on attempt {attempt + 1}/{retry_count}: {response.status_code}")
                if attempt == retry_count - 1:
                    raise PluginException(
                        cause=f"HTTP {response.status_code} error",
                        assistance=f"HaloITSM API returned an error: {response.text}",
                        data=str(e)
                    )
            except requests.exceptions.RequestException as e:
                if self.logger:
                    self.logger.warning(f"Request error on attempt {attempt + 1}/{retry_count}: {str(e)}")
                if attempt == retry_count - 1:
                    raise PluginException(
                        cause="Request failed",
                        assistance=f"Unable to connect to HaloITSM API: {str(e)}",
                        data=str(e)
                    )
            
            # Wait before retry with exponential backoff
            time.sleep(1 * (attempt + 1))
    
    def get_ticket(self, ticket_id: int) -> Dict[str, Any]:
        """Get a specific ticket by ID"""
        response = self.make_request(
            method="GET",
            endpoint=f"/tickets/{ticket_id}"
        )
        return response
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ticket"""
        # HaloITSM expects an array of tickets
        response = self.make_request(
            method="POST",
            endpoint="/tickets",
            json_data=[ticket_data]
        )
        # Return first ticket from response
        if isinstance(response, list) and len(response) > 0:
            return response[0]
        return response
    
    def update_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing ticket"""
        # Ensure ticket has an ID
        if "id" not in ticket_data:
            raise PluginException(
                cause="Ticket ID missing",
                assistance="Ticket data must include an 'id' field to update"
            )
        
        # HaloITSM uses POST for both create and update
        response = self.make_request(
            method="POST",
            endpoint="/tickets",
            json_data=[ticket_data]
        )
        
        if isinstance(response, list) and len(response) > 0:
            return response[0]
        return response
    
    def search_tickets(self, filters: Dict[str, Any]) -> list:
        """Search for tickets with filters"""
        response = self.make_request(
            method="GET",
            endpoint="/tickets",
            params=filters
        )
        
        if isinstance(response, dict) and "tickets" in response:
            return response["tickets"]
        elif isinstance(response, list):
            return response
        return []
    
    def delete_ticket(self, ticket_id: int) -> bool:
        """Delete a ticket"""
        self.make_request(
            method="DELETE",
            endpoint=f"/tickets/{ticket_id}"
        )
        return True
    
    def add_comment(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a comment/note to a ticket"""
        response = self.make_request(
            method="POST",
            endpoint="/ticketnotes",
            json_data=[note_data]
        )
        
        if isinstance(response, list) and len(response) > 0:
            return response[0]
        return response
    
    def _normalize_ticket(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize ticket data to consistent format"""
        if not ticket:
            return {}
        
        normalized = {
            "id": ticket.get("id"),
            "summary": ticket.get("summary", ""),
            "details": ticket.get("details", ""),
            "status": self._get_nested_name(ticket.get("status")),
            "status_id": ticket.get("status_id"),
            "priority": self._get_nested_name(ticket.get("priority")),
            "priority_id": ticket.get("priority_id"),
            "ticket_type": self._get_nested_name(ticket.get("tickettype")),
            "ticket_type_id": ticket.get("tickettype_id"),
            "agent": self._get_nested_name(ticket.get("agent")),
            "agent_id": ticket.get("agent_id"),
            "team": self._get_nested_name(ticket.get("team")),
            "team_id": ticket.get("team_id"),
            "created_date": ticket.get("dateoccurred", ""),
            "last_updated": ticket.get("dateupdated", ""),
            "client": self._get_nested_name(ticket.get("client")),
            "client_id": ticket.get("client_id"),
            "site": self._get_nested_name(ticket.get("site")),
            "site_id": ticket.get("site_id"),
            "user": self._get_nested_name(ticket.get("user")),
            "user_id": ticket.get("user_id"),
            "category_1": ticket.get("category_1", ""),
            "category_2": ticket.get("category_2", ""),
            "category_3": ticket.get("category_3", ""),
            "category_4": ticket.get("category_4", ""),
            "resolution": ticket.get("resolution", ""),
            "url": f"{self.resource_server.replace('/api', '')}/tickets/{ticket.get('id', '')}"
        }
        
        # Remove None values
        return {k: v for k, v in normalized.items() if v is not None}
    
    def _get_nested_name(self, obj: Any) -> str:
        """Extract name from nested object or return string as-is"""
        if isinstance(obj, dict):
            return obj.get("name", "")
        elif isinstance(obj, str):
            return obj
        return ""