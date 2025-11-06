# GitHub Copilot Instructions - HaloITSM Plugin for Rapid7 InsightConnect

## Project Overview

This is a Rapid7 InsightConnect plugin that integrates HaloITSM (IT Service Management) with Rapid7's security platform. The plugin enables bidirectional communication between InsightIDR investigations, InsightVM remediation projects, and HaloITSM tickets.

## Architecture & Key Components

### Core Architecture
- **InsightConnect Plugin**: Standard Rapid7 plugin structure with actions, triggers, and connections
- **OAuth2 Authentication**: Client credentials flow for HaloITSM API access
- **Bidirectional Sync**: Webhooks for real-time status synchronization
- **Multi-Integration**: Supports InsightIDR investigations AND InsightVM remediation projects

### Key Components
- **Connection (`connection/`)**: OAuth2 client for HaloITSM API authentication
- **Actions (`actions/`)**: CRUD operations for tickets (create, update, get, search, close, assign, comment)
- **Triggers (`triggers/`)**: Webhook receivers for ticket events (created, updated, status_changed)
- **Utilities (`util/api.py`)**: HaloITSM API client with token management and retry logic

## Development Workflows

```bash
# Setup and build
pip install insightconnect-plugin-runtime
insight-plugin generate plugin.spec.yaml
pip install -r requirements.txt

# Development
make image                    # Build Docker container
insight-plugin validate       # Validate plugin spec
make test                     # Run unit tests

# Deployment
insight-plugin export         # Generate .plg file
# Upload to InsightConnect via UI or API
```

## Critical Implementation Details

### Plugin Structure (plugins/haloitsm/)
```
├── plugin.spec.yaml          # Complete plugin definition (2800+ lines)
├── komand_haloitsm/
│   ├── connection/           # OAuth2 connection with token refresh
│   ├── actions/             # 7 main actions (create/update/get/search/close/assign/comment)
│   ├── triggers/            # 3 webhook triggers (created/updated/status_changed)
│   └── util/api.py          # API client with retry logic
└── tests/                   # Unit and integration tests
```

### HaloITSM API Patterns
- **Base URLs**: `{tenant}.haloitsm.com/auth` (OAuth) + `{tenant}.haloitsm.com/api` (Resources)
- **Authentication**: Client credentials → Bearer token (1hr expiry)
- **Ticket Operations**: POST /api/tickets (array format for both create/update)
- **Webhooks**: JSON payloads to InsightConnect trigger URLs

### Status Mapping (Critical for Sync)
```python
# InsightVM → HaloITSM
"Not Started": 1,      # New
"In Progress": 2,      # In Progress  
"Remediated": 4,       # Resolved
"Will Not Fix": 5      # Closed
```

### Data Normalization
Always use the `_normalize_ticket()` helper to convert HaloITSM responses to plugin schema format. Handle nested objects (status.name, agent.name, etc.) properly.

## Code Conventions

### Error Handling
```python
from insightconnect_plugin_runtime.exceptions import PluginException

# Always wrap API calls
try:
    result = self.connection.client.create_ticket(data)
except Exception as e:
    raise PluginException(cause="Failed to create ticket", assistance=str(e))
```

### API Client Pattern
```python
# Token auto-refresh in util/api.py
def make_request(self, method, endpoint, retry_count=3):
    for attempt in range(retry_count):
        # Handle 401 token expiry with refresh
        # Implement exponential backoff
```

### Schema Consistency
- All ticket objects use the `ticket` type definition
- Use `credential_secret_key` for sensitive connection fields
- Follow naming: `{field}_id` for IDs, `{field}_name` for display names

## Integration Patterns

### InsightIDR → HaloITSM
1. Investigation created → Trigger workflow → Create ticket action
2. Store investigation_id in custom fields
3. Add ticket URL/ID as investigation note

### InsightVM → HaloITSM  
1. Remediation project → Parent ticket + Child tickets per solution
2. Template variables: `$PROJ_NAME`, `$SOL_NAME`, `$ASSET_COUNT`, etc.
3. Assignment rules based on asset ownership

### Webhook Sync (HaloITSM → Rapid7)
1. Status change in HaloITSM → Webhook to InsightConnect trigger
2. Look up mapping via custom fields
3. Update investigation/project status via API

## Key Files & Implementation Notes

### `plugin.spec.yaml`
- Complete 2800+ line specification with all actions, triggers, types
- Uses `plugin_spec_version: v2` format
- Includes detailed examples and help text

### `connection/connection.py`
- OAuth2 client credentials flow implementation
- Token caching with 60s buffer before expiry
- Connection test via simple API call

### `util/api.py`
- Central API client with automatic token refresh
- Handles HaloITSM's array format for ticket operations
- 3-retry logic with exponential backoff

### Action Implementation Pattern
```python
def run(self, params={}):
    # 1. Extract and validate inputs
    # 2. Build API payload (handle actioncode: 0=create, 1=update)
    # 3. Call API via self.connection.client
    # 4. Normalize response with _normalize_ticket()
    # 5. Return success + normalized data
```

## Testing Strategy

### Required Tests
- **Unit Tests**: Mock API responses, test error conditions
- **Integration Tests**: Real HaloITSM instance with env vars
- **Manual Testing**: Full ticket lifecycle (create→update→close)

### Test Environment Setup
```bash
export HALO_CLIENT_ID="your_client_id"
export HALO_CLIENT_SECRET="your_secret"  
export HALO_AUTH_SERVER="https://example.haloitsm.com/auth"
export HALO_RESOURCE_SERVER="https://example.haloitsm.com/api"
export HALO_TENANT="example"
```

## External Dependencies

- **HaloITSM API**: OAuth2 + REST API for ticket management
- **insightconnect-plugin-runtime**: Rapid7's Python plugin framework  
- **requests**: HTTP client for API calls
- **Rapid7 APIs**: InsightIDR (investigations) + InsightVM (remediation projects)

---

**Critical**: Review `PROJECT_DESCRIPTION.md` for complete API specifications, webhook configuration, and bidirectional sync implementation details before making changes.