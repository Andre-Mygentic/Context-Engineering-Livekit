# Deployment Guide

This guide covers various deployment options for the LiveKit Appointment Confirmation Agent.

## Table of Contents
- [Local Development with Docker](#local-development-with-docker)
- [Production Deployment](#production-deployment)
  - [AWS ECS/Fargate](#aws-ecsfargate)
  - [Docker Swarm](#docker-swarm)
  - [Kubernetes](#kubernetes)
- [Environment Configuration](#environment-configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Scaling Considerations](#scaling-considerations)

## Local Development with Docker

### Prerequisites
- Docker Engine 20.10+
- Docker Compose v2.0+
- Environment variables configured in `.env` file

### Quick Start

1. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Start services in background:**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f appointment-agent
   docker-compose logs -f token-server
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

### Service URLs
- Token Server: http://localhost:8002
- Frontend: http://localhost:3000
- Agent: Connects to LiveKit Cloud

## Production Deployment

### AWS ECS/Fargate

#### Prerequisites
- AWS CLI configured
- ECR repositories created
- Secrets Manager configured with API keys
- ECS cluster created

#### Setup Steps

1. **Create ECR repositories:**
   ```bash
   aws ecr create-repository --repository-name appointment-agent
   aws ecr create-repository --repository-name appointment-token-server
   ```

2. **Store secrets in AWS Secrets Manager:**
   ```bash
   aws secretsmanager create-secret --name appointment-agent/livekit-url \
     --secret-string "wss://your-project.livekit.cloud"
   
   aws secretsmanager create-secret --name appointment-agent/livekit-api-key \
     --secret-string "your-api-key"
   
   # Repeat for other secrets...
   ```

3. **Build and push images:**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin \
     123456789012.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and push appointment agent
   docker build -t appointment-agent .
   docker tag appointment-agent:latest \
     123456789012.dkr.ecr.us-east-1.amazonaws.com/appointment-agent:latest
   docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/appointment-agent:latest
   
   # Build and push token server
   docker build -t appointment-token-server ./token_server
   docker tag appointment-token-server:latest \
     123456789012.dkr.ecr.us-east-1.amazonaws.com/appointment-token-server:latest
   docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/appointment-token-server:latest
   ```

4. **Create ECS service:**
   ```bash
   # Update task definition with your account details
   sed -i 's/YOUR_ACCOUNT_ID/123456789012/g' deployment/ecs-task-definition.json
   sed -i 's/YOUR_REGION/us-east-1/g' deployment/ecs-task-definition.json
   
   # Register task definition
   aws ecs register-task-definition --cli-input-json file://deployment/ecs-task-definition.json
   
   # Create service
   aws ecs create-service \
     --cluster your-cluster-name \
     --service-name appointment-agent \
     --task-definition appointment-confirmation-agent \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
   ```

### Docker Swarm

1. **Initialize Swarm:**
   ```bash
   docker swarm init
   ```

2. **Deploy stack:**
   ```bash
   docker stack deploy -c docker-compose.yml -c deployment/docker-compose.prod.yml appointment-agent
   ```

3. **Scale services:**
   ```bash
   docker service scale appointment-agent_appointment-agent=5
   ```

### Kubernetes

1. **Create namespace:**
   ```bash
   kubectl create namespace appointment-agent
   ```

2. **Create secrets:**
   ```bash
   kubectl create secret generic appointment-agent-secrets \
     --from-env-file=.env \
     -n appointment-agent
   ```

3. **Apply manifests:**
   ```bash
   kubectl apply -f deployment/k8s/ -n appointment-agent
   ```

## Environment Configuration

### Required Environment Variables

```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# API Keys
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...

# Token Server
TOKEN_SERVER_PORT=8002
CORS_ORIGINS=https://your-app.com
TOKEN_EXPIRY_HOURS=24

# Agent Configuration
LOG_LEVEL=INFO
WORKER_CONCURRENCY=5
```

### Production Best Practices

1. **Use secrets management:**
   - AWS Secrets Manager
   - Kubernetes Secrets
   - HashiCorp Vault

2. **Enable HTTPS:**
   - Use TLS certificates
   - Configure reverse proxy

3. **Set resource limits:**
   - CPU and memory limits
   - Autoscaling policies

## Monitoring and Logging

### CloudWatch (AWS)

The ECS task definition includes CloudWatch logging configuration:

```json
"logConfiguration": {
  "logDriver": "awslogs",
  "options": {
    "awslogs-group": "/ecs/appointment-agent",
    "awslogs-region": "us-east-1",
    "awslogs-stream-prefix": "ecs"
  }
}
```

### Prometheus Metrics

Export metrics for monitoring:

```yaml
# docker-compose.yml addition
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"
```

### Health Checks

All services include health check endpoints:

- Token Server: `GET /health`
- Agent: Python process check

## Scaling Considerations

### Horizontal Scaling

1. **Agent Scaling:**
   - Multiple agent instances can run simultaneously
   - LiveKit handles job distribution automatically
   - Scale based on concurrent call volume

2. **Token Server Scaling:**
   - Stateless service, easy to scale
   - Place behind load balancer
   - Consider caching with Redis

### Resource Requirements

| Component | CPU | Memory | Notes |
|-----------|-----|--------|-------|
| Agent | 0.5-1 vCPU | 512MB-1GB | Depends on concurrent calls |
| Token Server | 0.25 vCPU | 256MB | Lightweight service |
| Redis (optional) | 0.25 vCPU | 256MB | For caching |

### Performance Optimization

1. **Enable production mode:**
   ```bash
   docker-compose -f docker-compose.yml -f deployment/docker-compose.prod.yml up
   ```

2. **Use multi-stage builds** (already implemented)

3. **Optimize Python:**
   - Use `PYTHONUNBUFFERED=1`
   - Disable bytecode generation in containers
   - Consider using `gunicorn` for token server

## Troubleshooting

### Common Issues

1. **Agent not connecting to LiveKit:**
   - Check API credentials
   - Verify network connectivity
   - Review CloudWatch logs

2. **High latency:**
   - Check resource allocation
   - Review agent concurrency settings
   - Monitor network performance

3. **Token server errors:**
   - Verify CORS configuration
   - Check API key permissions
   - Review request logs

### Debug Mode

Enable debug logging:

```bash
docker-compose run -e LOG_LEVEL=DEBUG appointment-agent
```

## CI/CD Pipeline

Use AWS CodeBuild with the provided `buildspec.yml`:

1. **Create CodeBuild project**
2. **Connect to GitHub repository**
3. **Configure environment variables**
4. **Set up CodePipeline for automated deployments**

## Security Considerations

1. **Network Security:**
   - Use VPC with private subnets
   - Configure security groups properly
   - Enable VPC Flow Logs

2. **Secrets Management:**
   - Never commit secrets to repository
   - Use AWS Secrets Manager or similar
   - Rotate API keys regularly

3. **Image Security:**
   - Scan images for vulnerabilities
   - Use specific version tags, not `latest`
   - Keep base images updated