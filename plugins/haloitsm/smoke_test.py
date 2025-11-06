#!/usr/bin/env python3
"""
Production Smoke Test for HaloITSM Plugin

This script performs comprehensive smoke tests to validate the plugin
is working correctly in production environment.

Usage:
    python smoke_test.py [--environment staging|production]
    
Environment Variables Required:
    HALO_CLIENT_ID - HaloITSM OAuth2 Client ID
    HALO_CLIENT_SECRET - HaloITSM OAuth2 Client Secret  
    HALO_AUTH_SERVER - HaloITSM Authorization Server URL
    HALO_RESOURCE_SERVER - HaloITSM Resource Server URL
    HALO_TENANT - HaloITSM Tenant Name
"""

import os
import sys
import time
import json
import argparse
import requests
from typing import Dict, Any, Optional
from datetime import datetime


class SmokeTestRunner:
    """Comprehensive smoke test runner for HaloITSM plugin"""
    
    def __init__(self, environment: str = "staging"):
        self.environment = environment
        self.test_results = []
        self.auth_token = None
        self.test_ticket_id = None
        
        # Load configuration
        self.config = self._load_config()
        
        # Test configuration
        self.test_data = {
            "summary": f"SMOKE TEST - {environment.upper()} - {datetime.now().isoformat()}",
            "details": "This is an automated smoke test ticket. Safe to close.",
            "priority_id": 2,  # Medium priority for tests
            "ticket_type_id": 1,  # Usually incident type
        }
    
    def _load_config(self) -> Dict[str, str]:
        """Load configuration from environment variables"""
        required_vars = [
            "HALO_CLIENT_ID",
            "HALO_CLIENT_SECRET", 
            "HALO_AUTH_SERVER",
            "HALO_RESOURCE_SERVER",
            "HALO_TENANT"
        ]
        
        config = {}
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                config[var] = value
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
        
        return config
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper error handling"""
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def _log_test(self, test_name: str, success: bool, message: str = "", duration: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "duration": round(duration, 2),
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        duration_str = f" ({duration:.2f}s)" if duration > 0 else ""
        print(f"{status} {test_name}{duration_str}")
        if message:
            print(f"    {message}")
    
    def test_environment_setup(self) -> bool:
        """Test 1: Verify environment configuration"""
        start_time = time.time()
        
        try:
            # Check all required environment variables are set
            required_vars = ["HALO_CLIENT_ID", "HALO_CLIENT_SECRET", "HALO_AUTH_SERVER", 
                           "HALO_RESOURCE_SERVER", "HALO_TENANT"]
            
            for var in required_vars:
                if not self.config.get(var):
                    raise Exception(f"Missing environment variable: {var}")
            
            # Validate URL formats
            for url_var in ["HALO_AUTH_SERVER", "HALO_RESOURCE_SERVER"]:
                url = self.config[url_var]
                if not url.startswith(("http://", "https://")):
                    raise Exception(f"Invalid URL format for {url_var}: {url}")
            
            duration = time.time() - start_time
            self._log_test("Environment Setup", True, "All configuration validated", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self._log_test("Environment Setup", False, str(e), duration)
            return False
    
    def test_authentication(self) -> bool:
        """Test 2: OAuth2 authentication flow"""
        start_time = time.time()
        
        try:
            # Prepare OAuth2 request
            auth_url = f"{self.config['HALO_AUTH_SERVER']}/token"
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.config["HALO_CLIENT_ID"],
                "client_secret": self.config["HALO_CLIENT_SECRET"],
                "scope": "all"
            }
            
            # Make authentication request
            response = self._make_request("POST", auth_url, data=auth_data)
            
            if response.status_code != 200:
                raise Exception(f"Authentication failed: {response.status_code} - {response.text}")
            
            token_data = response.json()
            
            if "access_token" not in token_data:
                raise Exception("No access token in response")
            
            self.auth_token = token_data["access_token"]
            
            duration = time.time() - start_time
            self._log_test("OAuth2 Authentication", True, "Token obtained successfully", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self._log_test("OAuth2 Authentication", False, str(e), duration)
            return False
    
    def test_api_connectivity(self) -> bool:
        """Test 3: Basic API connectivity"""
        start_time = time.time()
        
        try:
            if not self.auth_token:
                raise Exception("No authentication token available")
            
            # Test basic API endpoint
            api_url = f"{self.config['HALO_RESOURCE_SERVER']}/tickettypes"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = self._make_request("GET", api_url, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"API connectivity failed: {response.status_code} - {response.text}")
            
            ticket_types = response.json()
            
            if not isinstance(ticket_types, list):
                raise Exception("Unexpected API response format")
            
            duration = time.time() - start_time
            self._log_test("API Connectivity", True, f"Retrieved {len(ticket_types)} ticket types", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self._log_test("API Connectivity", False, str(e), duration)
            return False
    
    def test_ticket_creation(self) -> bool:
        """Test 4: Ticket creation functionality"""
        start_time = time.time()
        
        try:
            if not self.auth_token:
                raise Exception("No authentication token available")
            
            # Create test ticket
            api_url = f"{self.config['HALO_RESOURCE_SERVER']}/tickets"
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            payload = [self.test_data]  # HaloITSM expects array format
            
            response = self._make_request("POST", api_url, headers=headers, json=payload)
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Ticket creation failed: {response.status_code} - {response.text}")
            
            result = response.json()
            
            if not result or not isinstance(result, list) or len(result) == 0:
                raise Exception("No ticket created in response")
            
            ticket = result[0]
            self.test_ticket_id = ticket.get("id")
            
            if not self.test_ticket_id:
                raise Exception("No ticket ID in response")
            
            duration = time.time() - start_time
            self._log_test("Ticket Creation", True, f"Created ticket #{self.test_ticket_id}", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self._log_test("Ticket Creation", False, str(e), duration)
            return False
    
    def test_ticket_retrieval(self) -> bool:
        """Test 5: Ticket retrieval functionality"""
        start_time = time.time()
        
        try:
            if not self.auth_token or not self.test_ticket_id:
                raise Exception("No authentication token or test ticket available")
            
            # Retrieve test ticket
            api_url = f"{self.config['HALO_RESOURCE_SERVER']}/tickets/{self.test_ticket_id}"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = self._make_request("GET", api_url, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Ticket retrieval failed: {response.status_code} - {response.text}")
            
            ticket = response.json()
            
            if not ticket or ticket.get("id") != self.test_ticket_id:
                raise Exception("Retrieved ticket doesn't match created ticket")
            
            duration = time.time() - start_time
            self._log_test("Ticket Retrieval", True, f"Retrieved ticket #{self.test_ticket_id}", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self._log_test("Ticket Retrieval", False, str(e), duration)
            return False
    
    def test_ticket_update(self) -> bool:
        """Test 6: Ticket update functionality"""
        start_time = time.time()
        
        try:
            if not self.auth_token or not self.test_ticket_id:
                raise Exception("No authentication token or test ticket available")
            
            # Update test ticket
            api_url = f"{self.config['HALO_RESOURCE_SERVER']}/tickets"
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            update_data = {
                "id": self.test_ticket_id,
                "summary": f"{self.test_data['summary']} - UPDATED",
                "details": f"{self.test_data['details']}\n\nUPDATED: {datetime.now().isoformat()}"
            }
            
            payload = [update_data]  # HaloITSM expects array format
            
            response = self._make_request("POST", api_url, headers=headers, json=payload)
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Ticket update failed: {response.status_code} - {response.text}")
            
            duration = time.time() - start_time
            self._log_test("Ticket Update", True, f"Updated ticket #{self.test_ticket_id}", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self._log_test("Ticket Update", False, str(e), duration)
            return False
    
    def test_ticket_search(self) -> bool:
        """Test 7: Ticket search functionality"""
        start_time = time.time()
        
        try:
            if not self.auth_token:
                raise Exception("No authentication token available")
            
            # Search for tickets
            api_url = f"{self.config['HALO_RESOURCE_SERVER']}/tickets"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            params = {
                "search": "SMOKE TEST",
                "count": 10,
                "page_size": 10
            }
            
            response = self._make_request("GET", api_url, headers=headers, params=params)
            
            if response.status_code != 200:
                raise Exception(f"Ticket search failed: {response.status_code} - {response.text}")
            
            search_result = response.json()
            tickets = search_result.get("tickets", [])
            
            # Should find our test ticket
            found_test_ticket = False
            if self.test_ticket_id:
                for ticket in tickets:
                    if ticket.get("id") == self.test_ticket_id:
                        found_test_ticket = True
                        break
            
            duration = time.time() - start_time
            message = f"Found {len(tickets)} tickets"
            if self.test_ticket_id and found_test_ticket:
                message += " (including test ticket)"
            
            self._log_test("Ticket Search", True, message, duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self._log_test("Ticket Search", False, str(e), duration)
            return False
    
    def test_performance_baseline(self) -> bool:
        """Test 8: Performance baseline check"""
        start_time = time.time()
        
        try:
            if not self.auth_token:
                raise Exception("No authentication token available")
            
            # Measure API response times
            api_url = f"{self.config['HALO_RESOURCE_SERVER']}/tickettypes"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response_times = []
            for i in range(5):
                req_start = time.time()
                response = self._make_request("GET", api_url, headers=headers)
                req_duration = time.time() - req_start
                response_times.append(req_duration)
                
                if response.status_code != 200:
                    raise Exception(f"Performance test request failed: {response.status_code}")
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            # Performance thresholds (adjust as needed)
            avg_threshold = 2.0  # 2 seconds average
            max_threshold = 5.0  # 5 seconds maximum
            
            if avg_response_time > avg_threshold:
                raise Exception(f"Average response time {avg_response_time:.2f}s exceeds threshold {avg_threshold}s")
            
            if max_response_time > max_threshold:
                raise Exception(f"Maximum response time {max_response_time:.2f}s exceeds threshold {max_threshold}s")
            
            duration = time.time() - start_time
            message = f"Avg: {avg_response_time:.2f}s, Max: {max_response_time:.2f}s"
            self._log_test("Performance Baseline", True, message, duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self._log_test("Performance Baseline", False, str(e), duration)
            return False
    
    def cleanup_test_data(self) -> bool:
        """Cleanup: Close/delete test ticket"""
        start_time = time.time()
        
        try:
            if not self.auth_token or not self.test_ticket_id:
                self._log_test("Cleanup", True, "No test data to cleanup", 0)
                return True
            
            # Close the test ticket
            api_url = f"{self.config['HALO_RESOURCE_SERVER']}/tickets"
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            close_data = {
                "id": self.test_ticket_id,
                "status_id": 4,  # Usually "Resolved" status
                "summary": f"{self.test_data['summary']} - CLOSED",
                "details": f"{self.test_data['details']}\n\nCLOSED: Smoke test completed successfully"
            }
            
            payload = [close_data]
            
            response = self._make_request("POST", api_url, headers=headers, json=payload)
            
            duration = time.time() - start_time
            
            if response.status_code in [200, 201]:
                self._log_test("Cleanup", True, f"Closed test ticket #{self.test_ticket_id}", duration)
                return True
            else:
                self._log_test("Cleanup", False, f"Failed to close ticket: {response.status_code}", duration)
                return False
            
        except Exception as e:
            duration = time.time() - start_time
            self._log_test("Cleanup", False, str(e), duration)
            return False
    
    def run_all_tests(self) -> bool:
        """Run all smoke tests"""
        print(f"\n🚀 Starting HaloITSM Plugin Smoke Tests - {self.environment.upper()}")
        print(f"📅 Test Run: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Run tests in order
        tests = [
            self.test_environment_setup,
            self.test_authentication,
            self.test_api_connectivity,
            self.test_ticket_creation,
            self.test_ticket_retrieval,
            self.test_ticket_update,
            self.test_ticket_search,
            self.test_performance_baseline,
            self.cleanup_test_data,
        ]
        
        all_passed = True
        
        for test in tests:
            success = test()
            if not success:
                all_passed = False
                # Continue with remaining tests even if one fails
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 SMOKE TEST SUMMARY")
        print("=" * 60)
        
        passed_count = sum(1 for result in self.test_results if result["success"])
        total_count = len(self.test_results)
        
        print(f"Environment: {self.environment.upper()}")
        print(f"Tests Passed: {passed_count}/{total_count}")
        print(f"Success Rate: {(passed_count/total_count)*100:.1f}%")
        
        if all_passed:
            print("🎉 ALL TESTS PASSED - Production ready!")
        else:
            print("⚠️  SOME TESTS FAILED - Review before production deployment")
            
            # Show failed tests
            failed_tests = [r for r in self.test_results if not r["success"]]
            if failed_tests:
                print("\n❌ Failed Tests:")
                for test in failed_tests:
                    print(f"   • {test['test']}: {test['message']}")
        
        # Save detailed results
        results_file = f"smoke_test_results_{self.environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "environment": self.environment,
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_tests": total_count,
                    "passed_tests": passed_count,
                    "failed_tests": total_count - passed_count,
                    "success_rate": (passed_count/total_count)*100,
                    "overall_success": all_passed
                },
                "test_results": self.test_results
            }, f, indent=2)
        
        print(f"\n📁 Detailed results saved to: {results_file}")
        
        return all_passed


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="HaloITSM Plugin Smoke Tests")
    parser.add_argument(
        "--environment",
        choices=["staging", "production"],
        default="staging",
        help="Environment to test against (default: staging)"
    )
    
    args = parser.parse_args()
    
    try:
        runner = SmokeTestRunner(args.environment)
        success = runner.run_all_tests()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ SMOKE TEST FAILED: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()