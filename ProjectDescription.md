# HaloITSM Integration for Rapid7 InsightConnect - Technical Specification

## Executive Summary

This document provides comprehensive technical specifications for developing a HaloITSM plugin for Rapid7 InsightConnect SOAR platform. The plugin enables bidirectional integration between Rapid7 products (InsightIDR, InsightVM) and HaloITSM for ticket management and remediation workflow automation.

**Feasibility:** HIGH ✅  
**Development Effort:** 4-6 weeks for core plugin, 8-12 weeks for full InsightVM integration  
**Technical Complexity:** Medium  
**Reference Implementations:** ServiceNow plugin, Jira plugin

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [HaloITSM API Capabilities](#haloitsm-api-capabilities)
3. [Rapid7 Plugin Structure](#rapid7-plugin-structure)
4. [Plugin Specification](#plugin-specification)
5. [Connection Component](#connection-component)
6. [Actions Implementation](#actions-implementation)
7. [Triggers Implementation](#triggers-implementation)
8. [InsightVM Remediation Integration](#insightvm-remediation-integration)
9. [Bidirectional Sync Strategy](#bidirectional-sync-strategy)
10. [Code Examples](#code-examples)
11. [Testing Strategy](#testing-strategy)
12. [Deployment Guide](#deployment-guide)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Rapid7 Insight Platform                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │              │      │              │      │              │ │
│  │  InsightIDR  │──────│InsightConnect│──────│  InsightVM   │ │
│  │(Investigations)     │   (SOAR)     │      │(Remediation) │ │
│  │              │      │              │      │              │ │
│  └──────────────┘      └──────┬───────┘      └──────────────┘ │
│                                │                                │
└────────────────────────────────┼────────────────────────────────┘
                                 │
                                 │ REST API / Webhooks
                                 │
                    ┌────────────▼────────────┐
                    │                         │
                    │   HaloITSM Plugin       │
                    │                         │
                    │ ┌─────────────────────┐ │
                    │ │   Connection        │ │
                    │ │   (OAuth2)          │ │
                    │ └─────────────────────┘ │
                    │ ┌─────────────────────┐ │
                    │ │   Actions           │ │
                    │ │   - Create Ticket   │ │
                    │ │   - Update Ticket   │ │
                    │ │   - Close Ticket    │ │
                    │ │   - Search Tickets  │ │
                    │ └─────────────────────┘ │
                    │ ┌─────────────────────┐ │
                    │ │   Triggers          │ │
                    │ │   - Ticket Created  │ │
                    │ │   - Ticket Updated  │ │
                    │ └─────────────────────┘ │
                    │                         │
                    └────────────┬────────────┘
                                 │
                                 │ HTTPS
                                 │
                    ┌────────────▼────────────┐
                    │                         │
                    │      HaloITSM API       │
                    │                         │
                    │  Authorization Server   │
                    │  Resource Server        │
                    │  /api/tickets          │
                    │  Webhooks              │
                    │                         │
                    └─────────────────────────┘
```

### Integration Patterns

1. **Workflow-Based** (InsightConnect Plugin)
   - Manual ticket operations from workflows
   - Automated ticket creation from detection rules
   - Investigation data export

2. **Event-Driven** (Webhooks)
   - Real-time ticket status updates
   - Bidirectional synchronization
   - Trigger-based automation

3. **Native Integration** (InsightVM)
   - Remediation Project ticketing
   - Child ticket creation for solutions
   - Status mapping and field synchronization

---

## HaloITSM API Capabilities

### API Endpoints

**Base URL Structure:**
```
Authorization Server: https://{tenant}.haloitsm.com/auth
Resource Server: https://{tenant}.haloitsm.com/api
```

**Key Endpoints:**
- `GET /api/tickets` - Retrieve tickets with query parameters
- `POST /api/tickets` - Create or update tickets (array of ticket objects)
- `DELETE /api/tickets/{id}` - Delete a ticket
- `GET /api/tickets/{id}` - Get specific ticket details

### Authentication

**OAuth2 Client Credentials Flow:**

1. **Generate Application Credentials:**
   - Navigate to Configuration > Integrations > HaloITSM API
   - Click "View Applications" > "Add"
   - Select "Client ID and Secret (Services)"
   - Generate and save Client ID and Client Secret
   - Select Login Type: "Agent"
   - Assign permissions: `edit:tickets`, `read:tickets`, `delete:tickets`

2. **Token Request:**
```http
POST {authorization_server}/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&
client_id={client_id}&
client_secret={client_secret}&
scope=all
```

3. **Token Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "all"
}
```

4. **API Request:**
```http
GET {resource_server}/api/tickets
Authorization: Bearer {access_token}
Content-Type: application/json
```

### Ticket Object Structure

```json
{
  "id": 12345,
  "summary": "Ticket Summary",
  "details": "Detailed description of the issue",
  "tickettype_id": 1,
  "status_id": 1,
  "priority_id": 3,
  "category_id": 10,
  "agent_id": 100,
  "team_id": 5,
  "site_id": 1,
  "user_id": 500,
  "dateoccurred": "2025-11-06T14:35:55.618Z",
  "datecreated": "2025-11-06T14:35:55.618Z",
  "datemodified": "2025-11-06T15:20:10.000Z",
  "actioncode": 0,
  "customfields": [
    {
      "id": 1,
      "name": "Custom Field Name",
      "value": "Custom Value"
    }
  ]
}
```

### Common Field Values

**Action Codes:**
- `0` - New ticket
- `1` - Update ticket
- `2` - Close ticket

**Status IDs (configurable per instance):**
- `1` - New
- `2` - In Progress
- `3` - Awaiting Verification
- `4` - Resolved
- `5` - Closed

### Webhook Configuration

**Webhook Payload Structure:**
```json
{
  "ticket": {
    "id": 12345,
    "summary": "Ticket Summary",
    "status": {
      "id": 2,
      "name": "In Progress"
    },
    "assigned_agent": {
      "id": 100,
      "name": "John Doe"
    }
  },
  "event": "ticket_updated",
  "timestamp": "2025-11-06T15:20:10.000Z"
}
```

**Webhook Setup in HaloITSM:**
1. Configuration > Integrations > Webhooks
2. Click "New"
3. Configure Payload URL (InsightConnect trigger URL)
4. Select Events:
   - New Ticket Logged
   - Ticket Status Changed
   - Ticket Updated
5. Set Content-Type: `application/json`
6. Method: POST

---

## Rapid7 Plugin Structure

### Directory Layout

```
plugins/haloitsm/
├── Dockerfile
├── Makefile
├── plugin.spec.yaml          # Plugin definition
├── setup.py
├── requirements.txt          # Python dependencies
├── help.md                   # Plugin documentation
├── icon.png                  # 256x256 plugin icon
├── extension.png             # Extension library icon
├── komand_haloitsm/
│   ├── __init__.py
│   ├── connection/
│   │   ├── __init__.py
│   │   ├── connection.py    # OAuth2 connection logic
│   │   └── schema.py        # Connection schema
│   ├── actions/
│   │   ├── __init__.py
│   │   ├── create_ticket/
│   │   │   ├── __init__.py
│   │   │   ├── action.py   # Create ticket logic
│   │   │   └── schema.py   # Input/output schema
│   │   ├── update_ticket/
│   │   ├── close_ticket/
│   │   ├── get_ticket/
│   │   ├── search_tickets/
│   │   ├── add_comment/
│   │   └── assign_ticket/
│   ├── triggers/
│   │   ├── __init__.py
│   │   ├── ticket_created/
│   │   │   ├── __init__.py
│   │   │   ├── trigger.py  # Webhook trigger
│   │   │   └── schema.py
│   │   └── ticket_updated/
│   └── util/
│       ├── __init__.py
│       └── api.py          # API helper functions
└── tests/
    ├── create_ticket.json
    ├── update_ticket.json
    └── connection.json
```

### Key Files

#### plugin.spec.yaml
Core plugin definition file that describes metadata, connection requirements, actions, triggers, and data types.

#### connection.py
Handles OAuth2 authentication and maintains the API client for all actions and triggers.

#### action.py
Individual action implementations that call HaloITSM API endpoints.

#### trigger.py
Webhook receivers or polling mechanisms for event-driven automation.

---

## Plugin Specification

### Complete plugin.spec.yaml

```yaml
plugin_spec_version: v2
extension: plugin
products:
  - insightconnect
name: haloitsm
title: HaloITSM
description: Manage tickets and automate workflows with HaloITSM service desk
version: 1.0.0
vendor: rapid7
support: community
status: []
sdk:
  type: slim
  version: 5
  user: nobody
cloud_ready: true

key_features:
  - Create, update, and close tickets in HaloITSM
  - Search and retrieve ticket information
  - Assign tickets to agents and teams
  - Receive real-time webhook notifications for ticket events
  - Integrate with InsightIDR investigations and InsightVM remediation projects

requirements:
  - HaloITSM instance (cloud or on-premise)
  - API credentials (Client ID and Secret)
  - Network access to HaloITSM API endpoints

version_history:
  - 1.0.0 - Initial plugin release

links:
  - "[HaloITSM](https://haloitsm.com/)"
  - "[HaloITSM API Documentation](https://haloservicedesk.com/apidoc/)"

references:
  - "[HaloITSM API Guide](https://haloitsm.com/guides/article/?kbid=929)"

tags:
  - haloitsm
  - itsm
  - ticketing
  - service desk
  - incident management

hub_tags:
  use_cases:
    - remediation_management
    - threat_detection_and_response
  keywords:
    - haloitsm
    - tickets
    - itsm
    - service desk

resources:
  source_url: https://github.com/rapid7/insightconnect-plugins/tree/master/plugins/haloitsm
  license_url: https://github.com/rapid7/insightconnect-plugins/blob/master/LICENSE
  vendor_url: https://haloitsm.com

connection:
  client_id:
    title: Client ID
    description: OAuth2 Client ID for API authentication
    type: credential_secret_key
    required: true
    example: a1b2c3d4-e5f6-7890-abcd-ef1234567890
  client_secret:
    title: Client Secret
    description: OAuth2 Client Secret for API authentication
    type: credential_secret_key
    required: true
    example: 9z8y7x6w5v4u3t2s1r0q
  authorization_server:
    title: Authorization Server
    description: HaloITSM OAuth2 authorization server URL
    type: string
    required: true
    example: https://example.haloitsm.com/auth
  resource_server:
    title: Resource Server
    description: HaloITSM API resource server URL
    type: string
    required: true
    example: https://example.haloitsm.com/api
  tenant:
    title: Tenant
    description: HaloITSM tenant identifier
    type: string
    required: true
    example: example
  ssl_verify:
    title: SSL Verify
    description: Verify SSL certificate
    type: boolean
    required: false
    default: true

actions:
  create_ticket:
    title: Create Ticket
    description: Create a new ticket in HaloITSM
    input:
      summary:
        title: Summary
        description: Ticket summary/title
        type: string
        required: true
        example: Security incident detected
      details:
        title: Details
        description: Detailed description of the ticket
        type: string
        required: true
        example: Multiple failed login attempts detected from IP 192.168.1.100
      tickettype_id:
        title: Ticket Type ID
        description: ID of the ticket type
        type: integer
        required: true
        example: 1
      priority_id:
        title: Priority ID
        description: Priority level ID
        type: integer
        required: false
        example: 3
      status_id:
        title: Status ID
        description: Initial status ID
        type: integer
        required: false
        default: 1
        example: 1
      category_id:
        title: Category ID
        description: Ticket category ID
        type: integer
        required: false
        example: 10
      agent_id:
        title: Agent ID
        description: Assigned agent ID
        type: integer
        required: false
        example: 100
      team_id:
        title: Team ID
        description: Assigned team ID
        type: integer
        required: false
        example: 5
      site_id:
        title: Site ID
        description: Site/location ID
        type: integer
        required: false
        example: 1
      user_id:
        title: User ID
        description: End user ID (ticket requester)
        type: integer
        required: false
        example: 500
      customfields:
        title: Custom Fields
        description: Array of custom field objects
        type: "[]object"
        required: false
    output:
      ticket:
        title: Ticket
        description: Created ticket details
        type: ticket
        required: true
      success:
        title: Success
        description: Was the operation successful
        type: boolean
        required: true

  update_ticket:
    title: Update Ticket
    description: Update an existing ticket in HaloITSM
    input:
      ticket_id:
        title: Ticket ID
        description: ID of the ticket to update
        type: integer
        required: true
        example: 12345
      summary:
        title: Summary
        description: Updated ticket summary
        type: string
        required: false
        example: Security incident - Resolved
      details:
        title: Details
        description: Updated ticket details
        type: string
        required: false
        example: Investigation completed. False positive confirmed.
      status_id:
        title: Status ID
        description: Updated status ID
        type: integer
        required: false
        example: 4
      priority_id:
        title: Priority ID
        description: Updated priority ID
        type: integer
        required: false
        example: 2
      agent_id:
        title: Agent ID
        description: Updated assigned agent ID
        type: integer
        required: false
        example: 101
      customfields:
        title: Custom Fields
        description: Array of custom field objects to update
        type: "[]object"
        required: false
    output:
      ticket:
        title: Ticket
        description: Updated ticket details
        type: ticket
        required: true
      success:
        title: Success
        description: Was the operation successful
        type: boolean
        required: true

  close_ticket:
    title: Close Ticket
    description: Close a ticket in HaloITSM
    input:
      ticket_id:
        title: Ticket ID
        description: ID of the ticket to close
        type: integer
        required: true
        example: 12345
      resolution:
        title: Resolution
        description: Resolution notes
        type: string
        required: false
        example: Issue resolved by security team
      closed_status_id:
        title: Closed Status ID
        description: Status ID for closed state
        type: integer
        required: false
        default: 5
        example: 5
    output:
      ticket:
        title: Ticket
        description: Closed ticket details
        type: ticket
        required: true
      success:
        title: Success
        description: Was the operation successful
        type: boolean
        required: true

  get_ticket:
    title: Get Ticket
    description: Retrieve details of a specific ticket
    input:
      ticket_id:
        title: Ticket ID
        description: ID of the ticket to retrieve
        type: integer
        required: true
        example: 12345
      include_details:
        title: Include Details
        description: Include full ticket details
        type: boolean
        required: false
        default: true
    output:
      ticket:
        title: Ticket
        description: Ticket details
        type: ticket
        required: true
      found:
        title: Found
        description: Was the ticket found
        type: boolean
        required: true

  search_tickets:
    title: Search Tickets
    description: Search for tickets using filters
    input:
      summary_contains:
        title: Summary Contains
        description: Search tickets where summary contains this text
        type: string
        required: false
        example: Security incident
      status_id:
        title: Status ID
        description: Filter by status ID
        type: integer
        required: false
        example: 1
      agent_id:
        title: Agent ID
        description: Filter by assigned agent ID
        type: integer
        required: false
        example: 100
      team_id:
        title: Team ID
        description: Filter by team ID
        type: integer
        required: false
        example: 5
      priority_id:
        title: Priority ID
        description: Filter by priority ID
        type: integer
        required: false
        example: 3
      created_after:
        title: Created After
        description: Filter tickets created after this date (ISO 8601)
        type: date
        required: false
        example: "2025-11-01T00:00:00Z"
      created_before:
        title: Created Before
        description: Filter tickets created before this date (ISO 8601)
        type: date
        required: false
        example: "2025-11-06T23:59:59Z"
      max_results:
        title: Max Results
        description: Maximum number of results to return
        type: integer
        required: false
        default: 50
        example: 50
    output:
      tickets:
        title: Tickets
        description: List of tickets matching search criteria
        type: "[]ticket"
        required: true
      count:
        title: Count
        description: Number of tickets found
        type: integer
        required: true

  add_comment:
    title: Add Comment
    description: Add a comment/note to a ticket
    input:
      ticket_id:
        title: Ticket ID
        description: ID of the ticket
        type: integer
        required: true
        example: 12345
      comment:
        title: Comment
        description: Comment text to add
        type: string
        required: true
        example: Investigation in progress
      is_private:
        title: Is Private
        description: Make this comment private (agent-only)
        type: boolean
        required: false
        default: false
    output:
      success:
        title: Success
        description: Was the comment added successfully
        type: boolean
        required: true
      comment_id:
        title: Comment ID
        description: ID of the created comment
        type: integer
        required: false

  assign_ticket:
    title: Assign Ticket
    description: Assign a ticket to an agent or team
    input:
      ticket_id:
        title: Ticket ID
        description: ID of the ticket to assign
        type: integer
        required: true
        example: 12345
      agent_id:
        title: Agent ID
        description: Agent ID to assign ticket to
        type: integer
        required: false
        example: 100
      team_id:
        title: Team ID
        description: Team ID to assign ticket to
        type: integer
        required: false
        example: 5
      notify:
        title: Notify
        description: Send notification to assignee
        type: boolean
        required: false
        default: true
    output:
      ticket:
        title: Ticket
        description: Updated ticket details
        type: ticket
        required: true
      success:
        title: Success
        description: Was the assignment successful
        type: boolean
        required: true

triggers:
  ticket_created:
    title: Ticket Created
    description: Triggers when a new ticket is created in HaloITSM (webhook)
    input:
      tickettype_id:
        title: Ticket Type ID
        description: Only trigger for specific ticket type (optional)
        type: integer
        required: false
        example: 1
      priority_id:
        title: Priority ID
        description: Only trigger for specific priority (optional)
        type: integer
        required: false
        example: 3
    output:
      ticket:
        title: Ticket
        description: Newly created ticket details
        type: ticket
        required: true

  ticket_updated:
    title: Ticket Updated
    description: Triggers when a ticket is updated in HaloITSM (webhook)
    input:
      ticket_id:
        title: Ticket ID
        description: Only trigger for specific ticket ID (optional)
        type: integer
        required: false
        example: 12345
      status_changed:
        title: Status Changed
        description: Only trigger when status changes
        type: boolean
        required: false
        default: false
    output:
      ticket:
        title: Ticket
        description: Updated ticket details
        type: ticket
        required: true
      previous_status_id:
        title: Previous Status ID
        description: Previous status ID before update
        type: integer
        required: false

  ticket_status_changed:
    title: Ticket Status Changed
    description: Triggers specifically when ticket status changes (webhook)
    input:
      ticket_id:
        title: Ticket ID
        description: Only trigger for specific ticket ID (optional)
        type: integer
        required: false
        example: 12345
      new_status_id:
        title: New Status ID
        description: Only trigger when status changes to this value (optional)
        type: integer
        required: false
        example: 4
    output:
      ticket:
        title: Ticket
        description: Ticket details with new status
        type: ticket
        required: true
      old_status_id:
        title: Old Status ID
        description: Previous status ID
        type: integer
        required: true
      new_status_id:
        title: New Status ID
        description: New status ID
        type: integer
        required: true

types:
  ticket:
    id:
      title: ID
      description: Ticket ID
      type: integer
      required: false
    summary:
      title: Summary
      description: Ticket summary
      type: string
      required: false
    details:
      title: Details
      description: Ticket details
      type: string
      required: false
    tickettype_id:
      title: Ticket Type ID
      description: Ticket type identifier
      type: integer
      required: false
    status_id:
      title: Status ID
      description: Current status ID
      type: integer
      required: false
    status_name:
      title: Status Name
      description: Current status name
      type: string
      required: false
    priority_id:
      title: Priority ID
      description: Priority level ID
      type: integer
      required: false
    priority_name:
      title: Priority Name
      description: Priority level name
      type: string
      required: false
    category_id:
      title: Category ID
      description: Category ID
      type: integer
      required: false
    agent_id:
      title: Agent ID
      description: Assigned agent ID
      type: integer
      required: false
    agent_name:
      title: Agent Name
      description: Assigned agent name
      type: string
      required: false
    team_id:
      title: Team ID
      description: Assigned team ID
      type: integer
      required: false
    team_name:
      title: Team Name
      description: Assigned team name
      type: string
      required: false
    site_id:
      title: Site ID
      description: Site/location ID
      type: integer
      required: false
    user_id:
      title: User ID
      description: End user ID
      type: integer
      required: false
    user_name:
      title: User Name
      description: End user name
      type: string
      required: false
    dateoccurred:
      title: Date Occurred
      description: When the incident occurred
      type: date
      required: false
    datecreated:
      title: Date Created
      description: When the ticket was created
      type: date
      required: false
    datemodified:
      title: Date Modified
      description: When the ticket was last modified
      type: date
      required: false
    customfields:
      title: Custom Fields
      description: Custom field values
      type: "[]object"
      required: false
    url:
      title: URL
      description: Direct URL to ticket in HaloITSM
      type: string
      required: false
```

---

## Connection Component

### connection/connection.py

```python
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
```

### util/api.py

```python
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
        retry_count: int = 3
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
        
        for attempt in range(retry_count):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    verify=self.ssl_verify,
                    timeout=60
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
                    
            except requests.exceptions.HTTPError as e:
                if attempt == retry_count - 1:
                    raise PluginException(
                        cause=f"HTTP {response.status_code} error",
                        assistance=f"HaloITSM API returned an error: {response.text}",
                        data=str(e)
                    )
            except requests.exceptions.RequestException as e:
                if attempt == retry_count - 1:
                    raise PluginException(
                        cause="Request failed",
                        assistance=f"Unable to connect to HaloITSM API: {str(e)}",
                        data=str(e)
                    )
            
            # Wait before retry
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
        response = self.make_request(
            method="DELETE",
            endpoint=f"/tickets/{ticket_id}"
        )
        return True
```

---

## Actions Implementation

### actions/create_ticket/action.py

```python
import insightconnect_plugin_runtime
from .schema import CreateTicketInput, CreateTicketOutput, Input, Output, Component
from insightconnect_plugin_runtime.exceptions import PluginException


class CreateTicket(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="create_ticket",
            description=Component.DESCRIPTION,
            input=CreateTicketInput(),
            output=CreateTicketOutput()
        )

    def run(self, params={}):
        """
        Create a new ticket in HaloITSM
        """
        self.logger.info("CreateTicket: Starting ticket creation")
        
        # Build ticket data from input parameters
        ticket_data = {
            "summary": params.get(Input.SUMMARY),
            "details": params.get(Input.DETAILS),
            "tickettype_id": params.get(Input.TICKETTYPE_ID),
            "actioncode": 0  # 0 = New ticket
        }
        
        # Add optional fields if provided
        optional_fields = [
            Input.PRIORITY_ID, Input.STATUS_ID, Input.CATEGORY_ID,
            Input.AGENT_ID, Input.TEAM_ID, Input.SITE_ID, Input.USER_ID
        ]
        
        for field in optional_fields:
            value = params.get(field)
            if value is not None:
                ticket_data[field.replace("_", "")] = value
        
        # Add custom fields if provided
        custom_fields = params.get(Input.CUSTOMFIELDS, [])
        if custom_fields:
            ticket_data["customfields"] = custom_fields
        
        try:
            # Create ticket using API client
            result = self.connection.client.create_ticket(ticket_data)
            
            self.logger.info(f"CreateTicket: Ticket created successfully with ID {result.get('id')}")
            
            # Build output
            return {
                Output.TICKET: self._normalize_ticket(result),
                Output.SUCCESS: True
            }
            
        except Exception as e:
            self.logger.error(f"CreateTicket: Failed to create ticket: {str(e)}")
            raise PluginException(
                cause="Failed to create ticket",
                assistance=str(e)
            )
    
    def _normalize_ticket(self, ticket_data):
        """
        Normalize ticket data to match output schema
        """
        return {
            "id": ticket_data.get("id"),
            "summary": ticket_data.get("summary"),
            "details": ticket_data.get("details"),
            "tickettype_id": ticket_data.get("tickettype_id"),
            "status_id": ticket_data.get("status_id"),
            "status_name": ticket_data.get("status", {}).get("name") if isinstance(ticket_data.get("status"), dict) else None,
            "priority_id": ticket_data.get("priority_id"),
            "priority_name": ticket_data.get("priority", {}).get("name") if isinstance(ticket_data.get("priority"), dict) else None,
            "category_id": ticket_data.get("category_id"),
            "agent_id": ticket_data.get("agent_id"),
            "agent_name": ticket_data.get("agent", {}).get("name") if isinstance(ticket_data.get("agent"), dict) else None,
            "team_id": ticket_data.get("team_id"),
            "team_name": ticket_data.get("team", {}).get("name") if isinstance(ticket_data.get("team"), dict) else None,
            "site_id": ticket_data.get("site_id"),
            "user_id": ticket_data.get("user_id"),
            "user_name": ticket_data.get("user", {}).get("name") if isinstance(ticket_data.get("user"), dict) else None,
            "dateoccurred": ticket_data.get("dateoccurred"),
            "datecreated": ticket_data.get("datecreated"),
            "datemodified": ticket_data.get("datemodified"),
            "customfields": ticket_data.get("customfields", []),
            "url": ticket_data.get("url")
        }
```

### actions/update_ticket/action.py

```python
import insightconnect_plugin_runtime
from .schema import UpdateTicketInput, UpdateTicketOutput, Input, Output, Component
from insightconnect_plugin_runtime.exceptions import PluginException


class UpdateTicket(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="update_ticket",
            description=Component.DESCRIPTION,
            input=UpdateTicketInput(),
            output=UpdateTicketOutput()
        )

    def run(self, params={}):
        """
        Update an existing ticket in HaloITSM
        """
        ticket_id = params.get(Input.TICKET_ID)
        self.logger.info(f"UpdateTicket: Updating ticket {ticket_id}")
        
        # Build update data - only include fields that were provided
        ticket_data = {
            "id": ticket_id,
            "actioncode": 1  # 1 = Update ticket
        }
        
        # Add provided fields to update
        field_mapping = {
            Input.SUMMARY: "summary",
            Input.DETAILS: "details",
            Input.STATUS_ID: "status_id",
            Input.PRIORITY_ID: "priority_id",
            Input.AGENT_ID: "agent_id"
        }
        
        for input_field, api_field in field_mapping.items():
            value = params.get(input_field)
            if value is not None:
                ticket_data[api_field] = value
        
        # Handle custom fields
        custom_fields = params.get(Input.CUSTOMFIELDS, [])
        if custom_fields:
            ticket_data["customfields"] = custom_fields
        
        try:
            # Update ticket using API client
            result = self.connection.client.update_ticket(ticket_data)
            
            self.logger.info(f"UpdateTicket: Ticket {ticket_id} updated successfully")
            
            # Build output (reuse normalize method from create_ticket)
            from komand_haloitsm.actions.create_ticket.action import CreateTicket
            normalized_ticket = CreateTicket()._normalize_ticket(result)
            
            return {
                Output.TICKET: normalized_ticket,
                Output.SUCCESS: True
            }
            
        except Exception as e:
            self.logger.error(f"UpdateTicket: Failed to update ticket: {str(e)}")
            raise PluginException(
                cause=f"Failed to update ticket {ticket_id}",
                assistance=str(e)
            )
```

### actions/search_tickets/action.py

```python
import insightconnect_plugin_runtime
from .schema import SearchTicketsInput, SearchTicketsOutput, Input, Output, Component
from insightconnect_plugin_runtime.exceptions import PluginException


class SearchTickets(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="search_tickets",
            description=Component.DESCRIPTION,
            input=SearchTicketsInput(),
            output=SearchTicketsOutput()
        )

    def run(self, params={}):
        """
        Search for tickets in HaloITSM
        """
        self.logger.info("SearchTickets: Starting ticket search")
        
        # Build query parameters
        filters = {}
        
        # Add search filters
        if params.get(Input.SUMMARY_CONTAINS):
            filters["search"] = params.get(Input.SUMMARY_CONTAINS)
        
        if params.get(Input.STATUS_ID):
            filters["status_id"] = params.get(Input.STATUS_ID)
        
        if params.get(Input.AGENT_ID):
            filters["agent_id"] = params.get(Input.AGENT_ID)
        
        if params.get(Input.TEAM_ID):
            filters["team_id"] = params.get(Input.TEAM_ID)
        
        if params.get(Input.PRIORITY_ID):
            filters["priority_id"] = params.get(Input.PRIORITY_ID)
        
        # Date filters
        if params.get(Input.CREATED_AFTER):
            filters["startdate"] = params.get(Input.CREATED_AFTER)
        
        if params.get(Input.CREATED_BEFORE):
            filters["enddate"] = params.get(Input.CREATED_BEFORE)
        
        # Set page size
        max_results = params.get(Input.MAX_RESULTS, 50)
        filters["count"] = max_results
        
        try:
            # Search tickets using API client
            results = self.connection.client.search_tickets(filters)
            
            # Normalize ticket data
            from komand_haloitsm.actions.create_ticket.action import CreateTicket
            normalize_func = CreateTicket()._normalize_ticket
            normalized_tickets = [normalize_func(ticket) for ticket in results]
            
            self.logger.info(f"SearchTickets: Found {len(normalized_tickets)} tickets")
            
            return {
                Output.TICKETS: normalized_tickets,
                Output.COUNT: len(normalized_tickets)
            }
            
        except Exception as e:
            self.logger.error(f"SearchTickets: Search failed: {str(e)}")
            raise PluginException(
                cause="Failed to search tickets",
                assistance=str(e)
            )
```

---

## Triggers Implementation

### triggers/ticket_created/trigger.py

```python
import insightconnect_plugin_runtime
from .schema import TicketCreatedInput, TicketCreatedOutput, Input, Output, Component
from insightconnect_plugin_runtime.exceptions import PluginException
import time


class TicketCreated(insightconnect_plugin_runtime.Trigger):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="ticket_created",
            description=Component.DESCRIPTION,
            input=TicketCreatedInput(),
            output=TicketCreatedOutput()
        )
        self.last_check_time = None

    def run(self, params={}):
        """
        Webhook trigger for new ticket creation
        This runs as a webhook receiver in InsightConnect
        """
        # Get optional filters
        filter_tickettype = params.get(Input.TICKETTYPE_ID)
        filter_priority = params.get(Input.PRIORITY_ID)
        
        self.logger.info("TicketCreated: Webhook trigger started")
        
        while True:
            try:
                # In webhook mode, this will be called by InsightConnect
                # when a webhook payload is received
                # The webhook payload will be in self.webhook_payload
                
                if hasattr(self, 'webhook_payload'):
                    ticket_data = self.webhook_payload.get('ticket', {})
                    
                    # Apply filters if specified
                    if filter_tickettype and ticket_data.get('tickettype_id') != filter_tickettype:
                        continue
                    
                    if filter_priority and ticket_data.get('priority_id') != filter_priority:
                        continue
                    
                    # Normalize ticket data
                    from komand_haloitsm.actions.create_ticket.action import CreateTicket
                    normalized_ticket = CreateTicket()._normalize_ticket(ticket_data)
                    
                    self.logger.info(f"TicketCreated: New ticket {ticket_data.get('id')} detected")
                    
                    # Send normalized ticket to workflow
                    self.send({Output.TICKET: normalized_ticket})
                
            except Exception as e:
                self.logger.error(f"TicketCreated: Error processing webhook: {str(e)}")
            
            # Webhook triggers should not sleep - they wait for incoming requests
            # If running in polling mode, add appropriate sleep
            time.sleep(0.1)
```

### triggers/ticket_updated/trigger.py

```python
import insightconnect_plugin_runtime
from .schema import TicketUpdatedInput, TicketUpdatedOutput, Input, Output, Component
from insightconnect_plugin_runtime.exceptions import PluginException
import time


class TicketUpdated(insightconnect_plugin_runtime.Trigger):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="ticket_updated",
            description=Component.DESCRIPTION,
            input=TicketUpdatedInput(),
            output=TicketUpdatedOutput()
        )

    def run(self, params={}):
        """
        Webhook trigger for ticket updates
        """
        filter_ticket_id = params.get(Input.TICKET_ID)
        filter_status_changed = params.get(Input.STATUS_CHANGED, False)
        
        self.logger.info("TicketUpdated: Webhook trigger started")
        
        while True:
            try:
                if hasattr(self, 'webhook_payload'):
                    ticket_data = self.webhook_payload.get('ticket', {})
                    previous_status = self.webhook_payload.get('previous_status_id')
                    
                    # Apply filters
                    if filter_ticket_id and ticket_data.get('id') != filter_ticket_id:
                        continue
                    
                    # If filtering for status changes only
                    if filter_status_changed:
                        current_status = ticket_data.get('status_id')
                        if not previous_status or current_status == previous_status:
                            continue
                    
                    # Normalize ticket data
                    from komand_haloitsm.actions.create_ticket.action import CreateTicket
                    normalized_ticket = CreateTicket()._normalize_ticket(ticket_data)
                    
                    self.logger.info(f"TicketUpdated: Ticket {ticket_data.get('id')} updated")
                    
                    # Send to workflow
                    self.send({
                        Output.TICKET: normalized_ticket,
                        Output.PREVIOUS_STATUS_ID: previous_status
                    })
                    
            except Exception as e:
                self.logger.error(f"TicketUpdated: Error processing webhook: {str(e)}")
            
            time.sleep(0.1)
```

---

## InsightVM Remediation Integration

### Overview

The InsightVM Remediation Projects integration requires a different approach than the standard InsightConnect plugin. This integration is built into InsightVM's core interface and follows the pattern established by Jira and ServiceNow integrations.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    InsightVM Console                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Remediation Projects Interface                   │  │
│  │                                                          │  │
│  │  [Project 1] ──► Solutions ──► Assets ──► Vulnerabilities│  │
│  │      │                                                   │  │
│  │      └──► Ticketing Connection                          │  │
│  │              • Connection Settings                       │  │
│  │              • Status Mapping                            │  │
│  │              • Field Mapping                             │  │
│  │              • Assignment Rules                          │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            │ REST API Calls
                            │
              ┌─────────────▼──────────────┐
              │                            │
              │  HaloITSM Ticketing        │
              │  Integration Module        │
              │                            │
              │  • OAuth2 Client           │
              │  • Ticket Creation Logic   │
              │  • Status Sync Handler     │
              │  • Webhook Listener        │
              │                            │
              └─────────────┬──────────────┘
                            │
                            │
              ┌─────────────▼──────────────┐
              │      HaloITSM API          │
              │                            │
              │  POST /api/tickets         │
              │  • Parent ticket (Project) │
              │  • Child tickets (Solutions)│
              │                            │
              └────────────────────────────┘
```

### Implementation Requirements

#### 1. Ticketing Connection Configuration

**UI Wizard Steps:**

**Step 1: Connection Details**
```
Connection Name: [HaloITSM Production]
Connection Type: ● HaloITSM

Authentication:
  Client ID: [●●●●●●●●●●●]
  Client Secret: [●●●●●●●●●●●]
  Authorization Server: [https://example.haloitsm.com/auth]
  Resource Server: [https://example.haloitsm.com/api]
  Tenant: [example]

[Test Connection]  [Cancel]  [Next →]
```

**Step 2: Status Mapping**
```
Map InsightVM Solution statuses to HaloITSM ticket statuses:

InsightVM Status          HaloITSM Status
─────────────────────────────────────────────────
Not Started          ──►  [New              ▼]
In Progress          ──►  [In Progress      ▼]
Awaiting Verification ──► [Awaiting Verification ▼]
Remediated           ──►  [Resolved         ▼]
Will Not Fix         ──►  [Closed - Won't Fix ▼]
Exception            ──►  [Closed - Exception ▼]

[← Back]  [Cancel]  [Next →]
```

**Step 3: Field Mapping**
```
Configure ticket template:

Ticket Type: [Incident                    ▼]
Priority:    [Use vulnerability severity  ▼]

Summary Template:
┌────────────────────────────────────────────────────┐
│ Security Vulnerability: $SOL_NAME                  │
└────────────────────────────────────────────────────┘

Description Template:
┌────────────────────────────────────────────────────┐
│ Remediation Project: $PROJ_NAME                    │
│ Solution: $SOL_NAME                                │
│ Affected Assets: $ASSET_COUNT                      │
│                                                    │
│ Assets:                                            │
│ $ASSET_NAME_LIST                                   │
│                                                    │
│ Vulnerabilities: $VULN_COUNT                       │
│ Top CVE: $TOP_CVE                                  │
│ Risk Score: $RISK_SCORE                            │
│                                                    │
│ Recommended Fix:                                   │
│ $SOL_FIX                                           │
└────────────────────────────────────────────────────┘

[Syntax Help]  [Preview]  [← Back]  [Next →]
```

**Step 4: Assignment Rules**
```
Create rules for automatically assigning tickets:

Rule 1:
  If: [Asset Owner is                       ▼]
      [contains               ▼] [engineering]
  Assign To: [Agent: John Smith            ▼]
  Team: [Security Engineering              ▼]
  [Delete Rule]

[+ New Rule]

Default Assignee:
  Agent: [Unassigned                        ▼]
  Team: [Security Operations                ▼]

[← Back]  [Cancel]  [Save & Enable]
```

#### 2. Template Variables

Support for InsightVM template variables:

**Project Variables:**
- `$PROJ_NAME` - Remediation project name
- `$PROJ_ID` - Project ID
- `$PROJ_OWNER` - Project owner
- `$PROJ_PRIORITY` - Project priority
- `$PROJ_DUE_DATE` - Project due date

**Solution Variables:**
- `$SOL_NAME` - Solution name
- `$SOL_ID` - Solution ID
- `$SOL_FIX` - Remediation instructions
- `$SOL_RISK_SCORE` - Solution risk score
- `$SOL_TYPE` - Solution type (patch, config, etc.)

**Asset Variables:**
- `$ASSET_COUNT` - Number of affected assets
- `$ASSET_NAME_LIST` - Comma-separated asset names
- `$ASSET_IP_LIST` - Comma-separated IP addresses
- `$ASSET_OS_LIST` - Operating systems

**Vulnerability Variables:**
- `$VULN_COUNT` - Number of vulnerabilities
- `$TOP_CVE` - Highest severity CVE
- `$TOP_CVSS` - Highest CVSS score
- `$VULN_LIST` - List of vulnerability titles
- `$RISK_SCORE` - Overall risk score

#### 3. Ticket Creation Logic

**Parent Ticket (Remediation Project):**
```python
def create_remediation_project_ticket(project):
    """
    Create parent ticket for remediation project
    """
    ticket_data = {
        "summary": template.render_summary({
            "PROJ_NAME": project.name,
            "SOL_COUNT": len(project.solutions)
        }),
        "details": template.render_description(project),
        "tickettype_id": config.ticket_type_id,
        "priority_id": map_priority(project.priority),
        "customfields": [
            {
                "id": config.custom_field_id_project,
                "name": "InsightVM Project ID",
                "value": str(project.id)
            }
        ]
    }
    
    parent_ticket = halo_api.create_ticket(ticket_data)
    
    # Store ticket reference
    db.store_ticket_mapping(
        project_id=project.id,
        ticket_id=parent_ticket["id"],
        ticket_type="project"
    )
    
    return parent_ticket
```

**Child Tickets (Solutions):**
```python
def create_solution_tickets(project, parent_ticket_id):
    """
    Create child tickets for each solution in project
    """
    child_tickets = []
    
    for solution in project.solutions:
        ticket_data = {
            "summary": template.render_solution_summary(solution),
            "details": template.render_solution_description(solution),
            "tickettype_id": config.ticket_type_id,
            "priority_id": map_vulnerability_severity(solution.max_severity),
            "parent_id": parent_ticket_id,  # Link to parent
            "customfields": [
                {
                    "id": config.custom_field_id_solution,
                    "name": "InsightVM Solution ID",
                    "value": str(solution.id)
                },
                {
                    "id": config.custom_field_id_assets,
                    "name": "Affected Assets",
                    "value": str(len(solution.assets))
                }
            ]
        }
        
        # Apply assignment rules
        assignment = apply_assignment_rules(solution.assets)
        if assignment:
            ticket_data["agent_id"] = assignment.agent_id
            ticket_data["team_id"] = assignment.team_id
        
        child_ticket = halo_api.create_ticket(ticket_data)
        
        # Store mapping
        db.store_ticket_mapping(
            project_id=project.id,
            solution_id=solution.id,
            ticket_id=child_ticket["id"],
            ticket_type="solution"
        )
        
        child_tickets.append(child_ticket)
    
    return child_tickets
```

#### 4. Status Synchronization

**HaloITSM → InsightVM (Webhook Handler):**
```python
@webhook_handler("/insightvm/halo/status_update")
def handle_status_update(webhook_payload):
    """
    Handle status updates from HaloITSM
    """
    ticket_id = webhook_payload["ticket"]["id"]
    new_status_id = webhook_payload["ticket"]["status_id"]
    
    # Look up solution mapping
    mapping = db.get_ticket_mapping(ticket_id=ticket_id)
    
    if not mapping:
        logger.warning(f"No mapping found for ticket {ticket_id}")
        return
    
    # Map HaloITSM status to InsightVM status
    insightvm_status = status_mapping.get(new_status_id)
    
    if not insightvm_status:
        logger.warning(f"No status mapping for HaloITSM status {new_status_id}")
        return
    
    # Update solution status in InsightVM
    if mapping.solution_id:
        insightvm_api.update_solution_status(
            project_id=mapping.project_id,
            solution_id=mapping.solution_id,
            status=insightvm_status
        )
        logger.info(f"Updated solution {mapping.solution_id} to {insightvm_status}")
    
    # If multiple child tickets exist, apply priority logic
    # (e.g., "Awaiting Verification" takes precedence)
    if mapping.project_id:
        reconcile_project_status(mapping.project_id)
```

**InsightVM → HaloITSM (Status Change Handler):**
```python
def on_solution_status_change(solution_id, old_status, new_status):
    """
    Handle status changes in InsightVM
    """
    mapping = db.get_ticket_mapping(solution_id=solution_id)
    
    if not mapping:
        return
    
    # Map InsightVM status to HaloITSM status
    halo_status_id = reverse_status_mapping.get(new_status)
    
    if not halo_status_id:
        logger.warning(f"No reverse mapping for status {new_status}")
        return
    
    # Update ticket in HaloITSM
    halo_api.update_ticket({
        "id": mapping.ticket_id,
        "status_id": halo_status_id,
        "notes": f"Status updated from InsightVM: {new_status}"
    })
```

#### 5. Comment Synchronization

**Add Comment When:**
- Vulnerability is rediscovered on an asset
- New asset is added to a solution
- Asset is removed from a solution
- Remediation verification fails

```python
def add_ticket_comment(solution_id, comment_text, is_private=False):
    """
    Add comment to HaloITSM ticket
    """
    mapping = db.get_ticket_mapping(solution_id=solution_id)
    
    if not mapping:
        return
    
    halo_api.add_comment(
        ticket_id=mapping.ticket_id,
        comment=comment_text,
        is_private=is_private
    )
```

---

## Bidirectional Sync Strategy

### Sync Architecture

```
┌────────────────────────────────────────────────────┐
│              InsightVM / InsightIDR                 │
├────────────────────────────────────────────────────┤
│                                                    │
│  1. Create Investigation/Project                   │
│  2. Generate ticket data                           │
│  3. POST to HaloITSM API                           │
│  4. Store ticket ID mapping                        │
│                                                    │
└─────────────────┬──────────────────────────────────┘
                  │
                  │ REST API
                  ▼
┌─────────────────────────────────────────────────────┐
│                 HaloITSM API                        │
│  • Creates ticket                                   │
│  • Returns ticket ID                                │
│  • Configures webhooks                              │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ Webhook Callbacks
                  ▼
┌─────────────────────────────────────────────────────┐
│         InsightConnect Webhook Trigger              │
│                                                     │
│  1. Receives webhook from HaloITSM                  │
│  2. Parses ticket status change                     │
│  3. Looks up ticket mapping                         │
│  4. Calls InsightVM API to update status            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Implementation Steps

#### Step 1: Initial Ticket Creation
```python
# From InsightIDR Investigation
investigation_id = "INV-12345"
investigation_data = get_investigation(investigation_id)

# Create ticket in HaloITSM
ticket = halo_client.create_ticket({
    "summary": f"Security Investigation: {investigation_data.title}",
    "details": format_investigation_details(investigation_data),
    "tickettype_id": 1,
    "priority_id": map_priority(investigation_data.priority)
})

# Store bidirectional mapping
store_mapping({
    "investigation_id": investigation_id,
    "halo_ticket_id": ticket["id"],
    "sync_enabled": True,
    "last_synced": datetime.now()
})
```

#### Step 2: Configure Webhook in HaloITSM
```python
# Register webhook endpoint
webhook_url = f"{insightconnect_url}/triggers/halo_ticket_update"

halo_client.create_webhook({
    "name": "InsightConnect Sync",
    "payload_url": webhook_url,
    "events": ["ticket_updated", "ticket_status_changed"],
    "conditions": {
        "customfield_insightvm_id": {"exists": True}
    }
})
```

#### Step 3: Webhook Handler
```python
@app.route("/triggers/halo_ticket_update", methods=["POST"])
def handle_halo_webhook():
    payload = request.json
    
    ticket_id = payload["ticket"]["id"]
    new_status = payload["ticket"]["status"]["id"]
    
    # Look up mapping
    mapping = get_mapping_by_ticket_id(ticket_id)
    
    if not mapping:
        return {"status": "ignored", "reason": "no mapping"}
    
    # Update InsightVM/IDR
    if mapping["investigation_id"]:
        update_investigation_status(
            investigation_id=mapping["investigation_id"],
            status=map_halo_status_to_idr(new_status)
        )
    
    return {"status": "success"}
```

#### Step 4: Status Mapping Configuration
```python
# Bidirectional status mapping
STATUS_MAP = {
    # HaloITSM → InsightIDR
    "halo_to_idr": {
        1: "OPEN",           # New → Open
        2: "INVESTIGATING",  # In Progress → Investigating
        3: "INVESTIGATING",  # Awaiting Info → Investigating
        4: "CLOSED",         # Resolved → Closed
        5: "CLOSED"          # Closed → Closed
    },
    # InsightIDR → HaloITSM
    "idr_to_halo": {
        "OPEN": 1,
        "INVESTIGATING": 2,
        "CLOSED": 4
    }
}
```

---

## Code Examples

### Example 1: Create Ticket from InsightIDR Investigation

```python
# InsightConnect Workflow: Create HaloITSM Ticket from Investigation

from datetime import datetime

# Step 1: Get Investigation Details (from InsightIDR trigger)
investigation = {
    "id": "{{[get_investigation].[investigation].[id]}}",
    "title": "{{[get_investigation].[investigation].[title]}}",
    "priority": "{{[get_investigation].[investigation].[priority]}}",
    "assignee": "{{[get_investigation].[investigation].[assignee]}}",
    "status": "{{[get_investigation].[investigation].[status]}}",
    "created_time": "{{[get_investigation].[investigation].[created_time]}}",
    "alerts": "{{[get_investigation].[investigation].[alerts]}}"
}

# Step 2: Format Ticket Description
description = f"""
Security Investigation from InsightIDR

Investigation ID: {investigation['id']}
Priority: {investigation['priority']}
Status: {investigation['status']}
Created: {investigation['created_time']}
Assignee: {investigation['assignee']}

Alert Summary:
{investigation['alerts']}

Please review and take appropriate action.
"""

# Step 3: Create Ticket in HaloITSM
ticket_params = {
    "summary": f"[InsightIDR] {investigation['title']}",
    "details": description,
    "tickettype_id": 1,  # Incident
    "priority_id": 3 if investigation['priority'] == 'HIGH' else 2,
    "customfields": [
        {
            "id": 100,
            "name": "InsightIDR Investigation ID",
            "value": investigation['id']
        }
    ]
}

# Call HaloITSM Create Ticket action
ticket_result = haloitsm.create_ticket(ticket_params)

# Step 4: Add Comment to Investigation
investigation_comment = f"""
HaloITSM ticket created:
Ticket ID: {ticket_result['ticket']['id']}
Ticket URL: {ticket_result['ticket']['url']}
Status: {ticket_result['ticket']['status_name']}
"""

insightidr.add_note_to_investigation(
    investigation_id=investigation['id'],
    note=investigation_comment
)
```

### Example 2: Sync Ticket Status Changes

```python
# InsightConnect Workflow: Sync HaloITSM Status to InsightIDR

# Trigger: HaloITSM Ticket Updated
ticket_update = {
    "ticket_id": "{{[trigger].[ticket].[id]}}",
    "new_status_id": "{{[trigger].[ticket].[status_id]}}",
    "new_status_name": "{{[trigger].[ticket].[status_name]}}",
    "summary": "{{[trigger].[ticket].[summary]}}"
}

# Get Investigation ID from custom field
custom_fields = "{{[trigger].[ticket].[customfields]}}"
investigation_id = None

for field in custom_fields:
    if field['name'] == 'InsightIDR Investigation ID':
        investigation_id = field['value']
        break

if investigation_id:
    # Map HaloITSM status to InsightIDR status
    status_mapping = {
        1: "OPEN",
        2: "INVESTIGATING",
        4: "CLOSED",
        5: "CLOSED"
    }
    
    idr_status = status_mapping.get(ticket_update['new_status_id'])
    
    if idr_status:
        # Update Investigation Status
        insightidr.set_status_of_investigation(
            investigation_id=investigation_id,
            status=idr_status
        )
        
        # Add Note
        note = f"Status updated from HaloITSM ticket #{ticket_update['ticket_id']}: {ticket_update['new_status_name']}"
        insightidr.add_note_to_investigation(
            investigation_id=investigation_id,
            note=note
        )
```

### Example 3: Create Remediation Tickets

```python
# InsightVM: Create HaloITSM Tickets for Remediation Project

from datetime import datetime

def create_remediation_tickets(project_id):
    """
    Create HaloITSM tickets for InsightVM remediation project
    """
    # Get project details
    project = insightvm_api.get_project(project_id)
    
    # Create parent ticket for project
    parent_ticket = haloitsm.create_ticket({
        "summary": f"[InsightVM] Remediation: {project.name}",
        "details": f"""
Remediation Project: {project.name}
Project ID: {project.id}
Priority: {project.priority}
Due Date: {project.due_date}
Owner: {project.owner}

Total Solutions: {len(project.solutions)}
Affected Assets: {project.total_assets}
Total Vulnerabilities: {project.total_vulnerabilities}
Risk Score: {project.risk_score}

This is the parent ticket for the remediation project.
Individual solution tickets will be created as child tickets.
        """,
        "tickettype_id": 1,
        "priority_id": map_priority(project.priority),
        "customfields": [
            {
                "id": 101,
                "name": "InsightVM Project ID",
                "value": str(project.id)
            },
            {
                "id": 102,
                "name": "Project Type",
                "value": "Remediation"
            }
        ]
    })
    
    parent_ticket_id = parent_ticket['ticket']['id']
    
    # Create child tickets for each solution
    child_tickets = []
    
    for solution in project.solutions:
        child_ticket = haloitsm.create_ticket({
            "summary": f"[Solution] {solution.name}",
            "details": f"""
Solution: {solution.name}
Solution ID: {solution.id}
Parent Project: {project.name}

Affected Assets ({len(solution.assets)}):
{', '.join(asset.name for asset in solution.assets)}

Vulnerabilities ({len(solution.vulnerabilities)}):
{format_vulnerability_list(solution.vulnerabilities)}

Recommended Fix:
{solution.fix_description}

Risk Reduction: {solution.risk_reduction}
Effort: {solution.estimated_effort}
            """,
            "tickettype_id": 2,  # Task
            "priority_id": map_vulnerability_severity(solution.max_severity),
            "parent_id": parent_ticket_id,
            "customfields": [
                {
                    "id": 103,
                    "name": "InsightVM Solution ID",
                    "value": str(solution.id)
                },
                {
                    "id": 104,
                    "name": "Affected Asset Count",
                    "value": str(len(solution.assets))
                },
                {
                    "id": 105,
                    "name": "Top CVE",
                    "value": solution.top_cve
                }
            ]
        })
        
        child_tickets.append(child_ticket['ticket'])
    
    return {
        "parent_ticket": parent_ticket['ticket'],
        "child_tickets": child_tickets,
        "total_tickets": 1 + len(child_tickets)
    }

def map_priority(priority):
    """Map InsightVM priority to HaloITSM priority"""
    mapping = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1
    }
    return mapping.get(priority, 2)

def map_vulnerability_severity(severity):
    """Map vulnerability severity to ticket priority"""
    mapping = {
        10: 4,  # Critical severity → Critical priority
        9: 4,
        8: 3,   # High severity → High priority
        7: 3,
        6: 2,   # Medium severity → Medium priority
        5: 2,
        4: 1,   # Low severity → Low priority
        3: 1
    }
    return mapping.get(severity, 2)
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_create_ticket.py

import sys
import os
sys.path.append(os.path.abspath('../'))

from unittest import TestCase
from komand_haloitsm.actions.create_ticket import CreateTicket
from komand_haloitsm.actions.create_ticket.schema import Input, Output
from unittest.mock import Mock, patch
import json


class TestCreateTicket(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.action = CreateTicket()
        cls.action.connection = Mock()
        cls.action.logger = Mock()
    
    @patch('komand_haloitsm.util.api.HaloITSMAPI.create_ticket')
    def test_create_ticket_success(self, mock_create):
        # Mock API response
        mock_create.return_value = {
            "id": 12345,
            "summary": "Test Ticket",
            "details": "Test Details",
            "status_id": 1,
            "tickettype_id": 1,
            "priority_id": 3,
            "datecreated": "2025-11-06T14:35:55.618Z"
        }
        
        # Test input
        input_params = {
            Input.SUMMARY: "Test Ticket",
            Input.DETAILS: "Test Details",
            Input.TICKETTYPE_ID: 1,
            Input.PRIORITY_ID: 3
        }
        
        # Mock connection client
        self.action.connection.client.create_ticket = mock_create
        
        # Run action
        result = self.action.run(input_params)
        
        # Assertions
        self.assertTrue(result[Output.SUCCESS])
        self.assertEqual(result[Output.TICKET]["id"], 12345)
        self.assertEqual(result[Output.TICKET]["summary"], "Test Ticket")
        mock_create.assert_called_once()
    
    def test_create_ticket_missing_required_field(self):
        # Test with missing required field
        input_params = {
            Input.SUMMARY: "Test Ticket",
            # Missing DETAILS and TICKETTYPE_ID
        }
        
        # Should raise exception
        with self.assertRaises(Exception):
            self.action.run(input_params)
```

### Integration Tests

```python
# tests/integration/test_haloitsm_integration.py

import os
import json
from komand_haloitsm.connection.connection import Connection
from komand_haloitsm.actions.create_ticket import CreateTicket
from komand_haloitsm.actions.get_ticket import GetTicket
from komand_haloitsm.actions.update_ticket import UpdateTicket


class TestHaloITSMIntegration:
    """
    Integration tests - require real HaloITSM instance
    Set environment variables:
    - HALO_CLIENT_ID
    - HALO_CLIENT_SECRET
    - HALO_AUTH_SERVER
    - HALO_RESOURCE_SERVER
    - HALO_TENANT
    """
    
    @classmethod
    def setup_class(cls):
        # Create connection
        cls.connection = Connection()
        connection_params = {
            "client_id": {"secretKey": os.getenv("HALO_CLIENT_ID")},
            "client_secret": {"secretKey": os.getenv("HALO_CLIENT_SECRET")},
            "authorization_server": os.getenv("HALO_AUTH_SERVER"),
            "resource_server": os.getenv("HALO_RESOURCE_SERVER"),
            "tenant": os.getenv("HALO_TENANT"),
            "ssl_verify": True
        }
        cls.connection.connect(connection_params)
        
        # Initialize actions
        cls.create_action = CreateTicket()
        cls.create_action.connection = cls.connection
        
        cls.get_action = GetTicket()
        cls.get_action.connection = cls.connection
        
        cls.update_action = UpdateTicket()
        cls.update_action.connection = cls.connection
    
    def test_full_ticket_lifecycle(self):
        """Test creating, retrieving, updating, and closing a ticket"""
        
        # Step 1: Create ticket
        print("Creating ticket...")
        create_result = self.create_action.run({
            "summary": "Integration Test Ticket",
            "details": "This is an integration test ticket created by automated tests",
            "tickettype_id": 1,
            "priority_id": 2
        })
        
        assert create_result["success"] is True
        ticket_id = create_result["ticket"]["id"]
        print(f"Created ticket ID: {ticket_id}")
        
        # Step 2: Retrieve ticket
        print(f"Retrieving ticket {ticket_id}...")
        get_result = self.get_action.run({
            "ticket_id": ticket_id,
            "include_details": True
        })
        
        assert get_result["found"] is True
        assert get_result["ticket"]["id"] == ticket_id
        assert get_result["ticket"]["summary"] == "Integration Test Ticket"
        print("Ticket retrieved successfully")
        
        # Step 3: Update ticket
        print(f"Updating ticket {ticket_id}...")
        update_result = self.update_action.run({
            "ticket_id": ticket_id,
            "summary": "Integration Test Ticket - UPDATED",
            "status_id": 2  # In Progress
        })
        
        assert update_result["success"] is True
        assert update_result["ticket"]["summary"] == "Integration Test Ticket - UPDATED"
        print("Ticket updated successfully")
        
        # Step 4: Close ticket (cleanup)
        print(f"Closing ticket {ticket_id}...")
        from komand_haloitsm.actions.close_ticket import CloseTicket
        close_action = CloseTicket()
        close_action.connection = self.connection
        
        close_result = close_action.run({
            "ticket_id": ticket_id,
            "resolution": "Test completed successfully",
            "closed_status_id": 5
        })
        
        assert close_result["success"] is True
        print("Ticket closed successfully")
        
        print("\n✓ Full ticket lifecycle test passed")
```

### Manual Testing Checklist

```markdown
## HaloITSM Plugin Testing Checklist

### Connection Testing
- [ ] Test connection with valid credentials
- [ ] Test connection with invalid credentials
- [ ] Test connection with incorrect server URLs
- [ ] Verify SSL certificate validation
- [ ] Test OAuth2 token refresh

### Create Ticket Action
- [ ] Create ticket with minimum required fields
- [ ] Create ticket with all optional fields
- [ ] Create ticket with custom fields
- [ ] Create ticket with invalid ticket type
- [ ] Verify ticket created in HaloITSM UI

### Update Ticket Action
- [ ] Update ticket summary
- [ ] Update ticket status
- [ ] Update ticket priority
- [ ] Update ticket assignment
- [ ] Update ticket custom fields
- [ ] Try updating non-existent ticket

### Get Ticket Action
- [ ] Get existing ticket by ID
- [ ] Get non-existent ticket
- [ ] Verify all fields returned
- [ ] Test with/without details flag

### Search Tickets Action
- [ ] Search by summary text
- [ ] Search by status
- [ ] Search by priority
- [ ] Search by assigned agent
- [ ] Search by date range
- [ ] Search with multiple filters
- [ ] Test pagination

### Close Ticket Action
- [ ] Close ticket with resolution
- [ ] Close ticket without resolution
- [ ] Verify status updated correctly
- [ ] Close already closed ticket

### Add Comment Action
- [ ] Add public comment
- [ ] Add private comment
- [ ] Add comment with special characters
- [ ] Add very long comment

### Assign Ticket Action
- [ ] Assign to specific agent
- [ ] Assign to team
- [ ] Assign with notification
- [ ] Assign without notification
- [ ] Reassign ticket

### Ticket Created Trigger
- [ ] Test webhook reception
- [ ] Test filtering by ticket type
- [ ] Test filtering by priority
- [ ] Verify ticket data in output

### Ticket Updated Trigger
- [ ] Test webhook for status changes
- [ ] Test webhook for assignment changes
- [ ] Test filtering by ticket ID
- [ ] Test status_changed filter

### InsightIDR Integration
- [ ] Create ticket from investigation
- [ ] Update investigation when ticket changes
- [ ] Sync status bidirectionally
- [ ] Add investigation notes

### InsightVM Integration
- [ ] Create parent ticket for project
- [ ] Create child tickets for solutions
- [ ] Map statuses correctly
- [ ] Test assignment rules
- [ ] Verify comment synchronization
```

---

## Deployment Guide

### Prerequisites

1. **Development Environment:**
   ```bash
   # Install Python 3.8+
   python3 --version
   
   # Install insight-plugin tool
   pip install insightconnect-plugin-runtime
   pip install insight-plugin
   
   # Clone Rapid7 plugins repository
   git clone https://github.com/rapid7/insightconnect-plugins.git
   cd insightconnect-plugins
   ```

2. **HaloITSM Setup:**
   - Create API application in HaloITSM
   - Note Client ID and Client Secret
   - Configure webhook endpoints
   - Set up custom fields (optional)

3. **Network Access:**
   - Ensure InsightConnect can reach HaloITSM API
   - Configure firewall rules if needed
   - Set up SSL certificates

### Build Plugin

```bash
# Navigate to plugin directory
cd plugins/haloitsm

# Generate plugin from spec
insight-plugin generate plugin.spec.yaml

# Install dependencies
pip install -r requirements.txt

# Build Docker image
make image

# Validate plugin
insight-plugin validate

# Run unit tests
make test

# Export plugin
insight-plugin export
```

### Upload to InsightConnect

1. **Via UI:**
   - Navigate to Settings > Plugins & Tools
   - Click "Import"
   - Select "From Local Drive"
   - Choose the `.plg` file generated by `insight-plugin export`
   - Click "Import"

2. **Via API:**
   ```bash
   curl -X POST \
     https://us.api.insight.rapid7.com/connect/v1/plugins \
     -H "X-Api-Key: YOUR_API_KEY" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@haloitsm-1.0.0.plg"
   ```

### Create Connection

1. Navigate to Settings > Plugins & Tools > Connections
2. Click "Add Connection"
3. Select "HaloITSM"
4. Fill in connection details:
   - **Connection Name:** HaloITSM Production
   - **Client ID:** `[your-client-id]`
   - **Client Secret:** `[your-client-secret]`
   - **Authorization Server:** `https://example.haloitsm.com/auth`
   - **Resource Server:** `https://example.haloitsm.com/api`
   - **Tenant:** `example`
5. Test connection
6. Save

### Create Workflow

**Example: Create Ticket from Investigation**

1. Create new workflow
2. Add trigger: "Investigation Created" (InsightIDR)
3. Add step: "Create Ticket" (HaloITSM)
   - Map investigation fields to ticket fields
   - Use template for description
4. Add step: "Add Note to Investigation" (InsightIDR)
   - Include ticket ID and URL
5. Save and activate workflow

### Configure Webhooks

**In HaloITSM:**

1. Navigate to Configuration > Integrations > Webhooks
2. Click "New"
3. Configure webhook:
   - **Name:** InsightConnect Ticket Updates
   - **Payload URL:** `[InsightConnect trigger URL]`
   - **Method:** POST
   - **Content-Type:** application/json
   - **Events:**
     - ✓ New Ticket Logged
     - ✓ Ticket Status Changed
     - ✓ Ticket Updated
4. Save webhook

**Get Trigger URL:**
1. In InsightConnect workflow
2. Add trigger: "Ticket Updated" (HaloITSM)
3. Copy webhook URL from trigger configuration
4. Paste into HaloITSM webhook configuration

### Production Deployment

```markdown
## Pre-Production Checklist

### Testing
- [ ] All unit tests pass
- [ ] Integration tests pass in staging
- [ ] Manual testing completed
- [ ] Performance testing completed
- [ ] Security review completed

### Documentation
- [ ] Plugin help.md updated
- [ ] Workflow templates documented
- [ ] Troubleshooting guide created
- [ ] API rate limits documented

### Configuration
- [ ] Production credentials configured
- [ ] SSL certificates valid
- [ ] Webhook endpoints accessible
- [ ] Custom fields mapped
- [ ] Assignment rules configured

### Monitoring
- [ ] Logging configured
- [ ] Alerts set up
- [ ] Dashboard created
- [ ] Error tracking enabled

### Rollback Plan
- [ ] Previous plugin version backed up
- [ ] Rollback procedure documented
- [ ] Emergency contacts listed
```

### Monitoring and Maintenance

**Log Locations:**
- InsightConnect: Settings > Jobs > View Logs
- Plugin Logs: Settings > Plugins & Tools > [Plugin] > Logs

**Key Metrics to Monitor:**
- Workflow execution success rate
- API request latency
- Token refresh failures
- Webhook delivery failures
- Ticket creation rate

**Troubleshooting:**

1. **Connection Failures:**
   ```python
   # Check token expiration
   # Verify credentials
   # Test network connectivity
   # Review SSL certificate
   ```

2. **Webhook Not Received:**
   - Verify webhook URL is accessible
   - Check HaloITSM webhook logs
   - Test webhook with manual trigger
   - Verify events are configured

3. **Status Sync Issues:**
   - Check status mapping configuration
   - Verify custom field values
   - Review bidirectional sync logic
   - Check for race conditions

---

## Appendix

### A. HaloITSM API Reference

Full API documentation: https://haloservicedesk.com/apidoc/

Key Endpoints:
- GET /api/tickets
- POST /api/tickets
- DELETE /api/tickets/{id}
- GET /api/agents
- GET /api/teams
- GET /api/tickettypes
- GET /api/statuses

### B. Status Mapping Reference

| InsightVM Status | HaloITSM Status | Status ID |
|------------------|-----------------|-----------|
| Not Started | New | 1 |
| In Progress | In Progress | 2 |
| Awaiting Verification | Awaiting Verification | 3 |
| Remediated | Resolved | 4 |
| Will Not Fix | Closed - Won't Fix | 5 |
| Exception | Closed - Exception | 6 |

### C. Priority Mapping Reference

| Severity/Priority | HaloITSM Priority | Priority ID |
|-------------------|-------------------|-------------|
| Critical | Critical | 4 |
| High | High | 3 |
| Medium | Medium | 2 |
| Low | Low | 1 |

### D. Template Variable Reference

Complete list of supported template variables for InsightVM integration:

**Project Variables:**
- $PROJ_NAME, $PROJ_ID, $PROJ_OWNER, $PROJ_PRIORITY, $PROJ_DUE_DATE

**Solution Variables:**
- $SOL_NAME, $SOL_ID, $SOL_FIX, $SOL_RISK_SCORE, $SOL_TYPE

**Asset Variables:**
- $ASSET_COUNT, $ASSET_NAME_LIST, $ASSET_IP_LIST, $ASSET_OS_LIST

**Vulnerability Variables:**
- $VULN_COUNT, $TOP_CVE, $TOP_CVSS, $VULN_LIST, $RISK_SCORE

---

## Document Version

**Version:** 1.0  
**Last Updated:** November 6, 2025  
**Author:** Development Team  
**Status:** Draft

---

**End of Technical Specification**