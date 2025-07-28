# LiveKit Token Server

A FastAPI-based JWT token server for LiveKit authentication. This server generates secure tokens that allow clients to join LiveKit rooms with appropriate permissions.

## Quick Start

### 1. Start the Token Server
```bash
./start_token_server.sh
```

Or manually:
```bash
source venv/bin/activate
python token_server.py
```

The server will start on port 8002 by default (configurable via `TOKEN_SERVER_PORT` in `.env`).

### 2. Request a Token

Use the provided script:
```bash
python request_token.py
```

With custom parameters:
```bash
python request_token.py --email john@example.com --name "John Doe" --room "appointment-123"
```

## API Endpoints

### POST `/token`
Generate a JWT token for LiveKit room access.

**Request Body:**
```json
{
  "user_email": "john@example.com",
  "full_name": "John Doe",
  "user_id": "user-123",
  "room_name": "appointment-456"  // Optional
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "room_name": "appointment-456"
}
```

### POST `/validate`
Validate and decode a LiveKit JWT token.

**Query Parameter:**
- `token`: The JWT token to validate

**Response:**
```json
{
  "valid": true,
  "identity": "user-123",
  "name": "John Doe",
  "room": "appointment-456",
  "expires_at": "2025-07-29T15:37:23"
}
```

### GET `/`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "LiveKit Token Server",
  "version": "1.0.0",
  "timestamp": "2025-07-28T15:37:23"
}
```

## Configuration

Configure via environment variables in `.env`:

```bash
# Token Server
TOKEN_SERVER_PORT=8002
CORS_ORIGINS=http://localhost:3000,http://localhost:3005
TOKEN_EXPIRY_HOURS=24

# LiveKit (required)
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
```

## Token Permissions

Generated tokens include the following LiveKit grants:
- `roomJoin`: Can join the specified room
- `canPublish`: Can publish audio/video streams
- `canSubscribe`: Can receive audio/video streams
- `canUpdateOwnMetadata`: Can update their own metadata

## Testing

### Basic Test Suite
```bash
python test_token_server.py
```

### Manual Token Request
```bash
# Default test user
python request_token.py

# Custom user for appointment
python request_token.py \
  --email patient@example.com \
  --name "Jane Smith" \
  --room "dr-johnson-2pm-cleaning"
```

## Frontend Integration

Example JavaScript/TypeScript code to use the token:

```javascript
// Request token from your backend
const response = await fetch('http://localhost:8002/token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_email: 'john@example.com',
    full_name: 'John Doe',
    user_id: 'user-123'
  })
});

const { token, room_name } = await response.json();

// Use token to connect to LiveKit
import { Room } from 'livekit-client';

const room = new Room();
await room.connect('wss://your-livekit-server.com', token);
console.log(`Connected to room: ${room_name}`);
```

## Security Notes

- Never expose your `LIVEKIT_API_SECRET` to frontend clients
- Always validate user identity before generating tokens
- Consider adding authentication middleware in production
- Use HTTPS in production environments
- Restrict CORS origins to specific domains in production

## Troubleshooting

### Port Already in Use
If port 8002 is occupied, change it in `.env`:
```bash
TOKEN_SERVER_PORT=8003
```

### Connection Refused
Ensure the server is running:
```bash
ps aux | grep token_server
```

### Invalid Token
Check that:
1. `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` are correctly set
2. Token hasn't expired (default 24 hours)
3. Room name matches between token and connection attempt