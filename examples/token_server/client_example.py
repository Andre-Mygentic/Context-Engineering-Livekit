#!/usr/bin/env python
"""
Example client for the LiveKit token server.

This demonstrates how to request tokens from the server
and use them to connect to LiveKit rooms.
"""

import asyncio
import json
import os
from typing import Optional

import aiohttp
from livekit import rtc


class TokenClient:
    """Client for requesting tokens from the token server."""
    
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url.rstrip("/")
    
    async def get_token(
        self,
        room_name: str,
        participant_name: str,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Request a token from the server.
        
        Args:
            room_name: Name of the room to join
            participant_name: Name of the participant
            metadata: Optional metadata dictionary
            
        Returns:
            Token response with token, url, and expiry
        """
        async with aiohttp.ClientSession() as session:
            payload = {
                "room_name": room_name,
                "participant_name": participant_name,
            }
            
            if metadata:
                payload["metadata"] = json.dumps(metadata)
            
            async with session.post(
                f"{self.server_url}/token",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def check_health(self) -> bool:
        """Check if the token server is healthy."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/health") as response:
                    return response.status == 200
        except Exception:
            return False


async def example_usage():
    """Demonstrate token client usage."""
    # Create client
    client = TokenClient()
    
    # Check server health
    print("Checking server health...")
    is_healthy = await client.check_health()
    if not is_healthy:
        print("❌ Token server is not healthy!")
        return
    print("✅ Token server is healthy")
    
    # Request a token
    print("\nRequesting token...")
    try:
        token_response = await client.get_token(
            room_name="test-room-123",
            participant_name="test-user",
            metadata={"role": "participant", "source": "example"}
        )
        
        print(f"✅ Got token!")
        print(f"   Token: {token_response['token'][:50]}...")
        print(f"   URL: {token_response['url']}")
        print(f"   Expires: {token_response['expires_at']}")
        
        # Example: Connect to room with the token
        # room = rtc.Room()
        # await room.connect(
        #     token_response['url'],
        #     token_response['token']
        # )
        
    except aiohttp.ClientError as e:
        print(f"❌ Failed to get token: {e}")


def example_sync_usage():
    """Example using requests library (synchronous)."""
    import requests
    
    # Check health
    try:
        response = requests.get("http://localhost:8080/health")
        response.raise_for_status()
        print("✅ Server is healthy")
    except requests.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Get token
    try:
        response = requests.post(
            "http://localhost:8080/token",
            json={
                "room_name": "sync-test-room",
                "participant_name": "sync-user",
            }
        )
        response.raise_for_status()
        token_data = response.json()
        print(f"✅ Got token: {token_data['token'][:50]}...")
        
    except requests.RequestException as e:
        print(f"❌ Failed to get token: {e}")


if __name__ == "__main__":
    print("=== LiveKit Token Client Example ===\n")
    
    # Run async example
    print("Running async example:")
    asyncio.run(example_usage())
    
    print("\n" + "="*40 + "\n")
    
    # Run sync example
    print("Running sync example:")
    example_sync_usage()