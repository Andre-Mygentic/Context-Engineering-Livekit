# LiveKit Agents Core Patterns

This document covers essential patterns and best practices for building LiveKit Agents.

## Agent Architecture Patterns

### Basic Agent Pattern
The fundamental pattern for all LiveKit agents:

```python
from livekit.agents import Agent

class MyAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="Agent personality and behavior instructions"
        )
    
    async def on_enter(self):
        """Called when agent joins the session"""
        self.session.generate_reply()
```

### Agent Lifecycle Events
- `on_enter()`: Agent joins session, generate initial response
- `on_leave()`: Agent leaves session, cleanup
- `on_error()`: Handle agent-level errors

## AgentSession Configuration

### Complete Configuration Options
```python
session = AgentSession(
    # Core components
    stt=deepgram.STT(model="nova-3"),
    llm=openai.LLM(model="gpt-4o-mini"),
    tts=openai.TTS(voice="alloy"),
    vad=silero.VAD.load(),
    
    # Turn detection
    turn_detection=MultilingualModel(),  # or "vad" or "manual"
    
    # Behavior settings
    allow_interruptions=True,
    min_interruption_duration=0.5,
    min_endpointing_delay=0.4,
    max_endpointing_delay=6.0,
    
    # Advanced features
    preemptive_generation=False,
    use_tts_aligned_transcript=False,
    discard_audio_if_uninterruptible=True,
    
    # State management
    userdata=None,  # Or typed dataclass
    
    # Tool configuration
    mcp_servers=[],  # MCP server integrations
)
```

### Parameter Defaults and Meanings
- `allow_interruptions` (True): User can interrupt agent speech
- `min_interruption_duration` (0.5s): Minimum speech to trigger interruption
- `min_endpointing_delay` (0.4s): Minimum wait after speech ends
- `max_endpointing_delay` (6.0s): Maximum wait when user likely to continue

## Event Handling Patterns

### Session Events
```python
@session.on("user_state_changed")
def on_user_state_changed(ev):
    """User states: speaking, listening, away"""
    if ev.new_state == "speaking":
        logger.info("User started speaking")

@session.on("agent_state_changed")
def on_agent_state_changed(ev):
    """Agent states: thinking, speaking, listening"""
    if ev.new_state == "thinking":
        logger.info("Agent processing")

@session.on("metrics_collected")
def on_metrics_collected(ev):
    """Metrics for monitoring"""
    metrics.log_metrics(ev.metrics)
```

### Room Events
```python
@ctx.room.on("participant_connected")
def on_participant_connected(participant):
    logger.info(f"Participant joined: {participant.identity}")

@ctx.room.on("track_subscribed")
def on_track_subscribed(track, publication, participant):
    if track.kind == rtc.TrackKind.KIND_AUDIO:
        # Handle audio track
        pass
```

## Multi-Agent Handoff Strategies

### Tool Return Pattern
```python
class IntakeAgent(Agent):
    @function_tool
    async def transfer_to_specialist(self, context: RunContext):
        """Transfer to specialist agent"""
        # Return message and new agent
        return "Transferring to specialist", SpecialistAgent(chat_ctx=self.chat_ctx)
```

### Manual Update Pattern
```python
# Update agent programmatically
session.update_agent(new_agent)
```

### State Preservation
```python
# Preserve conversation context
new_agent = SpecialistAgent(chat_ctx=self.chat_ctx)

# Share state with userdata
@dataclass
class SharedState:
    user_info: dict = field(default_factory=dict)

session = AgentSession[SharedState](userdata=SharedState())
```

## Voice Pipeline Optimization

### Component Selection Guide

**STT Providers**:
- Deepgram: Best accuracy, multi-language support
- OpenAI: Good for English, integrates with OpenAI ecosystem
- Configuration: Always specify model and language

**LLM Selection**:
- `gpt-4o-mini`: Cost-effective, fast responses
- `gpt-4o`: Higher quality, more complex reasoning
- `gpt-4o-realtime`: Direct audio processing

**TTS Providers**:
- OpenAI: Simple, multiple voices (alloy, echo, fable, nova, onyx, shimmer)
- Cartesia: High quality, natural sounding
- ElevenLabs: Premium quality, more expensive

### Turn Detection Models

**VAD (Voice Activity Detection)**:
```python
session = AgentSession(
    turn_detection="vad",
    vad=silero.VAD.load()
)
```

**Context-Aware Models**:
```python
from livekit.plugins.turn_detector.english import EnglishModel
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# English (200MB RAM, ~10ms inference)
turn_detection=EnglishModel()

# Multilingual (400MB RAM, ~25ms inference)
# Supports: EN, FR, ES, DE, IT, PT, NL, ZH, JA, KO, ID, RU, TR
turn_detection=MultilingualModel()
```

## Function Tool Patterns

### Basic Tool Pattern
```python
@function_tool
async def get_weather(context: RunContext, location: str) -> str:
    """Get weather for a location.
    
    Args:
        location: City name or coordinates
    """
    return f"Weather in {location}: Sunny, 70°F"
```

### Raw Schema Pattern
```python
@function_tool(raw_schema={
    "type": "function",
    "name": "complex_tool",
    "description": "Tool with complex parameters",
    "parameters": {
        "type": "object",
        "properties": {
            "data": {"type": "object"},
            "options": {"type": "array"}
        }
    }
})
async def complex_tool(raw_arguments: dict, context: RunContext):
    # Handle complex arguments
    pass
```

### RPC Tool Pattern
```python
@function_tool
async def get_user_location(context: RunContext) -> dict:
    """Get user's location via RPC to frontend"""
    room = get_job_context().room
    participant = next(iter(room.remote_participants))
    
    response = await room.local_participant.perform_rpc(
        destination_identity=participant,
        method="getUserLocation",
        payload=json.dumps({}),
        response_timeout=5.0,
    )
    return response
```

## Error Handling with ToolError

```python
from livekit.agents import ToolError

@function_tool
async def api_call(context: RunContext, endpoint: str):
    try:
        result = await external_api.call(endpoint)
        return result
    except APIError as e:
        # User-friendly error message
        raise ToolError(f"Service temporarily unavailable: {e.service}")
    except Exception as e:
        # Generic error handling
        raise ToolError("An unexpected error occurred")
```

## Session Lifecycle Management

### Complete Session Flow
```python
async def entrypoint(ctx: JobContext):
    # 1. Connect to room
    await ctx.connect()
    
    # 2. Create session with configuration
    session = AgentSession(...)
    
    # 3. Set up event handlers
    @session.on("metrics_collected")
    def handle_metrics(ev):
        pass
    
    # 4. Start session with agent
    await session.start(
        agent=MyAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(),
        room_output_options=RoomOutputOptions(
            transcription_enabled=True
        )
    )
    
    # Session runs until room closes or participants leave
```

### Graceful Shutdown
```python
# Add shutdown callbacks
async def cleanup():
    logger.info("Session ending, performing cleanup")
    # Save state, close connections, etc.

ctx.add_shutdown_callback(cleanup)
```

## Performance Patterns

### Prewarm Function
```python
def prewarm(proc: JobProcess):
    """Load heavy resources before job assignment"""
    # Load VAD model
    proc.userdata["vad"] = silero.VAD.load()
    
    # Pre-load other models if needed
    # proc.userdata["custom_model"] = load_model()

# Use in worker
cli.run_app(WorkerOptions(
    entrypoint_fnc=entrypoint,
    prewarm_fnc=prewarm
))
```

### Resource Management
```python
# Proper audio stream cleanup
async def process_audio(track):
    audio_stream = rtc.AudioStream(track)
    try:
        async for event in audio_stream:
            # Process audio
            pass
    finally:
        await audio_stream.aclose()  # Always cleanup
```

### Metrics Collection
```python
from livekit.agents import metrics

usage_collector = metrics.UsageCollector()

@session.on("metrics_collected")
def collect_metrics(ev):
    metrics.log_metrics(ev.metrics)
    usage_collector.collect(ev.metrics)

# Log summary on shutdown
async def log_usage():
    summary = usage_collector.get_summary()
    logger.info(f"Session usage: {summary}")

ctx.add_shutdown_callback(log_usage)
```

## Testing Patterns

### Basic Test Structure
```python
@pytest.mark.asyncio
async def test_agent():
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(MyAgent())
        
        result = await session.run(user_input="Hello")
        
        # Validate with LLM judge
        await result.expect.next_event().is_message(
            role="assistant"
        ).judge(llm, intent="Friendly greeting")
```

### Tool Testing
```python
# Test function calls
result = await session.run(user_input="What's the weather?")

result.expect.next_event().is_function_call(
    name="get_weather",
    arguments={"location": "San Francisco"}
)

# Mock tools
from livekit.agents.testing import mock_tools

with mock_tools(MyAgent, {"get_weather": lambda: "Sunny"}):
    result = await session.run(user_input="Weather?")
    # Test with mocked response
```

These patterns form the foundation for building robust, production-ready LiveKit agents with proper error handling, performance optimization, and testing strategies.