# Testing HaloITSM Connection Locally

## Quick Start

### 1. Set Environment Variables

```bash
# Required credentials
export HALO_CLIENT_ID="your-client-id-here"
export HALO_CLIENT_SECRET="your-client-secret-here"
export HALO_AUTH_SERVER="https://your-tenant.haloitsm.com/auth"
export HALO_RESOURCE_SERVER="https://your-tenant.haloitsm.com/api"
export HALO_TENANT="your-tenant-name"

# Optional (defaults)
export HALO_SSL_VERIFY="true"
export HALO_DEFAULT_TICKET_TYPE_ID="1"
export HALO_DEFAULT_PRIORITY_ID="3"
```

### 2. Run Connection Test

```bash
cd /media/derrick/0011-8D39/Derrick/Code/Rapid7HaloITSM/plugins/haloitsm

# Activate virtual environment
source ~/rapid7-haloitsm-venv/bin/activate

# Run test
python test_connection.py
```

## What the Test Does

The script will:
1. ✅ Validate environment variables
2. ✅ Initialize connection object
3. ✅ Connect to HaloITSM
4. ✅ Test OAuth2 authentication (get token)
5. ✅ Test API access (retrieve tickets)
6. ✅ Run full connection test

## Expected Output

```
============================================================
HaloITSM Plugin Connection Test
============================================================

Connection Parameters:
  Auth Server: https://example.haloitsm.com/auth
  Resource Server: https://example.haloitsm.com/api
  Tenant: example
  Client ID: a1b2c3d4e5...
  SSL Verify: True

============================================================
Step 1: Initializing connection...
============================================================
✓ Connection object created

============================================================
Step 2: Connecting to HaloITSM...
============================================================
✓ Connected successfully

============================================================
Step 3: Testing OAuth2 authentication...
============================================================
✓ OAuth2 token obtained: eyJ0eXAiOiJKV1QiLC...

============================================================
Step 4: Testing API access...
============================================================
✓ API call successful
  Response type: <class 'list'>
  Retrieved 1 ticket(s)

============================================================
Step 5: Running connection test...
============================================================
✓ Connection test PASSED

============================================================
✅ ALL TESTS PASSED - Connection is working!
============================================================
```

## Troubleshooting

### Authentication Failures

**Error**: `OAuth2 authentication failed: 401 Unauthorized`

**Solutions**:
1. Verify Client ID and Secret are correct
2. Check if credentials have expired
3. Verify OAuth2 scope permissions in HaloITSM admin panel

**Example**:
```bash
# Test OAuth2 endpoint directly
curl -X POST "https://your-tenant.haloitsm.com/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_ID&client_secret=YOUR_SECRET&scope=all"
```

### API Access Failures

**Error**: `API call failed: 403 Forbidden`

**Solutions**:
1. Check API permissions for the OAuth2 client
2. Verify the resource server URL is correct
3. Ensure the client has access to the tickets endpoint

### SSL Certificate Issues

**Error**: `SSL certificate verification failed`

**Solution**:
```bash
# Temporarily disable SSL verification for testing
export HALO_SSL_VERIFY="false"

# Re-run test
python test_connection.py
```

⚠️ **Note**: Only disable SSL verification for testing. Enable it for production.

### Connection Timeout

**Error**: `Connection timeout`

**Solutions**:
1. Check firewall rules - ensure InsightConnect can reach HaloITSM
2. Verify URLs are accessible: `curl https://your-tenant.haloitsm.com/api/tickets`
3. Check if HaloITSM instance is running

## Manual API Testing

Test the HaloITSM API directly:

```bash
# Get OAuth2 token
TOKEN=$(curl -s -X POST "https://your-tenant.haloitsm.com/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=$HALO_CLIENT_ID&client_secret=$HALO_CLIENT_SECRET&scope=all" \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# Test API access
curl -X GET "https://your-tenant.haloitsm.com/api/tickets?count=1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Common Issues in InsightConnect

If the test passes locally but fails in InsightConnect:

1. **Network/Firewall**: InsightConnect runs in Rapid7's cloud - ensure HaloITSM allows connections from Rapid7 IP ranges
2. **URL Format**: Double-check authorization_server and resource_server URLs in the connection config
3. **SSL Certificates**: If using self-signed certificates, they may be rejected by InsightConnect

## Next Steps

Once the local test passes:
1. ✅ Upload plugin to InsightConnect
2. ✅ Create connection with same credentials
3. ✅ Test connection in InsightConnect UI
4. ✅ Create test workflow using an action

---

**Created**: November 26, 2025  
**Test Script**: `test_connection.py`
