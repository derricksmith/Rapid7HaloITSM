# Production Deployment Guide - HaloITSM Plugin

## Overview
This comprehensive guide ensures the HaloITSM plugin is ready for production deployment in your Rapid7 InsightConnect environment. Use this as both a procedural guide and a checklist for tracking readiness.

## Pre-Production Requirements

### Code Quality & Testing
- [ ] All unit tests pass (`make test`)
- [ ] Integration tests completed against staging HaloITSM
- [ ] Smoke tests pass in staging environment  
- [ ] Code coverage above 80%
- [ ] Security scan (Bandit) passes with no high-severity issues
- [ ] Dependency scan (Safety) shows no known vulnerabilities
- [ ] Plugin validation passes (`insight-plugin validate`)
- [ ] Load testing completed (if applicable)
- [ ] Code review completed
- [ ] Performance testing completed

### Security & Compliance
- [ ] OAuth2 credentials generated for production HaloITSM
- [ ] SSL/TLS certificate validation enabled
- [ ] Input validation implemented for all user inputs
- [ ] Error messages don't expose sensitive information
- [ ] Credentials stored in InsightConnect vault (not hardcoded)
- [ ] API permissions follow least privilege principle
- [ ] Network security requirements documented
- [ ] Compliance requirements reviewed (SOC2, GDPR, etc.)
- [ ] Security review completed

### Configuration & Documentation
- [ ] Production HaloITSM instance configured and tested
- [ ] Default configurations validated for your organization
- [ ] Webhook endpoints configured in HaloITSM
- [ ] User documentation complete and reviewed (`help.md`)
- [ ] Configuration guide updated (`CONFIGURATION.md`)
- [ ] API documentation reviewed
- [ ] Troubleshooting guide available
- [ ] Operational runbook created
- [ ] HaloITSM outage procedures documented (manual fallback)
- [ ] Change management process defined
- [ ] Version history documented

### Infrastructure & Monitoring
- [ ] InsightConnect environment prepared
- [ ] Network connectivity verified (InsightConnect ↔ HaloITSM)
- [ ] Firewall rules configured
- [ ] Monitoring and alerting configured
- [ ] Log aggregation setup
- [ ] Performance baselines established
- [ ] Backup and recovery procedures tested
- [ ] Dashboard requirements defined
- [ ] Error tracking configured

## Production Deployment Process

### Step 1: Pre-Deployment Validation
```bash
# Run full quality gate
cd plugins/haloitsm
make quality-gate

# Build and validate plugin
make install
make test
make validate
make image

# Run smoke tests against staging
python smoke_test.py --environment staging
```

### Step 2: Build & Package
```bash
# Export production-ready plugin
make export

# This generates the .plg file ready for deployment
```

### Step 3: Pre-Production Testing
```bash
# Set up test environment variables
export HALO_CLIENT_ID="test-client-id"
export HALO_CLIENT_SECRET="test-client-secret"
export HALO_AUTH_SERVER="https://test.haloitsm.com/auth"
export HALO_RESOURCE_SERVER="https://test.haloitsm.com/api"
export HALO_TENANT="test-tenant"

# Run comprehensive integration tests
python tests/test_integration.py
```

### Step 4: Production Deployment
1. **Upload Plugin to InsightConnect**
   - Navigate to Settings → Plugins & Tools
   - Click "Import" → "From Local Drive"
   - Upload the generated `.plg` file
   - Verify successful import

2. **Create Production Connection**
   - Use production OAuth2 credentials from vault
   - Configure organizational default values
   - Test connection thoroughly

3. **Configure Workflows**
   - Create workflows using the new connection
   - Test critical workflows end-to-end
   - Validate webhook triggers work correctly

4. **Configure Webhooks in HaloITSM**
   - Set up webhook URLs in HaloITSM admin panel
   - Test webhook delivery
   - Configure appropriate events (ticket_created, ticket_updated, ticket_status_changed)

### Step 5: Post-Deployment Validation
```bash
# Run production smoke tests
cd plugins/haloitsm
python smoke_test.py --environment production
```

### Step 6: Monitoring Setup
- [ ] Configure alerting for plugin errors
- [ ] Set up dashboard for plugin metrics
- [ ] Establish SLA monitoring
- [ ] Test incident response procedures

### Step 7: Rollout Strategy
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

## Success Metrics & Performance Targets

### Performance Targets
- [ ] Plugin action execution time < 10 seconds (95th percentile)
- [ ] API response time < 5 seconds (average)
- [ ] Success rate > 99%
- [ ] Token refresh success rate > 99.9%

### Business Metrics
- [ ] Time to create ticket < 30 seconds
- [ ] Webhook delivery success > 95%
- [ ] Status sync accuracy > 99%
- [ ] User adoption targets met

## Validation Testing

### Functional Testing Checklist
- [ ] Create ticket via action
- [ ] Update ticket via action  
- [ ] Get ticket via action
- [ ] Search tickets via action
- [ ] Close ticket via action
- [ ] Assign ticket via action
- [ ] Add comment via action
- [ ] Webhook triggers fire correctly
- [ ] Status synchronization works
- [ ] Error handling works properly

### Security Testing Checklist
- [ ] Invalid credentials are rejected
- [ ] Token expiration is handled gracefully
- [ ] SSL certificate validation works
- [ ] Input validation prevents injection
- [ ] Sensitive data is not logged
- [ ] Rate limiting is respected

### Performance Testing Checklist
- [ ] High-volume ticket creation
- [ ] Concurrent API requests
- [ ] Memory usage under load
- [ ] Database connection pooling (if applicable)
- [ ] Token refresh under load

### Integration Testing Checklist
- [ ] InsightIDR investigation sync
- [ ] InsightVM remediation project sync
- [ ] Custom field mapping
- [ ] Assignment rule processing
- [ ] Escalation workflows

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

## Sign-off Requirements

### Technical Sign-off
- [ ] **Lead Developer**: Code quality and architecture approved
- [ ] **QA Lead**: All testing completed and passed
- [ ] **Security Team**: Security review completed
- [ ] **DevOps**: Infrastructure and monitoring ready

### Business Sign-off  
- [ ] **IT Operations**: Operational procedures reviewed
- [ ] **Security Operations**: Integration requirements met
- [ ] **Compliance**: Regulatory requirements satisfied
- [ ] **Management**: Deployment authorized

## Emergency Contacts

| Role | Contact | Phone | Email |
|------|---------|--------|-------|
| Plugin Owner | [Name] | [Phone] | [Email] |
| DevOps Lead | [Name] | [Phone] | [Email] |  
| Security Lead | [Name] | [Phone] | [Email] |
| HaloITSM Admin | [Name] | [Phone] | [Email] |
| InsightConnect Admin | [Name] | [Phone] | [Email] |

---

## Final Production Readiness Status

### Pre-Launch Checklist
- [ ] All items in this guide completed
- [ ] Production smoke tests pass
- [ ] Stakeholder sign-offs obtained
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Go-live date scheduled
- [ ] Communication plan executed

### Production Readiness Summary

| Category | Status | Notes |
|----------|---------|-------|
| Code Quality | ☐ Complete | All tests pass, code reviewed |
| Security | ☐ Complete | OAuth2, SSL, input validation |
| Documentation | ☐ Complete | User guides, troubleshooting |
| Testing | ☐ Complete | Unit, integration, security tests |
| Monitoring | ☐ Complete | Metrics, alerting, dashboards |
| Deployment | ☐ Ready | Build process, rollout strategy |

**Production Readiness Status**: ☐ Ready ☐ Not Ready

**Approved By**: _________________ **Date**: _________________

**Notes**: 
```
_________________________________________________
_________________________________________________
_________________________________________________
```

**Recommendation**: This plugin is production-ready when all checklist items are completed and proper monitoring/operational procedures are in place.