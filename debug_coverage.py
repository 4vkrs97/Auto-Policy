#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

def test_coverage_step():
    """Debug the coverage step specifically"""
    base_url = "https://motor-policy-jiffy.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Create session
    response = requests.post(f"{api_url}/sessions", json={"user_agent": "debug-test"})
    session_data = response.json()
    session_id = session_data['id']
    print(f"Session ID: {session_id}")
    
    # Welcome message
    requests.post(f"{api_url}/welcome/{session_id}")
    
    # Step through to coverage
    steps = [
        ("car", "Car"),
        ("Toyota", "Toyota"), 
        ("Camry", "Camry"),
        ("1601cc - 2000cc", "1601cc - 2000cc"),
        ("no", "No, Normal")
    ]
    
    for value, content in steps:
        response = requests.post(f"{api_url}/chat", json={
            "session_id": session_id,
            "content": content,
            "quick_reply_value": value
        })
        print(f"Step: {content} -> Status: {response.status_code}")
    
    # Now test coverage step
    print("\n=== Testing Coverage Step ===")
    response = requests.post(f"{api_url}/chat", json={
        "session_id": session_id,
        "content": "Comprehensive",
        "quick_reply_value": "comprehensive"
    })
    
    print(f"Coverage Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        
        if 'message' in data:
            message = data['message']
            print(f"Message keys: {list(message.keys())}")
            
            if 'cards' in message:
                cards = message['cards']
                print(f"Cards: {cards}")
                print(f"Cards type: {type(cards)}")
                if cards:
                    print(f"Number of cards: {len(cards)}")
                    for i, card in enumerate(cards):
                        print(f"Card {i}: {card}")
                else:
                    print("Cards is empty or None")
            else:
                print("No 'cards' key in message")
        else:
            print("No 'message' key in response")
            
        print(f"Full response: {json.dumps(data, indent=2)}")
    else:
        print(f"Error response: {response.text}")

if __name__ == "__main__":
    test_coverage_step()