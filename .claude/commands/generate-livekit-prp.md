# Generate LiveKit Agents PRP

## Feature file: $ARGUMENTS

Generate a comprehensive PRP for LiveKit Agents implementation with thorough research. This command is specialized for creating real-time voice and multimodal AI agents using the LiveKit framework.

## Research Process

1. **LiveKit Architecture Analysis**
   - Review LiveKit Agents documentation for patterns
   - Understand Worker → Job → Session lifecycle
   - Analyze voice pipeline components (STT, LLM, TTS, VAD)
   - Study turn detection and interruption handling
   - Research OpenAI Realtime API integration patterns

2. **Codebase Analysis**
   - Search for existing agent implementations
   - Identify function tool patterns
   - Review multi-agent handoff examples
   - Check testing patterns for agents
   - Note deployment configurations

3. **External Research**
   - LiveKit official documentation (https://docs.livekit.io/agents/)
   - Provider integrations (OpenAI, Deepgram, Cartesia, etc.)
   - WebRTC and real-time communication patterns
   - Production deployment best practices
   - Community examples and patterns

4. **Voice Pipeline Research**
   - Compare STT→LLM→TTS vs Realtime API pipelines
   - Research latency optimization techniques
   - Study VAD configuration patterns
   - Analyze turn detection models

## PRP Generation

Using PRPs/templates/prp_livekit_base.md as template:

### Critical Context to Include
- **LiveKit Documentation**: 
  - Agent lifecycle and architecture
  - Voice pipeline configuration
  - Function tools and decorators
  - Multi-agent patterns
  - Deployment strategies

- **Code Examples**:
  - Basic voice agent with all components
  - Realtime API agent for low latency
  - Multi-agent handoff patterns
  - Function tool implementations
  - Testing patterns

- **Provider Integration**:
  - OpenAI (standard and realtime)
  - Deepgram STT configuration
  - Cartesia/ElevenLabs TTS
  - Silero VAD setup

- **Production Patterns**:
  - Worker configuration and scaling
  - Environment management
  - Monitoring and metrics
  - Error handling

### Implementation Blueprint
- Start with environment setup (.env configuration)
- Define agent architecture (Agent class pattern)
- Configure voice pipeline components
- Implement function tools as needed
- Set up proper error handling
- Include deployment configuration

### Validation Gates (Must be Executable)
```bash
# Python environment check
python --version | grep -E "3\.(9|10|11)"

# Dependency installation
pip install -r requirements.txt

# Syntax validation
python -m py_compile agent.py

# Import verification
python -c "from livekit.agents import Agent, AgentSession, JobContext"

# Environment validation
python -c "import os; assert os.getenv('LIVEKIT_URL'), 'Missing LIVEKIT_URL'"

# Local testing (if LiveKit server available)
# python agent.py dev
```

*** CRITICAL: Research LiveKit-specific patterns before writing PRP ***
*** Include OpenAI Realtime API patterns for low-latency applications ***
*** Document turn detection and VAD configuration thoroughly ***

## LiveKit-Specific Considerations

### Agent Patterns
- Always inherit from Agent base class
- Implement on_enter() for initial behavior
- Use function_tool decorator for LLM tools
- Handle async operations properly

### Voice Pipeline
- Choose components based on use case
- Configure turn detection appropriately
- Handle interruptions gracefully
- Optimize for latency when needed

### Multi-Agent Systems
- Design clear handoff patterns
- Preserve conversation context
- Share state with typed userdata
- Test agent transitions

### Production Readiness
- Use prewarm for model loading
- Configure health checks
- Implement metrics collection
- Plan for graceful shutdown

## Output
Save as: `PRPs/livekit-{feature-name}.md`

## Quality Checklist
- [ ] Worker lifecycle clearly explained
- [ ] Voice pipeline configuration documented
- [ ] Function tools properly defined
- [ ] Multi-agent patterns included (if applicable)
- [ ] Deployment configuration provided
- [ ] Validation gates are executable
- [ ] Error handling comprehensive
- [ ] Monitoring strategy defined

Score the PRP on a scale of 1-10 (confidence level for successful LiveKit agent implementation).

Remember: The goal is creating production-ready real-time AI agents with proper patterns and comprehensive context.