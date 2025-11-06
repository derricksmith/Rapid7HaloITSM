# Production Readiness Checklist

## 🎯 Overview
This checklist ensures the HaloITSM plugin is ready for production deployment in your Rapid7 InsightConnect environment.

## ✅ Pre-Production Requirements

### Code Quality & Testing
- [ ] All unit tests pass (`make test`)
- [ ] Integration tests completed against staging HaloITSM
- [ ] Smoke tests pass in staging environment  
- [ ] Code coverage above 80%
- [ ] Security scan (Bandit) passes with no high-severity issues
- [ ] Dependency scan (Safety) shows no known vulnerabilities
- [ ] Plugin validation passes (`insight-plugin validate`)
- [ ] Load testing completed (if applicable)

### Security & Compliance
- [ ] OAuth2 credentials generated for production HaloITSM
- [ ] SSL/TLS certificate validation enabled
- [ ] Input validation implemented for all user inputs
- [ ] Error messages don't expose sensitive information
- [ ] Credentials stored in InsightConnect vault (not hardcoded)
- [ ] API permissions follow least privilege principle
- [ ] Network security requirements documented
- [ ] Compliance requirements reviewed (SOC2, GDPR, etc.)

### Configuration & Documentation
- [ ] Production HaloITSM instance configured and tested
- [ ] Default configurations validated for your organization
- [ ] Webhook endpoints configured in HaloITSM
- [ ] User documentation complete and reviewed
- [ ] Troubleshooting guide available
- [ ] Operational runbook created
- [ ] HaloITSM outage procedures documented (manual fallback)
- [ ] Change management process defined

### Infrastructure & Monitoring
- [ ] InsightConnect environment prepared
- [ ] Network connectivity verified (InsightConnect ↔ HaloITSM)
- [ ] Firewall rules configured
- [ ] Monitoring and alerting configured
- [ ] Log aggregation setup
- [ ] Performance baselines established
- [ ] Backup and recovery procedures tested

## 🚀 Deployment Process

### Step 1: Pre-Deployment Validation
```bash
# Run full test suite
make quality-gate

# Build and validate plugin
make build

# Run smoke tests against staging
cd plugins/haloitsm
python smoke_test.py --environment staging
```

### Step 2: Production Deployment
1. **Export Plugin Package**
   ```bash
   make export
   ```

2. **Upload to InsightConnect**
   - Navigate to Settings → Plugins & Tools
   - Click "Import" → "From Local Drive"  
   - Upload the generated `.plg` file
   - Verify successful import

3. **Create Production Connection**
   - Use production OAuth2 credentials
   - Configure appropriate default values
   - Test connection thoroughly

4. **Configure Workflows**
   - Create workflows using the new connection
   - Test critical workflows end-to-end
   - Validate webhook triggers work correctly

### Step 3: Post-Deployment Validation
```bash
# Run production smoke tests
cd plugins/haloitsm
python smoke_test.py --environment production
```

### Step 4: Monitoring Setup
- [ ] Configure alerting for plugin errors
- [ ] Set up dashboard for plugin metrics
- [ ] Establish SLA monitoring
- [ ] Test incident response procedures

## 🔧 Production Configuration

### Required Environment Variables
```bash
# HaloITSM Production Settings
HALO_CLIENT_ID=your-production-client-id
HALO_CLIENT_SECRET=your-production-client-secret
HALO_AUTH_SERVER=https://yourcompany.haloitsm.com/auth
HALO_RESOURCE_SERVER=https://yourcompany.haloitsm.com/api
HALO_TENANT=yourcompany
```

### InsightConnect Connection Configuration
```yaml
Name: "HaloITSM Production"
Client ID: "${VAULT:halo_prod_client_id}"
Client Secret: "${VAULT:halo_prod_client_secret}"
Authorization Server: "https://yourcompany.haloitsm.com/auth"
Resource Server: "https://yourcompany.haloitsm.com/api"
Tenant: "yourcompany"
SSL Verify: true

# Organizational Defaults
Default Ticket Type ID: 1
Default Priority ID: 3
Default Team ID: 15
Default Agent ID: 42  
Default Category ID: 8
```

### Webhook Configuration
Configure these webhooks in HaloITSM admin panel:

| Event | Webhook URL | Description |
|-------|-------------|-------------|
| ticket_created | `https://region.api.insight.rapid7.com/connect/v1/webhooks/your-created-webhook-id` | New ticket notifications |
| ticket_updated | `https://region.api.insight.rapid7.com/connect/v1/webhooks/your-updated-webhook-id` | Ticket update notifications |
| ticket_status_changed | `https://region.api.insight.rapid7.com/connect/v1/webhooks/your-status-webhook-id` | Status change notifications |

## 📊 Success Metrics

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

## 🚨 Business Continuity Planning

### HaloITSM Service Outage Procedures
**Since most organizations only have one HaloITSM instance:**

#### Preparation Checklist
- [ ] Manual incident tracking spreadsheet template created
- [ ] Alternative communication channels identified (Slack, Teams, email)
- [ ] Stakeholder notification list maintained
- [ ] Security operations team trained on manual procedures
- [ ] Critical ticket template library documented

#### During Outage Response Plan
1. **Immediate (0-5 min)**:
   - [ ] Disable HaloITSM plugin to prevent errors
   - [ ] Activate manual incident tracking
   - [ ] Notify security operations of service degradation
   
2. **Short-term (5-30 min)**:
   - [ ] Switch to spreadsheet/manual ticket tracking
   - [ ] Continue security investigations with manual documentation
   - [ ] Monitor HaloITSM status and recovery estimates
   - [ ] Update stakeholders on impact and timeline

3. **Recovery (when service returns)**:
   - [ ] Test HaloITSM connectivity before re-enabling
   - [ ] Manually create tickets for incidents during outage
   - [ ] Resume automated workflows gradually
   - [ ] Validate all integrations working normally

### Plugin Rollback Plan

### Immediate Rollback (< 5 minutes)
1. Disable plugin in InsightConnect
2. Pause affected workflows
3. Notify stakeholders
4. Activate manual processes

### Complete Rollback (< 30 minutes)
1. Uninstall plugin from InsightConnect
2. Restore previous plugin version (if applicable)
3. Revert configuration changes
4. Update documentation
5. Conduct post-incident review

## 🔍 Validation Checklist

### Functional Testing
- [ ] Create ticket via action
- [ ] Update ticket via action  
- [ ] Search tickets via action
- [ ] Close ticket via action
- [ ] Assign ticket via action
- [ ] Add comment via action
- [ ] Get ticket via action
- [ ] Webhook triggers fire correctly
- [ ] Status synchronization works
- [ ] Error handling works properly

### Security Testing
- [ ] Invalid credentials are rejected
- [ ] Token expiration is handled gracefully
- [ ] SSL certificate validation works
- [ ] Input validation prevents injection
- [ ] Sensitive data is not logged
- [ ] Rate limiting is respected

### Performance Testing
- [ ] High-volume ticket creation
- [ ] Concurrent API requests
- [ ] Memory usage under load
- [ ] Database connection pooling
- [ ] Token refresh under load

### Integration Testing
- [ ] InsightIDR investigation sync
- [ ] InsightVM remediation project sync
- [ ] Custom field mapping
- [ ] Assignment rule processing
- [ ] Escalation workflows

## 📋 Sign-off Requirements

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

## 📞 Emergency Contacts

| Role | Contact | Phone | Email |
|------|---------|--------|-------|
| Plugin Owner | [Name] | [Phone] | [Email] |
| DevOps Lead | [Name] | [Phone] | [Email] |  
| Security Lead | [Name] | [Phone] | [Email] |
| HaloITSM Admin | [Name] | [Phone] | [Email] |
| InsightConnect Admin | [Name] | [Phone] | [Email] |

---

## 🎉 Final Checklist

Before marking as production ready:

- [ ] All items in this checklist completed
- [ ] Production smoke tests pass
- [ ] Stakeholder sign-offs obtained
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Go-live date scheduled
- [ ] Communication plan executed

**Production Readiness Status**: ⬜ Ready ⬜ Not Ready

**Approved By**: _________________ **Date**: _________________

**Notes**: 
_________________________________________________
_________________________________________________
_________________________________________________