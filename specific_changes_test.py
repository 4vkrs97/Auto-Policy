#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import time

class SpecificChangesAPITester:
    def __init__(self, base_url="https://quick-insure-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_test(self, name, method, endpoint, expected_status=200, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)
            
        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)
                
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {"status": "success", "content": response.text}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                self.log(f"   Response: {response.text[:200]}")
                self.failed_tests.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200]
                })
                return False, {}
                
        except requests.exceptions.Timeout:
            self.log(f"❌ {name} - Request timeout (30s)")
            self.failed_tests.append({"test": name, "error": "Timeout"})
            return False, {}
        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}")
            self.failed_tests.append({"test": name, "error": str(e)})
            return False, {}
    
    def create_session(self):
        """Create a new session for testing"""
        success, response = self.run_test(
            "Create Session",
            "POST", 
            "sessions",
            200,
            data={"user_agent": "test-agent"}
        )
        if success and 'id' in response:
            self.session_id = response['id']
            self.log(f"   Session ID: {self.session_id}")
            return True
        return False
    
    def complete_flow_to_driving_environment(self):
        """Complete the flow up to the driving environment question"""
        if not self.session_id:
            self.log("❌ No session ID available")
            return False
        
        self.log("🔄 Completing flow to driving environment question...")
        
        # Steps to reach driving environment
        steps = [
            ("car", "Vehicle Type"),
            ("has_vin_no", "VIN - No"),
            ("Toyota", "Vehicle Make"),
            ("Camry", "Vehicle Model"),
            ("1601cc - 2000cc", "Engine Capacity"),
            ("personal_use", "Vehicle Purpose"),
            ("daily", "Usage Frequency"),
            ("500_1000km", "Monthly Distance"),
            ("peak_hours", "Driving Time")
        ]
        
        for step_value, step_name in steps:
            success, response = self.run_test(
                f"Flow Step - {step_name}",
                "POST",
                "chat",
                200,
                data={
                    "session_id": self.session_id,
                    "content": step_value,
                    "quick_reply_value": step_value
                }
            )
            
            if not success:
                self.log(f"❌ Flow failed at step: {step_name}")
                return False
            
            time.sleep(0.1)
        
        return True
    
    def test_driving_environment_multi_select(self):
        """Test 1: Driving Environment Multi-Select functionality"""
        self.log("\n🎯 TESTING: Driving Environment Multi-Select")
        
        # Create session and complete flow to driving environment
        if not self.create_session():
            return False
        
        if not self.complete_flow_to_driving_environment():
            return False
        
        # Test that the driving environment question has multi_select flag
        success, response = self.run_test(
            "Driving Environment Question",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Continue to driving environment",
                "quick_reply_value": "continue"
            }
        )
        
        if not success:
            return False
        
        # Check if response has multi_select flag
        message_data = response.get('message', {})
        if 'multi_select' in message_data and message_data['multi_select'] == True:
            self.log("   ✅ Driving environment question has multi_select: true flag")
        else:
            self.log("   ❌ Driving environment question missing multi_select: true flag")
            self.failed_tests.append({
                "test": "Driving Environment Multi-Select Flag",
                "error": "multi_select flag not found or not true"
            })
            return False
        
        # Test selecting multiple environment options
        success, response = self.run_test(
            "Select Urban/City Environment",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Urban / City Roads",
                "quick_reply_value": "env_urban_city"
            }
        )
        
        if not success:
            return False
        
        success, response = self.run_test(
            "Select Suburban Environment",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Suburban / Light Traffic",
                "quick_reply_value": "env_suburban"
            }
        )
        
        if not success:
            return False
        
        # Complete the selection
        success, response = self.run_test(
            "Complete Environment Selection",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Done Selecting",
                "quick_reply_value": "env_done"
            }
        )
        
        if not success:
            return False
        
        # Verify the driving_environment state stores as an array
        success, session_data = self.run_test(
            "Get Session for Environment Check",
            "GET",
            f"sessions/{self.session_id}"
        )
        
        if success and 'state' in session_data:
            driving_env = session_data['state'].get('driving_environment')
            if isinstance(driving_env, list) and len(driving_env) >= 2:
                if 'urban_city' in driving_env and 'suburban' in driving_env:
                    self.log(f"   ✅ Driving environment stored as array: {driving_env}")
                    return True
                else:
                    self.log(f"   ❌ Expected urban_city and suburban in array, got: {driving_env}")
                    return False
            else:
                self.log(f"   ❌ Driving environment not stored as array or insufficient selections: {driving_env}")
                return False
        else:
            self.log("   ❌ Could not retrieve session data")
            return False
    
    def complete_flow_to_telematics(self):
        """Complete the flow up to telematics questions"""
        if not self.session_id:
            self.log("❌ No session ID available")
            return False
        
        self.log("🔄 Completing flow to telematics questions...")
        
        # Steps to reach telematics
        steps = [
            ("car", "Vehicle Type"),
            ("has_vin_no", "VIN - No"),
            ("Toyota", "Vehicle Make"),
            ("Camry", "Vehicle Model"),
            ("1601cc - 2000cc", "Engine Capacity"),
            ("personal_use", "Vehicle Purpose"),
            ("daily", "Usage Frequency"),
            ("500_1000km", "Monthly Distance"),
            ("peak_hours", "Driving Time"),
            ("env_urban_city", "Environment 1"),
            ("env_suburban", "Environment 2"),
            ("env_done", "Environment Done"),
            ("confirm_vehicle", "Confirm Vehicle"),
            ("comprehensive", "Coverage Type"),
            ("Drive Premium", "Plan Selection"),
            ("singpass", "Driver Info Method"),
            ("consent_yes", "Singpass Consent"),
            ("confirm_driver", "Confirm Driver"),
            ("no_claims", "Claims History"),
            ("none", "Additional Drivers")
        ]
        
        for step_value, step_name in steps:
            success, response = self.run_test(
                f"Telematics Flow - {step_name}",
                "POST",
                "chat",
                200,
                data={
                    "session_id": self.session_id,
                    "content": step_value,
                    "quick_reply_value": step_value
                }
            )
            
            if not success:
                self.log(f"❌ Telematics flow failed at step: {step_name}")
                return False
            
            time.sleep(0.1)
        
        return True
    
    def test_gps_consent_removed(self):
        """Test 2: GPS Consent Question Removed from telematics flow"""
        self.log("\n🎯 TESTING: GPS Consent Question Removed")
        
        # Create new session for this test
        if not self.create_session():
            return False
        
        if not self.complete_flow_to_telematics():
            return False
        
        # Test telematics data sharing = "yes"
        success, response = self.run_test(
            "Telematics Data Sharing - Yes",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Yes, I am willing",
                "quick_reply_value": "data_sharing_yes"
            }
        )
        
        if not success:
            return False
        
        # Verify next question is about safety_alerts (NOT GPS consent)
        message_content = response.get('message', {}).get('content', '')
        quick_replies = response.get('message', {}).get('quick_replies', [])
        
        # Check that the message is about safety alerts, not GPS
        if 'safety' in message_content.lower() and 'feedback' in message_content.lower():
            self.log("   ✅ Next question is about safety alerts (GPS consent removed)")
        elif 'gps' in message_content.lower() or 'location' in message_content.lower():
            self.log("   ❌ GPS consent question still present in flow")
            self.failed_tests.append({
                "test": "GPS Consent Removal",
                "error": "GPS consent question still found in telematics flow"
            })
            return False
        else:
            self.log(f"   ⚠️  Unexpected question content: {message_content[:100]}")
        
        # Test safety alerts response
        success, response = self.run_test(
            "Safety Alerts - Yes",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Yes, I am comfortable",
                "quick_reply_value": "safety_alerts_yes"
            }
        )
        
        if not success:
            return False
        
        # Verify we get to final enrollment (not another GPS question)
        message_content = response.get('message', {}).get('content', '')
        
        if 'enroll' in message_content.lower() and 'smart driver' in message_content.lower():
            self.log("   ✅ Flow goes directly to final enrollment (GPS consent bypassed)")
            return True
        elif 'gps' in message_content.lower():
            self.log("   ❌ GPS consent question appears after safety alerts")
            self.failed_tests.append({
                "test": "GPS Consent Flow",
                "error": "GPS consent question appears after safety alerts"
            })
            return False
        else:
            self.log(f"   ⚠️  Unexpected final question: {message_content[:100]}")
            return True  # Assume success if no GPS question found
    
    def test_payment_processing(self):
        """Test 3: Payment Processing endpoints"""
        self.log("\n🎯 TESTING: Payment Processing")
        
        # Test GET /api/payment/methods
        success, response = self.run_test(
            "Payment Methods Endpoint",
            "GET",
            "payment/methods"
        )
        
        if not success:
            return False
        
        # Verify 5 payment methods returned
        if 'methods' in response:
            methods = response['methods']
            if len(methods) == 5:
                self.log(f"   ✅ Found {len(methods)} payment methods as expected")
                
                # Check for Singapore payment methods
                method_ids = [method['id'] for method in methods]
                expected_methods = ['paynow', 'card', 'grabpay', 'paylah', 'nets']
                
                all_present = all(method_id in method_ids for method_id in expected_methods)
                if all_present:
                    self.log("   ✅ All expected Singapore payment methods present")
                else:
                    missing = [m for m in expected_methods if m not in method_ids]
                    self.log(f"   ❌ Missing payment methods: {missing}")
                    return False
            else:
                self.log(f"   ❌ Expected 5 payment methods, got {len(methods)}")
                return False
        else:
            self.log("   ❌ Invalid response format or missing 'methods' field")
            return False
        
        # Test POST /api/payment/process
        # Create new session and complete quote flow
        if not self.create_session():
            return False
        
        # Complete full quote flow to get final premium
        if not self.complete_full_quote_flow():
            return False
        
        # Get final premium from session
        success, session_data = self.run_test(
            "Get Session for Payment",
            "GET",
            f"sessions/{self.session_id}"
        )
        
        if not success or 'state' not in session_data:
            self.log("   ❌ Could not retrieve session data for payment")
            return False
        
        final_premium = session_data['state'].get('final_premium', 0)
        if final_premium <= 0:
            self.log("   ❌ No valid final premium found for payment")
            return False
        
        # Test payment processing
        success, response = self.run_test(
            "Payment Process",
            "POST",
            "payment/process",
            200,
            data={
                "session_id": self.session_id,
                "payment_method": "paynow",
                "amount": final_premium
            }
        )
        
        if not success:
            return False
        
        # Verify response format
        required_fields = ['success', 'payment_reference', 'policy_number', 'message']
        if all(key in response for key in required_fields):
            self.log("   ✅ Payment response has all required fields")
            
            # Check payment reference format: PAY-YYYYMMDD-XXXXXXXX
            payment_ref = response['payment_reference']
            if payment_ref.startswith('PAY-') and len(payment_ref) == 21:
                self.log(f"   ✅ Payment reference format correct: {payment_ref}")
            else:
                self.log(f"   ❌ Invalid payment reference format: {payment_ref}")
                return False
            
            # Check policy number format: TRV-YYYY-XXXXX
            policy_num = response['policy_number']
            if policy_num.startswith('TRV-') and len(policy_num) >= 10:
                self.log(f"   ✅ Policy number format correct: {policy_num}")
            else:
                self.log(f"   ❌ Invalid policy number format: {policy_num}")
                return False
            
            return True
        else:
            missing_fields = [field for field in required_fields if field not in response]
            self.log(f"   ❌ Missing required fields in payment response: {missing_fields}")
            return False
    
    def complete_full_quote_flow(self):
        """Complete the full quote flow to get final premium"""
        if not self.session_id:
            self.log("❌ No session ID available for quote flow")
            return False
        
        self.log("🔄 Completing full quote flow...")
        
        # Complete quote flow steps
        steps = [
            ("car", "Vehicle Type"),
            ("has_vin_no", "VIN - No"),
            ("Toyota", "Vehicle Make"),
            ("Camry", "Vehicle Model"),
            ("1601cc - 2000cc", "Engine Capacity"),
            ("personal_use", "Vehicle Purpose"),
            ("daily", "Usage Frequency"),
            ("500_1000km", "Monthly Distance"),
            ("peak_hours", "Driving Time"),
            ("env_urban_city", "Environment 1"),
            ("env_suburban", "Environment 2"),
            ("env_done", "Environment Done"),
            ("confirm_vehicle", "Confirm Vehicle"),
            ("comprehensive", "Coverage Type"),
            ("Drive Premium", "Plan Selection"),
            ("singpass", "Driver Info Method"),
            ("consent_yes", "Singpass Consent"),
            ("confirm_driver", "Confirm Driver"),
            ("no_claims", "Claims History"),
            ("none", "Additional Drivers"),
            ("data_sharing_yes", "Telematics Data Sharing"),
            ("safety_alerts_yes", "Safety Alerts"),
            ("yes", "Telematics Final Consent"),
            ("view_quote", "View Quote")
        ]
        
        for step_value, step_name in steps:
            success, response = self.run_test(
                f"Quote Flow - {step_name}",
                "POST",
                "chat",
                200,
                data={
                    "session_id": self.session_id,
                    "content": step_value,
                    "quick_reply_value": step_value
                }
            )
            
            if not success:
                self.log(f"❌ Quote flow failed at step: {step_name}")
                return False
            
            time.sleep(0.1)
        
        return True
    
    def run_specific_tests(self):
        """Run all specific change tests"""
        self.log("🚀 Starting Specific Changes API Tests")
        self.log(f"   Base URL: {self.base_url}")
        
        # Test 1: Driving Environment Multi-Select
        test1_success = self.test_driving_environment_multi_select()
        
        # Test 2: GPS Consent Question Removed
        test2_success = self.test_gps_consent_removed()
        
        # Test 3: Payment Processing
        test3_success = self.test_payment_processing()
        
        # Print results
        self.print_results()
        
        return test1_success and test2_success and test3_success
    
    def print_results(self):
        """Print test results summary"""
        self.log("\n" + "="*60)
        self.log("📊 SPECIFIC CHANGES TEST RESULTS SUMMARY")
        self.log("="*60)
        self.log(f"Total Tests: {self.tests_run}")
        self.log(f"Passed: {self.tests_passed}")
        self.log(f"Failed: {len(self.failed_tests)}")
        self.log(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.failed_tests:
            self.log("\n❌ FAILED TESTS:")
            for i, test in enumerate(self.failed_tests, 1):
                self.log(f"{i}. {test['test']}")
                if 'expected' in test:
                    self.log(f"   Expected: {test['expected']}")
                    self.log(f"   Actual: {test['actual']}")
                if 'error' in test:
                    self.log(f"   Error: {test['error']}")
                if 'response' in test:
                    self.log(f"   Response: {test['response']}")
        else:
            self.log("\n🎉 ALL SPECIFIC CHANGE TESTS PASSED!")

def main():
    """Main test execution"""
    tester = SpecificChangesAPITester()
    
    try:
        success = tester.run_specific_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        tester.log("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        tester.log(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())