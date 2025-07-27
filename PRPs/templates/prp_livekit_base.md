# PRP: [LiveKit Agent Feature Name]

## Overview
[Brief description of the LiveKit agent to be built, its purpose, and key capabilities]

## LiveKit Architecture Context

### Agent Lifecycle
LiveKit Agents follow a Worker → Job → Session pattern:
1. **Worker**: Registers with LiveKit server, accepts job requests
2. **Job**: Created when a room needs an agent, runs in isolated process
3. **Session**: Manages the agent's participation in the room

### Voice Pipeline Options
1. **STT→LLM→TTS Pipeline**: Traditional approach with ~2-4 second latency
2. **OpenAI Realtime API**: Direct audio processing with sub-second latency

### Key Components
- **Agent**: Core logic and personality (instructions, tools)
- **AgentSession**: Orchestrates media streams and AI pipeline
- **JobContext**: Room connection and lifecycle management
- **Function Tools**: LLM-accessible functions for extended capabilities

## Requirements

### Functional Requirements
- [List specific agent behaviors and capabilities]
- [Voice interaction patterns needed]
- [Integration requirements]
- [Performance targets]

### Technical Requirements
- Python 3.9+ (3.11 recommended)
- LiveKit Agents SDK ~1.0
- Required providers: [OpenAI, Deepgram, etc.]
- Environment: [Development/Production specifications]

## Implementation Plan

### Phase 1: Environment Setup
1. Create virtual environment with Python 3.11
2. Install dependencies:
   ```bash
   pip install "livekit-agents[openai,deepgram,silero]~=1.0"
   ```
3. Configure .env file:
   ```
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your-key
   LIVEKIT_API_SECRET=your-secret
   OPENAI_API_KEY=your-openai-key
   ```

### Phase 2: Agent Implementation

#### Core Agent Structure
```python
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, openai, silero

class [AgentName](Agent):
    def __init__(self):
        super().__init__(
            instructions="[Agent personality and behavior instructions]"
        )
    
    async def on_enter(self):
        # Initial behavior when agent joins
        self.session.generate_reply()

async def entrypoint(ctx: JobContext):
    await ctx.connect()  # ALWAYS connect first
    
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-3"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="alloy"),
    )
    
    await session.start(
        agent=[AgentName](),
        room=ctx.room
    )
```

#### Voice Pipeline Configuration
[Specify component choices and configuration based on requirements]

#### Function Tools
[Define any function tools needed for the agent]

### Phase 3: Testing & Validation
1. Local testing with LiveKit server
2. Voice interaction testing
3. Function tool validation
4. Performance measurements
5. Error scenario testing

### Phase 4: Production Preparation
1. Container configuration
2. Environment variable management
3. Monitoring setup
4. Deployment configuration

## Voice Pipeline Details

### Component Selection Rationale
- **STT**: [Provider choice and why]
- **LLM**: [Model choice and configuration]
- **TTS**: [Voice selection and settings]
- **VAD**: [Turn detection approach]

### Latency Optimization
[If using Realtime API or other optimization strategies]

## Function Tools Design

### Tool Definitions
```python
@function_tool
async def [tool_name](context: RunContext, [parameters]) -> [return_type]:
    """[Clear description for LLM]
    
    Args:
        [parameter]: [description]
    """
    # Implementation
```

### Error Handling
- Use ToolError for user-friendly error messages
- Validate all inputs
- Handle async operations properly

## Multi-Agent Patterns
[If applicable, describe agent handoff patterns and state management]

## Testing Strategy

### Unit Tests
- Test agent initialization
- Validate function tools
- Mock external dependencies

### Integration Tests
- Test with LiveKit server
- Validate voice pipeline
- Test agent interactions

### Performance Tests
- Measure response latency
- Monitor resource usage
- Validate scalability

## Deployment Configuration

### Container Setup
```dockerfile
FROM python:3.11-slim
# ... LiveKit-specific configuration
```

### Environment Variables
[List all required environment variables]

### Scaling Considerations
- Worker pool configuration
- Resource requirements (4 cores per 25 agents)
- Graceful shutdown handling

## Monitoring & Observability

### Metrics Collection
```python
from livekit.agents import metrics

# ... metrics setup
```

### Logging Strategy
- Session lifecycle events
- Error tracking
- Performance metrics

## Common Gotchas

### Voice Pipeline
- VAD sensitivity tuning
- Turn detection edge cases
- Audio format compatibility

### Performance
- Model loading in prewarm
- Memory management
- Connection stability

### Production
- API rate limiting
- Cost optimization
- Security considerations

## Validation Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Agent connects successfully
- [ ] Voice pipeline functional
- [ ] Function tools tested
- [ ] Error handling verified

### Post-deployment
- [ ] Monitoring active
- [ ] Metrics collecting
- [ ] Logs accessible
- [ ] Performance acceptable
- [ ] Costs within budget

## Success Metrics
- Response latency: [Target]
- Successful interactions: [Target]
- Error rate: [Target]
- User satisfaction: [Measurement]

## References
- LiveKit Agents Docs: https://docs.livekit.io/agents/
- Provider Documentation: [Links]
- Example Implementations: [Links]

## Appendix

### Complete Code Template
[Include full agent implementation template]

### Troubleshooting Guide
[Common issues and solutions]

### Cost Estimation
[Provider costs and optimization strategies]