# Production Deployment Guide - HaloITSM Plugin

## Pre-Production Checklist

### ✅ **Code Quality & Testing**
- [ ] All unit tests pass (`make test`)
- [ ] Integration tests completed with real HaloITSM instance
- [ ] Code review completed
- [ ] Security review completed
- [ ] Performance testing completed
- [ ] Plugin validation passes (`insight-plugin validate`)

### ✅ **Documentation**
- [ ] User documentation complete (`help.md`)
- [ ] Configuration guide updated (`CONFIGURATION.md`)
- [ ] API documentation reviewed
- [ ] Troubleshooting guide available
- [ ] Version history documented

### ✅ **Security**
- [ ] OAuth2 credentials secured
- [ ] SSL/TLS verification enabled
- [ ] Input validation implemented
- [ ] Error messages don't expose sensitive data
- [ ] Network security requirements documented

### ✅ **Configuration**
- [ ] Production HaloITSM instance configured
- [ ] API credentials generated and tested
- [ ] Webhook endpoints configured
- [ ] Default configurations validated
- [ ] Rate limiting understood and documented

### ✅ **Monitoring**
- [ ] Logging configuration reviewed
- [ ] Alerting setup planned
- [ ] Dashboard requirements defined
- [ ] Error tracking configured

## Production Deployment Steps

### Step 1: Build & Package
```bash
# Build and validate the plugin
cd plugins/haloitsm
make install
make test
make validate
make image
make export
```

### Step 2: Pre-Production Testing
```bash
# Set up test environment variables
export HALO_CLIENT_ID="test-client-id"
export HALO_CLIENT_SECRET="test-client-secret"
export HALO_AUTH_SERVER="https://test.haloitsm.com/auth"
export HALO_RESOURCE_SERVER="https://test.haloitsm.com/api"
export HALO_TENANT="test-tenant"

# Run integration tests
python tests/test_integration.py
```

### Step 3: Production Deployment
1. **Upload Plugin to InsightConnect**
   - Navigate to Settings → Plugins & Tools
   - Click "Import" → "From Local Drive"
   - Upload the generated `.plg` file
   - Verify import success

2. **Create Production Connection**
   - Use production HaloITSM credentials
   - Configure appropriate defaults for your organization
   - Test connection thoroughly

3. **Configure Webhooks**
   - Set up webhook URLs in HaloITSM
   - Test webhook delivery
   - Configure appropriate events

### Step 4: Rollout Strategy
1. **Pilot Deployment**
   - Deploy to limited user group first
   - Monitor for issues
   - Collect feedback

2. **Gradual Rollout**
   - Expand to additional teams
   - Monitor performance metrics
   - Address issues as they arise

3. **Full Production**
   - Deploy to all teams
   - Implement monitoring and alerting
   - Document operational procedures

## Production Configuration

### HaloITSM Production Setup
```yaml
# Production Connection Configuration
connection_name: "HaloITSM Production"
client_id: "${VAULT:halo_prod_client_id}"
client_secret: "${VAULT:halo_prod_client_secret}"
authorization_server: "https://company.haloitsm.com/auth"
resource_server: "https://company.haloitsm.com/api"
tenant: "company"
ssl_verify: true

# Security Team Defaults
default_ticket_type_id: 1         # Incident
default_priority_id: 3            # High
default_team_id: 15               # Security Operations
default_agent_id: 42              # Security Manager
default_category_id: 8            # Cybersecurity
```

### Webhook Configuration
```json
{
  "name": "InsightConnect Production Webhook",
  "payload_url": "https://your-region.api.insight.rapid7.com/connect/v1/webhooks/your-webhook-id",
  "content_type": "application/json",
  "events": [
    "ticket_created",
    "ticket_updated", 
    "ticket_status_changed"
  ],
  "active": true,
  "ssl_verification": true
}
```

## Monitoring & Alerting

### Key Metrics to Monitor
- **Plugin Performance**
  - Action execution time
  - Success/failure rates
  - API response times
  - Token refresh frequency

- **Business Metrics**
  - Tickets created per day
  - Average resolution time
  - Status sync accuracy
  - Webhook delivery success

### Alerting Thresholds
```yaml
alerts:
  - name: "HaloITSM API Errors"
    condition: "error_rate > 5%"
    window: "5 minutes"
    
  - name: "High API Latency"
    condition: "avg_response_time > 5 seconds"
    window: "10 minutes"
    
  - name: "Webhook Failures"
    condition: "webhook_failure_rate > 10%"
    window: "15 minutes"
    
  - name: "Authentication Failures"
    condition: "auth_failure_count > 3"
    window: "5 minutes"
```

### Logging Configuration
```python
# Configure structured logging for production
log_config = {
    "version": 1,
    "formatters": {
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "component": "haloitsm", "message": "%(message)s", "request_id": "%(request_id)s"}'
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "level": "INFO"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}
```

## Security Considerations

### Network Security
- **Firewall Rules**: Ensure InsightConnect can reach HaloITSM API endpoints
- **IP Whitelisting**: Configure HaloITSM to accept connections from InsightConnect IPs
- **Certificate Management**: Ensure SSL certificates are valid and up-to-date

### Credential Management
- **Vault Storage**: Store all credentials in InsightConnect vault
- **Rotation Policy**: Implement regular credential rotation
- **Least Privilege**: Use minimal required API permissions
- **Audit Logging**: Log all credential usage

### Data Protection
- **Encryption**: All data in transit encrypted with TLS 1.2+
- **Data Residency**: Understand where ticket data is stored
- **Retention**: Configure appropriate data retention policies
- **Privacy**: Ensure compliance with data privacy regulations

## Troubleshooting Guide

### Common Production Issues

#### 1. Authentication Failures
**Symptoms**: 401 errors, "Invalid credentials" messages
**Solutions**:
- Verify Client ID/Secret are correct
- Check OAuth2 token expiration
- Validate API permissions in HaloITSM
- Test connection manually

#### 2. Rate Limiting
**Symptoms**: 429 errors, "Rate limit exceeded" 
**Solutions**:
- Review API usage patterns
- Implement exponential backoff
- Contact HaloITSM admin for limit increases
- Optimize workflow frequency

#### 3. Webhook Delivery Issues
**Symptoms**: Missing trigger events, delayed notifications
**Solutions**:
- Verify webhook URL accessibility
- Check webhook configuration in HaloITSM
- Review InsightConnect trigger logs
- Test webhook manually with tools like ngrok

#### 4. Performance Issues
**Symptoms**: Slow action execution, timeouts
**Solutions**:
- Monitor API response times
- Check network connectivity
- Review plugin resource usage
- Optimize data payload sizes

### Emergency Procedures

#### HaloITSM Service Outage Response
**Most organizations have a single HaloITSM instance - here's how to handle outages:**

1. **Immediate Response (0-5 minutes)**:
   - Disable HaloITSM plugin in InsightConnect to prevent errors
   - Pause all workflows that create/update tickets
   - Activate manual incident tracking procedures
   - Notify security operations team of service degradation

2. **Short-term Mitigation (5-30 minutes)**:
   - Implement temporary ticket tracking (spreadsheet/alternative system)
   - Continue security operations with manual documentation
   - Monitor HaloITSM status and estimated recovery time
   - Communicate status to stakeholders

3. **Recovery Procedures (when HaloITSM returns)**:
   - Re-enable plugin and test connectivity
   - Manually create tickets for incidents tracked during outage
   - Resume automated workflows
   - Validate all systems are functioning normally

#### Plugin Emergency Procedures
1. **Plugin Disabled**: How to quickly disable plugin during incidents
2. **Rollback Plan**: Steps to revert to previous plugin version  
3. **Contact Information**: Key stakeholders and support contacts
4. **Escalation Path**: When and how to escalate issues

## Maintenance & Updates

### Regular Maintenance Tasks
- **Weekly**: Review error logs and performance metrics
- **Monthly**: Check credential expiration dates
- **Quarterly**: Review and update documentation
- **Annually**: Security review and penetration testing

### Update Procedures
1. **Test Environment**: Always test updates in staging first
2. **Backup**: Backup current configuration before updates
3. **Rollback Plan**: Have rollback procedures ready
4. **Communication**: Notify stakeholders of maintenance windows

## Compliance & Governance

### Documentation Requirements
- **Change Management**: Document all configuration changes
- **Audit Trails**: Maintain logs of all plugin activities
- **Compliance Reports**: Generate regular compliance reports
- **Risk Assessments**: Periodic security risk assessments

### Governance Policies
- **Approval Process**: Define who can modify plugin configurations
- **Testing Requirements**: Mandatory testing before production changes
- **Incident Response**: Define incident response procedures
- **Data Handling**: Policies for handling sensitive ticket data

---

## Production Readiness Checklist Summary

| Category | Status | Notes |
|----------|---------|-------|
| ✅ Code Quality | Complete | All tests pass, code reviewed |
| ✅ Security | Complete | OAuth2, SSL, input validation |
| ✅ Documentation | Complete | User guides, troubleshooting |
| ✅ Testing | Complete | Unit, integration, security tests |
| 🔄 Monitoring | In Progress | Metrics, alerting, dashboards |
| 🔄 Deployment | Ready | Build process, rollout strategy |

**Recommendation**: This plugin is production-ready with proper monitoring and operational procedures in place.