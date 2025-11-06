# Example HaloITSM Connection Configuration

## Basic Configuration
```yaml
connection_name: "HaloITSM Production"
client_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
client_secret: "9z8y7x6w5v4u3t2s1r0q"
authorization_server: "https://yourcompany.haloitsm.com/auth"
resource_server: "https://yourcompany.haloitsm.com/api"
tenant: "yourcompany"
ssl_verify: true
```

## Enhanced Configuration with Defaults
```yaml
connection_name: "HaloITSM Security Team"
client_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
client_secret: "9z8y7x6w5v4u3t2s1r0q"
authorization_server: "https://yourcompany.haloitsm.com/auth"
resource_server: "https://yourcompany.haloitsm.com/api"
tenant: "yourcompany"
ssl_verify: true

# Default ticket configuration
default_ticket_type_id: 1         # Incident
default_priority_id: 3            # High priority for security issues
default_team_id: 15               # Security Operations Team
default_agent_id: 42              # Security Manager
default_category_id: 8            # Cybersecurity category
```

## Ticket Type Configuration Examples

### Common Ticket Types (configure based on your HaloITSM setup):
- **1** - Incident
- **2** - Service Request  
- **3** - Problem
- **4** - Change Request
- **5** - Project Task

### Priority Levels:
- **1** - Low
- **2** - Medium
- **3** - High
- **4** - Critical

### Usage Examples:

#### 1. Security Incident Response
```yaml
default_ticket_type_id: 1    # Incident
default_priority_id: 4       # Critical
default_team_id: 15          # SOC Team
default_category_id: 8       # Cybersecurity
```

#### 2. Vulnerability Management
```yaml
default_ticket_type_id: 2    # Service Request
default_priority_id: 3       # High
default_team_id: 22          # Vulnerability Management Team
default_category_id: 9       # Vulnerability Remediation
```

#### 3. Compliance Requests
```yaml
default_ticket_type_id: 2    # Service Request
default_priority_id: 2       # Medium
default_team_id: 18          # Compliance Team
default_category_id: 12      # Compliance
```

## Workflow Usage

### Option 1: Use Connection Defaults
```python
# Ticket will use all connection defaults
action: create_ticket
inputs:
  summary: "Security Alert: Suspicious Login Activity"
  details: "Multiple failed login attempts detected..."
  # No other fields needed - uses connection defaults
```

### Option 2: Override Specific Fields
```python
# Override priority for this specific ticket
action: create_ticket
inputs:
  summary: "Low Priority Security Notice"
  details: "Minor configuration drift detected..."
  priority_id: 1  # Override to Low priority
  # Other fields use connection defaults
```

### Option 3: Full Override
```python
# Specify all fields explicitly
action: create_ticket
inputs:
  summary: "Emergency Security Incident"
  details: "Active data breach detected..."
  tickettype_id: 1     # Incident
  priority_id: 4       # Critical
  team_id: 15          # Emergency Response Team
  agent_id: 100        # Security Director
  category_id: 8       # Cybersecurity
```

## Benefits

1. **Consistency**: All security tickets automatically get appropriate type/priority
2. **Reduced Configuration**: Workflows don't need to specify common values
3. **Flexibility**: Can still override defaults when needed
4. **Centralized Management**: Change defaults in one place
5. **Team-Specific**: Different connections for different teams/use cases