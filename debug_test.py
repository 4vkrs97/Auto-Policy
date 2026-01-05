#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import time

class DebugTester:
    def __init__(self, base_url="https://quick-insure-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def create_session(self):
        """Create a new session for testing"""
        response = requests.post(f"{self.api_url}/sessions", json={"user_agent": "test-agent"})
        if response.status_code == 200:
            data = response.json()
            self.session_id = data['id']
            self.log(f"Session created: {self.session_id}")
            return True
        return False
    
    def send_chat(self, content, quick_reply_value=None):
        """Send a chat message and return response"""
        data = {
            "session_id": self.session_id,
            "content": content,
            "quick_reply_value": quick_reply_value or content
        }
        response = requests.post(f"{self.api_url}/chat", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            self.log(f"Chat failed: {response.status_code} - {response.text}")
            return None
    
    def debug_driving_environment(self):
        """Debug the driving environment multi-select issue"""
        self.log("🔍 Debugging driving environment multi-select...")
        
        if not self.create_session():
            return False
        
        # Complete flow to driving environment
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
            response = self.send_chat(step_value, step_value)
            if not response:
                self.log(f"Failed at step: {step_name}")
                return False
            time.sleep(0.1)
        
        # Now check the driving environment question
        response = self.send_chat("continue", "continue")
        if response:
            self.log("🔍 Driving Environment Response:")
            self.log(json.dumps(response, indent=2))
            
            message_data = response.get('message', {})
            if 'multi_select' in message_data:
                self.log(f"✅ multi_select found: {message_data['multi_select']}")
            else:
                self.log("❌ multi_select not found in response")
                self.log(f"Available keys: {list(message_data.keys())}")
        
        return True
    
    def debug_payment_format(self):
        """Debug the payment policy number format"""
        self.log("🔍 Debugging payment policy number format...")
        
        # Test payment methods first
        response = requests.get(f"{self.api_url}/payment/methods")
        if response.status_code == 200:
            data = response.json()
            self.log(f"Payment methods: {len(data.get('methods', []))} methods found")
        
        # Create session and complete quote flow
        if not self.create_session():
            return False
        
        # Complete full quote flow (abbreviated for debugging)
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
            response = self.send_chat(step_value, step_value)
            if not response:
                self.log(f"Failed at step: {step_name}")
                return False
            time.sleep(0.05)  # Faster for debugging
        
        # Get session to check final premium
        session_response = requests.get(f"{self.api_url}/sessions/{self.session_id}")
        if session_response.status_code == 200:
            session_data = session_response.json()
            final_premium = session_data['state'].get('final_premium', 0)
            self.log(f"Final premium: ${final_premium}")
            
            if final_premium > 0:
                # Test payment processing
                payment_data = {
                    "session_id": self.session_id,
                    "payment_method": "paynow",
                    "amount": final_premium
                }
                payment_response = requests.post(f"{self.api_url}/payment/process", json=payment_data)
                
                if payment_response.status_code == 200:
                    payment_result = payment_response.json()
                    self.log("🔍 Payment Response:")
                    self.log(json.dumps(payment_result, indent=2))
                    
                    policy_num = payment_result.get('policy_number', '')
                    self.log(f"Policy number: {policy_num}")
                    self.log(f"Expected format: TRV-YYYY-XXXXX")
                    self.log(f"Actual format: {policy_num[:3]}-YYYY-XXXXX")
                else:
                    self.log(f"Payment failed: {payment_response.status_code}")
        
        return True

def main():
    """Main debug execution"""
    debugger = DebugTester()
    
    print("=== DEBUGGING SPECIFIC ISSUES ===")
    
    # Debug driving environment multi-select
    debugger.debug_driving_environment()
    
    print("\n" + "="*50 + "\n")
    
    # Debug payment format
    debugger.debug_payment_format()

if __name__ == "__main__":
    main()