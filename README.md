# LiveKit Appointment Confirmation Voice Agent

A human-like voice agent built with LiveKit that makes appointment confirmation calls. The agent sounds natural and conversational, using advanced speech synthesis and conversation management to confirm appointments 24 hours in advance.

## 🎯 Project Overview

This project implements a voice agent that:
- Makes outbound calls to confirm appointments
- Sounds convincingly human with natural speech patterns
- Handles various customer responses gracefully
- Maintains conversation context throughout calls
- Achieves sub-200ms response latency

### Key Features
- **Natural Conversation**: Filler phrases, pauses, and acknowledgments
- **Smart Error Recovery**: Progressive clarification strategies
- **Voice Pipeline**: Deepgram STT → GPT-4o-mini → OpenAI TTS
- **Turn Detection**: LiveKit's multilingual semantic model
- **Production Ready**: Docker deployment, monitoring, metrics

## 📁 Project Structure

```
appointment-confirmation-agent/
├── agent/                  # Core agent implementation
│   └── appointment_agent.py
├── token_server/          # JWT token server for authentication
│   ├── token_server.py
│   ├── request_token.py
│   ├── test_token_server.py
│   ├── start_token_server.sh
│   └── README.md
├── examples/              # Example implementations
├── PRPs/                  # Product Requirements Prompts
├── logs/                  # Application logs
├── venv/                  # Python virtual environment
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── start_agent.sh        # Agent startup script
└── README.md             # This file
```

## 🏗️ Architecture

```
Voice Pipeline:
┌─────────┐     ┌─────────┐     ┌─────────┐
│Deepgram │ --> │GPT-4o   │ --> │OpenAI   │
│Nova-2   │     │mini     │     │Nova TTS │
└─────────┘     └─────────┘     └─────────┘
     ↑                               ↓
     └──── LiveKit Agent Session ────┘
              (VAD + Turn Detection)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- LiveKit Cloud account or self-hosted server
- API keys: OpenAI, Deepgram, LiveKit

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/andrep/appointment-confirmation-agent.git
   cd appointment-confirmation-agent
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the agent**
   ```bash
   ./start_agent.sh
   # Or manually: python agent/appointment_agent.py dev
   ```

## 🧪 Testing

### Start the Token Server

Before testing with a frontend, start the token server:

```bash
cd token_server
./start_token_server.sh
# Server runs on http://localhost:8002
```

Test token generation:
```bash
python token_server/request_token.py --email test@example.com --name "Test User"
```

### Using the React Frontend

1. **Clone the testing UI**
   ```bash
   git clone https://github.com/livekit-examples/agent-starter-react.git appointment-frontend
   cd appointment-frontend
   npm install
   ```

2. **Configure and run**
   ```bash
   cp .env.example .env.local
   # Add your LiveKit credentials
   npm run dev
   ```

3. **Access at** http://localhost:3000

### Test Scenarios
- ✅ Customer confirms appointment
- 📅 Customer requests reschedule
- ❓ Customer acts confused
- 🔊 Background noise handling

## 📋 Project Management with Archon

This project uses the Archon MCP server for comprehensive task tracking and knowledge management.

### Archon Project ID
`49edfe6d-f6d1-4338-9222-97d5679da1a3`

### View Project Tasks
```python
# Check current tasks
archon:manage_task(
  action="list",
  filter_by="project",
  filter_value="49edfe6d-f6d1-4338-9222-97d5679da1a3"
)
```

### Task Workflow
1. **Todo** → Pick highest priority task
2. **Doing** → Update status when starting
3. **Review** → Mark for testing/validation
4. **Done** → Complete after verification

### Current Features
- Environment Setup
- Core Agent
- Voice Pipeline
- Natural Conversation
- Testing Frontend
- Testing
- Deployment
- Monitoring
- Documentation

## 🔧 Configuration

### Voice Components
- **STT**: Deepgram Nova-2 (multilingual)
- **LLM**: GPT-4o-mini (temperature: 0.8)
- **TTS**: OpenAI Nova (female, professional)
- **VAD**: Silero with multilingual turn detection

### Natural Speech Features
- Filler phrases: "um", "let me see", "one moment"
- Acknowledgments: "mm-hmm", "I see", "got it"
- Response variation to avoid repetition
- SSML markup for natural pauses

## 🚢 Deployment

### Docker
```bash
docker build -t appointment-agent .
docker run --env-file .env appointment-agent
```

### AWS ECS
See `deployment/ecs-task-definition.json`

### Environment Variables
```env
# Required
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-key
LIVEKIT_API_SECRET=your-secret
OPENAI_API_KEY=your-openai-key
DEEPGRAM_API_KEY=your-deepgram-key

# Optional
WORKER_CONCURRENCY=5
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

## 📊 Monitoring

- **Metrics**: Prometheus-compatible metrics endpoint
- **Logging**: Structured JSON logs with context
- **Health Check**: `/health` endpoint
- **Performance**: Sub-200ms latency tracking

## 💰 Cost Estimation

Per average 2-minute call:
- Deepgram STT: ~$0.025
- GPT-4o-mini: ~$0.03
- OpenAI TTS: ~$0.05
- **Total**: ~$0.10-0.20 per call

## 🤝 Contributing

1. Check Archon tasks for current priorities
2. Update task status when working
3. Follow existing code patterns
4. Add tests for new features
5. Update documentation

## 📚 Documentation

- [Product Requirements Prompt (PRP)](PRPs/livekit-appointment-confirmation.md)
- [Initial Requirements](INITIAL.md)
- [Development Guidelines](CLAUDE.md)
- [LiveKit Agents Docs](https://docs.livekit.io/agents/)

## 🐛 Troubleshooting

### Common Issues

**Agent sounds robotic**
- Check temperature setting (0.7-0.8)
- Verify natural speech features enabled
- Test response variation

**High latency**
- Ensure prewarm is loading models
- Check network to API providers
- Consider response caching

**Poor recognition**
- Verify audio quality
- Check Deepgram language settings
- Test noise suppression

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

Built with:
- [LiveKit](https://livekit.io) - Real-time communication infrastructure
- [Deepgram](https://deepgram.com) - Speech recognition
- [OpenAI](https://openai.com) - Language model and speech synthesis
- [Archon](https://archon.ai) - Project and knowledge management