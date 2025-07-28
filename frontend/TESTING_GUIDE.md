# Testing Guide for Appointment Confirmation Agent

This guide explains how to test the appointment confirmation voice agent using the React frontend.

## Prerequisites

Before testing, ensure all three components are running:

1. **Token Server** (port 8002)
2. **LiveKit Agent** (connects to LiveKit cloud)
3. **React Frontend** (port 3000)

## Quick Start

### 1. Start All Services

Open three terminal windows:

**Terminal 1 - Token Server:**
```bash
cd token_server
./start_token_server.sh
```

**Terminal 2 - LiveKit Agent:**
```bash
./start_agent.sh
```

**Terminal 3 - Frontend:**
```bash
cd frontend
./start_frontend.sh
```

### 2. Access the Frontend

Open http://localhost:3000 in your browser.

## Testing Scenarios

### Scenario 1: Happy Path - Confirm Appointment
1. Click "Test Appointment Call"
2. When the agent greets you, say: "Hi, this is [your name]"
3. When asked about the appointment, say: "Yes, I'll be there"
4. The agent should confirm and end the call politely

### Scenario 2: Reschedule Request
1. Start a new call
2. When asked about the appointment, say: "I need to reschedule"
3. The agent should acknowledge and provide next steps
4. Note how the agent handles this gracefully

### Scenario 3: Confusion/Wrong Person
1. Start a new call
2. When greeted, say: "I don't have any appointment"
3. Observe how the agent clarifies the situation
4. The agent should handle confusion professionally

### Scenario 4: Interruption Testing
1. Start a new call
2. Interrupt the agent mid-sentence
3. The agent should stop and listen
4. Response should be natural, not robotic

### Scenario 5: Background Noise
1. Start a call in a noisy environment
2. Or play background audio during the call
3. Check if the agent can still understand you
4. Voice should remain clear and professional

## What to Look For

### Voice Quality
- [ ] Agent sounds natural, not robotic
- [ ] Uses filler phrases like "um" and "let me see"
- [ ] Has natural pauses in speech
- [ ] Voice speed is conversational

### Conversation Flow
- [ ] Responds quickly (< 200ms latency)
- [ ] Handles interruptions gracefully
- [ ] Doesn't repeat exact same phrases
- [ ] Acknowledges what you say ("I see", "mm-hmm")

### Professional Behavior
- [ ] Maintains receptionist persona
- [ ] Stays polite even when confused
- [ ] Provides clear information
- [ ] Ends calls appropriately

## Troubleshooting

### "Connection Failed" Error
1. Check token server is running on port 8002
2. Verify agent is connected to LiveKit
3. Check browser console for errors

### No Audio
1. Allow microphone permissions
2. Check system audio settings
3. Refresh the page and try again

### Agent Not Responding
1. Check agent logs: `tail -f logs/appointment_agent.log`
2. Verify OpenAI API key is valid
3. Restart the agent

### High Latency
1. Check internet connection
2. Verify all services are local
3. Monitor CPU usage

## Advanced Testing

### Custom Appointment Details
Modify `agent/appointment_agent.py` to test different scenarios:
- Different appointment types
- Various times and dates
- Multiple providers
- Different locations

### Performance Testing
1. Make multiple concurrent calls
2. Test long conversations (5+ minutes)
3. Monitor resource usage
4. Check for memory leaks

## Debugging Tips

### View Logs
```bash
# Token server logs
tail -f logs/token_server.log

# Agent logs
tail -f logs/appointment_agent.log

# Frontend logs (in browser)
Open Developer Console (F12)
```

### Test Token Generation
```bash
python token_server/request_token.py --email test@clinic.com --name "Test Patient"
```

### Verify Connection
The frontend shows connection status in the UI. Green = connected, Red = disconnected.

## Reporting Issues

When reporting issues, include:
1. Which scenario you were testing
2. Exact words spoken
3. Agent's response
4. Any error messages
5. Browser console logs
6. Server logs if available