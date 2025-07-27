# LiveKit Agents Deployment Strategies

This guide covers production deployment patterns, scaling strategies, and best practices for LiveKit Agents.

## Worker Architecture Overview

LiveKit Agents use a **worker pool model** where:
- Workers register with LiveKit server via WebSocket
- Each worker can handle multiple concurrent jobs
- Jobs run in isolated processes for fault tolerance
- No inbound ports required (outbound WebSocket only)

## Container Configuration

### Production Dockerfile
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check endpoint
EXPOSE 8081
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/ || exit 1

# Run the agent
CMD ["python", "agent.py", "start"]
```

### Container Optimization
- **Base Image**: Use python:3.11-slim for optimal size
- **Dependencies**: Install only required system packages
- **Layer Caching**: Order Dockerfile for optimal caching
- **Non-root User**: Run as non-root for security

## Kubernetes Deployment

### Basic Deployment Manifest
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: livekit-agents
  labels:
    app: livekit-agents
spec:
  replicas: 3
  selector:
    matchLabels:
      app: livekit-agents
  template:
    metadata:
      labels:
        app: livekit-agents
    spec:
      containers:
      - name: agent
        image: your-registry/livekit-agent:latest
        ports:
        - containerPort: 8081
          name: health
        env:
        - name: LIVEKIT_URL
          valueFrom:
            secretKeyRef:
              name: livekit-secrets
              key: url
        - name: LIVEKIT_API_KEY
          valueFrom:
            secretKeyRef:
              name: livekit-secrets
              key: api-key
        - name: LIVEKIT_API_SECRET
          valueFrom:
            secretKeyRef:
              name: livekit-secrets
              key: api-secret
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-secrets
              key: openai-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /
            port: 8081
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /
            port: 8081
          initialDelaySeconds: 10
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: livekit-agents
spec:
  selector:
    app: livekit-agents
  ports:
  - port: 8081
    targetPort: 8081
    name: health
```

### Horizontal Pod Autoscaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: livekit-agents-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: livekit-agents
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Environment Management

### Required Environment Variables
```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# AI Provider Configuration
OPENAI_API_KEY=your-openai-key
DEEPGRAM_API_KEY=your-deepgram-key
CARTESIA_API_KEY=your-cartesia-key

# Application Configuration
LOG_LEVEL=INFO
HEALTH_CHECK_PORT=8081
NODE_ENV=production

# Worker Configuration
WORKER_MAX_JOBS=10
WORKER_IDLE_TIMEOUT=300
```

### Secrets Management
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: livekit-secrets
type: Opaque
stringData:
  url: "wss://your-project.livekit.cloud"
  api-key: "your-api-key"
  api-secret: "your-api-secret"
---
apiVersion: v1
kind: Secret
metadata:
  name: ai-secrets
type: Opaque
stringData:
  openai-key: "your-openai-key"
  deepgram-key: "your-deepgram-key"
```

## Scaling Strategies

### Worker Scaling Guidelines
Based on production benchmarks:
- **4 cores per 25 voice agents** (recommended ratio)
- **Memory**: 512MB base + 50MB per concurrent session
- **Network**: 100Kbps per active voice session

### Resource Planning

| Agent Type | CPU/Agent | Memory/Agent | Network/Agent |
|------------|-----------|--------------|---------------|
| Voice Only | 0.16 cores | 50MB | 100Kbps |
| Voice + Tools | 0.2 cores | 75MB | 150Kbps |
| Realtime API | 0.25 cores | 100MB | 200Kbps |
| Multi-Modal | 0.5 cores | 200MB | 500Kbps |

### Auto-scaling Configuration
```python
# Worker configuration for auto-scaling
worker_options = WorkerOptions(
    entrypoint_fnc=entrypoint,
    prewarm_fnc=prewarm,
    max_jobs=10,  # Max concurrent jobs per worker
    shutdown_grace_period=600,  # 10 minutes for graceful shutdown
)
```

## Network Requirements

### Connectivity
- **Outbound Only**: Workers connect to LiveKit via WebSocket
- **No Inbound Ports**: No firewall configuration needed
- **WebSocket Support**: Ensure proxies support WebSocket
- **SSL/TLS**: Always use wss:// for secure connections

### Network Architecture
```
┌─────────────┐     WebSocket      ┌──────────────┐
│   Workers   │ ─────────────────> │ LiveKit Cloud│
└─────────────┘                     └──────────────┘
      ↓                                    ↓
  No inbound                          Dispatches
  connections                            jobs
```

## Monitoring and Observability

### Metrics Collection
```python
from livekit.agents import metrics
import prometheus_client

# Prometheus metrics
job_counter = prometheus_client.Counter(
    'livekit_agent_jobs_total',
    'Total number of jobs processed'
)

job_duration = prometheus_client.Histogram(
    'livekit_agent_job_duration_seconds',
    'Job processing duration'
)

# Collect LiveKit metrics
@session.on("metrics_collected")
def on_metrics_collected(ev):
    metrics.log_metrics(ev.metrics)
    
    # Export to Prometheus
    job_counter.inc()
    job_duration.observe(ev.metrics.duration)
```

### Logging Configuration
```python
import logging
import json

# Structured logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add context fields
        if hasattr(record, 'room_name'):
            log_obj['room_name'] = record.room_name
        if hasattr(record, 'session_id'):
            log_obj['session_id'] = record.session_id
            
        return json.dumps(log_obj)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.root.setLevel(logging.INFO)
logging.root.addHandler(handler)
```

### Health Check Implementation
```python
from aiohttp import web

async def health_check(request):
    """Health check endpoint for container orchestration"""
    # Check worker status
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'worker_id': os.getenv('HOSTNAME', 'unknown'),
        'active_jobs': get_active_job_count(),
    }
    
    # Check dependencies
    try:
        # Verify LiveKit connection
        if not worker.is_connected():
            status['status'] = 'unhealthy'
            status['error'] = 'LiveKit disconnected'
            return web.json_response(status, status=503)
            
        return web.json_response(status, status=200)
    except Exception as e:
        status['status'] = 'unhealthy'
        status['error'] = str(e)
        return web.json_response(status, status=503)

# Start health check server
app = web.Application()
app.router.add_get('/', health_check)
web.run_app(app, port=8081)
```

## Production Best Practices

### Graceful Shutdown
```python
import signal
import asyncio

class GracefulShutdown:
    def __init__(self):
        self.shutdown_event = asyncio.Event()
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        logger.info(f"Received signal {signum}, starting graceful shutdown")
        self.shutdown_event.set()
    
    async def wait_for_shutdown(self):
        await self.shutdown_event.wait()
        
        # Stop accepting new jobs
        worker.stop_accepting_jobs()
        
        # Wait for active sessions to complete
        timeout = 600  # 10 minutes
        await worker.wait_for_completion(timeout)
```

### Resource Cleanup
```python
async def cleanup_resources():
    """Clean up resources on shutdown"""
    # Close database connections
    if hasattr(ctx, 'db'):
        await ctx.db.close()
    
    # Save session state
    if hasattr(ctx, 'session_state'):
        await save_session_state(ctx.session_state)
    
    # Close external connections
    await close_external_connections()
    
    logger.info("Resource cleanup completed")

ctx.add_shutdown_callback(cleanup_resources)
```

### Error Recovery
```python
class RobustWorker:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 5
    
    async def run(self):
        retries = 0
        while retries < self.max_retries:
            try:
                await self.start_worker()
            except Exception as e:
                logger.error(f"Worker failed: {e}")
                retries += 1
                
                if retries < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("Max retries reached, exiting")
                    raise
```

## Security Considerations

### Container Security
```dockerfile
# Run as non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Copy only necessary files
COPY --chown=appuser:appuser . /app

# Minimal permissions
RUN chmod -R 555 /app
RUN chmod -R 755 /app/logs
```

### Network Security
- Use TLS for all connections (wss://)
- Implement API key rotation
- Use secrets management systems
- Monitor for anomalous behavior

### Runtime Security
```python
# Input validation
def validate_input(data):
    """Validate and sanitize user input"""
    # Remove potential injection attacks
    sanitized = data.replace('<script>', '').replace('</script>', '')
    
    # Validate length
    if len(sanitized) > 1000:
        raise ValueError("Input too long")
    
    return sanitized

# Rate limiting
from collections import defaultdict
from time import time

class RateLimiter:
    def __init__(self, max_requests=100, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def check_rate_limit(self, user_id):
        now = time()
        # Clean old requests
        self.requests[user_id] = [
            t for t in self.requests[user_id] 
            if now - t < self.window
        ]
        
        if len(self.requests[user_id]) >= self.max_requests:
            raise Exception("Rate limit exceeded")
        
        self.requests[user_id].append(now)
```

## Cost Optimization

### Instance Selection
- **Development**: Burstable instances (t3.medium)
- **Production**: Compute-optimized (c5.large)
- **High-load**: Memory-optimized (r5.xlarge)

### Auto-scaling Policies
```yaml
# Scale based on queue depth
- type: External
  external:
    metric:
      name: livekit_queue_depth
      selector:
        matchLabels:
          queue: agent-jobs
    target:
      type: Value
      value: "10"  # Target 10 jobs per worker
```

### Cost Monitoring
```python
# Track API usage costs
class CostTracker:
    def __init__(self):
        self.costs = {
            'openai': 0.0,
            'deepgram': 0.0,
            'livekit': 0.0,
        }
    
    def track_openai(self, tokens):
        # $0.002 per 1K tokens (example)
        self.costs['openai'] += (tokens / 1000) * 0.002
    
    def track_deepgram(self, audio_minutes):
        # $0.0125 per minute (example)
        self.costs['deepgram'] += audio_minutes * 0.0125
    
    def get_daily_cost(self):
        return sum(self.costs.values())
```

This comprehensive deployment guide ensures production-ready LiveKit Agents with proper scaling, monitoring, and security practices.