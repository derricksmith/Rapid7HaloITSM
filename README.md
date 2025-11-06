# HaloITSM Plugin for Rapid7 InsightConnect

A comprehensive Rapid7 InsightConnect plugin that integrates HaloITSM (IT Service Management) with Rapid7's security platform, enabling bidirectional communication between InsightIDR investigations, InsightVM remediation projects, and HaloITSM tickets.

## Features

- **Complete Ticket Management**: Create, update, get, search, close, assign, and comment on HaloITSM tickets
- **Real-time Webhooks**: Receive notifications for ticket creation, updates, and status changes
- **OAuth2 Authentication**: Secure client credentials flow integration
- **Bidirectional Sync**: Synchronize status changes between Rapid7 products and HaloITSM
- **Custom Fields Support**: Handle HaloITSM custom fields for advanced integrations
- **InsightVM Integration**: Support for remediation project ticketing workflows

## Quick Start

### Prerequisites

- HaloITSM instance (cloud or on-premise) with API access
- Rapid7 InsightConnect platform
- Network connectivity between platforms

### Installation

1. **Download Plugin**: Get the latest `.plg` file from releases
2. **Upload to InsightConnect**: 
   - Navigate to Settings → Plugins & Tools
   - Click "Import" → "From Local Drive"  
   - Select the HaloITSM plugin file
3. **Create Connection**: Configure OAuth2 credentials and server endpoints

### Basic Configuration

```yaml
# Connection Parameters
client_id: "your-halo-client-id"
client_secret: "your-halo-client-secret"  
authorization_server: "https://your-tenant.haloitsm.com/auth"
resource_server: "https://your-tenant.haloitsm.com/api"
tenant: "your-tenant-name"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Rapid7 Insight Platform                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐   │
│  │  InsightIDR  │──────│InsightConnect│──────│  InsightVM   │   │
│  │              │      │   (SOAR)     │      │              │   │
│  └──────────────┘      └──────┬───────┘      └──────────────┘   │
└───────────────────────────────┼─────────────────────────────────┘
                                │
                                │ REST API / Webhooks
                                │
                   ┌────────────▼────────────┐
                   │   HaloITSM Plugin       │
                   │                         │
                   │ • OAuth2 Authentication │
                   │ • Ticket Operations     │
                   │ • Webhook Receivers     │
                   │ • Status Synchronization│
                   └─────────────────────────┘
```

## Usage Examples

### Create Ticket from Security Alert

```python
# Workflow: Security Alert → HaloITSM Ticket
trigger: alert_created (InsightIDR)

action: create_ticket (HaloITSM)
inputs:
  summary: "[SECURITY] {{alert.title}}"
  details: |
    Security Alert Details:
    - Source: {{alert.source}}
    - Severity: {{alert.severity}}
    - Affected Assets: {{alert.assets}}
    
    Investigation Required.
  tickettype_id: 1
  priority_id: 3
  customfields:
    - id: 100
      name: "Alert ID"
      value: "{{alert.id}}"
```

### Sync Status Changes

```python
# Workflow: HaloITSM Status → InsightIDR Update
trigger: ticket_status_changed (HaloITSM)

condition: ticket.customfields contains "investigation_id"

action: set_investigation_status (InsightIDR)
inputs:
  investigation_id: "{{ticket.customfields.investigation_id}}"
  status: |
    {% if ticket.status_id == 4 %}
      CLOSED
    {% elif ticket.status_id == 2 %}  
      INVESTIGATING
    {% else %}
      OPEN
    {% endif %}
```

## Available Actions

| Action | Description | Key Inputs |
|--------|-------------|------------|
| `create_ticket` | Create new ticket | summary, details, tickettype_id |
| `update_ticket` | Update existing ticket | ticket_id, fields to update |
| `get_ticket` | Retrieve ticket details | ticket_id |
| `search_tickets` | Find tickets by criteria | filters, max_results |
| `close_ticket` | Close with resolution | ticket_id, resolution |
| `add_comment` | Add note to ticket | ticket_id, comment |
| `assign_ticket` | Assign to agent/team | ticket_id, agent_id/team_id |

## Available Triggers

| Trigger | Description | Use Case |
|---------|-------------|----------|
| `ticket_created` | New ticket webhook | Auto-respond to new issues |
| `ticket_updated` | Ticket change webhook | Track all modifications |
| `ticket_status_changed` | Status change webhook | Sync workflow states |

## Development

### Building the Plugin

```bash
# Install dependencies
pip install -r requirements.txt

# Generate plugin structure  
insight-plugin generate plugin.spec.yaml

# Build Docker image
make image

# Validate specification
make validate

# Run tests
make test

# Export for deployment
make export
```

### Project Structure

```
plugins/haloitsm/
├── plugin.spec.yaml          # Plugin definition
├── komand_haloitsm/
│   ├── connection/           # OAuth2 authentication
│   ├── actions/             # Ticket operations
│   ├── triggers/            # Webhook receivers  
│   └── util/api.py          # HaloITSM API client
├── tests/                   # Unit & integration tests
└── help.md                  # User documentation
```

### Testing

```bash
# Unit tests
python -m pytest tests/test_*.py

# Integration tests (requires HaloITSM instance)
export HALO_CLIENT_ID="your-id"
export HALO_CLIENT_SECRET="your-secret"  
export HALO_AUTH_SERVER="https://example.haloitsm.com/auth"
export HALO_RESOURCE_SERVER="https://example.haloitsm.com/api"
export HALO_TENANT="example"

python tests/test_integration.py
```

## API Reference

### HaloITSM API Endpoints

- **Authentication**: `POST /auth/token` (OAuth2 client credentials)
- **Tickets**: `GET|POST /api/tickets` (CRUD operations)
- **Comments**: `POST /api/ticketnotes` (Add ticket notes)

### Status Mappings

| InsightVM Status | HaloITSM Status | Status ID |
|------------------|-----------------|-----------|
| Not Started | New | 1 |
| In Progress | In Progress | 2 |
| Remediated | Resolved | 4 |
| Will Not Fix | Closed | 5 |

## Security Considerations

- **OAuth2 Credentials**: Store Client ID/Secret securely in InsightConnect vault
- **SSL/TLS**: Enable SSL verification for production deployments  
- **Network Access**: Restrict API access to authorized IP ranges
- **Permissions**: Use least-privilege API permissions in HaloITSM
- **Webhook Security**: Validate webhook payloads and use HTTPS endpoints

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify Client ID/Secret are correct
   - Check OAuth2 scope permissions
   - Ensure authorization server URL is accessible

2. **Webhook Delivery Issues**  
   - Confirm webhook URL is publicly accessible
   - Check HaloITSM webhook configuration
   - Review InsightConnect trigger logs

3. **API Rate Limiting**
   - Monitor API request volume
   - Implement workflow delays if needed
   - Contact HaloITSM admin for rate limit increases

### Logging

Enable debug logging in InsightConnect to troubleshoot issues:
- Plugin logs: Settings → Plugins & Tools → HaloITSM → Logs
- Workflow logs: Workflows → [Workflow] → Executions → View Details

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`  
5. Open Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Production Deployment

For production deployment, please review the comprehensive guides:

- **[Production Deployment Guide](PRODUCTION.md)**: Complete production setup instructions
- **[Production Readiness Checklist](PRODUCTION_CHECKLIST.md)**: Pre-deployment validation checklist
- **[Configuration Guide](CONFIGURATION.md)**: Detailed configuration examples

### Quick Production Setup

1. **Review Requirements**
   ```bash
   # Run production readiness check
   make quality-gate
   ```

2. **Build Release Package**
   ```bash
   # Create production-ready package
   make package
   ```

3. **Deploy to Production**
   - Follow [PRODUCTION.md](PRODUCTION.md) for detailed steps
   - Complete [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
   - Run smoke tests: `python smoke_test.py --environment production`

4. **Monitor Deployment**
   - Set up monitoring dashboards
   - Configure alerting thresholds
   - Validate webhook delivery

### CI/CD Integration

This plugin includes GitHub Actions for automated:
- Code quality checks (linting, security scans)
- Unit and integration testing
- Plugin validation and building
- Automated releases with smoke testing

See [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml) for the complete pipeline.

## Support

- **Documentation**: [Rapid7 InsightConnect Docs](https://docs.rapid7.com/insightconnect/)
- **HaloITSM API**: [API Documentation](https://haloservicedesk.com/apidoc/)
- **Issues**: [GitHub Issues](https://github.com/derricksmith/Rapid7HaloITSM/issues)
- **Community**: [Rapid7 Community](https://community.rapid7.com/)

---

**Version**: 1.0.0  
**Last Updated**: November 6, 2025  
**Compatibility**: InsightConnect 4.0+, HaloITSM Cloud/On-Premise  
**Production Status**: Production Ready