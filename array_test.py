#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import time

class ArrayStorageTester:
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
    
    def test_driving_environment_array_storage(self):
        """Test if driving environment is stored as an array"""
        self.log("🔍 Testing driving environment array storage...")
        
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
        
        # Select multiple environments
        self.log("Selecting urban environment...")
        response = self.send_chat("Urban / City Roads", "env_urban_city")
        if response:
            state = response.get('state', {})
            self.log(f"State after urban selection: driving_environment = {state.get('driving_environment')}")
        
        self.log("Selecting suburban environment...")
        response = self.send_chat("Suburban / Light Traffic", "env_suburban")
        if response:
            state = response.get('state', {})
            self.log(f"State after suburban selection: driving_environment = {state.get('driving_environment')}")
        
        self.log("Completing selection...")
        response = self.send_chat("Done Selecting", "env_done")
        if response:
            state = response.get('state', {})
            driving_env = state.get('driving_environment')
            self.log(f"Final driving_environment: {driving_env}")
            self.log(f"Type: {type(driving_env)}")
            
            if isinstance(driving_env, list):
                self.log(f"✅ Driving environment stored as array with {len(driving_env)} items")
                self.log(f"Contents: {driving_env}")
                return True
            else:
                self.log(f"❌ Driving environment not stored as array: {driving_env}")
                return False
        
        return False

def main():
    """Main test execution"""
    tester = ArrayStorageTester()
    
    print("=== TESTING DRIVING ENVIRONMENT ARRAY STORAGE ===")
    
    success = tester.test_driving_environment_array_storage()
    
    if success:
        print("\n✅ Array storage test PASSED")
    else:
        print("\n❌ Array storage test FAILED")

if __name__ == "__main__":
    main()