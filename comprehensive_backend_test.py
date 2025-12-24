#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import time

class ComprehensiveMotorInsuranceTest:
    def __init__(self, base_url="https://motor-policy-jiffy.preview.emergentagent.com"):
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
                self.log(f"   Response: {response.text[:300]}")
                self.failed_tests.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:300]
                })
                return False, {}
                
        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}")
            self.failed_tests.append({"test": name, "error": str(e)})
            return False, {}
    
    def test_complete_chat_flow(self):
        """Test the complete chat flow from Car to Document generation"""
        self.log("🚀 Starting Complete Chat Flow Test")
        
        # Create session
        success, response = self.run_test(
            "Create Session for Flow",
            "POST", 
            "sessions",
            200,
            data={"user_agent": "comprehensive-test-agent"}
        )
        if not success:
            return False
            
        self.session_id = response['id']
        self.log(f"   Session ID: {self.session_id}")
        
        # Get welcome message
        success, response = self.run_test(
            "Welcome Message",
            "POST",
            f"welcome/{self.session_id}"
        )
        if not success:
            return False
            
        # Step 1: Vehicle Type - Car
        success, response = self.run_test(
            "Step 1: Vehicle Type (Car)",
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
        
        # Verify quick replies are present
        if 'message' in response and 'quick_replies' in response['message']:
            self.log(f"   ✅ Quick replies present: {len(response['message']['quick_replies'])} options")
        else:
            self.log("   ⚠️ No quick replies in response")
            
        # Step 2: Vehicle Make - Toyota
        success, response = self.run_test(
            "Step 2: Vehicle Make (Toyota)",
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
            
        # Step 3: Vehicle Model - Camry
        success, response = self.run_test(
            "Step 3: Vehicle Model (Camry)",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Camry",
                "quick_reply_value": "Camry"
            }
        )
        if not success:
            return False
            
        # Step 4: Engine Capacity
        success, response = self.run_test(
            "Step 4: Engine Capacity",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "1601cc - 2000cc",
                "quick_reply_value": "1601cc - 2000cc"
            }
        )
        if not success:
            return False
            
        # Step 5: Off-peak status (for cars)
        success, response = self.run_test(
            "Step 5: Off-peak Status",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "No, Normal",
                "quick_reply_value": "no"
            }
        )
        if not success:
            return False
            
        # Step 6: Coverage Type - Comprehensive
        success, response = self.run_test(
            "Step 6: Coverage Type (Comprehensive)",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Comprehensive",
                "quick_reply_value": "comprehensive"
            }
        )
        if not success:
            return False
            
        # Check for coverage comparison cards
        if 'message' in response and 'cards' in response['message']:
            self.log(f"   ✅ Coverage cards present: {len(response['message']['cards'])} cards")
        else:
            self.log("   ⚠️ No coverage cards in response")
            
        # Step 7: Plan Selection - Drive Premium
        success, response = self.run_test(
            "Step 7: Plan Selection (Drive Premium)",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Drive Premium",
                "quick_reply_value": "Drive Premium"
            }
        )
        if not success:
            return False
            
        # Step 8: Singpass Identity
        success, response = self.run_test(
            "Step 8: Identity Method (Singpass)",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Use Singpass",
                "quick_reply_value": "singpass"
            }
        )
        if not success:
            return False
            
        # Step 9: Singpass Consent
        success, response = self.run_test(
            "Step 9: Singpass Consent",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Yes, I Consent",
                "quick_reply_value": "consent_yes"
            }
        )
        if not success:
            return False
            
        # Step 10: Claims History
        success, response = self.run_test(
            "Step 10: Claims History",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "No Claims",
                "quick_reply_value": "no_claims"
            }
        )
        if not success:
            return False
            
        # Step 11: Additional Drivers
        success, response = self.run_test(
            "Step 11: Additional Drivers",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "No, Just Me",
                "quick_reply_value": "none"
            }
        )
        if not success:
            return False
            
        # Step 12: Telematics
        success, response = self.run_test(
            "Step 12: Telematics Opt-in",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Yes, Save 5%!",
                "quick_reply_value": "yes"
            }
        )
        if not success:
            return False
            
        # Check for quote summary card
        if 'message' in response and 'cards' in response['message']:
            cards = response['message']['cards']
            quote_card = next((card for card in cards if card.get('type') == 'quote_summary'), None)
            if quote_card:
                self.log(f"   ✅ Quote card present with premium: {quote_card.get('premium', 'N/A')}")
            else:
                self.log("   ⚠️ No quote summary card found")
        else:
            self.log("   ⚠️ No cards in response")
            
        # Step 13: Generate Documents
        success, response = self.run_test(
            "Step 13: Generate Documents",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "content": "Generate Documents",
                "quick_reply_value": "generate"
            }
        )
        if not success:
            return False
            
        # Check for policy document card
        if 'message' in response and 'cards' in response['message']:
            cards = response['message']['cards']
            policy_card = next((card for card in cards if card.get('type') == 'policy_document'), None)
            if policy_card:
                self.log(f"   ✅ Policy card present with policy number: {policy_card.get('policy_number', 'N/A')}")
            else:
                self.log("   ⚠️ No policy document card found")
        else:
            self.log("   ⚠️ No cards in response")
            
        # Test document generation endpoints
        success1 = self.run_test("HTML Document Generation", "GET", f"document/{self.session_id}/html")[0]
        success2 = self.test_pdf_generation()
        
        return success1 and success2
    
    def test_pdf_generation(self):
        """Test PDF generation with proper content type check"""
        self.log("🔍 Testing PDF Document Generation...")
        try:
            url = f"{self.api_url}/document/{self.session_id}/pdf"
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    self.tests_passed += 1
                    self.log("✅ PDF Document - Generated successfully with correct content type")
                    return True
                else:
                    self.log(f"❌ PDF Document - Wrong content type: {content_type}")
                    self.failed_tests.append({
                        "test": "PDF Document Content Type",
                        "expected": "application/pdf",
                        "actual": content_type
                    })
                    return False
            else:
                self.log(f"❌ PDF Document - Status: {response.status_code}")
                self.failed_tests.append({
                    "test": "PDF Document",
                    "expected": 200,
                    "actual": response.status_code
                })
                return False
                
        except Exception as e:
            self.log(f"❌ PDF Document - Error: {str(e)}")
            self.failed_tests.append({"test": "PDF Document", "error": str(e)})
            return False
        finally:
            self.tests_run += 1
    
    def test_session_state_updates(self):
        """Test that session state updates correctly through conversation"""
        if not self.session_id:
            return False
            
        success, response = self.run_test(
            "Session State Check",
            "GET",
            f"sessions/{self.session_id}"
        )
        
        if success and 'state' in response:
            state = response['state']
            expected_fields = [
                'vehicle_type', 'vehicle_make', 'vehicle_model', 
                'engine_capacity', 'coverage_type', 'plan_name',
                'driver_name', 'claims_history', 'telematics_consent',
                'final_premium'
            ]
            
            present_fields = [field for field in expected_fields if state.get(field)]
            self.log(f"   ✅ Session state has {len(present_fields)}/{len(expected_fields)} expected fields")
            
            if len(present_fields) >= 8:  # Most fields should be present
                return True
            else:
                self.log(f"   ⚠️ Missing important state fields: {set(expected_fields) - set(present_fields)}")
                return False
        
        return False
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        self.log("🚀 Starting Comprehensive Motor Insurance Tests")
        self.log(f"   Base URL: {self.base_url}")
        
        # Test complete chat flow
        flow_success = self.test_complete_chat_flow()
        
        # Test session state updates
        state_success = self.test_session_state_updates()
        
        # Print results
        self.print_results()
        
        return flow_success and state_success
    
    def print_results(self):
        """Print test results summary"""
        self.log("\n" + "="*60)
        self.log("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
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
        else:
            self.log("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")

def main():
    """Main test execution"""
    tester = ComprehensiveMotorInsuranceTest()
    
    try:
        success = tester.run_comprehensive_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        tester.log("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        tester.log(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())