#!/usr/bin/env python
"""
HL7 v2.3 Message Sender

This script sends HL7 v2.3 messages to a REST API endpoint over HTTPS.
"""
import os
import sys
import time
import json
import argparse
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default API endpoint if not specified
DEFAULT_ENDPOINT = os.getenv("HL7_API_ENDPOINT", "http://localhost:3000/api/hl7")
DEFAULT_API_KEY = os.getenv("HL7_API_KEY", "")

def read_hl7_messages(file_path):
    """Read HL7 messages from a file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Split the content by double newlines to separate messages
        messages = [msg.strip() for msg in content.split('\n\n') if msg.strip()]
        return messages
    except Exception as e:
        print(f"Error reading HL7 messages: {e}")
        return []

def encode_hl7_message(message):
    """Encode HL7 message to Base64 for transmission"""
    return base64.b64encode(message.encode('utf-8')).decode('utf-8')

def send_hl7_message(message, endpoint, api_key=None, method="POST"):
    """Send HL7 message to REST API endpoint"""
    
    # Prepare message for sending
    encoded_message = encode_hl7_message(message)
    
    # Extract message type (MSH-9) for logging
    message_lines = message.split('\n')
    if message_lines and message_lines[0].startswith('MSH|'):
        msh_fields = message_lines[0].split('|')
        if len(msh_fields) > 9:
            message_type = msh_fields[8]
        else:
            message_type = "Unknown"
    else:
        message_type = "Unknown"
    
    # Prepare request data
    payload = {
        "message": encoded_message,
        "messageType": message_type,
        "sendTime": datetime.now().isoformat()
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Add API key if provided
    if api_key:
        headers["X-API-Key"] = api_key
    
    try:
        # Send request to endpoint
        if method.upper() == "POST":
            response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
        else:
            response = requests.put(endpoint, data=json.dumps(payload), headers=headers)
        
        # Process response
        if response.status_code in [200, 201, 202]:
            print(f"Successfully sent {message_type} message. Status: {response.status_code}")
            try:
                resp_data = response.json()
                print(f"Response: {json.dumps(resp_data, indent=2)}")
                return True
            except:
                print(f"Response: {response.text}")
                return True
        else:
            print(f"Failed to send message. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Send HL7 v2.3 messages to REST API')
    parser.add_argument('--input', type=str, required=True, help='Input file containing HL7 messages')
    parser.add_argument('--endpoint', type=str, default=DEFAULT_ENDPOINT, help='REST API endpoint')
    parser.add_argument('--apikey', type=str, default=DEFAULT_API_KEY, help='API key for authentication')
    parser.add_argument('--method', type=str, choices=['POST', 'PUT'], default='POST', help='HTTP method to use')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between messages in seconds')
    
    args = parser.parse_args()
    
    print(f"Reading HL7 messages from {args.input}...")
    messages = read_hl7_messages(args.input)
    
    if not messages:
        print("No messages found in the input file.")
        return
    
    print(f"Found {len(messages)} HL7 messages. Sending to {args.endpoint}...")
    
    success_count = 0
    
    for i, message in enumerate(messages):
        print(f"\nSending message {i+1}/{len(messages)}...")
        if send_hl7_message(message, args.endpoint, args.apikey, args.method):
            success_count += 1
        
        # Add delay between messages
        if i < len(messages) - 1:
            time.sleep(args.delay)
    
    print(f"\nSending complete. Successfully sent {success_count}/{len(messages)} messages.")

if __name__ == "__main__":
    main() 