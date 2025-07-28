#!/bin/bash

# Check status of all services for the appointment confirmation agent

echo "🔍 Checking Appointment Confirmation Agent Services..."
echo "=================================================="

# Check Token Server
echo -e "\n📝 Token Server (Port 8002):"
if lsof -i :8002 > /dev/null 2>&1; then
    echo "✅ Token Server is running on port 8002"
    curl -s http://localhost:8002/ | jq . 2>/dev/null || echo "   (Health check response)"
else
    echo "❌ Token Server is NOT running"
    echo "   Start with: cd token_server && ./start_token_server.sh"
fi

# Check Frontend
echo -e "\n🌐 Frontend (Port 3000):"
if lsof -i :3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running on port 3000"
else
    echo "❌ Frontend is NOT running"
    echo "   Start with: cd frontend && ./start_frontend.sh"
fi

# Check for agent process
echo -e "\n🤖 LiveKit Agent:"
if pgrep -f "appointment_agent.py" > /dev/null 2>&1; then
    echo "✅ LiveKit Agent appears to be running"
    echo "   Check logs: tail -f logs/appointment_agent.log"
else
    echo "❌ LiveKit Agent is NOT running"
    echo "   Start with: ./start_agent.sh"
fi

# Check environment
echo -e "\n🔧 Environment Check:"
if [ -f .env ]; then
    echo "✅ .env file exists"
    # Check for required keys
    if grep -q "LIVEKIT_API_KEY" .env && grep -q "OPENAI_API_KEY" .env && grep -q "DEEPGRAM_API_KEY" .env; then
        echo "✅ Required API keys appear to be configured"
    else
        echo "⚠️  Some API keys may be missing in .env"
    fi
else
    echo "❌ .env file not found!"
fi

echo -e "\n=================================================="
echo "📋 Quick Start Commands:"
echo "1. Terminal 1: cd token_server && ./start_token_server.sh"
echo "2. Terminal 2: ./start_agent.sh"
echo "3. Terminal 3: cd frontend && ./start_frontend.sh"
echo "4. Open browser: http://localhost:3000"