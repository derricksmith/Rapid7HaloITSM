# Plugin Upload Troubleshooting

## Issue: "Network Error" on Import

The "Network Error" when importing the plugin (77-90 MB file) is likely due to:

### **Possible Causes:**

1. **File Size Limit**: InsightConnect web UI may have upload size limits (typically 50-100MB)
2. **Timeout**: Large file uploads can timeout on the web interface
3. **Browser Limitations**: Some browsers struggle with large file uploads

### **Solutions:**

#### **Option 1: Use API Upload (Recommended)**

Upload via the InsightConnect API instead of the web UI:

```bash
# Set your API key (get from InsightConnect: Settings → API Keys)
export INSIGHT_API_KEY="your-api-key-here"
export INSIGHT_REGION="us"  # or eu, ca, au, ap

# Upload plugin
curl -X POST \
  "https://${INSIGHT_REGION}.api.insight.rapid7.com/connect/v1/plugins" \
  -H "X-Api-Key: ${INSIGHT_API_KEY}" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@derricksmith_haloitsm_1.0.0.plg" \
  --max-time 600
```

#### **Option 2: Use Different Browser**

Try uploading with:
- Chrome (usually best for large files)
- Firefox
- Edge

Clear browser cache before attempting.

#### **Option 3: Contact Rapid7 Support**

If the plugin needs to be uploaded manually, contact:
- **Email**: IntegrationAlliance@rapid7.com
- **Support**: Rapid7 Customer Support
- Provide the `.plg` file and request manual installation

#### **Option 4: Reduce Plugin Size (Advanced)**

The Docker image is ~200MB. We could reduce it by:
1. Using alpine-based parent image (smaller base)
2. Removing unnecessary dependencies
3. Using `--platform=linux/amd64` flag

### **Current Plugin Details:**

```
File: derricksmith_haloitsm_1.0.0.plg
Size: 77-90 MB (compressed Docker image)
Docker Image Size: ~200 MB (uncompressed)
Format: Gzipped tar of Docker image (correct format ✅)
```

### **Verification Steps:**

1. **Check API Key Permissions**:
   - Settings → API Keys
   - Ensure key has "Plugin Management" permissions

2. **Check Region**:
   - Verify you're using correct region (us/eu/ca/au/ap)
   - API endpoint must match your InsightConnect instance

3. **Check Network**:
   - Ensure no proxy/firewall blocking large uploads
   - Try from different network if possible

### **Alternative: Build on InsightConnect Server**

Some organizations upload the Dockerfile and build on the server:
1. Contact Rapid7 support
2. Provide plugin source code
3. They build and install server-side

### **Next Steps:**

1. Try API upload first (most reliable for large files)
2. If API fails, check error message for specific issue
3. Contact Rapid7 support if needed with error details

---

**Note**: The plugin build is correct - the issue is upload mechanism, not plugin format.
