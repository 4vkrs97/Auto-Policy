#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import time

class MotorInsuranceAPITester:
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
            201,
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
    
    def test_messages_endpoint(self):
        """Test messages retrieval"""
        if not self.session_id:
            self.log("❌ No session ID available for messages test")
            return False
            
        return self.run_test("Get Messages", "GET", f"messages/{self.session_id}")[0]
    
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