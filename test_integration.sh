#!/bin/bash

echo "🧪 Testing Appointment Confirmation Agent Integration"
echo "==================================================="

# Test 1: Token Server Health Check
echo -e "\n1️⃣ Testing Token Server:"
HEALTH_RESPONSE=$(curl -s http://localhost:8002/)
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo "✅ Token server health check passed"
else
    echo "❌ Token server health check failed"
    exit 1
fi

# Test 2: Token Generation
echo -e "\n2️⃣ Testing Token Generation:"
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8002/token \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "integration-test@example.com",
    "full_name": "Integration Test User",
    "user_id": "test-user-123",
    "room_name": "test-room-integration"
  }')

if [[ $TOKEN_RESPONSE == *"token"* ]]; then
    echo "✅ Token generation successful"
    echo "   Room: $(echo $TOKEN_RESPONSE | jq -r .room_name)"
else
    echo "❌ Token generation failed"
    echo "   Response: $TOKEN_RESPONSE"
    exit 1
fi

# Test 3: Frontend Connection Details API
echo -e "\n3️⃣ Testing Frontend API:"
FRONTEND_RESPONSE=$(curl -s http://localhost:3000/api/connection-details)
if [[ $FRONTEND_RESPONSE == *"participantToken"* ]]; then
    echo "✅ Frontend API is working"
    echo "   Room: $(echo $FRONTEND_RESPONSE | jq -r .roomName)"
else
    echo "❌ Frontend API failed"
    echo "   Response: $FRONTEND_RESPONSE"
    exit 1
fi

# Test 4: Agent Status
echo -e "\n4️⃣ Checking Agent Status:"
if pgrep -f "appointment_agent.py" > /dev/null; then
    echo "✅ Agent process is running"
    LATEST_LOG=$(tail -1 logs/appointment_agent.log)
    echo "   Latest log: ${LATEST_LOG:0:80}..."
else
    echo "❌ Agent is not running"
    exit 1
fi

echo -e "\n==================================================="
echo "✅ All integration tests passed!"
echo ""
echo "📱 Ready for manual testing:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Click 'Test Appointment Call'"
echo "3. Allow microphone access"
echo "4. Start talking when the agent greets you"
echo ""
echo "📋 Test scenarios to try:"
echo "- Say 'Hi, this is John' when greeted"
echo "- Confirm the appointment: 'Yes, I'll be there'"
echo "- Request reschedule: 'I need to reschedule'"
echo "- Act confused: 'I don't have any appointment'"