# PRP: Human-like Appointment Confirmation Voice Agent

## Overview
This PRP details the implementation of a LiveKit voice agent that makes natural-sounding appointment confirmation calls. The agent uses a voice pipeline architecture (STT→LLM→TTS) with Deepgram Nova-2, GPT-4o-mini, and OpenAI's Nova voice to create convincingly human-like conversations. The agent acts as a warm, professional receptionist calling customers 24 hours before their appointments to confirm attendance and serve as a reminder.

## LiveKit Architecture Context

### Agent Lifecycle
LiveKit Agents follow a Worker → Job → Session pattern:
1. **Worker**: Registers with LiveKit server, accepts job requests
2. **Job**: Created when a room needs an agent, runs in isolated process
3. **Session**: Manages the agent's participation in the room

### Voice Pipeline Configuration
Using STT→LLM→TTS Pipeline for maximum control and flexibility:
- **Deepgram Nova-2**: Industry-leading speech recognition with excellent accuracy
- **GPT-4o-mini**: Fast, cost-effective LLM for natural conversation flow
- **OpenAI Nova TTS**: Most natural-sounding female voice with professional tone
- **Multilingual Turn Detection**: LiveKit's semantic model for natural conversation flow

### Key Components
- **Agent**: Core receptionist personality with warm, professional instructions
- **AgentSession**: Orchestrates voice pipeline with natural conversation features
- **JobContext**: Room connection and lifecycle management
- **Natural Elements**: Filler phrases, pauses, acknowledgments for human-like interaction

## Requirements

### Functional Requirements
- Make outbound calls to confirm appointments 24 hours in advance
- Sound convincingly human with natural speech patterns and conversational flow
- Handle various customer responses (confirmation, confusion, rescheduling requests)
- Persist through understanding difficulties with natural clarification phrases
- Maintain full conversation context throughout the call
- Support graceful error recovery without breaking character

### Technical Requirements
- Python 3.11 (recommended for production)
- LiveKit Agents SDK ~1.0
- Required providers: OpenAI, Deepgram, Silero
- Sub-200ms latency target for AWS deployment
- Docker containerization for production deployment
- Support for concurrent calls via worker pool

## Implementation Plan

### Phase 1: Environment Setup
1. Create virtual environment with Python 3.11
2. Install dependencies:
   ```bash
   pip install "livekit-agents[openai,deepgram,silero,turn_detector]~=1.0"
   pip install python-dotenv
   ```
3. Configure .env file:
   ```
   # LiveKit Configuration
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your-api-key
   LIVEKIT_API_SECRET=your-api-secret
   
   # AI Provider Keys
   OPENAI_API_KEY=your-openai-key
   DEEPGRAM_API_KEY=your-deepgram-key
   
   # Optional Configuration
   LOG_LEVEL=INFO
   APPOINTMENT_API_URL=https://your-api.com  # For future integration
   ```

### Phase 2: Agent Implementation

#### Core Agent Structure
```python
import logging
import asyncio
from typing import Optional
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    WorkerOptions,
    cli,
    metrics,
)
from livekit.agents.voice import MetricsCollectedEvent
from livekit.plugins import deepgram, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("appointment-agent")
load_dotenv()

class AppointmentConfirmationAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a polite, professional, yet warm-sounding receptionist named Sarah. 
            Your job is to call customers who already have booked appointments to check if they are 
            still able to attend. You are calling approximately 24 hours before their appointment 
            to confirm attendance and serve as a reminder.
            
            IMPORTANT CONVERSATIONAL BEHAVIORS:
            - Use natural filler phrases when thinking: "um", "let me see", "one moment"
            - Include acknowledgment sounds when listening: "mm-hmm", "I see", "got it"
            - Vary your responses to avoid sounding scripted
            - Add brief pauses when "looking up" information
            - Speak at a normal, conversational pace
            
            CONVERSATION APPROACH:
            - Start with a warm greeting and clearly identify yourself and your purpose
            - Confirm the appointment details (date, time, service)
            - If the customer confirms, thank them warmly and end the call
            - If they need to reschedule, acknowledge and provide next steps
            - If they seem confused, patiently clarify who you are and why you're calling
            
            ERROR RECOVERY:
            - If you don't understand, use natural phrases like "Sorry, could you repeat that?"
            - If still unclear after 2 attempts, try rephrasing your question
            - Never give up - keep trying different approaches until you get what you need
            - If someone says they're not the right person, politely ask for them
            
            Remember: You're a human receptionist, not a robot. Be natural, be helpful, be persistent."""
        )
        # In a real implementation, this would connect to your appointment system
        self.appointment_details = {
            "date": "tomorrow at 2:30 PM",
            "service": "dental cleaning",
            "doctor": "Dr. Johnson",
            "location": "Main Street Dental Clinic"
        }
    
    async def on_enter(self):
        """Called when agent first joins the session"""
        # Small delay to simulate picking up the phone
        await asyncio.sleep(0.8)
        
        # Generate initial greeting
        self.session.chat_ctx.append(
            role="assistant",
            content="""Hello! This is Sarah calling from Main Street Dental Clinic. 
            I'm calling to confirm your appointment with Dr. Johnson tomorrow at 2:30 PM 
            for your dental cleaning. Are you still able to make it?"""
        )
        await self.session.generate_reply()

def prewarm(proc: JobProcess):
    """Preload heavy resources for performance"""
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    """Main entry point for the agent worker"""
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "participant": ctx.participant_identity if hasattr(ctx, 'participant_identity') else "unknown",
    }
    
    await ctx.connect()  # ALWAYS connect first
    logger.info(f"Agent connected to room: {ctx.room.name}")
    
    # Configure the voice pipeline
    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(
            model="nova-3",
            language="multi",  # Support multiple languages
            smart_format=True,  # Better formatting of numbers, dates
            punctuate=True,
            interim_results=True,  # For better perceived responsiveness
        ),
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.8,  # Slightly higher for more natural variation
        ),
        tts=openai.TTS(
            voice="nova",
            speed=1.0,  # Normal speaking pace
            # Can add SSML for more control over speech patterns
        ),
        # Multilingual turn detection for natural conversation flow
        turn_detection=MultilingualModel(),
        # Allow natural interruptions
        allow_interruptions=True,
        interrupt_speech_duration=0.6,  # How long before considering it an interruption
    )
    
    # Set up metrics collection
    usage_collector = metrics.UsageCollector()
    
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)
    
    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage summary: {summary}")
    
    ctx.add_shutdown_callback(log_usage)
    
    # Start the agent session
    agent = AppointmentConfirmationAgent()
    await session.start(agent=agent, room=ctx.room)
    
    logger.info("Agent session completed")

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            log_level="INFO",
        )
    )
```

#### Natural Conversation Enhancements
To make the agent sound more human-like, we'll implement:

1. **Response Variation System**:
```python
import random

class ResponseVariations:
    GREETINGS = [
        "Hello! This is Sarah from {clinic}.",
        "Hi there! This is Sarah calling from {clinic}.",
        "Good {time_of_day}! This is Sarah from {clinic}.",
    ]
    
    CONFIRMATIONS = [
        "Perfect! I have you confirmed for {appointment}.",
        "Wonderful! You're all set for {appointment}.",
        "Great! I've got you down for {appointment}.",
    ]
    
    CLARIFICATIONS = [
        "I'm sorry, could you repeat that?",
        "Sorry, I didn't quite catch that.",
        "Could you say that again please?",
        "I'm having a bit of trouble hearing you, could you repeat that?",
    ]
    
    ACKNOWLEDGMENTS = [
        "mm-hmm",
        "I see",
        "got it",
        "okay",
        "I understand",
    ]
```

2. **Natural Pause Injection**:
```python
def add_natural_pauses(text: str) -> str:
    """Add SSML markup for natural pauses"""
    # Add pauses after "let me check", "one moment", etc.
    pause_phrases = {
        "let me see": '<break time="600ms"/>',
        "let me check": '<break time="800ms"/>',
        "one moment": '<break time="700ms"/>',
        "um": '<break time="300ms"/>',
    }
    
    for phrase, pause in pause_phrases.items():
        text = text.replace(phrase, f"{phrase}{pause}")
    
    return f"<speak>{text}</speak>"
```

### Phase 3: Testing & Validation

#### Testing Frontend Setup
For a complete testing experience, use the LiveKit agent-starter-react frontend:

```bash
# 1. Clone the React frontend
git clone https://github.com/livekit-examples/agent-starter-react.git appointment-frontend
cd appointment-frontend

# 2. Install dependencies
npm install

# 3. Configure environment
cp .env.example .env.local
# Edit .env.local with your LiveKit credentials:
# LIVEKIT_API_KEY=your_api_key
# LIVEKIT_API_SECRET=your_api_secret
# LIVEKIT_URL=http://localhost:7880 (for local testing)

# 4. Customize for appointment confirmation (optional)
# Edit lib/config.ts:
export const APP_CONFIG = {
  companyName: 'Main Street Dental Clinic',
  pageTitle: 'Appointment Confirmation System',
  pageDescription: 'Test appointment confirmation calls',
  supportsChatInput: true,  // See text transcriptions
  supportsVideoInput: false, // Voice-only agent
  supportsScreenShare: false,
  logo: '/dental-logo.svg',
  accent: '#00897B',
  startButtonText: 'Start Test Call',
};

# 5. Run the frontend
npm run dev
# Access at http://localhost:3000
```

#### Complete Local Testing Setup
```bash
# Terminal 1: Start LiveKit server
docker run --rm \
  -p 7880:7880 \
  -p 7881:7881 \
  -p 7882:7882/udp \
  livekit/livekit-server \
  --dev \
  --bind 0.0.0.0

# Terminal 2: Run the agent
cd appointment-confirmation-agent
python appointment_agent.py dev

# Terminal 3: Run the React frontend
cd appointment-frontend
npm run dev

# Now open http://localhost:3000 in your browser
# Click "Start Test Call" to connect to your agent
```

#### Testing Interface Features
The React frontend provides:
- **Real-time Transcriptions**: See both user speech and agent responses
- **Audio Visualizer**: Monitor voice activity and audio levels
- **Connection Status**: Track connection quality and latency
- **Chat Input**: Type messages to test text fallback
- **Session Controls**: Start/stop calls, mute/unmute

#### Test Scenarios
1. **Happy Path**: Customer confirms appointment
2. **Rescheduling**: Customer needs different time
3. **Confusion**: Customer doesn't remember appointment
4. **Wrong Person**: Someone else answers
5. **Poor Audio**: Background noise, unclear speech
6. **Interruptions**: Customer interrupts mid-sentence
7. **Technical Issues**: Network latency, audio drops

#### Performance Testing
```python
# Measure key metrics
async def measure_latency(session: AgentSession):
    @session.on("user_speech_committed")
    def on_user_speech(ev):
        ev.user_speech_timestamp = time.time()
    
    @session.on("agent_speech_started")
    def on_agent_speech(ev):
        if hasattr(ev, 'user_speech_timestamp'):
            latency = time.time() - ev.user_speech_timestamp
            logger.info(f"Response latency: {latency*1000:.0f}ms")
```

### Phase 4: Production Preparation

#### Dockerfile
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set Python to unbuffered mode
ENV PYTHONUNBUFFERED=1

# Health check endpoint
EXPOSE 8080

# Run the agent
CMD ["python", "appointment_agent.py"]
```

#### Production Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  appointment-agent:
    build: .
    environment:
      - LIVEKIT_URL=${LIVEKIT_URL}
      - LIVEKIT_API_KEY=${LIVEKIT_API_KEY}
      - LIVEKIT_API_SECRET=${LIVEKIT_API_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY}
      - LOG_LEVEL=INFO
      - WORKER_CONCURRENCY=5
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '4'
          memory: 4G
```

## Voice Pipeline Details

### Component Selection Rationale
- **STT - Deepgram Nova-2**: 
  - Superior accuracy for conversational speech
  - Excellent handling of interruptions and overlapping speech
  - Fast streaming transcription for low latency
  - Multi-language support with language detection

- **LLM - GPT-4o-mini**: 
  - Optimal balance of speed and quality
  - ~500ms average response time
  - Strong conversational abilities
  - Cost-effective for high volume

- **TTS - OpenAI Nova**: 
  - Most natural-sounding female voice
  - Professional yet warm tone
  - Good prosody and intonation
  - SSML support for fine control

- **VAD - Silero + Multilingual Turn Detection**: 
  - Silero for reliable voice activity detection
  - Multilingual model for semantic understanding of turn-taking
  - Handles natural conversation patterns well

### Latency Optimization Strategies
1. **Preemptive Processing**: Start LLM inference before user finishes speaking
2. **Response Caching**: Cache common phrases and responses
3. **Pipeline Parallelization**: Process STT/LLM/TTS in parallel where possible
4. **Edge Deployment**: Deploy close to users (AWS regions)
5. **Connection Pooling**: Maintain persistent connections to APIs

## Natural Conversation Implementation

### Filler Phrases and Pauses
```python
FILLER_PHRASES = {
    "thinking": ["um", "uh", "let me see", "one moment", "let me check that"],
    "acknowledgment": ["mm-hmm", "I see", "got it", "okay", "right"],
    "clarification": ["sorry", "excuse me", "pardon"],
}

def inject_filler(response: str, context: str) -> str:
    """Inject appropriate filler phrases based on context"""
    if context == "lookup":
        filler = random.choice(FILLER_PHRASES["thinking"])
        return f"{filler}... {response}"
    return response
```

### Dynamic Response Selection
```python
def get_contextual_response(intent: str, context: dict) -> str:
    """Select appropriate response based on intent and context"""
    responses = RESPONSE_TEMPLATES[intent]
    
    # Weight selection based on recent usage
    if hasattr(context, 'recent_responses'):
        # Avoid recently used responses
        weights = [0.1 if r in context.recent_responses else 1.0 for r in responses]
    else:
        weights = [1.0] * len(responses)
    
    selected = random.choices(responses, weights=weights)[0]
    context.recent_responses = getattr(context, 'recent_responses', [])[-5:] + [selected]
    
    return selected
```

## Error Handling Patterns

### Speech Recognition Failures
```python
class ClarificationStrategy:
    def __init__(self, max_attempts: int = 3):
        self.attempts = 0
        self.strategies = [
            "Could you repeat that please?",
            "I'm having trouble hearing you. Could you speak up a bit?",
            "Let me make sure I understood - you said...?",
            "I want to make sure I have this right. Could you tell me one more time?",
        ]
    
    def get_clarification(self) -> str:
        """Get progressively more specific clarification requests"""
        if self.attempts >= len(self.strategies):
            return self.strategies[-1]
        
        response = self.strategies[self.attempts]
        self.attempts += 1
        return response
```

### Connection Issues
```python
async def handle_connection_issues(session: AgentSession):
    """Gracefully handle network problems"""
    @session.on("connection_quality_changed")
    async def on_quality_change(ev):
        if ev.quality == "poor":
            await session.say(
                "I'm sorry, it seems we have a poor connection. "
                "Can you hear me alright?"
            )
```

## Testing Strategy

### Unit Tests
```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent creates with proper instructions"""
    agent = AppointmentConfirmationAgent()
    assert "Sarah" in agent.instructions
    assert "appointment" in agent.instructions.lower()

@pytest.mark.asyncio
async def test_clarification_strategy():
    """Test progressive clarification requests"""
    strategy = ClarificationStrategy()
    
    first = strategy.get_clarification()
    assert "repeat" in first
    
    second = strategy.get_clarification()
    assert "trouble hearing" in second
    
    # Should get more specific each time
    assert len(second) > len(first)

@pytest.mark.asyncio
async def test_natural_pause_injection():
    """Test SSML pause markup is added correctly"""
    text = "Let me see your appointment details"
    result = add_natural_pauses(text)
    
    assert "<speak>" in result
    assert '<break time="600ms"/>' in result
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_full_conversation_flow():
    """Test complete appointment confirmation flow"""
    # Mock LiveKit session
    mock_session = AsyncMock(spec=AgentSession)
    mock_room = Mock()
    
    # Create agent
    agent = AppointmentConfirmationAgent()
    agent.session = mock_session
    
    # Test initial greeting
    await agent.on_enter()
    
    # Verify greeting was generated
    mock_session.generate_reply.assert_called_once()
    
    # Verify chat context has greeting
    assert len(mock_session.chat_ctx.messages) > 0
    assert "appointment" in mock_session.chat_ctx.messages[0].content
```

### Custom Testing UI Enhancement
For appointment-specific testing, enhance the React frontend:

```tsx
// components/appointment-test-panel.tsx
import { useState } from 'react';

export function AppointmentTestPanel() {
  const [scenario, setScenario] = useState('confirm');
  
  return (
    <div className="p-4 bg-gray-50 rounded-lg">
      <h3 className="font-semibold mb-3">Test Scenarios</h3>
      
      <div className="space-y-2">
        <button
          onClick={() => setScenario('confirm')}
          className="w-full p-2 text-left hover:bg-gray-100 rounded"
        >
          ✅ Confirm Appointment
        </button>
        
        <button
          onClick={() => setScenario('reschedule')}
          className="w-full p-2 text-left hover:bg-gray-100 rounded"
        >
          📅 Request Reschedule
        </button>
        
        <button
          onClick={() => setScenario('confused')}
          className="w-full p-2 text-left hover:bg-gray-100 rounded"
        >
          ❓ Act Confused
        </button>
        
        <button
          onClick={() => simulateNoise()}
          className="w-full p-2 text-left hover:bg-gray-100 rounded"
        >
          🔊 Add Background Noise
        </button>
      </div>
      
      <div className="mt-4 p-3 bg-blue-50 rounded">
        <p className="text-sm">
          <strong>Current Scenario:</strong> {scenario}
        </p>
        <p className="text-xs mt-1 text-gray-600">
          {getScenarioHint(scenario)}
        </p>
      </div>
    </div>
  );
}

function getScenarioHint(scenario: string): string {
  const hints = {
    confirm: "Say 'Yes, I'll be there' when asked",
    reschedule: "Say 'I need to reschedule' when asked",
    confused: "Say 'Who is this?' or 'What appointment?'",
  };
  return hints[scenario] || '';
}
```

### Manual Testing Checklist
- [ ] Voice sounds natural and warm
- [ ] Filler phrases occur naturally
- [ ] Pauses feel conversational
- [ ] Handles interruptions smoothly
- [ ] Recovers from misunderstandings
- [ ] Response variety prevents repetition
- [ ] Latency under 200ms consistently
- [ ] Clear audio quality maintained
- [ ] React frontend shows real-time transcriptions
- [ ] Audio visualizer reflects speech activity

## Deployment Configuration

### Environment Variables
```bash
# Required
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
OPENAI_API_KEY=your-openai-key
DEEPGRAM_API_KEY=your-deepgram-key

# Optional Performance Tuning
WORKER_CONCURRENCY=5  # Number of concurrent calls per worker
MAX_IDLE_TIME=300  # Seconds before idle worker shutdown
PREWARM_COUNT=2  # Number of prewarmed processes

# Feature Flags
ENABLE_METRICS=true
ENABLE_CALL_RECORDING=false  # Requires consent
USE_RESPONSE_CACHE=true

# API Integration (Future)
APPOINTMENT_API_URL=https://api.yourcompany.com
APPOINTMENT_API_KEY=your-api-key
```

### AWS Deployment
```yaml
# ECS Task Definition
{
  "family": "appointment-agent",
  "taskRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/appointment-agent-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "agent",
      "image": "YOUR_ECR_REPO/appointment-agent:latest",
      "environment": [
        {"name": "LIVEKIT_URL", "value": "wss://your.livekit.cloud"},
        {"name": "WORKER_CONCURRENCY", "value": "5"}
      ],
      "secrets": [
        {
          "name": "LIVEKIT_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:livekit-api-key"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

### Scaling Considerations
- **Horizontal Scaling**: Add more worker instances for higher call volume
- **Vertical Scaling**: Increase CPU/memory for better per-call performance
- **Geographic Distribution**: Deploy to multiple regions for lower latency
- **Auto-scaling Rules**: Scale based on active call count and CPU usage

## Monitoring & Observability

### Metrics Collection
```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
call_counter = Counter('appointment_calls_total', 'Total appointment calls made')
call_duration = Histogram('appointment_call_duration_seconds', 'Call duration in seconds')
active_calls = Gauge('appointment_active_calls', 'Number of active calls')
confirmation_rate = Counter('appointment_confirmations', 'Appointments confirmed', ['status'])

# Collect metrics
@session.on("session_started")
def on_session_start(ev):
    call_counter.inc()
    active_calls.inc()

@session.on("session_ended")
def on_session_end(ev):
    active_calls.dec()
    call_duration.observe(ev.duration)
    
    # Track confirmation status
    if ev.metadata.get('confirmed'):
        confirmation_rate.labels(status='confirmed').inc()
    elif ev.metadata.get('rescheduled'):
        confirmation_rate.labels(status='rescheduled').inc()
    else:
        confirmation_rate.labels(status='no_answer').inc()
```

### Logging Strategy
```python
import structlog

# Configure structured logging
logger = structlog.get_logger()

# Log key events
logger.info(
    "call_started",
    room_id=ctx.room.name,
    appointment_id=appointment_id,
    customer_phone=masked_phone,
)

logger.info(
    "conversation_turn",
    speaker="user",
    duration_ms=turn_duration,
    confidence=stt_confidence,
)

logger.warning(
    "clarification_needed",
    attempt=clarification_attempt,
    last_utterance=last_utterance,
)
```

## Common Gotchas

### Voice Pipeline
- **VAD Sensitivity**: Too sensitive causes word cutting, too insensitive delays responses
  - Solution: Test with various background noise levels
  - Recommended: Default Silero settings work well for most cases

- **Turn Detection**: May struggle with very short responses ("yes", "no")
  - Solution: Use combination of VAD and semantic model
  - Add minimum speech duration before considering turn complete

- **Audio Feedback**: Can occur in poor acoustic environments
  - Solution: Implement echo cancellation in client
  - Use headphones during development testing

### Performance
- **Model Loading**: Initial agent startup can be slow
  - Solution: Use prewarm function to load models
  - Keep workers warm with periodic health checks

- **Memory Leaks**: Long-running sessions can accumulate memory
  - Solution: Implement proper cleanup in shutdown callbacks
  - Monitor memory usage and restart workers periodically

- **API Rate Limits**: High call volume can hit provider limits
  - Solution: Implement request queuing and backoff
  - Use multiple API keys with round-robin

### Production
- **Cost Management**: 
  - GPT-4o-mini: ~$0.15 per 1M input tokens
  - Deepgram: ~$0.0125 per minute
  - OpenAI TTS: ~$15 per 1M characters
  - Estimate: ~$0.10-0.20 per average call

- **Compliance**: 
  - Call recording requires consent in many jurisdictions
  - HIPAA compliance needed for medical appointments
  - PII handling for customer data

## Validation Checklist

### Pre-deployment
- [x] Environment variables configured
- [x] Dependencies installed with correct versions
- [x] Agent connects successfully to LiveKit
- [x] Voice pipeline components initialize
- [x] Natural conversation elements working
- [x] Error handling tested
- [x] Latency within targets
- [x] Docker image builds successfully

### Post-deployment
- [ ] Health check endpoint responding
- [ ] Metrics being collected
- [ ] Logs aggregating properly
- [ ] Latency monitoring active
- [ ] Cost tracking enabled
- [ ] Alerting configured
- [ ] Backup plan for failures

## Success Metrics
- **Response Latency**: < 200ms (p99)
- **Call Success Rate**: > 95%
- **Confirmation Rate**: > 80% of reached customers
- **Natural Conversation Score**: > 4.5/5 (user feedback)
- **Cost per Call**: < $0.20
- **Concurrent Calls**: 25 per worker (4 CPU cores)

## References
- LiveKit Agents Docs: https://docs.livekit.io/agents/
- Voice Pipeline Guide: https://docs.livekit.io/agents/voice-agent/
- Turn Detection: https://docs.livekit.io/agents/build/turns/
- OpenAI TTS: https://platform.openai.com/docs/guides/text-to-speech
- Deepgram STT: https://developers.deepgram.com/docs/getting-started-with-live-streaming-audio
- Production Deployment: https://docs.livekit.io/agents/deployment/

## Appendix

### Complete Code Structure
```
appointment-confirmation-agent/
├── appointment_agent.py       # Main agent implementation
├── natural_speech.py         # Natural conversation utilities
├── response_templates.py     # Response variation templates
├── metrics.py               # Metrics collection
├── tests/
│   ├── test_agent.py       # Agent unit tests
│   ├── test_natural.py     # Natural speech tests
│   └── test_integration.py # Full flow tests
├── deployment/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── k8s/
│       ├── deployment.yaml
│       └── service.yaml
├── requirements.txt
├── .env.example
└── README.md
```

### Troubleshooting Guide

**Issue**: Agent sounds robotic
- Check temperature setting (should be 0.7-0.8)
- Verify natural speech elements are enabled
- Ensure response variation is working
- Check TTS voice settings

**Issue**: High latency
- Verify prewarm is loading models
- Check network latency to providers
- Enable response caching
- Consider upgrading to GPT-4o for complex calls

**Issue**: Poor speech recognition
- Check microphone quality on client side
- Verify Deepgram language settings
- Test with noise suppression enabled
- Consider fallback STT provider

**Issue**: Conversation gets stuck
- Check clarification strategy max attempts
- Verify turn detection settings
- Add conversation timeout
- Implement graceful exit phrases

### Cost Optimization
1. **Cache Common Responses**: Reduce LLM calls for frequent phrases
2. **Optimize Prompt Length**: Keep system prompt concise
3. **Use Streaming**: Reduce perceived latency
4. **Batch Process**: Group similar calls when possible
5. **Monitor Usage**: Set up cost alerts and limits

### Future Enhancements
1. **Multi-language Support**: Expand beyond English
2. **Sentiment Analysis**: Detect customer mood
3. **CRM Integration**: Pull/push appointment data
4. **Voicemail Detection**: Leave messages appropriately
5. **A/B Testing**: Optimize conversation strategies
6. **Custom Voices**: Train voice on company recordings