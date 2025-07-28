"""
Test script for the LiveKit token server.

This script tests the token generation and validation endpoints.
"""

import requests
import json
import sys


def test_health_check(base_url):
    """Test the health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{base_url}/")
    
    if response.status_code == 200:
        print("✅ Health check passed")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
        print(f"   Response: {response.text}")
    return response.status_code == 200


def test_token_generation(base_url):
    """Test token generation endpoint."""
    print("\nTesting token generation...")
    
    # Test data
    test_user = {
        "user_email": "test@example.com",
        "full_name": "Test User",
        "user_id": "test-user-123",
        "room_name": "test-appointment-room"
    }
    
    response = requests.post(
        f"{base_url}/token",
        json=test_user,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Token generation passed")
        print(f"   Room: {data['room_name']}")
        print(f"   Token length: {len(data['token'])} characters")
        print(f"   Token preview: {data['token'][:50]}...")
        return data.get("token")
    else:
        print(f"❌ Token generation failed: {response.status_code}")
        print(f"   Response: {response.text}")
    return None


def test_token_validation(base_url, token):
    """Test token validation endpoint."""
    print("\nTesting token validation...")
    
    if not token:
        print("⚠️  No token to validate, skipping...")
        return False
    
    response = requests.post(
        f"{base_url}/validate",
        params={"token": token}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("valid"):
            print("✅ Token validation passed")
            print(f"   Identity: {data.get('identity')}")
            print(f"   Name: {data.get('name')}")
            print(f"   Room: {data.get('room')}")
            print(f"   Expires: {data.get('expires_at')}")
        else:
            print("❌ Token is invalid")
            print(f"   Error: {data.get('error')}")
        return data.get("valid", False)
    else:
        print(f"❌ Token validation failed: {response.status_code}")
        print(f"   Response: {response.text}")
    return False


def test_cors_headers(base_url):
    """Test CORS headers."""
    print("\nTesting CORS headers...")
    
    response = requests.options(
        f"{base_url}/token",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        }
    )
    
    cors_headers = {
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers"
    }
    
    found_headers = set(response.headers.keys()) & cors_headers
    
    if found_headers:
        print("✅ CORS headers present")
        for header in found_headers:
            print(f"   {header}: {response.headers[header]}")
    else:
        print("❌ CORS headers missing")
    
    return len(found_headers) > 0


def main():
    """Run all tests."""
    # Default to localhost:8001
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
    
    print(f"Testing LiveKit Token Server at {base_url}")
    print("=" * 50)
    
    # Run tests
    health_ok = test_health_check(base_url)
    token = test_token_generation(base_url) if health_ok else None
    validation_ok = test_token_validation(base_url, token) if token else False
    cors_ok = test_cors_headers(base_url) if health_ok else False
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"  Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"  Token Generation: {'✅ PASS' if token else '❌ FAIL'}")
    print(f"  Token Validation: {'✅ PASS' if validation_ok else '❌ FAIL'}")
    print(f"  CORS Headers: {'✅ PASS' if cors_ok else '❌ FAIL'}")
    
    # Exit code
    all_passed = health_ok and token and validation_ok and cors_ok
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()