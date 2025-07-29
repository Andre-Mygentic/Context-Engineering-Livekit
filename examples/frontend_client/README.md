# Frontend Client for LiveKit Appointment Agent

This guide explains how to set up a frontend client to test and interact with the LiveKit Appointment Confirmation Agent.

## Overview

The frontend client provides a web interface for:
- Initiating calls with the appointment agent
- Testing different conversation scenarios
- Monitoring agent responses
- Debugging voice interactions

## Getting the Frontend Client

### Option 1: Use the LiveKit Agent Playground (Recommended for Testing)

The easiest way to test your agent is using the official LiveKit Agent Playground:

1. **Visit the Playground:**
   - Go to https://agent-playground.livekit.io/
   - Or clone locally: `git clone https://github.com/livekit/agent-playground`

2. **Configure Connection:**
   - Enter your LiveKit Cloud URL
   - Use the token from your token server
   - Connect to a room

### Option 2: Use the Included Frontend (Customized for Appointments)

We've included a customized frontend based on `agent-starter-react` in the main project that's already configured for appointment testing:

```bash
cd frontend/
npm install
npm run dev
```

Access at http://localhost:3000

### Option 3: Clone LiveKit's agent-starter-react (Original Source)

This project's frontend was based on the official LiveKit React starter. To start fresh:

```bash
git clone https://github.com/livekit-examples/agent-starter-react.git
cd agent-starter-react
npm install
```

**Note:** The frontend included in this project is a customized version of agent-starter-react specifically tailored for appointment confirmation testing.

## Configuration

### 1. Environment Setup

Create a `.env.local` file in the frontend directory:

```env
# LiveKit Server Configuration (for server-side token generation if not using external token server)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# Token Server URL (for client-side token requests)
NEXT_PUBLIC_TOKEN_SERVER_URL=http://localhost:8002

# Optional: App Configuration
NEXT_PUBLIC_APP_CONFIG_ENDPOINT=
SANDBOX_ID=

# Optional: Agent Configuration
NEXT_PUBLIC_AGENT_ROOM_PREFIX=appointment-test-
```

**Note:** If you're using the external token server (recommended), you only need `NEXT_PUBLIC_TOKEN_SERVER_URL`. The LiveKit credentials (`LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`) should be kept on the token server for security.

### 2. Token Server Integration

The frontend needs to authenticate with LiveKit. Update the token fetching logic:

```typescript
// app/api/token/route.ts or similar
export async function POST(request: Request) {
  const { roomName, participantName } = await request.json();
  
  const response = await fetch(`${process.env.NEXT_PUBLIC_TOKEN_SERVER_URL}/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      room_name: roomName || `appointment-test-${Date.now()}`,
      participant_name: participantName || `user-${Date.now()}`,
      metadata: JSON.stringify({ role: 'participant' })
    }),
  });

  const data = await response.json();
  return Response.json(data);
}
```

### 3. Customize for Appointment Testing

Add appointment-specific UI elements:

```typescript
// components/AppointmentTestPanel.tsx
export function AppointmentTestPanel() {
  const scenarios = [
    { id: 'confirm', label: 'Confirm Appointment', action: 'Yes, I\'ll be there' },
    { id: 'reschedule', label: 'Request Reschedule', action: 'I need to reschedule' },
    { id: 'confused', label: 'Act Confused', action: 'What appointment?' },
    { id: 'wrong-person', label: 'Wrong Person', action: 'This isn\'t the right person' },
  ];

  return (
    <div className="appointment-test-panel">
      <h3>Test Scenarios</h3>
      {scenarios.map(scenario => (
        <button key={scenario.id} onClick={() => handleScenario(scenario)}>
          {scenario.label}
        </button>
      ))}
    </div>
  );
}
```

## Running the Frontend

### Development Mode

1. **Start the token server first:**
   ```bash
   cd token_server
   python token_server.py
   ```

2. **Start the appointment agent:**
   ```bash
   cd agent
   python appointment_agent.py dev
   ```

3. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

4. **Access the application:**
   - Open http://localhost:3000
   - The frontend will automatically request a token
   - Click "Connect" to join a room with the agent

### Production Mode

For production deployment:

```bash
# Build the frontend
npm run build

# Start production server
npm start

# Or deploy to Vercel/Netlify/etc
vercel --prod
```

## Key Features to Implement

### 1. Connection Status Display
```typescript
const connectionState = room.state;
const isConnected = connectionState === 'connected';
```

### 2. Audio Controls
```typescript
<button onClick={() => room.localParticipant.setMicrophoneEnabled(!micEnabled)}>
  {micEnabled ? 'Mute' : 'Unmute'}
</button>
```

### 3. Call Transcript
```typescript
const [transcript, setTranscript] = useState<Message[]>([]);

// Listen for transcription events
room.on('transcriptionReceived', (transcription) => {
  setTranscript(prev => [...prev, transcription]);
});
```

### 4. Metrics Display
```typescript
useEffect(() => {
  const fetchMetrics = async () => {
    const response = await fetch('http://localhost:8081/metrics/json');
    const data = await response.json();
    setMetrics(data);
  };
  
  const interval = setInterval(fetchMetrics, 5000);
  return () => clearInterval(interval);
}, []);
```

## Testing the Integration

### 1. Basic Connection Test
- Start all services (token server, agent, frontend)
- Open frontend and click "Connect"
- Verify agent joins the room
- Check for greeting message

### 2. Conversation Flow Test
- Wait for agent's greeting
- Respond with "Yes, I'll be there"
- Verify agent confirms the appointment
- Check metrics are updated

### 3. Error Scenarios
- Test with invalid token
- Test network disconnection
- Test audio permission denial

## Troubleshooting

### Common Issues

1. **"Failed to get token"**
   - Ensure token server is running on port 8002
   - Check CORS settings in token server
   - Verify environment variables

2. **"Agent not joining room"**
   - Check agent is running and connected to LiveKit
   - Verify room name pattern matches
   - Check agent logs for errors

3. **"No audio from agent"**
   - Ensure browser has microphone permissions
   - Check audio output device settings
   - Verify agent TTS configuration

4. **"High latency"**
   - Check network connection
   - Verify LiveKit server region
   - Monitor agent response times

### Debug Mode

Enable debug logging in the frontend:

```typescript
// Add to your LiveKit room configuration
const room = new Room({
  logLevel: LogLevel.debug,
  // ... other options
});
```

## Advanced Configuration

### Custom Room Names
```typescript
const roomName = `appointment-${userId}-${Date.now()}`;
```

### Participant Metadata
```typescript
const metadata = {
  appointmentId: '12345',
  patientName: 'John Doe',
  appointmentTime: '2024-07-30T14:30:00Z'
};
```

### WebRTC Configuration
```typescript
const room = new Room({
  rtcConfig: {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' }
    ]
  }
});
```

## Resources

- [LiveKit React SDK Docs](https://docs.livekit.io/client-sdk-js/)
- [Agent Playground Source](https://github.com/livekit/agent-playground)
- [LiveKit Examples](https://github.com/livekit-examples)
- [Next.js Documentation](https://nextjs.org/docs)

## Next Steps

1. **Customize UI** for your specific use case
2. **Add authentication** for production
3. **Implement analytics** tracking
4. **Create test automation** scripts
5. **Deploy to production** hosting