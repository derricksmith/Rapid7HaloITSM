# InsightIDR Investigation to HaloITSM Ticket Sync - Complete Workflow Guide

## Overview
This guide provides step-by-step instructions for creating workflows that sync InsightIDR investigations to HaloITSM tickets with full alert details.

### ⚠️ Important Note About InsightConnect Limitations

**Loop Functionality:** InsightConnect's Loop step **cannot directly iterate over complex nested objects** returned from API actions like "List Alerts for Investigation". The alerts array contains nested objects with multiple fields, which the Loop step cannot properly handle.

**Solution:** Use **direct array index references** instead:
- ✅ `{{["List Alerts for Investigation"].alerts[0].title}}`
- ✅ `{{["List Alerts for Investigation"].alerts[1].title}}`
- ❌ Loop over `{{["List Alerts for Investigation"].alerts}}` (not supported)

This guide uses the array index approach throughout, which is reliable and covers 95% of use cases (showing first 5-10 alerts).

---

## Workflow 1: Investigation → HaloITSM Ticket (with Alert Details)

### Architecture
```
[Get New Investigations Trigger]
        ↓
[List Alerts for Investigation]
        ↓
[Map Priority (Decision Step)]
        ↓
[Create HaloITSM Ticket]
  (with formatted details template)
        ↓
[Create Comment in InsightIDR]
```

**Note:** No scripting or Python code required! All formatting is done using InsightConnect's built-in template syntax directly in the Create Ticket action.

---

## Step-by-Step Implementation

### Step 1: Get New Investigations Trigger

**Configuration:**
```json
{
  "frequency": 15,
  "search": []
}
```

**Available Investigation Fields:**
- `title` - Investigation title
- `rrn` - Unique investigation identifier (CRITICAL - use this for lookups!)
- `priority` - CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN
- `status` - OPEN, INVESTIGATING, CLOSED, WAITING
- `disposition` - BENIGN, MALICIOUS, FALSE_POSITIVE, NOT_APPLICABLE, SECURITY_TEST, UNDECIDED, UNKNOWN
- `created_time` - When investigation was created
- `first_alert_time` - Time of first alert
- `latest_alert_time` - Time of most recent alert
- `assignee.email` - Assigned user email
- `assignee.name` - Assigned user name
- `source` - ALERT, MANUAL, HUNT, AUTOMATION
- `responsibility` - MDR, CUSTOMER, etc.
- `tags` - Array of tags
- `organization_id` - Organization identifier

**Reference in workflow:**
```
{{["Get New Investigations"].investigation.rrn}}
{{["Get New Investigations"].investigation.title}}
{{["Get New Investigations"].investigation.priority}}
```

---

### Step 2: List Alerts for Investigation

**Action:** InsightIDR - List Alerts for Investigation

**Configuration:**
```json
{
  "id": "{{["Get New Investigations"].investigation.rrn}}",
  "index": 0,
  "size": 20
}
```

**Available Alert Fields:**
- `id` - Alert ID
- `title` - Alert title/description
- `alert_type` - Type of alert (e.g., "Account Created", "Brute Force")
- `alert_type_description` - Description of alert type
- `created_time` - When alert was created
- `first_event_time` - Time of first event
- `latest_event_time` - Time of latest event
- `detection_rule_rrn` - Detection rule that triggered alert

**Reference in workflow:**
```
{{["List Alerts for Investigation"].alerts}}
{{["List Alerts for Investigation"].metadata.total_data}}
```

---

### Step 3: Format Alert Details (Using InsightConnect Variables)

**Purpose:** Build formatted alert summary for HaloITSM ticket details

**NOTE:** InsightConnect doesn't have a built-in Python script action. You can format the details directly in the Create Ticket step using InsightConnect's template syntax, or use one of these approaches:

#### **Approach A: Direct Template in Create Ticket (Recommended)**

Skip this step entirely and use the formatted template directly in Step 5's "details" field.

#### **Approach B: Use String Operations Plugin**

**Action:** String Operations → Format String

**Template:**
```
═══════════════════════════════════════════════════════════
RAPID7 INSIGHTIDR INVESTIGATION
═══════════════════════════════════════════════════════════

Investigation ID: {{["Get New Investigations"].investigation.rrn}}
Title: {{["Get New Investigations"].investigation.title}}
Status: {{["Get New Investigations"].investigation.status}}
Priority: {{["Get New Investigations"].investigation.priority}}
Disposition: {{["Get New Investigations"].investigation.disposition}}
Source: {{["Get New Investigations"].investigation.source}}
Responsibility: {{["Get New Investigations"].investigation.responsibility}}

─────────────────────────────────────────────────────────
TIMELINE
─────────────────────────────────────────────────────────
Created: {{["Get New Investigations"].investigation.created_time}}
First Alert: {{["Get New Investigations"].investigation.first_alert_time}}
Latest Alert: {{["Get New Investigations"].investigation.latest_alert_time}}
Last Accessed: {{["Get New Investigations"].investigation.last_accessed}}

─────────────────────────────────────────────────────────
ASSIGNMENT
─────────────────────────────────────────────────────────
Assigned To: {{["Get New Investigations"].investigation.assignee.name}} ({{["Get New Investigations"].investigation.assignee.email}})

─────────────────────────────────────────────────────────
ALERTS ({{["List Alerts for Investigation"].metadata.total_data}} total)
─────────────────────────────────────────────────────────

Alert #1:
  Title: {{["List Alerts for Investigation"].alerts[0].title}}
  Type: {{["List Alerts for Investigation"].alerts[0].alert_type}}
  Description: {{["List Alerts for Investigation"].alerts[0].alert_type_description}}
  Created: {{["List Alerts for Investigation"].alerts[0].created_time}}
  First Event: {{["List Alerts for Investigation"].alerts[0].first_event_time}}
  Latest Event: {{["List Alerts for Investigation"].alerts[0].latest_event_time}}
  Alert ID: {{["List Alerts for Investigation"].alerts[0].id}}

Alert #2:
  Title: {{["List Alerts for Investigation"].alerts[1].title}}
  Type: {{["List Alerts for Investigation"].alerts[1].alert_type}}
  Description: {{["List Alerts for Investigation"].alerts[1].alert_type_description}}
  Created: {{["List Alerts for Investigation"].alerts[1].created_time}}
  First Event: {{["List Alerts for Investigation"].alerts[1].first_event_time}}
  Latest Event: {{["List Alerts for Investigation"].alerts[1].latest_event_time}}
  Alert ID: {{["List Alerts for Investigation"].alerts[1].id}}

Alert #3:
  Title: {{["List Alerts for Investigation"].alerts[2].title}}
  Type: {{["List Alerts for Investigation"].alerts[2].alert_type}}
  Description: {{["List Alerts for Investigation"].alerts[2].alert_type_description}}
  Created: {{["List Alerts for Investigation"].alerts[2].created_time}}
  First Event: {{["List Alerts for Investigation"].alerts[2].first_event_time}}
  Latest Event: {{["List Alerts for Investigation"].alerts[2].latest_event_time}}
  Alert ID: {{["List Alerts for Investigation"].alerts[2].id}}

═══════════════════════════════════════════════════════════
END OF RAPID7 INSIGHTIDR INVESTIGATION DATA
═══════════════════════════════════════════════════════════
```

**Output Variable:** `formatted_details`

#### **Approach C: AWS Lambda / Azure Function (Advanced)**

If you need complex Python logic, deploy a serverless function and call it via HTTP Request action. See appendix for details.

---

### Step 4: Map Priority (Decision Step)

**Purpose:** Convert InsightIDR priority to HaloITSM priority ID

**Decision Logic:**
```javascript
const priority = {{["Get New Investigations"].investigation.priority}};

const priorityMap = {
  "CRITICAL": 1,
  "HIGH": 2,
  "MEDIUM": 3,
  "LOW": 4,
  "UNKNOWN": 4  // Default to Low
};

return priorityMap[priority] || 4;
```

**Output Variable:** `halo_priority_id`

---

### Step 5: Create HaloITSM Ticket

**Action:** HaloITSM - Create Ticket

**Configuration:**

**Summary:**
```
[{{["Get New Investigations"].investigation.priority}}] {{["Get New Investigations"].investigation.title}}
```

**Details:** (Use direct template - no Script step needed)
```
═══════════════════════════════════════════════════════════
RAPID7 INSIGHTIDR INVESTIGATION
═══════════════════════════════════════════════════════════

Investigation ID: {{["Get New Investigations"].investigation.rrn}}
Title: {{["Get New Investigations"].investigation.title}}
Status: {{["Get New Investigations"].investigation.status}}
Priority: {{["Get New Investigations"].investigation.priority}}
Disposition: {{["Get New Investigations"].investigation.disposition}}
Source: {{["Get New Investigations"].investigation.source}}
Responsibility: {{["Get New Investigations"].investigation.responsibility}}

─────────────────────────────────────────────────────────
TIMELINE
─────────────────────────────────────────────────────────
Created: {{["Get New Investigations"].investigation.created_time}}
First Alert: {{["Get New Investigations"].investigation.first_alert_time}}
Latest Alert: {{["Get New Investigations"].investigation.latest_alert_time}}

─────────────────────────────────────────────────────────
ASSIGNMENT
─────────────────────────────────────────────────────────
Assigned To: {{["Get New Investigations"].investigation.assignee.name}} ({{["Get New Investigations"].investigation.assignee.email}})

─────────────────────────────────────────────────────────
ALERTS ({{["List Alerts for Investigation"].metadata.total_data}} total)
─────────────────────────────────────────────────────────

Alert #1:
  Title: {{["List Alerts for Investigation"].alerts[0].title}}
  Type: {{["List Alerts for Investigation"].alerts[0].alert_type}}
  Description: {{["List Alerts for Investigation"].alerts[0].alert_type_description}}
  Created: {{["List Alerts for Investigation"].alerts[0].created_time}}

Alert #2:
  Title: {{["List Alerts for Investigation"].alerts[1].title}}
  Type: {{["List Alerts for Investigation"].alerts[1].alert_type}}
## Alternative: Simplified Details Format

If you prefer a more concise format, use this template instead:

```
Investigation: {{["Get New Investigations"].investigation.title}}
RRN: {{["Get New Investigations"].investigation.rrn}}
Priority: {{["Get New Investigations"].investigation.priority}}
Status: {{["Get New Investigations"].investigation.status}}
Disposition: {{["Get New Investigations"].investigation.disposition}}
Alert Count: {{["List Alerts for Investigation"].metadata.total_data}}

ALERTS:
1. {{["List Alerts for Investigation"].alerts[0].alert_type}} - {{["List Alerts for Investigation"].alerts[0].title}}
2. {{["List Alerts for Investigation"].alerts[1].alert_type}} - {{["List Alerts for Investigation"].alerts[1].title}}
3. {{["List Alerts for Investigation"].alerts[2].alert_type}} - {{["List Alerts for Investigation"].alerts[2].title}}
4. {{["List Alerts for Investigation"].alerts[3].alert_type}} - {{["List Alerts for Investigation"].alerts[3].title}}
5. {{["List Alerts for Investigation"].alerts[4].alert_type}} - {{["List Alerts for Investigation"].alerts[4].title}}

View full investigation in InsightIDR.
```
**Required HaloITSM Custom Fields:**
1. **Field ID 50** - "Rapid7 Investigation RRN" (Text)
2. **Field ID 51** - "Rapid7 Priority" (Text) 
3. **Field ID 52** - "Alert Count" (Number)

---

### Step 6: Create Comment in InsightIDR

**Action:** InsightIDR - Create Comment

**Configuration:**
```json
{
  "target": "{{["Get New Investigations"].investigation.rrn}}",
  "body": "HaloITSM ticket created:\n\nTicket ID: {{["Create Ticket"].ticket.id}}\nTicket URL: {{["Create Ticket"].ticket.url}}\nStatus: {{["Create Ticket"].ticket.status_name}}\nCreated: {{["Create Ticket"].ticket.datecreated}}"
}
```

---

## Alternative: Simplified Details Format

If you prefer a more concise format, use this script instead:

```python
def format_alerts_simple(investigation, alerts_response):
    """
    Simple format for HaloITSM ticket details
    """
    inv = investigation
    alerts = alerts_response.get('alerts', [])
    alert_count = alerts_response.get('metadata', {}).get('total_data', 0)
    
    # Build summary
    summary = []
    summary.append(f"Investigation: {inv.get('title', 'N/A')}")
    summary.append(f"RRN: {inv.get('rrn', 'N/A')}")
    summary.append(f"Priority: {inv.get('priority', 'N/A')}")
    summary.append(f"Status: {inv.get('status', 'N/A')}")
    summary.append(f"Disposition: {inv.get('disposition', 'UNDECIDED')}")
    summary.append(f"Alert Count: {alert_count}")
    summary.append("")
    summary.append("ALERTS:")
    
    for i, alert in enumerate(alerts[:5], 1):
        summary.append(f"{i}. {alert.get('alert_type', 'Unknown')} - {alert.get('title', 'N/A')}")
    
    if alert_count > 5:
        summary.append(f"... and {alert_count - 5} more alerts")
    
    return "\n".join(summary)

investigation = {{["Get New Investigations"].investigation}}
alerts_response = {{["List Alerts for Investigation"]}}
result = format_alerts_simple(investigation, alerts_response)
```

---

## Complete Ticket Example

**Ticket Summary:**
```
[CRITICAL] Suspicious Activity Detected - Multiple Failed Logins
```

**Ticket Details:**
```
═══════════════════════════════════════════════════════════
RAPID7 INSIGHTIDR INVESTIGATION
═══════════════════════════════════════════════════════════

Investigation ID: rrn:investigation:us:01234567-89ab-cdef-0000-123123123123:investigation:ABCDEF543210
Title: Suspicious Activity Detected - Multiple Failed Logins
Status: OPEN
Priority: CRITICAL
Disposition: UNDECIDED
Source: ALERT
Responsibility: CUSTOMER

─────────────────────────────────────────────────────────
TIMELINE
─────────────────────────────────────────────────────────
Created: 2025-12-03T14:30:00Z
First Alert: 2025-12-03T14:25:00Z
Latest Alert: 2025-12-03T14:28:00Z
Last Accessed: 2025-12-03T14:30:00Z

─────────────────────────────────────────────────────────
ASSIGNMENT
─────────────────────────────────────────────────────────
Assigned To: John Doe (john.doe@example.com)

Tags: brute-force, authentication, suspicious

─────────────────────────────────────────────────────────
ALERTS (3 total)
─────────────────────────────────────────────────────────

Alert #1:
  Title: Brute Force Attack Detected
  Type: Authentication
  Description: Multiple failed login attempts from single source
  Created: 2025-12-03T14:25:00Z
  First Event: 2025-12-03T14:20:00Z
  Latest Event: 2025-12-03T14:24:00Z
  Alert ID: 11111111-1111-1111-1111-111111111111

Alert #2:
  Title: Account Lockout Detected
  Type: Account Management
  Description: User account locked due to failed login attempts
  Created: 2025-12-03T14:26:00Z
  First Event: 2025-12-03T14:25:00Z
  Latest Event: 2025-12-03T14:25:30Z
  Alert ID: 22222222-2222-2222-2222-222222222222

Alert #3:
  Title: Successful Login After Failed Attempts
  Type: Authentication
  Description: Successful login following multiple failures
  Created: 2025-12-03T14:28:00Z
  First Event: 2025-12-03T14:27:00Z
  Latest Event: 2025-12-03T14:27:00Z
  Alert ID: 33333333-3333-3333-3333-333333333333

═══════════════════════════════════════════════════════════
END OF RAPID7 INSIGHTIDR INVESTIGATION DATA
═══════════════════════════════════════════════════════════
```

**Custom Fields:**
- Investigation RRN: `rrn:investigation:us:01234567-89ab-cdef-0000-123123123123:investigation:ABCDEF543210`
- Rapid7 Priority: `CRITICAL`
- Alert Count: `3`

---

## Workflow 2: Bidirectional Status Sync

### HaloITSM → InsightIDR (Status Update)

```
[Ticket Updated Trigger - HaloITSM]
        ↓
[Get Ticket - HaloITSM]
        ↓
[Extract Investigation RRN from Custom Fields]
        ↓
[Decision: Is Status "Resolved"?]
        ↓ YES
[Set Status of Investigation - InsightIDR]
   status: CLOSED
        ↓
[Add Comment - HaloITSM]
   "Investigation closed in InsightIDR"
```

### InsightIDR → HaloITSM (Status Update)

```
[Get New Investigations Trigger]
   search: [{"field": "status", "operator": "EQUALS", "value": "CLOSED"}]
        ↓
[Search Tickets - HaloITSM]
   filter by custom field: Investigation RRN
        ↓
[Decision: Ticket Found?]
        ↓ YES
[Update Ticket - HaloITSM]
   status_id: 4  # Resolved
        ↓
[Add Comment - HaloITSM]
   "Investigation closed in InsightIDR"
```

---

## Status Mapping Reference

### InsightIDR → HaloITSM Status

| InsightIDR Status | HaloITSM Status ID | HaloITSM Status Name |
|-------------------|-------------------|---------------------|
| OPEN              | 1                 | New                 |
| INVESTIGATING     | 2                 | In Progress         |
| WAITING           | 3                 | On Hold             |
| CLOSED            | 4                 | Resolved            |

### InsightIDR → HaloITSM Priority

| InsightIDR Priority | HaloITSM Priority ID | HaloITSM Priority Name |
|---------------------|---------------------|----------------------|
| CRITICAL            | 1                   | Critical             |
| HIGH                | 2                   | High                 |
| MEDIUM              | 3                   | Medium               |
| LOW                 | 4                   | Low                  |
| UNKNOWN             | 4                   | Low (default)        |

### InsightIDR Disposition Values

- `BENIGN` - No threat detected
- `MALICIOUS` - Confirmed security incident
- `FALSE_POSITIVE` - Incorrectly flagged as threat
- `NOT_APPLICABLE` - Does not apply to environment
- `SECURITY_TEST` - Authorized security testing
- `UNDECIDED` - Under investigation
- `UNKNOWN` - Cannot determine

---

## Testing Checklist

### Phase 1: Basic Ticket Creation
- [ ] Workflow triggers on new investigation
- [ ] Ticket created in HaloITSM with investigation title
- [ ] Investigation RRN stored in custom field
- [ ] Priority correctly mapped
- [ ] Comment added to InsightIDR with ticket link

### Phase 2: Alert Details
- [ ] List Alerts action retrieves alerts successfully
- [ ] Alert details formatted correctly
- [ ] Multiple alerts displayed properly
- [ ] Alert count stored in custom field

### Phase 3: Bidirectional Sync
- [ ] HaloITSM status change updates InsightIDR
- [ ] InsightIDR status change updates HaloITSM
- [ ] Comments added in both systems
- [ ] No duplicate tickets created

---

## Troubleshooting

### Issue: "Loop input is not a valid array" Error
**Cause:** InsightConnect Loop step cannot iterate over complex API response objects.

**Solution:** Use direct array index references instead of Loop:
```
❌ Don't use: Loop over {{["List Alerts for Investigation"].alerts}}
✅ Do use: {{["List Alerts for Investigation"].alerts[0]}}
✅ Do use: {{["List Alerts for Investigation"].alerts[1]}}
✅ Do use: {{["List Alerts for Investigation"].alerts[2]}}
```

### Issue: Empty Alert Fields in Ticket
**Cause:** Investigation has fewer alerts than array indices referenced.

**Solution:** This is normal behavior. InsightConnect gracefully handles missing array indices by displaying empty values. No error will occur. Consider this:
- Investigation with 3 alerts referencing `alerts[0]` through `alerts[4]` → indices 3 and 4 will be empty
- Add note in template: "(Showing first 5 of {{metadata.total_data}} alerts)"

### Issue: No Alerts Retrieved
**Solution:** Check that investigation has associated alerts. Some manual investigations may have 0 alerts.

### Issue: Ticket Details Too Long
**Solution:** Reduce number of alerts shown. Reference `alerts[0]` through `alerts[2]` instead of `alerts[0]` through `alerts[9]`.

### Issue: Custom Field Not Found
**Solution:** Verify custom field IDs in HaloITSM admin panel. Update workflow with correct IDs.

### Issue: Priority Mapping Incorrect
**Solution:** Check HaloITSM priority IDs. Your system may use different IDs than standard (1-4).

### Issue: Duplicate Tickets Created
**Solution:** Add check before creating ticket:
1. Search for existing ticket with same Investigation RRN
2. Only create if no existing ticket found

### Issue: Template Syntax Errors
**Common mistakes:**
- ❌ `{{["Step Name"].field[0]title}}` - Missing dot before nested field
- ✅ `{{["Step Name"].field[0].title}}` - Correct
- ❌ `{{[Step Name].field}}` - Missing quotes around step name
- ✅ `{{["Step Name"].field}}` - Correct

---

## Advanced: Webhook Configuration

For real-time sync from HaloITSM to InsightIDR, configure webhooks:

1. **HaloITSM Webhook URL:** Your InsightConnect workflow trigger URL
2. **Trigger Events:** Ticket Updated, Status Changed
3. **Payload:** Include ticket ID and custom fields

---

## Next Steps

1. **Deploy HaloITSM Plugin v2.0.20** (includes webhook triggers and agent email support)
2. **Create custom fields in HaloITSM** (Investigation RRN, Priority, Alert Count)
3. **Build Workflow 1** (Investigation → Ticket with alerts)
4. **Test with manual investigation**
5. **Add Workflow 2** (Bidirectional status sync)
6. **Monitor and refine** based on actual usage

---

## Support Resources

- **HaloITSM Plugin Repo:** https://github.com/derricksmith/Rapid7HaloITSM
- **InsightIDR Plugin Docs:** `Rapid7.md`
- **Plugin Version:** v2.0.20
- **InsightConnect FQL Docs:** https://docs.rapid7.com/insightconnect/format-query-language/

---

## Appendix A: Advanced Python Processing (Optional)

If you need complex Python logic (loops, conditionals, string manipulation), you have two options:

### **Option 1: AWS Lambda Function**

1. **Create Lambda Function:**

```python
import json

def lambda_handler(event, context):
    """Format InsightIDR investigation and alerts for HaloITSM"""
    
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event
        investigation = body['investigation']
        alerts = body['alerts']
        alert_count = len(alerts)
        
        # Build formatted details
        lines = [
            "═══════════════════════════════════════════════════════════",
            "RAPID7 INSIGHTIDR INVESTIGATION",
            "═══════════════════════════════════════════════════════════",
            "",
            f"Investigation ID: {investigation.get('rrn', 'N/A')}",
            f"Title: {investigation.get('title', 'N/A')}",
            f"Status: {investigation.get('status', 'N/A')}",
            f"Priority: {investigation.get('priority', 'N/A')}",
            f"Disposition: {investigation.get('disposition', 'UNDECIDED')}",
            "",
            "─────────────────────────────────────────────────────────",
            f"ALERTS ({alert_count} total)",
            "─────────────────────────────────────────────────────────",
            ""
        ]
        
        # Add up to 10 alerts
        for i, alert in enumerate(alerts[:10], 1):
            lines.extend([
                f"Alert #{i}:",
                f"  Title: {alert.get('title', 'N/A')}",
                f"  Type: {alert.get('alert_type', 'N/A')}",
                f"  Created: {alert.get('created_time', 'N/A')}",
                ""
            ])
        
        if alert_count > 10:
            lines.append(f"... and {alert_count - 10} more alerts")
        
        lines.append("═══════════════════════════════════════════════════════════")
        
        formatted_details = "\n".join(lines)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'formatted_details': formatted_details,
                'alert_count': alert_count
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

2. **Deploy Lambda:**
   - Create Lambda function in AWS Console
   - Set runtime to Python 3.9+
   - Create API Gateway trigger (REST API)
   - Note the endpoint URL

3. **Call from InsightConnect:**

**Action:** HTTP Request

**Method:** POST

**URL:** `https://your-lambda-url.amazonaws.com/format`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "investigation": {{["Get New Investigations"].investigation}},
  "alerts": {{["List Alerts for Investigation"].alerts}}
}
```

**Extract from Response:**
```
{{["HTTP Request"].body.formatted_details}}
```

### **Option 2: Azure Function**

Similar to Lambda, create an Azure Function with HTTP trigger:

```python
import logging
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing investigation formatting request')

    try:
        req_body = req.get_json()
        investigation = req_body['investigation']
        alerts = req_body['alerts']
        
        # Format logic (same as Lambda above)
        formatted_details = format_investigation(investigation, alerts)
        
        return func.HttpResponse(
            json.dumps({'formatted_details': formatted_details}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=500
        )

def format_investigation(investigation, alerts):
    # Same formatting logic as Lambda
    pass
```

### **Option 3: Manual Array Expansion (Simplest No-Code Approach)**

Since InsightConnect Loop steps have limitations with complex objects, the **easiest approach is to directly reference array indices** in your template:

**Template for Create Ticket Details:**
```
Investigation: {{["Get New Investigations"].investigation.title}}
Priority: {{["Get New Investigations"].investigation.priority}}
Status: {{["Get New Investigations"].investigation.status}}
Alert Count: {{["List Alerts for Investigation"].metadata.total_data}}

ALERTS:
─────────────────────────────────────────────────────────
1. {{["List Alerts for Investigation"].alerts[0].alert_type}} - {{["List Alerts for Investigation"].alerts[0].title}}
   Created: {{["List Alerts for Investigation"].alerts[0].created_time}}

2. {{["List Alerts for Investigation"].alerts[1].alert_type}} - {{["List Alerts for Investigation"].alerts[1].title}}
   Created: {{["List Alerts for Investigation"].alerts[1].created_time}}

3. {{["List Alerts for Investigation"].alerts[2].alert_type}} - {{["List Alerts for Investigation"].alerts[2].title}}
   Created: {{["List Alerts for Investigation"].alerts[2].created_time}}

4. {{["List Alerts for Investigation"].alerts[3].alert_type}} - {{["List Alerts for Investigation"].alerts[3].title}}
   Created: {{["List Alerts for Investigation"].alerts[3].created_time}}

5. {{["List Alerts for Investigation"].alerts[4].alert_type}} - {{["List Alerts for Investigation"].alerts[4].title}}
   Created: {{["List Alerts for Investigation"].alerts[4].created_time}}

(Showing first 5 alerts - view full investigation in InsightIDR)
```

**Benefits:**
- ✅ No external services needed
- ✅ No loops or complex logic required
- ✅ Works with all InsightConnect versions
- ✅ Shows first 5 alerts (sufficient for most cases)

**Note:** If an investigation has fewer than 5 alerts, the missing alert references will simply be empty (InsightConnect handles missing array indices gracefully).

---

## Appendix B: InsightConnect Template Syntax Reference

### **Accessing Nested Fields:**
```
{{["Step Name"].field.nested_field}}
```

### **Array Access:**
```
{{["Step Name"].array[0]}}           # First item
{{["Step Name"].array[1]}}           # Second item
{{["Step Name"].array[-1]}}          # Last item
```

### **Conditional Display (FQL):**
```
{{if_defined(["Step Name"].optional_field, "Default Value")}}
```

### **String Functions:**
```
{{length(["Step Name"].string_field)}}
```

### **Current Loop Item:**
```
{{$item}}                            # In loop context
{{$item.field_name}}                 # Access field of loop item
```

---

*Last Updated: December 3, 2025*
