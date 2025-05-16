#!/usr/bin/env python
"""
HL7 v2.3 Message Sender (MLLP)

This script sends HL7 v2.3 messages using MLLP (Minimal Lower Layer Protocol) over TCP/IP.
"""
import os
import sys
import time
import socket
import json
import argparse
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default settings if not specified
DEFAULT_HOST = os.getenv("HL7_SERVER_HOST", "localhost")
DEFAULT_PORT = int(os.getenv("HL7_SERVER_PORT", "2575"))
DEFAULT_ENDPOINT = os.getenv("HL7_API_ENDPOINT", "http://localhost:3000/api/hl7")
DEFAULT_API_KEY = os.getenv("HL7_API_KEY", "")
DEFAULT_ACK_TIMEOUT = 10  # seconds

# MLLP control characters
MLLP_START_BLOCK = b'\x0b'  # <VT>
MLLP_END_BLOCK = b'\x1c\x0d'  # <FS><CR>

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
    """Encode HL7 message to Base64 for transmission via HTTP"""
    return base64.b64encode(message.encode('utf-8')).decode('utf-8')

def send_http_message(message, endpoint, api_key=None):
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
        print(f"Sending {message_type} message to REST API at {endpoint}...")
        response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
        
        # Process response
        if response.status_code in [200, 201, 202]:
            print(f"Successfully sent message. Status: {response.status_code}")
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
        print(f"Error sending message via HTTP: {e}")
        return False

def send_mllp_message(message, host, port, timeout=DEFAULT_ACK_TIMEOUT):
    """Send HL7 message using MLLP over TCP/IP and wait for ACK"""
    
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
    
    # Replace \n with \r as per HL7 standard
    message = message.replace('\n', '\r')
    
    # Convert to bytes
    message_bytes = message.encode('utf-8')
    
    # Create MLLP frame
    mllp_message = MLLP_START_BLOCK + message_bytes + MLLP_END_BLOCK
    
    try:
        # Create socket connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        
        print(f"Connected to MLLP server at {host}:{port}")
        print(f"Sending {message_type} message...")
        
        # Send the message
        s.sendall(mllp_message)
        
        # Wait for ACK
        print("Waiting for acknowledgment...")
        ack_data = b''
        
        # Read until we get the MLLP end block
        while True:
            chunk = s.recv(1024)
            if not chunk:
                break
            ack_data += chunk
            if MLLP_END_BLOCK in ack_data:
                break
                
        # Process ACK
        if ack_data:
            # Strip MLLP control characters
            if ack_data.startswith(MLLP_START_BLOCK):
                ack_data = ack_data[1:]
            if ack_data.endswith(MLLP_END_BLOCK):
                ack_data = ack_data[:-2]
                
            # Decode ACK
            ack_message = ack_data.decode('utf-8')
            ack_segments = ack_message.split('\r')
            
            if len(ack_segments) >= 2:
                msa_segment = ack_segments[1]
                msa_fields = msa_segment.split('|')
                
                if len(msa_fields) >= 2:
                    ack_code = msa_fields[1]
                    ack_text = msa_fields[2] if len(msa_fields) > 2 else ""
                    
                    if ack_code == "AA":
                        print(f"Message accepted: {ack_text}")
                        return True
                    elif ack_code == "AR":
                        print(f"Message rejected: {ack_text}")
                        return False
                    elif ack_code == "AE":
                        print(f"Error processing message: {ack_text}")
                        return False
                    else:
                        print(f"Unknown acknowledgment code: {ack_code}")
                        return False
            
            print(f"Received ACK: {ack_message}")
            return True
        else:
            print("No acknowledgment received")
            return False
    
    except socket.timeout:
        print(f"Timeout waiting for acknowledgment after {timeout} seconds")
        return False
    except ConnectionRefusedError:
        print(f"Connection refused to {host}:{port}")
        return False
    except Exception as e:
        print(f"Error sending message: {e}")
        return False
    finally:
        # Always close the socket
        try:
            s.close()
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description='Send HL7 v2.3 messages using MLLP or HTTP')
    parser.add_argument('--input', type=str, required=True, help='Input file containing HL7 messages')
    parser.add_argument('--host', type=str, default=DEFAULT_HOST, help='HL7 MLLP server hostname or IP')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='HL7 MLLP server port')
    parser.add_argument('--timeout', type=int, default=DEFAULT_ACK_TIMEOUT, help='Timeout for acknowledgment in seconds')
    parser.add_argument('--http', action='store_true', help='Use HTTP instead of MLLP for sending messages')
    parser.add_argument('--endpoint', type=str, default=DEFAULT_ENDPOINT, help='REST API endpoint (when using --http)')
    parser.add_argument('--apikey', type=str, default=DEFAULT_API_KEY, help='API key for authentication (when using --http)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between messages in seconds')
    
    args = parser.parse_args()
    
    print(f"Reading HL7 messages from {args.input}...")
    messages = read_hl7_messages(args.input)
    
    if not messages:
        print("No messages found in the input file.")
        return
    
    if args.http:
        print(f"Found {len(messages)} HL7 messages. Sending to REST API at {args.endpoint}...")
    else:
        print(f"Found {len(messages)} HL7 messages. Sending to MLLP server at {args.host}:{args.port}...")
    
    success_count = 0
    
    for i, message in enumerate(messages):
        print(f"\nSending message {i+1}/{len(messages)}...")
        
        if args.http:
            success = send_http_message(message, args.endpoint, args.apikey)
        else:
            success = send_mllp_message(message, args.host, args.port, args.timeout)
            
        if success:
            success_count += 1
        
        # Add delay between messages
        if i < len(messages) - 1:
            time.sleep(args.delay)
    
    print(f"\nSending complete. Successfully sent {success_count}/{len(messages)} messages.")

if __name__ == "__main__":
    main() 