# HaloITSM Plugin

## Overview

The HaloITSM plugin for Rapid7 InsightConnect enables seamless integration between your security orchestration workflows and HaloITSM service desk platform. This plugin allows you to create, update, search, and manage tickets directly from your InsightConnect workflows, while also receiving real-time notifications when tickets are modified in HaloITSM.

## Requirements

* HaloITSM instance (cloud or on-premise)
* API credentials (Client ID and Client Secret)
* Network connectivity between InsightConnect and HaloITSM

## Supported Product Versions

* HaloITSM Cloud and On-Premise versions with API access
* InsightConnect 4.0 and later

## Key Features

* **Ticket Management**: Create, update, search, and close tickets
* **Assignment Operations**: Assign tickets to agents or teams
* **Comments**: Add notes and comments to existing tickets
* **Real-time Notifications**: Receive webhook notifications for ticket events
* **Bidirectional Sync**: Synchronize status changes between InsightConnect and HaloITSM
* **Custom Fields**: Support for HaloITSM custom fields
* **Default Configuration**: Set default ticket types, priorities, teams, and categories at connection level
* **Flexible Overrides**: Override defaults on a per-action basis when needed

## Setup

### HaloITSM Configuration

1. **Generate API Credentials**:
   - Navigate to Configuration → Integrations → HaloITSM API
   - Click "View Applications" → "Add"
   - Select "Client ID and Secret (Services)"
   - Generate and save Client ID and Client Secret
   - Select Login Type: "Agent"
   - Assign permissions: `edit:tickets`, `read:tickets`, `delete:tickets`

2. **Configure Webhooks** (Optional):
   - Go to Configuration → Integrations → Webhooks
   - Create webhook pointing to your InsightConnect trigger URL
   - Select events: New Ticket Logged, Ticket Status Changed, Ticket Updated

### InsightConnect Configuration

1. **Create Connection**:
   - Navigate to Settings → Plugins & Tools → Connections
   - Select "HaloITSM" and click "Add Connection"
   - Fill in the required fields:
     - **Client ID**: Your HaloITSM API Client ID
     - **Client Secret**: Your HaloITSM API Client Secret  
     - **Authorization Server**: `https://your-tenant.haloitsm.com/auth`
     - **Resource Server**: `https://your-tenant.haloitsm.com/api`
     - **Tenant**: Your HaloITSM tenant name
   - **Optional Default Configuration** (recommended for consistency):
     - **Default Ticket Type ID**: Default ticket type (e.g., 1 for Incident)
     - **Default Priority ID**: Default priority level (e.g., 3 for High)
     - **Default Team ID**: Default team assignment (e.g., 15 for SOC Team)
     - **Default Agent ID**: Default agent assignment
     - **Default Category ID**: Default ticket category
   - Test the connection and save

#### Benefits of Default Configuration:
- **Consistency**: All tickets automatically use appropriate defaults
- **Simplified Workflows**: Less configuration needed in each action
- **Team-Specific**: Create different connections for different teams
- **Flexibility**: Can still override defaults when needed

## Actions

### Create Ticket
Create a new ticket in HaloITSM.

**Input:**
- **Summary** (required): Ticket title
- **Details** (required): Ticket description
- **Ticket Type ID**: ID of the ticket type (uses connection default if not specified)
- **Priority ID**: Priority level (uses connection default if not specified)
- **Status ID**: Initial status (default: 1=New)
- **Agent ID**: Assigned agent ID (uses connection default if not specified)
- **Team ID**: Assigned team ID (uses connection default if not specified)
- **Category ID**: Ticket category (uses connection default if not specified)
- **Custom Fields**: Array of custom field objects

**Note**: With default configuration, only Summary and Details are required. All other fields will use connection defaults unless explicitly specified.

**Examples:**

*Using connection defaults:*
```
Summary: "Security Alert: Suspicious Activity"
Details: "Multiple failed login attempts detected from IP 192.168.1.100"
```

*Overriding specific fields:*
```
Summary: "Critical Security Incident"  
Details: "Data breach suspected - immediate attention required"
Priority ID: 4  # Override to Critical priority
Agent ID: 100   # Assign to specific security lead
```
- **Team ID**: Assigned team ID
- **Custom Fields**: Array of custom field objects

**Output:**
- **Ticket**: Created ticket object with ID, summary, status, etc.
- **Success**: Boolean indicating operation success

### Update Ticket
Update an existing ticket in HaloITSM.

**Input:**
- **Ticket ID** (required): ID of ticket to update
- **Summary**: Updated title
- **Details**: Updated description
- **Status ID**: New status ID
- **Priority ID**: New priority ID
- **Agent ID**: New assigned agent

**Output:**
- **Ticket**: Updated ticket object
- **Success**: Boolean indicating operation success

### Get Ticket
Retrieve details of a specific ticket.

**Input:**
- **Ticket ID** (required): ID of ticket to retrieve
- **Include Details**: Whether to include full details (default: true)

**Output:**
- **Ticket**: Complete ticket object
- **Found**: Boolean indicating if ticket was found

### Search Tickets
Search for tickets using various filters.

**Input:**
- **Summary Contains**: Text to search in ticket summaries
- **Status ID**: Filter by status
- **Agent ID**: Filter by assigned agent
- **Team ID**: Filter by team
- **Priority ID**: Filter by priority
- **Created After**: Start date for creation filter
- **Created Before**: End date for creation filter
- **Max Results**: Maximum tickets to return (default: 50)

**Output:**
- **Tickets**: Array of matching ticket objects
- **Count**: Number of tickets found

### Close Ticket
Close a ticket with resolution notes.

**Input:**
- **Ticket ID** (required): ID of ticket to close
- **Resolution**: Resolution notes
- **Closed Status ID**: Status ID for closed state (default: 5)

**Output:**
- **Ticket**: Closed ticket object
- **Success**: Boolean indicating operation success

### Add Comment
Add a comment or note to an existing ticket.

**Input:**
- **Ticket ID** (required): ID of target ticket
- **Comment** (required): Comment text
- **Is Private**: Make comment agent-only (default: false)

**Output:**
- **Success**: Boolean indicating operation success
- **Comment ID**: ID of created comment

### Assign Ticket
Assign a ticket to an agent or team.

**Input:**
- **Ticket ID** (required): ID of ticket to assign
- **Agent ID**: Agent to assign to
- **Team ID**: Team to assign to  
- **Notify**: Send notification to assignee (default: true)

**Output:**
- **Ticket**: Updated ticket object
- **Success**: Boolean indicating operation success

## Triggers

### Ticket Created
Triggers when a new ticket is created in HaloITSM (webhook).

**Configuration:**
- **Ticket Type ID**: Filter for specific ticket type (optional)
- **Priority ID**: Filter for specific priority (optional)

**Output:**
- **Ticket**: Newly created ticket object

### Ticket Updated  
Triggers when a ticket is updated in HaloITSM (webhook).

**Configuration:**
- **Ticket ID**: Filter for specific ticket (optional)
- **Status Changed**: Only trigger on status changes (default: false)

**Output:**
- **Ticket**: Updated ticket object
- **Previous Status ID**: Status before update

### Ticket Status Changed
Triggers specifically when ticket status changes (webhook).

**Configuration:**
- **Ticket ID**: Filter for specific ticket (optional)
- **New Status ID**: Filter for specific target status (optional)

**Output:**
- **Ticket**: Ticket object with new status
- **Old Status ID**: Previous status
- **New Status ID**: New status

## Integration Examples

### InsightIDR Investigation to HaloITSM Ticket

```yaml
trigger: investigation_created (InsightIDR)
↓
action: create_ticket (HaloITSM)
  - summary: "[InsightIDR] {{investigation.title}}"
  - details: "Investigation ID: {{investigation.id}}\\nPriority: {{investigation.priority}}"
  - tickettype_id: 1
  - priority_id: 3
↓
action: add_note_to_investigation (InsightIDR)
  - note: "HaloITSM ticket created: {{ticket.id}}"
```

### HaloITSM Status Change to InsightIDR Update

```yaml
trigger: ticket_status_changed (HaloITSM)
↓
action: set_status_of_investigation (InsightIDR)
  - investigation_id: "{{ticket.customfields.investigation_id}}"
  - status: "CLOSED" (if ticket status = 4)
```

## Common Status Mappings

| HaloITSM Status | Status ID | InsightIDR Status | InsightVM Status |
|----------------|-----------|-------------------|------------------|
| New | 1 | OPEN | Not Started |
| In Progress | 2 | INVESTIGATING | In Progress |
| Awaiting Verification | 3 | INVESTIGATING | Awaiting Verification |
| Resolved | 4 | CLOSED | Remediated |
| Closed | 5 | CLOSED | Will Not Fix |

## Troubleshooting

### Connection Issues

**Error: "Failed to obtain OAuth2 token"**
- Verify Client ID and Client Secret are correct
- Check that Authorization Server URL is accessible
- Ensure API application has required permissions

**Error: "Connection test failed"**  
- Verify Resource Server URL is correct
- Check network connectivity to HaloITSM instance
- Confirm SSL certificate is valid (or disable SSL verification for testing)

### Webhook Issues

**Webhooks not received**
- Verify webhook URL is accessible from HaloITSM
- Check that webhook events are properly configured
- Review HaloITSM webhook logs for delivery failures

### API Limitations

- **Rate Limits**: HaloITSM may have API rate limits. Plugin implements automatic retry with backoff.
- **Token Expiry**: OAuth tokens expire after 1 hour. Plugin automatically refreshes tokens.
- **Field Validation**: HaloITSM validates required fields. Ensure ticket type, status, and priority IDs exist.

## Version History

- **1.0.0**: Initial release with core ticket operations and webhook triggers

## Support

For support with this plugin:
- Check the [Rapid7 InsightConnect documentation](https://docs.rapid7.com/insightconnect/)  
- Review [HaloITSM API documentation](https://haloservicedesk.com/apidoc/)
- Contact your HaloITSM administrator for instance-specific configuration