#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import time

class MotorInsuranceAPITester:
    def __init__(self, base_url="https://quick-insure-2.preview.emergentagent.com"):
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
    
    def test_api_status(self):
        """Test basic API status"""
        return self.run_test("API Status", "GET", "")
    
    def test_create_session(self):
        """Test session creation"""
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
    
    def test_get_session(self):
        """Test getting session by ID"""
        if not self.session_id:
            self.log("❌ No session ID available for get session test")
            return False
            
        return self.run_test(
            "Get Session",
            "GET",
            f"sessions/{self.session_id}"
        )[0]
    
    def test_welcome_message(self):
        """Test welcome message endpoint"""
        if not self.session_id:
            self.log("❌ No session ID available for welcome message test")
            return False
            
        return self.run_test(
            "Welcome Message",
            "POST",
            f"welcome/{self.session_id}"
        )[0]
    
    def test_chat_flow(self):
        """Test complete chat flow"""
        if not self.session_id:
            self.log("❌ No session ID available for chat flow test")
            return False
        
        # Test vehicle type selection
        success, response = self.run_test(
            "Chat - Vehicle Type",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Car",
                "quick_reply_value": "car"
            }
        )
        
        if not success:
            return False
            
        # Test vehicle make selection
        success, response = self.run_test(
            "Chat - Vehicle Make",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Toyota",
                "quick_reply_value": "Toyota"
            }
        )
        
        if not success:
            return False
            
        # Test vehicle model selection
        success, response = self.run_test(
            "Chat - Vehicle Model",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Camry",
                "quick_reply_value": "Camry"
            }
        )
        
        return success
    
    def test_vehicle_endpoints(self):
        """Test vehicle data endpoints"""
        # Test vehicle makes
        success1 = self.run_test("Vehicle Makes - Car", "GET", "vehicle-makes/car")[0]
        success2 = self.run_test("Vehicle Makes - Motorcycle", "GET", "vehicle-makes/motorcycle")[0]
        
        # Test vehicle models
        success3 = self.run_test("Vehicle Models - Toyota", "GET", "vehicle-models/Toyota")[0]
        
        return success1 and success2 and success3
    
    def test_mock_services(self):
        """Test mock Singpass and LTA services"""
        # Test Singpass mock
        success1 = self.run_test("Mock Singpass", "GET", "singpass-retrieve/S1234567A")[0]
        
        # Test LTA mock
        success2 = self.run_test("Mock LTA Lookup", "GET", "lta-lookup/SGX1234A")[0]
        
        return success1 and success2
    
    def test_document_generation(self):
        """Test document generation endpoints"""
        if not self.session_id:
            self.log("❌ No session ID available for document generation test")
            return False
            
        # Test HTML document
        success1 = self.run_test("HTML Document", "GET", f"document/{self.session_id}/html")[0]
        
        # Test PDF document (might take longer)
        self.log("🔍 Testing PDF Document Generation (may take longer)...")
        try:
            url = f"{self.api_url}/document/{self.session_id}/pdf"
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
                self.tests_passed += 1
                self.log("✅ PDF Document - Generated successfully")
                success2 = True
            else:
                self.log(f"❌ PDF Document - Status: {response.status_code}")
                self.failed_tests.append({
                    "test": "PDF Document",
                    "expected": "200 with PDF content",
                    "actual": f"{response.status_code} with {response.headers.get('content-type')}"
                })
                success2 = False
                
            self.tests_run += 1
            
        except Exception as e:
            self.log(f"❌ PDF Document - Error: {str(e)}")
            self.failed_tests.append({"test": "PDF Document", "error": str(e)})
            success2 = False
            self.tests_run += 1
        
        return success1 and success2
    
    def test_payment_methods(self):
        """Test payment methods endpoint"""
        success, response = self.run_test(
            "Payment Methods",
            "GET",
            "payment/methods"
        )
        
        if success and 'methods' in response:
            methods = response['methods']
            if len(methods) == 5:
                self.log(f"   ✅ Found {len(methods)} payment methods as expected")
                # Check for Singapore payment methods
                method_ids = [method['id'] for method in methods]
                expected_methods = ['paynow', 'card', 'grabpay', 'paylah', 'nets']
                
                all_present = all(method_id in method_ids for method_id in expected_methods)
                if all_present:
                    self.log("   ✅ All expected Singapore payment methods present")
                    return True
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
    
    def complete_quote_flow(self):
        """Complete the full quote flow to get final_premium"""
        if not self.session_id:
            self.log("❌ No session ID available for quote flow")
            return False, 0
        
        self.log("🔄 Completing quote flow to get final premium...")
        
        # Step-by-step quote completion
        steps = [
            ("car", "Vehicle Type"),
            ("Toyota", "Vehicle Make"),
            ("Camry", "Vehicle Model"),
            ("1601cc - 2000cc", "Engine Capacity"),
            ("no_offpeak", "Off-peak Status"),
            ("confirm_vehicle", "Confirm Vehicle"),
            ("comprehensive", "Coverage Type"),
            ("Drive Premium", "Plan Selection"),
            ("singpass", "Driver Info Method"),
            ("consent_yes", "Singpass Consent"),
            ("confirm_driver", "Confirm Driver"),
            ("no_claims", "Claims History"),
            ("none", "Additional Drivers"),
            ("yes", "Telematics Consent"),
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
                return False, 0
            
            # Small delay between steps
            time.sleep(0.1)
        
        # Get session to check final premium
        success, session_data = self.run_test(
            "Get Session for Premium",
            "GET",
            f"sessions/{self.session_id}"
        )
        
        if success and 'state' in session_data:
            final_premium = session_data['state'].get('final_premium', 0)
            if final_premium > 0:
                self.log(f"   ✅ Quote completed with final premium: ${final_premium}")
                return True, final_premium
            else:
                self.log("   ❌ Final premium not calculated or is zero")
                return False, 0
        else:
            self.log("   ❌ Could not retrieve session data")
            return False, 0
    
    def test_payment_process(self):
        """Test payment processing endpoint"""
        # First complete the quote flow
        quote_success, final_premium = self.complete_quote_flow()
        if not quote_success:
            self.log("❌ Cannot test payment without completed quote")
            return False
        
        # Test payment processing with different methods
        payment_methods = ["paynow", "card", "grabpay", "paylah", "nets"]
        
        for method in payment_methods:
            success, response = self.run_test(
                f"Payment Process - {method.upper()}",
                "POST",
                "payment/process",
                200,
                data={
                    "session_id": self.session_id,
                    "payment_method": method,
                    "amount": final_premium
                }
            )
            
            if success:
                # Verify response format
                if all(key in response for key in ['success', 'payment_reference', 'policy_number', 'message']):
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
                    
                    # Verify session state updated
                    success_session, session_data = self.run_test(
                        "Verify Payment State",
                        "GET",
                        f"sessions/{self.session_id}"
                    )
                    
                    if success_session and 'state' in session_data:
                        state = session_data['state']
                        if state.get('payment_completed') == True:
                            self.log(f"   ✅ Session state updated with payment_completed=True")
                            return True
                        else:
                            self.log(f"   ❌ Session state not updated correctly")
                            return False
                    else:
                        self.log(f"   ❌ Could not verify session state")
                        return False
                else:
                    self.log(f"   ❌ Missing required fields in payment response")
                    return False
            else:
                return False
            
            # Only test one payment method to avoid duplicate payments
            break
        
        return True
    
    def run_all_tests(self):
        """Run all API tests"""
        self.log("🚀 Starting Motor Insurance API Tests")
        self.log(f"   Base URL: {self.base_url}")
        
        # Basic API tests
        self.log("\n📋 Testing Basic API Endpoints...")
        self.test_api_status()
        
        # Session management tests
        self.log("\n🔐 Testing Session Management...")
        if self.test_create_session():
            self.test_get_session()
            self.test_welcome_message()
            self.test_messages_endpoint()
        
        # Chat flow tests
        self.log("\n💬 Testing Chat Flow...")
        self.test_chat_flow()
        
        # Vehicle data tests
        self.log("\n🚗 Testing Vehicle Data Endpoints...")
        self.test_vehicle_endpoints()
        
        # Mock services tests
        self.log("\n🔧 Testing Mock Services...")
        self.test_mock_services()
        
        # Document generation tests
        self.log("\n📄 Testing Document Generation...")
        self.test_document_generation()
        
        # Print results
        self.print_results()
        
        return self.tests_passed == self.tests_run
    
    def print_results(self):
        """Print test results summary"""
        self.log("\n" + "="*50)
        self.log("📊 TEST RESULTS SUMMARY")
        self.log("="*50)
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
            self.log("\n🎉 ALL TESTS PASSED!")

def main():
    """Main test execution"""
    tester = MotorInsuranceAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        tester.log("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        tester.log(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())