# LiveKit Appointment Confirmation Agent

> An experimental implementation using the Product Requirements Prompt (PRP) framework with Archon V2 orchestration

This project demonstrates building a production-ready voice agent for appointment confirmations using LiveKit's real-time communication infrastructure. It showcases how modern AI agents can handle natural conversations with human-like speech patterns and responses.

## 🚀 Project Overview

This appointment confirmation agent was built as an experiment to validate the **PRP (Product Requirements Prompt) framework** - a methodology for translating complex product requirements into AI-implemented solutions. The entire development process was orchestrated using **Archon V2**, which managed task allocation, progress tracking, and knowledge retrieval throughout the implementation.

### Key Achievements

- ✅ **Natural Conversation Flow** - Implements human-like speech with fillers, pauses, and acknowledgments
- ✅ **Production Architecture** - Complete system with agent, token server, and frontend
- ✅ **Comprehensive Examples** - Seven different implementation patterns and use cases
- ✅ **Full Containerization** - Docker support for all components
- ✅ **End-to-End Testing** - Verified voice interactions and conversation scenarios

### Technology Stack

- **LiveKit** - Real-time voice communication infrastructure
- **Python 3.11** - Agent implementation
- **FastAPI** - Token server
- **React/Next.js** - Frontend testing interface
- **Docker** - Containerization and deployment
- **AWS ECS** - Production deployment target

## 📁 Project Structure

```
appointment-confirmation-agent/
├── agent/                      # Core voice agent implementation
│   └── appointment_agent.py    # Main agent with natural speech
├── token_server/              # JWT authentication server
│   ├── token_server.py        # FastAPI implementation
│   └── Dockerfile             # Container configuration
├── frontend/                  # React testing interface (from agent-starter-react)
│   ├── app/                   # Next.js app directory
│   └── components/            # UI components
├── examples/                  # Comprehensive implementation examples
│   ├── basic_voice_agent/     # Simple agent pattern
│   ├── testing_patterns/      # Unit and integration tests
│   ├── multi_agent_system/    # Agent orchestration
│   ├── tool_enabled_agent/    # Function calling examples
│   ├── metrics_monitoring/    # Observability patterns
│   ├── token_server/          # Authentication implementation
│   └── frontend_client/       # Frontend setup guide
├── deployment/                # Production deployment configs
│   ├── ecs-task-definition.json
│   ├── buildspec.yml
│   └── docker-compose.prod.yml
├── PRPs/                      # Product Requirements Prompts
│   ├── livekit-appointment-confirmation.md
│   └── ai_docs/              # Supporting documentation
├── docker-compose.yml         # Local development setup
├── Dockerfile                 # Agent container definition
└── requirements.txt           # Python dependencies
```

## 🎯 The PRP Framework Experiment

This project serves as a proof-of-concept for the **Product Requirements Prompt (PRP)** framework, which aims to bridge the gap between product requirements and AI-driven implementation. 

### What is PRP?

The PRP framework provides:
- Structured format for capturing product requirements
- AI-friendly specifications that can be directly implemented
- Clear success criteria and testing scenarios
- Built-in best practices and patterns

### Archon V2 Orchestration

The entire development was managed by **Archon V2**, an AI orchestration system that:
- Managed task breakdown and prioritization
- Tracked implementation progress
- Provided contextual knowledge retrieval
- Coordinated between requirements and implementation

You can find the original PRP document at: `PRPs/livekit-appointment-confirmation.md`

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 16+
- Docker and Docker Compose
- LiveKit Cloud account (or self-hosted)
- API keys: OpenAI, Deepgram, LiveKit

### 1. Clone and Setup

```bash
git clone https://github.com/Andre-Mygentic/appointment-confirmation-agent
cd appointment-confirmation-agent

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys:
# - LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
# - OPENAI_API_KEY
# - DEEPGRAM_API_KEY
```

### 3. Start with Docker (Recommended)

```bash
# Start all services
docker-compose up

# Services will be available at:
# - Token Server: http://localhost:8002
# - Frontend: http://localhost:3000
# - Agent: Connects to LiveKit Cloud
```

### 4. Manual Start (Development)

```bash
# Terminal 1: Token Server
cd token_server
python token_server.py

# Terminal 2: Agent
python agent/appointment_agent.py dev

# Terminal 3: Frontend
cd frontend
npm install
npm run dev
```

### 5. Test the Agent

1. Open http://localhost:3000
2. Click "Connect" to start a call
3. Wait for the agent's greeting
4. Try responses like:
   - "Yes, I'll be there" (confirm)
   - "I need to reschedule" (reschedule)
   - "What appointment?" (confusion)

## 🎭 Natural Conversation Features

The agent implements human-like conversation patterns:

### Speech Characteristics
- **Filler phrases**: "um", "let me see", "one moment"
- **Acknowledgments**: "mm-hmm", "I see", "got it"
- **Natural pauses**: Using SSML markup
- **Response variation**: Multiple ways to say the same thing
- **Error recovery**: Progressive clarification strategies

### Conversation Flow
1. **Warm greeting** with time-appropriate salutation
2. **Clear purpose** statement
3. **Appointment details** confirmation
4. **Natural responses** to various scenarios
5. **Graceful handling** of confusion or errors

## 📚 Examples Collection

The `examples/` directory contains seven comprehensive examples:

### 1. **basic_voice_agent/**
- Minimal agent implementation
- Core concepts and patterns
- Perfect starting point

### 2. **testing_patterns/**
- Unit test examples
- Integration testing strategies
- Mock implementations

### 3. **multi_agent_system/**
- Agent handoff patterns
- Specialist agent routing
- Complex conversation flows

### 4. **tool_enabled_agent/**
- Function calling implementation
- Database integration
- External API usage

### 5. **metrics_monitoring/**
- Prometheus metrics
- Performance tracking
- Observability patterns

### 6. **token_server/**
- Complete authentication server
- JWT token generation
- Production security patterns

### 7. **frontend_client/**
- Frontend setup guide
- Integration instructions
- Testing scenarios

## 🚢 Deployment

### Local Development

```bash
docker-compose up
```

### Production Deployment

#### AWS ECS/Fargate

```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URI
docker build -t appointment-agent .
docker tag appointment-agent:latest $ECR_URI/appointment-agent:latest
docker push $ECR_URI/appointment-agent:latest

# Deploy with ECS
aws ecs register-task-definition --cli-input-json file://deployment/ecs-task-definition.json
aws ecs create-service --cluster your-cluster --service-name appointment-agent ...
```

#### Docker Swarm

```bash
docker stack deploy -c docker-compose.yml -c deployment/docker-compose.prod.yml appointment
```

See `deployment/README.md` for detailed deployment instructions.

## 📊 Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│Token Server │────▶│   LiveKit   │
│  (React)    │     │  (FastAPI)  │     │   Cloud     │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │    Agent    │
                                        │  (Python)   │
                                        └─────────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    ▼                          ▼                          ▼
            ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
            │  Deepgram   │           │   OpenAI    │           │   OpenAI    │
            │    (STT)    │           │  (GPT-4)    │           │    (TTS)    │
            └─────────────┘           └─────────────┘           └─────────────┘
```

## 🧪 Testing

### Manual Testing

Use the included frontend to test various scenarios:
- Appointment confirmation
- Reschedule requests
- Wrong person handling
- Confusion scenarios

### Automated Testing

```bash
# Run unit tests
pytest tests/

# Run integration tests
python examples/testing_patterns/test_integration.py
```

## 💰 Cost Analysis

Estimated per 2-minute call:
- Deepgram STT: ~$0.025
- GPT-4o-mini: ~$0.03
- OpenAI TTS: ~$0.05
- **Total: ~$0.10-0.20**

Cost optimization strategies:
- Cache common responses
- Use streaming for lower latency
- Implement call duration limits
- Monitor usage with included metrics

## 🐛 Troubleshooting

### Common Issues

1. **Agent not joining room**
   - Check room name pattern in frontend
   - Verify LiveKit credentials
   - Review agent logs

2. **No audio from agent**
   - Ensure ffmpeg is installed (included in Docker)
   - Check browser microphone permissions
   - Verify TTS API key

3. **High latency**
   - Check LiveKit server region
   - Monitor network connectivity
   - Review agent performance metrics

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=DEBUG python agent/appointment_agent.py dev
```

## 🤝 Contributing

This project was an experiment in AI-driven development using:
- **PRP Framework** for requirements specification
- **Archon V2** for task orchestration
- **Claude** for implementation

To contribute:
1. Review the PRP document for context
2. Check existing examples for patterns
3. Follow the established code style
4. Add tests for new features
5. Update documentation

## 📄 License

This project is provided as an educational example of the PRP framework and modern voice agent development.

## 🙏 Acknowledgments

- **LiveKit** - Exceptional real-time communication infrastructure
- **Deepgram** - High-quality speech recognition
- **OpenAI** - Natural language processing and speech synthesis
- **Archon V2** - AI orchestration and task management
- **agent-starter-react** - Frontend foundation

## 📚 Resources

- [LiveKit Documentation](https://docs.livekit.io)
- [PRP Framework](PRPs/livekit-appointment-confirmation.md)
- [Deployment Guide](deployment/README.md)
- [Examples Documentation](examples/README.md)

---

*This project demonstrates the potential of AI-driven development when combining structured requirements (PRP) with intelligent orchestration (Archon V2). The resulting implementation showcases production-ready patterns while maintaining code quality and comprehensive documentation.*