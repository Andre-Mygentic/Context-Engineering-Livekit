# LiveKit Token Server Example

This example demonstrates how to create a secure token server for LiveKit agents and applications. The token server is responsible for generating JWT tokens that authorize participants to join LiveKit rooms.

## Overview

A token server is essential for production LiveKit deployments because:
- It controls who can access your LiveKit rooms
- It assigns permissions to participants (publish, subscribe, etc.)
- It adds metadata to identify participants
- It prevents unauthorized access to your infrastructure

## Features

- **JWT Token Generation**: Creates secure access tokens for LiveKit
- **CORS Support**: Allows web frontends to request tokens
- **Configurable Expiry**: Set how long tokens remain valid
- **Room Validation**: Ensures room names meet requirements
- **Error Handling**: Proper HTTP status codes and error messages
- **Health Checks**: Monitor server availability

## Prerequisites

- Python 3.8+
- LiveKit API credentials (key and secret)

## Installation

1. Install dependencies:
```bash
pip install fastapi uvicorn livekit-api
```

2. Set environment variables:
```bash
export LIVEKIT_API_KEY="your-api-key"
export LIVEKIT_API_SECRET="your-api-secret"
export LIVEKIT_URL="wss://your-project.livekit.cloud"
```

## Usage

### Starting the Server

```bash
python token_server.py
```

The server will start on `http://localhost:8080` by default.

### Configuration

Configure the server using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `LIVEKIT_API_KEY` | Your LiveKit API key | Required |
| `LIVEKIT_API_SECRET` | Your LiveKit API secret | Required |
| `LIVEKIT_URL` | LiveKit server URL | Required |
| `TOKEN_SERVER_PORT` | Port to run server on | 8080 |
| `CORS_ORIGINS` | Comma-separated allowed origins | http://localhost:3000 |
| `TOKEN_EXPIRY_HOURS` | Token validity duration | 24 |

### API Endpoints

#### POST /token
Generate an access token for a participant.

**Request:**
```json
{
  "room_name": "appointment-test-123",
  "participant_name": "user-456",
  "metadata": "{\"role\": \"participant\"}"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "url": "wss://your-project.livekit.cloud",
  "expires_at": "2024-07-30T12:00:00Z"
}
```

#### GET /health
Check server health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "livekit-token-server",
  "timestamp": "2024-07-29T12:00:00Z"
}
```

## Security Considerations

1. **HTTPS Only**: Always use HTTPS in production
2. **Authentication**: Add authentication to your token endpoint
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Input Validation**: Validate room and participant names
5. **Logging**: Log token generation for audit trails

## Integration Examples

### JavaScript/TypeScript Frontend

```typescript
async function getToken(roomName: string, participantName: string) {
  const response = await fetch('http://localhost:8080/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      room_name: roomName,
      participant_name: participantName,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to get token');
  }

  const data = await response.json();
  return data.token;
}
```

### Python Client

```python
import requests

def get_token(room_name: str, participant_name: str) -> str:
    response = requests.post(
        'http://localhost:8080/token',
        json={
            'room_name': room_name,
            'participant_name': participant_name,
        }
    )
    response.raise_for_status()
    return response.json()['token']
```

## Production Deployment

### Using Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY token_server.py .

EXPOSE 8080

CMD ["python", "token_server.py"]
```

### Environment File

Create a `.env` file for production:
```env
LIVEKIT_API_KEY=your-production-key
LIVEKIT_API_SECRET=your-production-secret
LIVEKIT_URL=wss://your-project.livekit.cloud
TOKEN_SERVER_PORT=8080
CORS_ORIGINS=https://your-app.com,https://www.your-app.com
TOKEN_EXPIRY_HOURS=12
```

### Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name api.your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring

### Health Check Script

```bash
#!/bin/bash
# health_check.sh

HEALTH_URL="http://localhost:8080/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "Token server is healthy"
    exit 0
else
    echo "Token server is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
```

### Logging

The server logs all token generation events:
```
2024-07-29 12:00:00 - token-server - INFO - Token generated for user user-456 in room appointment-test-123
```

## Troubleshooting

### Common Issues

1. **"LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set"**
   - Ensure environment variables are exported before starting the server

2. **CORS errors in browser**
   - Add your frontend URL to CORS_ORIGINS environment variable

3. **Token expired errors**
   - Increase TOKEN_EXPIRY_HOURS or refresh tokens more frequently

4. **Connection refused**
   - Check if the server is running on the correct port
   - Verify firewall settings

## Next Steps

- Add authentication middleware (OAuth, API keys, etc.)
- Implement rate limiting
- Add request logging
- Set up monitoring and alerts
- Deploy to production environment