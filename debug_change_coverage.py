#!/usr/bin/env python3

import requests
import json

def test_change_coverage_debug():
    base_url = "https://quick-insure-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Create session
    print("Creating session...")
    response = requests.post(f"{api_url}/sessions", json={"user_agent": "debug-test"})
    session_data = response.json()
    session_id = session_data['id']
    print(f"Session ID: {session_id}")
    
    def send_message(content, quick_reply=None):
        data = {
            "session_id": session_id,
            "content": content,
            "quick_reply_value": quick_reply or content
        }
        response = requests.post(f"{api_url}/chat", json=data)
        result = response.json()
        print(f"\n--- Sent: {content} ---")
        print(f"Message: {result['message']['content'][:100]}...")
        if 'quick_replies' in result['message']:
            replies = [r['value'] for r in result['message']['quick_replies']]
            print(f"Quick replies: {replies}")
        print(f"State change_coverage: {result['state'].get('change_coverage')}")
        print(f"State modify_quote: {result['state'].get('modify_quote')}")
        return result
    
    # Quick flow to get to quote
    send_message("car", "car")
    send_message("Toyota", "Toyota") 
    send_message("Camry", "Camry")
    send_message("1601cc - 2000cc", "1601cc - 2000cc")
    send_message("No, Regular Car", "no_offpeak")
    send_message("✓ Confirm & Continue", "confirm_vehicle")
    send_message("Comprehensive", "comprehensive")
    send_message("Drive Premium", "Drive Premium")
    send_message("🔐 Use Singpass", "singpass")
    send_message("✓ I Consent", "consent_yes")
    send_message("✓ Confirm Details", "confirm_driver")
    send_message("No Claims (NCD eligible)", "no_claims")
    send_message("No, Just Me", "none")
    send_message("Yes, Save 15%!", "yes")
    send_message("View My Quote", "view_quote")
    
    # Test modify
    print(f"\n=== TESTING MODIFY ===")
    result = send_message("Modify Quote", "modify")
    
    # Test change coverage
    print(f"\n=== TESTING CHANGE COVERAGE ===")
    result = send_message("Change Coverage Type", "change_coverage")

if __name__ == "__main__":
    test_change_coverage_debug()