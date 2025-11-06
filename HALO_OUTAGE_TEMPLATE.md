# HaloITSM Outage - Manual Incident Tracking Template

## Emergency Incident Tracking Sheet

**Use this template when HaloITSM is unavailable**

### Incident Record Template

| Field | Value | Notes |
|-------|--------|-------|
| **Incident ID** | MANUAL-{YYYY-MM-DD}-{###} | e.g., MANUAL-2025-11-06-001 |
| **Date/Time** | | |
| **Reporter** | | Who reported the issue |
| **Title/Summary** | | Brief description |
| **Source** | InsightIDR / InsightVM / Manual / Other | |
| **Priority** | Low / Medium / High / Critical | |
| **Affected Systems** | | List of impacted assets |
| **Initial Assessment** | | First findings |
| **Assigned To** | | Security analyst handling |
| **Status** | New / Investigating / Resolved / Closed | |
| **HaloITSM Ticket** | | Fill when HaloITSM returns |

### Current Active Incidents

#### Incident #1
- **ID**: MANUAL-2025-11-06-001
- **Time**: 
- **Title**: 
- **Priority**: 
- **Status**: 
- **Assigned**: 
- **Notes**: 

#### Incident #2
- **ID**: MANUAL-2025-11-06-002
- **Time**: 
- **Title**: 
- **Priority**: 
- **Status**: 
- **Assigned**: 
- **Notes**: 

#### Incident #3
- **ID**: MANUAL-2025-11-06-003
- **Time**: 
- **Title**: 
- **Priority**: 
- **Status**: 
- **Assigned**: 
- **Notes**: 

---

## Recovery Checklist

**When HaloITSM service is restored:**

### Step 1: Validate Service
- [ ] Test HaloITSM web interface accessibility
- [ ] Test API connectivity: `curl -X GET "https://tenant.haloitsm.com/api/tickettypes" -H "Authorization: Bearer {token}"`
- [ ] Verify plugin connection in InsightConnect
- [ ] Run smoke test: `python smoke_test.py --environment production`

### Step 2: Create HaloITSM Tickets
For each manual incident above:
- [ ] Create corresponding HaloITSM ticket
- [ ] Copy all details from manual tracking
- [ ] Update incident ID field with manual reference
- [ ] Notify assigned analyst of new ticket number

### Step 3: Resume Operations  
- [ ] Re-enable HaloITSM plugin in InsightConnect
- [ ] Resume automated workflows
- [ ] Test end-to-end ticket creation
- [ ] Monitor for any sync issues

### Step 4: Post-Incident
- [ ] Document outage duration and impact
- [ ] Review manual tracking effectiveness
- [ ] Update procedures based on lessons learned
- [ ] Communicate recovery to all stakeholders

---

## Emergency Contacts

| Role | Contact | Phone | Email |
|------|---------|--------|-------|
| **HaloITSM Admin** | [Name] | [Phone] | [Email] |
| **Security Ops Lead** | [Name] | [Phone] | [Email] |  
| **Platform Team** | [Name] | [Phone] | [Email] |
| **IT Operations** | [Name] | [Phone] | [Email] |

---

## Communication Templates

### Outage Notification
```
Subject: HaloITSM Service Outage - Manual Procedures Activated

Team,

HaloITSM is currently unavailable. We have activated manual incident tracking procedures:

1. All new security incidents will be tracked manually
2. Critical incidents should still be reported immediately via Slack/phone
3. Continue investigations and document findings
4. We will create HaloITSM tickets when service is restored

Estimated Resolution: [Update as available]
Next Update: [Time]

Questions? Contact Security Ops Lead.
```

### Recovery Notification  
```
Subject: HaloITSM Service Restored - Resuming Normal Operations

Team,

HaloITSM service has been restored. We are now:

1. Creating tickets for all manually tracked incidents
2. Re-enabling automated workflows
3. Resuming normal ITSM operations

All manual incidents from [start time] to [end time] are being processed.

Normal operations have resumed as of [time].
```

---

*This template should be customized for your organization's specific needs and contact information.*