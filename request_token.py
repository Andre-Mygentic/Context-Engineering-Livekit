#!/usr/bin/env python3
"""
Simple script to request a token from the LiveKit token server.

Usage:
    python request_token.py [--email EMAIL] [--name NAME] [--room ROOM]
    
Examples:
    python request_token.py
    python request_token.py --email john@example.com --name "John Doe"
    python request_token.py --room "appointment-123"
"""

import argparse
import requests
import json
import sys
from datetime import datetime


def request_token(
    server_url: str,
    email: str,
    full_name: str,
    user_id: str = None,
    room_name: str = None
):
    """Request a token from the token server."""
    
    # Generate user_id from email if not provided
    if not user_id:
        user_id = f"user-{email.split('@')[0]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Prepare request data
    data = {
        "user_email": email,
        "full_name": full_name,
        "user_id": user_id
    }
    
    # Add room name if provided
    if room_name:
        data["room_name"] = room_name
    
    print(f"\n🔐 Requesting token from: {server_url}/token")
    print(f"📧 Email: {email}")
    print(f"👤 Name: {full_name}")
    print(f"🆔 User ID: {user_id}")
    if room_name:
        print(f"🏠 Room: {room_name}")
    print("-" * 50)
    
    try:
        # Make request
        response = requests.post(
            f"{server_url}/token",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            token = result.get("token", "")
            room = result.get("room_name", "")
            
            print(f"\n✅ Token generated successfully!")
            print(f"\n🏠 Room Name: {room}")
            print(f"\n🔑 Token (first 100 chars):")
            print(f"   {token[:100]}...")
            print(f"\n📏 Token Length: {len(token)} characters")
            
            # Decode token header to show some info
            try:
                import base64
                header = token.split('.')[0]
                # Add padding if needed
                header += '=' * (4 - len(header) % 4)
                decoded_header = base64.b64decode(header)
                print(f"\n🔍 Token Header: {decoded_header.decode('utf-8')}")
            except:
                pass
            
            print(f"\n💡 Use this token to join the LiveKit room: {room}")
            print(f"\n📋 Full Token (for copying):")
            print(f"{token}")
            
            return token, room
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Could not connect to token server at {server_url}")
        print("   Make sure the token server is running:")
        print("   ./start_token_server.sh")
        return None, None
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None, None


def main():
    parser = argparse.ArgumentParser(
        description="Request a token from the LiveKit token server"
    )
    parser.add_argument(
        "--server",
        default="http://localhost:8002",
        help="Token server URL (default: http://localhost:8002)"
    )
    parser.add_argument(
        "--email",
        default="test@example.com",
        help="User email address"
    )
    parser.add_argument(
        "--name",
        default="Test User",
        help="User full name"
    )
    parser.add_argument(
        "--user-id",
        help="User ID (auto-generated if not provided)"
    )
    parser.add_argument(
        "--room",
        help="Specific room name to join (auto-generated if not provided)"
    )
    
    args = parser.parse_args()
    
    # Request token
    token, room = request_token(
        server_url=args.server,
        email=args.email,
        full_name=args.name,
        user_id=args.user_id,
        room_name=args.room
    )
    
    # Exit with appropriate code
    sys.exit(0 if token else 1)


if __name__ == "__main__":
    main()