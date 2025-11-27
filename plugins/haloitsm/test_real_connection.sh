#!/bin/bash
# Test connection with real HaloITSM credentials
# Usage: ./test_real_connection.sh

echo "Testing HaloITSM Plugin Connection"
echo "==================================="
echo ""
echo "Please provide your HaloITSM credentials:"
echo ""

read -p "Client ID: " CLIENT_ID
read -sp "Client Secret: " CLIENT_SECRET
echo ""
read -p "Authorization Server (e.g., https://yourcompany.haloitsm.com/auth): " AUTH_SERVER
read -p "Resource Server (e.g., https://yourcompany.haloitsm.com/api): " RESOURCE_SERVER
read -p "Tenant (e.g., yourcompany): " TENANT

# Create test JSON
cat > /tmp/test_real_connection.json << EOF
{
  "body": {
    "connection": {
      "client_id": "$CLIENT_ID",
      "client_secret": {
        "secretKey": "$CLIENT_SECRET"
      },
      "authorization_server": "$AUTH_SERVER",
      "resource_server": "$RESOURCE_SERVER",
      "tenant": "$TENANT",
      "ssl_verify": true
    }
  },
  "type": "connection_test",
  "version": "v1"
}
EOF

echo ""
echo "Testing connection..."
echo ""

# Run the test
sudo docker run --rm -i derricksmith/haloitsm:2.0.2 test < /tmp/test_real_connection.json 2>&1

# Cleanup
rm -f /tmp/test_real_connection.json

echo ""
echo "Test complete."
