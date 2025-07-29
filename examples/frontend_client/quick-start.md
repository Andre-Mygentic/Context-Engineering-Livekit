# Quick Start Guide - Frontend Client

## 5-Minute Setup

### Prerequisites
- Node.js 16+ installed
- Token server running (see token_server example)
- LiveKit appointment agent running

### Step 1: Get the Frontend

```bash
# Option A: Use the included frontend (recommended)
cd ../../frontend
npm install

# Option B: Clone LiveKit's original starter
git clone https://github.com/livekit-examples/agent-starter-react.git
cd agent-starter-react
npm install
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env.local

# Edit with your values
# - Set your LiveKit URL
# - Ensure token server URL is correct (default: http://localhost:8002)
```

### Step 3: Start Everything

Terminal 1 - Token Server:
```bash
cd token_server
python token_server.py
```

Terminal 2 - Agent:
```bash
cd agent
python appointment_agent.py dev
```

Terminal 3 - Frontend:
```bash
cd frontend
npm run dev
```

### Step 4: Test

1. Open http://localhost:3000
2. Click "Connect" or "Start Call"
3. Wait for agent greeting
4. Try saying "Yes, I'll be there" to confirm

## Quick Customization

### Change Agent Room Pattern

In your agent code:
```python
# Only join rooms starting with "appointment-test-"
if not ctx.room.name.startswith("appointment-test-"):
    return
```

### Add Test Buttons

In your frontend:
```jsx
<button onClick={() => say("Yes, I'll be there")}>
  Confirm Appointment
</button>
<button onClick={() => say("I need to reschedule")}>
  Request Reschedule
</button>
```

### Custom Token Logic

Modify `/api/token/route.ts`:
```typescript
// Add custom metadata
const metadata = {
  appointmentId: generateId(),
  testScenario: 'confirmation',
  timestamp: Date.now()
};
```

## Common Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Type checking
npm run type-check
```

## Minimal HTML Example

If you just want a basic HTML page to test:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Appointment Agent Test</title>
    <script src="https://unpkg.com/livekit-client/dist/livekit-client.umd.min.js"></script>
</head>
<body>
    <h1>Appointment Agent Test</h1>
    <button id="connect">Connect to Agent</button>
    <div id="status"></div>

    <script>
        const TOKEN_SERVER = 'http://localhost:8002';
        const LIVEKIT_URL = 'wss://your-project.livekit.cloud';

        document.getElementById('connect').onclick = async () => {
            // Get token
            const response = await fetch(`${TOKEN_SERVER}/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    room_name: `appointment-test-${Date.now()}`,
                    participant_name: `user-${Date.now()}`
                })
            });
            
            const { token } = await response.json();
            
            // Connect to room
            const room = new LivekitClient.Room();
            await room.connect(LIVEKIT_URL, token);
            
            // Enable microphone
            await room.localParticipant.setMicrophoneEnabled(true);
            
            document.getElementById('status').innerText = 'Connected! Speak to the agent.';
        };
    </script>
</body>
</html>
```

Save as `test.html` and open in browser!