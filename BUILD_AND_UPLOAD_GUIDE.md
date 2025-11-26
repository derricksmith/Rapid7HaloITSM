# Build and Upload Guide - HaloITSM Plugin

## Quick Start (5 Steps to Production)

This guide walks you through building and uploading your plugin to Rapid7 InsightConnect.

---

## Prerequisites

### Required Software
```bash
# 1. Python 3.9 or higher
python3 --version

# 2. pip (Python package manager)
pip --version

# 3. Rapid7 InsightConnect Plugin Runtime
pip install insightconnect-plugin-runtime
```

### Required Access
- [ ] Rapid7 InsightConnect account with admin privileges
- [ ] HaloITSM instance with API access
- [ ] HaloITSM OAuth2 Client ID and Secret

---

## Step 1: Install Dependencies

**Note**: If your project is on an external drive, Python virtual environments must be created in your home directory to support symlinks.

```bash
# Create virtual environment in home directory
python3 -m venv ~/rapid7-haloitsm-venv

# Activate virtual environment
source ~/rapid7-haloitsm-venv/bin/activate

# Install plugin dependencies
cd /media/derrick/0011-8D39/Derrick/Code/Rapid7HaloITSM/plugins/haloitsm
pip install -r requirements.txt

# Install development tools
pip install pytest
```

**Expected Output:**
```
Installing plugin dependencies...
Successfully installed insightconnect-plugin-runtime-6.x.x requests-2.x.x
```

**Important**: Always activate the virtual environment before building:
```bash
source ~/rapid7-haloitsm-venv/bin/activate
```

---

## Step 2: Build the Plugin

We use a custom build script to create the `.plg` file:

```bash
# Ensure virtual environment is activated
source ~/rapid7-haloitsm-venv/bin/activate

# Navigate to plugin directory
cd /media/derrick/0011-8D39/Derrick/Code/Rapid7HaloITSM/plugins/haloitsm

# Build plugin
python build_plugin.py
```

**Expected Output:**
```
Building haloitsm v1.0.0...
  ✓ Added plugin.spec.yaml
  ✓ Added setup.py
  ✓ Added help.md
  ✓ Added komand_haloitsm Python files
  
✅ Plugin built successfully!
   Output: haloitsm-1.0.0.plg
   Size: 33.4 KB
```

**The .plg file will be created in:**
```
/media/derrick/0011-8D39/Derrick/Code/Rapid7HaloITSM/plugins/haloitsm/haloitsm-1.0.0.plg
```

---

## Step 3: Upload to Rapid7 InsightConnect

### Option A: Via Web UI (Recommended for First Upload)

1. **Login to InsightConnect**
   - Navigate to: `https://us.insight.rapid7.com/` (or your region)
   - Login with your credentials

2. **Navigate to Plugins**
   - Click on **Settings** (gear icon, bottom left)
   - Select **Plugins & Tools**

3. **Import Plugin**
   - Click **"Import"** button (top right)
   - Select **"From Local Drive"**
   - Browse and select: `plugins/haloitsm/haloitsm-1.0.0.plg`
   - Click **"Upload"**

4. **Verify Upload**
   - You should see "HaloITSM" in your plugins list
   - Status should show as "Active"
   - Version should match your plugin version

### Option B: Via API (For Automation)

```bash
# Set your API key
export INSIGHT_API_KEY="your-api-key-here"
export INSIGHT_REGION="us"  # or eu, ca, au, ap

# Upload plugin
curl -X POST \
  "https://${INSIGHT_REGION}.api.insight.rapid7.com/connect/v1/plugins" \
  -H "X-Api-Key: ${INSIGHT_API_KEY}" \
  -H "Content-Type: multipart/form-data" \
  -F "plugin=@plugins/haloitsm/haloitsm-1.0.0.plg"
```

---

## Step 4: Configure Connection

After uploading, create a connection to HaloITSM:

1. **Create New Connection**
   - In InsightConnect, go to **Connections**
   - Click **"New Connection"**
   - Search for "HaloITSM"
   - Click **"Create Connection"**

2. **Enter Connection Details**
   ```yaml
   Connection Name: HaloITSM Production
   
   Client ID: your-halo-client-id
   Client Secret: your-halo-client-secret
   Authorization Server: https://your-tenant.haloitsm.com/auth
   Resource Server: https://your-tenant.haloitsm.com/api
   Tenant: your-tenant-name
   SSL Verify: true (recommended for production)
   ```

3. **Test Connection**
   - Click **"Test Connection"**
   - Should show: ✓ "Connection successful"

4. **Save Connection**
   - Click **"Save"**
   - Connection is now ready to use in workflows

---

## Verification & Testing

### Test the Plugin

Create a simple test workflow:

1. **Create New Workflow**
   - Go to **Workflows** → **New Workflow**
   - Name: "HaloITSM Test"

2. **Add Manual Trigger**
   - Trigger Type: Manual

3. **Add Create Ticket Action**
   - Search for "HaloITSM"
   - Select "Create Ticket"
   - Configure:
     ```yaml
     Summary: Test Ticket from InsightConnect
     Details: Testing HaloITSM plugin integration
     Ticket Type ID: 1
     Priority ID: 3
     ```

4. **Run Workflow**
   - Click **"Run"**
   - Check execution logs
   - Verify ticket created in HaloITSM

---

## Troubleshooting

### Common Issues

#### 1. "Plugin validation failed"
```bash
# Check plugin.spec.yaml syntax
cd plugins/haloitsm
insight-plugin validate --verbose
```

#### 2. "insightconnect-plugin-runtime not found"
```bash
# Install the runtime
pip install insightconnect-plugin-runtime

# Verify installation
pip show insightconnect-plugin-runtime
```

#### 3. "Connection test failed"
- **Check OAuth credentials**: Verify Client ID/Secret in HaloITSM
- **Check URLs**: Ensure authorization/resource server URLs are correct
- **Check network**: Verify InsightConnect can reach HaloITSM (firewall rules)
- **Check SSL**: Try with SSL verify disabled for testing (not recommended for production)

#### 4. "Cannot upload plugin"
- **File size**: Ensure .plg file is under 50MB
- **Permissions**: Verify you have admin rights in InsightConnect
- **Browser**: Try different browser or clear cache
- **API**: Use API upload method as fallback

#### 5. "Action execution failed"
- **Check logs**: View workflow execution logs in InsightConnect
- **Check connection**: Ensure connection is active and tested
- **Check inputs**: Verify all required inputs are provided
- **Check HaloITSM**: Verify ticket type ID, priority ID exist in HaloITSM

---

## Complete Build Commands (All-in-One)

For convenience, here's the complete sequence:

```bash
# Navigate to project
cd /media/derrick/0011-8D39/Derrick/Code/Rapid7HaloITSM

# Install dependencies
make install

# Run tests (optional but recommended)
make test

# Validate plugin
make validate

# Build and export
make export

# The plugin is now ready at:
# plugins/haloitsm/haloitsm-1.0.0.plg
```

---

## Production Deployment Checklist

Before deploying to production:

- [ ] All tests pass (`make test`)
- [ ] Plugin validation passes (`make validate`)
- [ ] Connection tested successfully
- [ ] Test workflow created and executed
- [ ] Documentation reviewed
- [ ] OAuth credentials secured (stored in vault, not plain text)
- [ ] SSL verification enabled
- [ ] Monitoring configured
- [ ] Team trained on plugin usage

---

## Next Steps

After successful upload:

1. **Configure Webhooks** (for triggers)
   - See `CONFIGURATION.md` for webhook setup
   - Configure in HaloITSM admin panel

2. **Create Workflows**
   - InsightIDR investigation → HaloITSM ticket
   - HaloITSM ticket update → InsightIDR status sync
   - InsightVM remediation → HaloITSM ticketing

3. **Monitor Usage**
   - Review workflow execution logs
   - Monitor API rate limits
   - Track ticket creation/update success rates

4. **Review Documentation**
   - `PRODUCTION.md` - Complete production guide
   - `CONFIGURATION.md` - Advanced configuration
   - `README.md` - Plugin overview

---

## Support

If you encounter issues:

1. **Check logs**: InsightConnect → Workflows → Executions → View Logs
2. **Review documentation**: `PRODUCTION.md`, `CONFIGURATION.md`
3. **Test connection**: Settings → Connections → Test
4. **Contact support**: Rapid7 support or HaloITSM support

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `make install` | Install dependencies |
| `make validate` | Validate plugin spec |
| `make test` | Run unit tests |
| `make export` | Build .plg file |
| `make package` | Create release package |
| `make quality-gate` | Run all checks |

---

**Version**: 1.0.0  
**Last Updated**: November 26, 2025  
**Plugin File**: `plugins/haloitsm/haloitsm-1.0.0.plg`
