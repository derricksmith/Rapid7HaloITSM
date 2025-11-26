#!/usr/bin/env python3
"""
Test HaloITSM plugin connection from development environment

Usage:
    python test_connection.py

Set environment variables:
    export HALO_CLIENT_ID="your-client-id"
    export HALO_CLIENT_SECRET="your-client-secret"
    export HALO_AUTH_SERVER="https://example.haloitsm.com/auth"
    export HALO_RESOURCE_SERVER="https://example.haloitsm.com/api"
    export HALO_TENANT="example"
"""

import os
import sys
import json
import logging

# Add plugin to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from komand_haloitsm.connection.connection import Connection
from komand_haloitsm.connection.schema import Input

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_connection_params():
    """Get connection parameters from environment variables"""
    params = {
        Input.CLIENT_ID: {
            "secretKey": os.getenv("HALO_CLIENT_ID")
        },
        Input.CLIENT_SECRET: {
            "secretKey": os.getenv("HALO_CLIENT_SECRET")
        },
        Input.AUTHORIZATION_SERVER: os.getenv("HALO_AUTH_SERVER"),
        Input.RESOURCE_SERVER: os.getenv("HALO_RESOURCE_SERVER"),
        Input.TENANT: os.getenv("HALO_TENANT"),
        Input.SSL_VERIFY: os.getenv("HALO_SSL_VERIFY", "true").lower() == "true"
    }
    
    # Optional defaults
    if os.getenv("HALO_DEFAULT_TICKET_TYPE_ID"):
        params[Input.DEFAULT_TICKET_TYPE_ID] = int(os.getenv("HALO_DEFAULT_TICKET_TYPE_ID"))
    if os.getenv("HALO_DEFAULT_PRIORITY_ID"):
        params[Input.DEFAULT_PRIORITY_ID] = int(os.getenv("HALO_DEFAULT_PRIORITY_ID"))
    
    return params

def validate_env_vars():
    """Check if required environment variables are set"""
    required = [
        "HALO_CLIENT_ID",
        "HALO_CLIENT_SECRET", 
        "HALO_AUTH_SERVER",
        "HALO_RESOURCE_SERVER",
        "HALO_TENANT"
    ]
    
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.info("\nSet the following environment variables:")
        logger.info("  export HALO_CLIENT_ID='your-client-id'")
        logger.info("  export HALO_CLIENT_SECRET='your-client-secret'")
        logger.info("  export HALO_AUTH_SERVER='https://example.haloitsm.com/auth'")
        logger.info("  export HALO_RESOURCE_SERVER='https://example.haloitsm.com/api'")
        logger.info("  export HALO_TENANT='example'")
        return False
    
    return True

def test_connection():
    """Test the HaloITSM connection"""
    logger.info("=" * 60)
    logger.info("HaloITSM Plugin Connection Test")
    logger.info("=" * 60)
    
    # Validate environment
    if not validate_env_vars():
        return False
    
    # Get connection params
    params = get_connection_params()
    
    logger.info("\nConnection Parameters:")
    logger.info(f"  Auth Server: {params[Input.AUTHORIZATION_SERVER]}")
    logger.info(f"  Resource Server: {params[Input.RESOURCE_SERVER]}")
    logger.info(f"  Tenant: {params[Input.TENANT]}")
    logger.info(f"  Client ID: {params[Input.CLIENT_ID]['secretKey'][:10]}...")
    logger.info(f"  SSL Verify: {params[Input.SSL_VERIFY]}")
    
    # Initialize connection
    logger.info("\n" + "=" * 60)
    logger.info("Step 1: Initializing connection...")
    logger.info("=" * 60)
    
    try:
        conn = Connection()
        conn.logger = logger
        logger.info("✓ Connection object created")
    except Exception as e:
        logger.error(f"✗ Failed to create connection: {e}")
        return False
    
    # Connect
    logger.info("\n" + "=" * 60)
    logger.info("Step 2: Connecting to HaloITSM...")
    logger.info("=" * 60)
    
    try:
        conn.connect(params)
        logger.info("✓ Connected successfully")
    except Exception as e:
        logger.error(f"✗ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test OAuth2 token
    logger.info("\n" + "=" * 60)
    logger.info("Step 3: Testing OAuth2 authentication...")
    logger.info("=" * 60)
    
    try:
        token = conn.client.get_access_token()
        logger.info(f"✓ OAuth2 token obtained: {token[:20]}...")
    except Exception as e:
        logger.error(f"✗ OAuth2 authentication failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test API call
    logger.info("\n" + "=" * 60)
    logger.info("Step 4: Testing API access...")
    logger.info("=" * 60)
    
    try:
        response = conn.client.make_request(
            method="GET",
            endpoint="/tickets",
            params={"count": 1}
        )
        logger.info(f"✓ API call successful")
        logger.info(f"  Response type: {type(response)}")
        if isinstance(response, list) and response:
            logger.info(f"  Retrieved {len(response)} ticket(s)")
        elif isinstance(response, dict):
            logger.info(f"  Response keys: {list(response.keys())}")
    except Exception as e:
        logger.error(f"✗ API call failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Run connection test
    logger.info("\n" + "=" * 60)
    logger.info("Step 5: Running connection test...")
    logger.info("=" * 60)
    
    try:
        result = conn.test()
        if result.get("success"):
            logger.info("✓ Connection test PASSED")
            logger.info("\n" + "=" * 60)
            logger.info("✅ ALL TESTS PASSED - Connection is working!")
            logger.info("=" * 60)
            return True
        else:
            logger.error("✗ Connection test failed")
            return False
    except Exception as e:
        logger.error(f"✗ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
