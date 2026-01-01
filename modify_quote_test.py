#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import time

class ModifyQuoteAPITester:
    def __init__(self, base_url="https://quick-insure-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.original_quote = None
        self.modified_quote = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def send_chat_message(self, content, quick_reply_value=None):
        """Send a chat message and return response"""
        url = f"{self.api_url}/chat"
        data = {
            "session_id": self.session_id,
            "content": content,
            "quick_reply_value": quick_reply_value or content
        }
        
        try:
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'}, timeout=30)
            if response.status_code == 200:
                return True, response.json()
            else:
                self.log(f"❌ Chat message failed - Status: {response.status_code}, Response: {response.text[:200]}")
                return False, {}
        except Exception as e:
            self.log(f"❌ Chat message error: {str(e)}")
            return False, {}
    
    def create_session(self):
        """Create a new session"""
        self.log("🔍 Creating new session...")
        url = f"{self.api_url}/sessions"
        data = {"user_agent": "modify-quote-test"}
        
        try:
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'}, timeout=30)
            if response.status_code == 200:
                result = response.json()
                self.session_id = result['id']
                self.log(f"✅ Session created: {self.session_id}")
                return True
            else:
                self.log(f"❌ Session creation failed - Status: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Session creation error: {str(e)}")
            return False
    
    def complete_quote_flow(self):
        """Complete the full quote flow as specified in the test request"""
        self.log("\n📋 Starting complete quote flow...")
        
        # Step 1: Select vehicle type: "car"
        success, response = self.send_chat_message("car", "car")
        if not success:
            self.log("❌ Failed at vehicle type selection")
            return False
        self.log("✅ Vehicle type selected: car")
        
        # Step 2: Select make: "Toyota"
        success, response = self.send_chat_message("Toyota", "Toyota")
        if not success:
            self.log("❌ Failed at vehicle make selection")
            return False
        self.log("✅ Vehicle make selected: Toyota")
        
        # Step 3: Select model: "Camry"
        success, response = self.send_chat_message("Camry", "Camry")
        if not success:
            self.log("❌ Failed at vehicle model selection")
            return False
        self.log("✅ Vehicle model selected: Camry")
        
        # Step 4: Select engine capacity: "1601cc - 2000cc"
        success, response = self.send_chat_message("1601cc - 2000cc", "1601cc - 2000cc")
        if not success:
            self.log("❌ Failed at engine capacity selection")
            return False
        self.log("✅ Engine capacity selected: 1601cc - 2000cc")
        
        # Step 5: Select off-peak: "no_offpeak"
        success, response = self.send_chat_message("No, Regular Car", "no_offpeak")
        if not success:
            self.log("❌ Failed at off-peak selection")
            return False
        self.log("✅ Off-peak selected: no_offpeak")
        
        # Step 6: Confirm vehicle: "confirm_vehicle"
        success, response = self.send_chat_message("✓ Confirm & Continue", "confirm_vehicle")
        if not success:
            self.log("❌ Failed at vehicle confirmation")
            return False
        self.log("✅ Vehicle confirmed")
        
        # Step 7: Select coverage: "comprehensive"
        success, response = self.send_chat_message("Comprehensive", "comprehensive")
        if not success:
            self.log("❌ Failed at coverage selection")
            return False
        self.log("✅ Coverage selected: comprehensive")
        
        # Step 8: Select plan: "Drive Premium"
        success, response = self.send_chat_message("Drive Premium", "Drive Premium")
        if not success:
            self.log("❌ Failed at plan selection")
            return False
        self.log("✅ Plan selected: Drive Premium")
        
        # Step 9: Select identity method: "singpass"
        success, response = self.send_chat_message("🔐 Use Singpass", "singpass")
        if not success:
            self.log("❌ Failed at identity method selection")
            return False
        self.log("✅ Identity method selected: singpass")
        
        # Step 10: Give consent: "consent_yes"
        success, response = self.send_chat_message("✓ I Consent", "consent_yes")
        if not success:
            self.log("❌ Failed at consent")
            return False
        self.log("✅ Consent given")
        
        # Step 11: Confirm driver: "confirm_driver"
        success, response = self.send_chat_message("✓ Confirm Details", "confirm_driver")
        if not success:
            self.log("❌ Failed at driver confirmation")
            return False
        self.log("✅ Driver confirmed")
        
        # Step 12: Claims history: "no_claims"
        success, response = self.send_chat_message("No Claims (NCD eligible)", "no_claims")
        if not success:
            self.log("❌ Failed at claims history")
            return False
        self.log("✅ Claims history: no_claims")
        
        # Step 13: Additional drivers: "none"
        success, response = self.send_chat_message("No, Just Me", "none")
        if not success:
            self.log("❌ Failed at additional drivers")
            return False
        self.log("✅ Additional drivers: none")
        
        # Step 14: Telematics: "yes"
        success, response = self.send_chat_message("Yes, Save 15%!", "yes")
        if not success:
            self.log("❌ Failed at telematics")
            return False
        self.log("✅ Telematics: yes")
        
        # Step 15: View quote: "view_quote"
        success, response = self.send_chat_message("View My Quote", "view_quote")
        if not success:
            self.log("❌ Failed at view quote")
            return False
        self.log("✅ Quote viewed")
        
        # Check if we have the quote summary with modify button
        if response and 'message' in response:
            message_data = response['message']
            if 'quick_replies' in message_data:
                quick_replies = message_data['quick_replies']
                modify_button_found = any(reply.get('value') == 'modify' for reply in quick_replies)
                accept_button_found = any(reply.get('value') == 'accept_quote' for reply in quick_replies)
                
                if modify_button_found and accept_button_found:
                    self.log("✅ Quote summary displayed with 'Accept & Generate Policy' and 'Modify Quote' buttons")
                    
                    # Store original quote data
                    if 'cards' in message_data and message_data['cards']:
                        card = message_data['cards'][0]
                        if card.get('type') == 'quote_summary':
                            self.original_quote = {
                                'premium': card.get('premium'),
                                'plan_name': card.get('plan_name'),
                                'coverage_type': card.get('coverage_type'),
                                'breakdown': card.get('breakdown', [])
                            }
                            self.log(f"✅ Original quote stored: {self.original_quote['premium']}")
                    
                    return True
                else:
                    self.log("❌ Quote summary missing expected buttons")
                    return False
            else:
                self.log("❌ No quick replies in quote response")
                return False
        else:
            self.log("❌ Invalid quote response")
            return False
    
    def test_modify_quote_flow(self):
        """Test the modify quote functionality"""
        self.log("\n🔧 Testing Modify Quote functionality...")
        
        # Step 1: Send "modify" - should return options to modify
        success, response = self.send_chat_message("Modify Quote", "modify")
        if not success:
            self.log("❌ Failed to initiate modify quote")
            return False
        
        # Check if modify options are presented
        if response and 'message' in response:
            message_data = response['message']
            if 'quick_replies' in message_data:
                quick_replies = message_data['quick_replies']
                expected_options = ['change_coverage', 'change_plan', 'change_telematics', 'keep_quote']
                found_options = [reply.get('value') for reply in quick_replies]
                
                if all(option in found_options for option in expected_options):
                    self.log("✅ Modify quote options displayed correctly")
                    self.log(f"   Available options: {found_options}")
                    return True
                else:
                    self.log(f"❌ Missing modify options. Expected: {expected_options}, Found: {found_options}")
                    return False
            else:
                self.log("❌ No quick replies in modify response")
                return False
        else:
            self.log("❌ Invalid modify response")
            return False
    
    def test_change_coverage_flow(self):
        """Test changing coverage type"""
        self.log("\n🔄 Testing Change Coverage functionality...")
        
        # Step 1: Send "change_coverage"
        success, response = self.send_chat_message("Change Coverage Type", "change_coverage")
        if not success:
            self.log("❌ Failed to initiate change coverage")
            return False
        
        # Verify response shows coverage type options
        if response and 'message' in response:
            message_data = response['message']
            if 'quick_replies' in message_data:
                quick_replies = message_data['quick_replies']
                coverage_options = [reply.get('value') for reply in quick_replies]
                
                if 'comprehensive' in coverage_options and 'third_party' in coverage_options:
                    self.log("✅ Coverage type options displayed correctly")
                    self.log(f"   Available coverage options: {coverage_options}")
                    
                    # Step 2: Select new coverage "third_party"
                    success, response = self.send_chat_message("Third Party Only", "third_party")
                    if not success:
                        self.log("❌ Failed to select third party coverage")
                        return False
                    self.log("✅ Third party coverage selected")
                    
                    # Continue the flow until new quote is generated
                    return self.complete_modified_quote_flow()
                else:
                    self.log(f"❌ Missing coverage options. Found: {coverage_options}")
                    return False
            else:
                self.log("❌ No quick replies in change coverage response")
                return False
        else:
            self.log("❌ Invalid change coverage response")
            return False
    
    def complete_modified_quote_flow(self):
        """Complete the flow after changing coverage to get new quote"""
        self.log("\n📊 Completing modified quote flow...")
        
        # We need to go through the plan selection again since coverage changed
        # The system should ask for plan selection for the new coverage type
        
        # Select plan for third party coverage
        success, response = self.send_chat_message("Drive Premium", "Drive Premium")
        if not success:
            self.log("❌ Failed to select plan for modified coverage")
            return False
        self.log("✅ Plan selected for modified coverage")
        
        # The system should now recalculate and show the new quote
        # We might need to trigger quote calculation
        success, response = self.send_chat_message("View My Quote", "view_quote")
        if not success:
            self.log("❌ Failed to view modified quote")
            return False
        
        # Check if we have a new quote with different premium
        if response and 'message' in response:
            message_data = response['message']
            if 'cards' in message_data and message_data['cards']:
                card = message_data['cards'][0]
                if card.get('type') == 'quote_summary':
                    self.modified_quote = {
                        'premium': card.get('premium'),
                        'plan_name': card.get('plan_name'),
                        'coverage_type': card.get('coverage_type'),
                        'breakdown': card.get('breakdown', [])
                    }
                    self.log(f"✅ Modified quote generated: {self.modified_quote['premium']}")
                    
                    # Verify the new quote has different premium values
                    if self.original_quote and self.modified_quote:
                        if self.original_quote['premium'] != self.modified_quote['premium']:
                            self.log("✅ New quote has different premium values than original")
                            self.log(f"   Original: {self.original_quote['premium']} (Comprehensive)")
                            self.log(f"   Modified: {self.modified_quote['premium']} (Third Party)")
                            return True
                        else:
                            self.log("❌ New quote has same premium as original")
                            return False
                    else:
                        self.log("❌ Cannot compare quotes - missing data")
                        return False
                else:
                    self.log("❌ Modified quote response missing quote summary card")
                    return False
            else:
                self.log("❌ Modified quote response missing cards")
                return False
        else:
            self.log("❌ Invalid modified quote response")
            return False
    
    def run_modify_quote_tests(self):
        """Run all modify quote tests"""
        self.log("🚀 Starting Modify Quote API Tests")
        self.log(f"   Base URL: {self.base_url}")
        
        # Step 1: Create session
        if not self.create_session():
            self.log("❌ Cannot proceed without session")
            return False
        
        # Step 2: Complete full quote flow
        if not self.complete_quote_flow():
            self.log("❌ Cannot proceed without completing quote flow")
            return False
        
        # Step 3: Test modify quote functionality
        if not self.test_modify_quote_flow():
            self.log("❌ Modify quote functionality failed")
            return False
        
        # Step 4: Test change coverage flow
        if not self.test_change_coverage_flow():
            self.log("❌ Change coverage functionality failed")
            return False
        
        self.log("\n🎉 ALL MODIFY QUOTE TESTS PASSED!")
        return True
    
    def print_results(self):
        """Print test results summary"""
        self.log("\n" + "="*60)
        self.log("📊 MODIFY QUOTE TEST RESULTS SUMMARY")
        self.log("="*60)
        
        if self.original_quote:
            self.log("📋 Original Quote:")
            self.log(f"   Premium: {self.original_quote['premium']}")
            self.log(f"   Coverage: {self.original_quote['coverage_type']}")
            self.log(f"   Plan: {self.original_quote['plan_name']}")
        
        if self.modified_quote:
            self.log("📋 Modified Quote:")
            self.log(f"   Premium: {self.modified_quote['premium']}")
            self.log(f"   Coverage: {self.modified_quote['coverage_type']}")
            self.log(f"   Plan: {self.modified_quote['plan_name']}")
        
        if self.original_quote and self.modified_quote:
            self.log("📊 Comparison:")
            self.log(f"   Premium Changed: {self.original_quote['premium'] != self.modified_quote['premium']}")
            self.log(f"   Coverage Changed: {self.original_quote['coverage_type'] != self.modified_quote['coverage_type']}")

def main():
    """Main test execution"""
    tester = ModifyQuoteAPITester()
    
    try:
        success = tester.run_modify_quote_tests()
        tester.print_results()
        return 0 if success else 1
    except KeyboardInterrupt:
        tester.log("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        tester.log(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())