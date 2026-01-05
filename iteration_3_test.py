#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import time

class MotorInsuranceAgenticTest:
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
            self.log(f"❌ {name} - Error: {str(e)}", "ERROR")
            self.failed_tests.append({
                "test": name,
                "error": str(e)
            })
            return False, {}

    def test_basic_api_health(self):
        """Test basic API connectivity"""
        self.log("=== Testing Basic API Health ===")
        success, _ = self.run_test("API Root", "GET", "")
        return success

    def test_session_creation(self):
        """Test session creation"""
        self.log("=== Testing Session Management ===")
        success, response = self.run_test(
            "Create Session", 
            "POST", 
            "sessions",
            200,
            {"user_agent": "Test Agent"}
        )
        
        if success and 'id' in response:
            self.session_id = response['id']
            self.log(f"✅ Session created: {self.session_id}")
            return True
        return False

    def test_welcome_message(self):
        """Test welcome message with agent name"""
        if not self.session_id:
            return False
            
        success, response = self.run_test(
            "Welcome Message",
            "POST",
            f"welcome/{self.session_id}"
        )
        
        if success:
            # Check if agent name is present
            agent = response.get('agent', '')
            if agent:
                self.log(f"✅ Agent name found: {agent}")
            else:
                self.log("⚠️ No agent name in welcome message")
        
        return success

    def test_vehicle_registration_flow(self):
        """Test new vehicle registration flow with LTA lookup"""
        if not self.session_id:
            return False
            
        self.log("=== Testing Vehicle Registration Flow ===")
        
        # Step 1: Select Car
        success, response = self.run_test(
            "Select Vehicle Type (Car)",
            "POST",
            "chat",
            data={
                "session_id": self.session_id,
                "content": "Car",
                "quick_reply_value": "car"
            }
        )
        
        if not success:
            return False
            
        # Check if response asks for registration number
        message_content = response.get('message', {}).get('content', '')
        if 'registration' in message_content.lower():
            self.log("✅ Registration number request detected")
        
        # Step 2: Enter registration number (SGX1234A)
        success, response = self.run_test(
            "Enter Registration Number",
            "POST",
            "chat",
            data={
                "session_id": self.session_id,
                "content": "SGX1234A",
                "quick_reply_value": "SGX1234A"
            }
        )
        
        if success:
            # Check if vehicle_fetch card is present
            message = response.get('message', {})
            cards = message.get('cards', [])
            
            vehicle_fetch_card = None
            for card in cards:
                if card.get('type') == 'vehicle_fetch':
                    vehicle_fetch_card = card
                    break
            
            if vehicle_fetch_card:
                self.log("✅ Vehicle fetch card found in response")
                data = vehicle_fetch_card.get('data', {})
                self.log(f"   Registration: {data.get('registration', 'N/A')}")
                self.log(f"   Make: {data.get('make', 'N/A')}")
                self.log(f"   Model: {data.get('model', 'N/A')}")
            else:
                self.log("⚠️ Vehicle fetch card not found")
        
        return success

    def test_lta_mock_service(self):
        """Test LTA mock service directly"""
        self.log("=== Testing LTA Mock Service ===")
        
        # Test with SGX1234A
        success, response = self.run_test(
            "LTA Lookup SGX1234A",
            "GET",
            "lta-lookup/SGX1234A"
        )
        
        if success and response.get('found'):
            data = response.get('data', {})
            self.log(f"✅ LTA data: {data.get('make')} {data.get('model')} {data.get('engine_cc')}")
        
        # Test with SBA5678B
        success2, response2 = self.run_test(
            "LTA Lookup SBA5678B",
            "GET",
            "lta-lookup/SBA5678B"
        )
        
        return success and success2

    def test_singpass_flow(self):
        """Test Singpass integration with DataFetchCard"""
        if not self.session_id:
            return False
            
        self.log("=== Testing Singpass Flow ===")
        
        # Continue the flow to reach Singpass step
        # First confirm vehicle details
        success, response = self.run_test(
            "Confirm Vehicle Details",
            "POST",
            "chat",
            data={
                "session_id": self.session_id,
                "content": "Confirm Details",
                "quick_reply_value": "confirm_vehicle"
            }
        )
        
        if not success:
            return False
        
        # Select coverage type
        success, response = self.run_test(
            "Select Coverage (Comprehensive)",
            "POST",
            "chat",
            data={
                "session_id": self.session_id,
                "content": "Comprehensive",
                "quick_reply_value": "comprehensive"
            }
        )
        
        if not success:
            return False
        
        # Select plan
        success, response = self.run_test(
            "Select Plan (Drive Premium)",
            "POST",
            "chat",
            data={
                "session_id": self.session_id,
                "content": "Drive Premium",
                "quick_reply_value": "Drive Premium"
            }
        )
        
        if not success:
            return False
        
        # Select Singpass
        success, response = self.run_test(
            "Select Singpass",
            "POST",
            "chat",
            data={
                "session_id": self.session_id,
                "content": "Use Singpass",
                "quick_reply_value": "singpass"
            }
        )
        
        if not success:
            return False
        
        # Give consent
        success, response = self.run_test(
            "Singpass Consent",
            "POST",
            "chat",
            data={
                "session_id": self.session_id,
                "content": "I Consent",
                "quick_reply_value": "consent_yes"
            }
        )
        
        if success:
            # Check for singpass_fetch card
            message = response.get('message', {})
            cards = message.get('cards', [])
            
            singpass_card = None
            for card in cards:
                if card.get('type') == 'singpass_fetch':
                    singpass_card = card
                    break
            
            if singpass_card:
                self.log("✅ Singpass fetch card found")
                data = singpass_card.get('data', {})
                self.log(f"   Name: {data.get('name', 'N/A')}")
                self.log(f"   NRIC: {data.get('nric', 'N/A')}")
            else:
                self.log("⚠️ Singpass fetch card not found")
        
        return success

    def test_risk_assessment_flow(self):
        """Test risk assessment with DataFetchCard"""
        if not self.session_id:
            return False
            
        self.log("=== Testing Risk Assessment Flow ===")
        
        # Continue flow - confirm driver details
        success, response = self.run_test(
            "Confirm Driver Details",
            "POST",
            "chat",
            data={
                "session_id": self.session_id,
                "content": "Confirm Details",
                "quick_reply_value": "confirm_driver"
            }
        )
        
        if not success:
            return False
        
        # Claims history
        success, response = self.run_test(
            "Claims History (No Claims)",
            "POST",
            "chat",
            data={
                "session_id": self.session_id,
                "content": "No Claims (NCD eligible)",
                "quick_reply_value": "no_claims"
            }
        )
        
        if not success:
            return False
        
        # Additional drivers
        success, response = self.run_test(
            "Additional Drivers (None)",
            "POST",
            "chat",
            data={
                "session_id": self.session_id,
                "content": "No, Just Me",
                "quick_reply_value": "none"
            }
        )
        
        if not success:
            return False
        
        # Telematics
        success, response = self.run_test(
            "Telematics (Yes)",
            "POST",
            "chat",
            data={
                "session_id": self.session_id,
                "content": "Yes, Save 15%!",
                "quick_reply_value": "yes"
            }
        )
        
        if success:
            # Check for risk_fetch card
            message = response.get('message', {})
            cards = message.get('cards', [])
            
            risk_card = None
            for card in cards:
                if card.get('type') == 'risk_fetch':
                    risk_card = card
                    break
            
            if risk_card:
                self.log("✅ Risk assessment card found")
                data = risk_card.get('data', {})
                self.log(f"   Claims: {data.get('claims', 'N/A')}")
                self.log(f"   Risk Level: {data.get('rating', 'N/A')}")
            else:
                self.log("⚠️ Risk assessment card not found")
        
        return success

    def test_quote_generation(self):
        """Test quote generation and premium calculation"""
        if not self.session_id:
            return False
            
        self.log("=== Testing Quote Generation ===")
        
        # View quote
        success, response = self.run_test(
            "View Quote",
            "POST",
            "chat",
            data={
                "session_id": self.session_id,
                "content": "View My Quote",
                "quick_reply_value": "view_quote"
            }
        )
        
        if success:
            # Check for quote_summary card
            message = response.get('message', {})
            cards = message.get('cards', [])
            
            quote_card = None
            for card in cards:
                if card.get('type') == 'quote_summary':
                    quote_card = card
                    break
            
            if quote_card:
                self.log("✅ Quote summary card found")
                self.log(f"   Plan: {quote_card.get('plan_name', 'N/A')}")
                self.log(f"   Coverage: {quote_card.get('coverage_type', 'N/A')}")
                self.log(f"   Premium: {quote_card.get('premium', 'N/A')}")
                
                # Check breakdown
                breakdown = quote_card.get('breakdown', [])
                if breakdown:
                    self.log("   Premium Breakdown:")
                    for item in breakdown:
                        self.log(f"     {item.get('item', 'N/A')}: {item.get('amount', 'N/A')}")
            else:
                self.log("⚠️ Quote summary card not found")
        
        return success

    def test_policy_document_generation(self):
        """Test policy document generation"""
        if not self.session_id:
            return False
            
        self.log("=== Testing Policy Document Generation ===")
        
        # Accept quote and generate policy
        success, response = self.run_test(
            "Accept Quote",
            "POST",
            "chat",
            data={
                "session_id": self.session_id,
                "content": "Accept & Generate Policy",
                "quick_reply_value": "accept_quote"
            }
        )
        
        if success:
            # Check for policy_document card
            message = response.get('message', {})
            cards = message.get('cards', [])
            
            policy_card = None
            for card in cards:
                if card.get('type') == 'policy_document':
                    policy_card = card
                    break
            
            if policy_card:
                self.log("✅ Policy document card found")
                self.log(f"   Policy Number: {policy_card.get('policy_number', 'N/A')}")
                self.log(f"   Vehicle: {policy_card.get('vehicle', 'N/A')}")
                self.log(f"   Premium: {policy_card.get('premium', 'N/A')}")
            else:
                self.log("⚠️ Policy document card not found")
        
        return success

    def test_pdf_download(self):
        """Test PDF download functionality"""
        if not self.session_id:
            return False
            
        self.log("=== Testing PDF Download ===")
        
        success, response = self.run_test(
            "PDF Download",
            "GET",
            f"document/{self.session_id}/pdf",
            expected_status=200
        )
        
        if success:
            self.log("✅ PDF download endpoint working")
        
        return success

    def test_agent_names_in_responses(self):
        """Test that agent names are present in chat responses"""
        if not self.session_id:
            return False
            
        self.log("=== Testing Agent Names in Responses ===")
        
        # Get messages for the session
        success, messages = self.run_test(
            "Get Messages",
            "GET",
            f"messages/{self.session_id}"
        )
        
        if success and isinstance(messages, list):
            agent_names_found = []
            for message in messages:
                if message.get('role') == 'assistant' and message.get('agent'):
                    agent_names_found.append(message.get('agent'))
            
            unique_agents = list(set(agent_names_found))
            if unique_agents:
                self.log(f"✅ Agent names found: {', '.join(unique_agents)}")
                return True
            else:
                self.log("⚠️ No agent names found in messages")
        
        return False

    def run_all_tests(self):
        """Run all tests"""
        self.log("🚀 Starting Agentic Motor Insurance Tests")
        self.log(f"Testing against: {self.base_url}")
        
        tests = [
            self.test_basic_api_health,
            self.test_session_creation,
            self.test_welcome_message,
            self.test_lta_mock_service,
            self.test_vehicle_registration_flow,
            self.test_singpass_flow,
            self.test_risk_assessment_flow,
            self.test_quote_generation,
            self.test_policy_document_generation,
            self.test_pdf_download,
            self.test_agent_names_in_responses
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                self.log(f"❌ Test {test.__name__} failed with exception: {str(e)}", "ERROR")
        
        # Print summary
        self.log("=" * 50)
        self.log(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.failed_tests:
            self.log("❌ Failed Tests:")
            for failure in self.failed_tests:
                self.log(f"   - {failure.get('test', 'Unknown')}: {failure.get('error', failure.get('response', 'Unknown error'))}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"✅ Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = MotorInsuranceAgenticTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)