# OpenAI Realtime API Integration Guide for LiveKit Agents

This guide covers comprehensive implementation details for using OpenAI's Realtime API with LiveKit Agents to achieve sub-second latency speech-to-speech interactions.

## Overview

The OpenAI Realtime API enables **direct audio processing** without intermediate text conversion, preserving emotional context and achieving response times under 500ms. This is a significant improvement over traditional STT→LLM→TTS pipelines which typically have 2-4 second latency.

## Configuration and Setup

### Installation
```bash
pip install "livekit-agents[openai]~=1.0"
```

### Basic Configuration
```python
from livekit.agents import AgentSession
from livekit.plugins import openai
from livekit.plugins.openai import realtime
from openai.types.beta.realtime.session import TurnDetection

# Configure realtime model
realtime_model = openai.realtime.RealtimeModel(
    model="gpt-4o-realtime-preview",  # or "gpt-4o-mini-realtime-preview"
    voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
    temperature=0.8,  # Range: 0.6-1.2
    modalities=["text", "audio"],  # Both text and audio output
)
```

## Model Selection

### Available Models
- **`gpt-4o-realtime-preview`**: Full capability model
- **`gpt-4o-mini-realtime-preview`**: 90% cost reduction, maintained quality

### Voice Options
Six preset voices with natural inflection capabilities:
- `alloy`: Neutral, balanced
- `echo`: Warm, engaging
- `fable`: Expressive, animated
- `onyx`: Deep, authoritative
- `nova`: Bright, enthusiastic
- `shimmer`: Gentle, soothing

## Speech-to-Speech Implementation

### Pure Audio Pipeline
```python
async def entrypoint(ctx: JobContext):
    await ctx.connect()
    
    # Pure speech-to-speech configuration
    realtime_model = openai.realtime.RealtimeModel(
        model="gpt-4o-realtime-preview",
        voice="alloy",
        temperature=0.8,
        modalities=["audio"],  # Audio-only for maximum speed
        turn_detection=TurnDetection(
            type="server_vad",
            threshold=0.5,
            prefix_padding_ms=300,
            silence_duration_ms=500,
            create_response=True,
            interrupt_response=True,
        )
    )
    
    # No STT/TTS needed with realtime model
    session = AgentSession(
        llm=realtime_model,
    )
    
    await session.start(
        room=ctx.room,
        agent=RealtimeAgent()
    )
```

### Benefits Over Traditional Pipeline

| Aspect | Realtime API | STT→LLM→TTS |
|--------|--------------|-------------|
| Latency | ~100-500ms | 2-4 seconds |
| Emotional Context | Preserved | Lost |
| Voice Nuance | Natural | Synthetic |
| Architecture | Simple | Complex |
| API Calls | Single | Multiple |

## Turn Detection Configuration

### Server VAD (Voice Activity Detection)
```python
turn_detection = TurnDetection(
    type="server_vad",
    threshold=0.5,  # 0.0-1.0, higher = louder required
    prefix_padding_ms=300,  # Audio before speech detection
    silence_duration_ms=500,  # Silence to end turn
    create_response=True,  # Auto-generate response
    interrupt_response=True,  # Allow interruptions
)
```

### Semantic VAD
More intelligent turn detection based on content understanding:
```python
turn_detection = TurnDetection(
    type="semantic_vad",
    eagerness="auto",  # Options: low, medium, high, auto
    create_response=True,
    interrupt_response=True,
)
```

### VAD Parameter Tuning

| Parameter | Low Latency | Natural Conversation | Noisy Environment |
|-----------|-------------|---------------------|-------------------|
| threshold | 0.4 | 0.5 | 0.7 |
| prefix_padding_ms | 200 | 300 | 400 |
| silence_duration_ms | 400 | 500 | 800 |

## Low-Latency Optimization

### Infrastructure Optimization
1. **Geographic Proximity**: Deploy workers close to OpenAI servers (US-based)
2. **Edge Deployment**: Use LiveKit Cloud edge servers
3. **Network Quality**: Ensure stable, low-latency connections

### Configuration for Speed
```python
# Optimized for lowest latency
realtime_model = openai.realtime.RealtimeModel(
    model="gpt-4o-mini-realtime-preview",  # Faster model
    voice="alloy",
    temperature=0.7,  # Slightly lower for consistency
    modalities=["audio"],  # Pure audio
    turn_detection=TurnDetection(
        type="server_vad",
        threshold=0.6,
        silence_duration_ms=400,  # Faster turn detection
        prefix_padding_ms=200,  # Minimal padding
    )
)
```

### Performance Metrics
- **First Token**: < 200ms achievable
- **Complete Response**: 500ms-1s typical
- **Interruption Handling**: < 100ms

## Interruption Handling

### Automatic Interruption Management
The Realtime API automatically handles interruptions when configured:

```python
turn_detection = TurnDetection(
    interrupt_response=True,  # Enable interruption
    create_response=True,
)
```

### Manual Interruption Control
For custom interruption logic:
```python
# Cancel current generation
session.interrupt()

# Clear audio buffer
session.clear_user_turn()
```

### Interruption Events
```python
@session.on("speech_interrupted")
def on_interrupted():
    logger.info("User interrupted agent speech")
```

## Common Issues and Solutions

### Function Tool Compatibility
**Issue**: Runtime error with function tools in older versions
```
Error in agent_activity.py line 1421
```

**Solution**:
```bash
pip install --upgrade "livekit-agents[openai]"
```

### Session Configuration
**Issue**: Parameters not applying correctly

**Solution**: Set all parameters during initialization
```python
# Correct - all parameters at initialization
realtime_model = openai.realtime.RealtimeModel(
    model="gpt-4o-realtime-preview",
    voice="alloy",
    temperature=0.8,
    turn_detection=turn_detection_config
)

# Incorrect - trying to update after creation
realtime_model.update_options(...)  # May not work
```

### High Latency Issues
**Issue**: Response times over 1 second

**Solutions**:
1. Use `gpt-4o-mini-realtime-preview`
2. Optimize VAD parameters
3. Check network latency
4. Use audio-only modalities

### Interruption Not Working
**Issue**: Agent continues talking when interrupted

**Solution**: Ensure proper configuration
```python
turn_detection = TurnDetection(
    type="server_vad",
    interrupt_response=True,  # Must be True
    create_response=True,
)
```

## Session Limits and Management

### Session Duration
- **Maximum Duration**: 30 minutes per session
- **Automatic Termination**: Session ends after max duration
- **Reconnection**: New session required after termination

### Resource Management
```python
# Monitor session duration
import time

class RealtimeAgent(Agent):
    def __init__(self):
        super().__init__()
        self.session_start = time.time()
    
    async def check_session_duration(self):
        elapsed = time.time() - self.session_start
        if elapsed > 1700:  # 28 minutes
            logger.warning("Session approaching 30-minute limit")
```

## Performance Comparison

### Latency Breakdown

**Traditional Pipeline (STT→LLM→TTS)**:
- STT Processing: 500-1000ms
- LLM Generation: 1000-2000ms
- TTS Synthesis: 500-1000ms
- **Total**: 2000-4000ms

**Realtime API**:
- Audio Processing + Response: 100-500ms
- **Total**: 100-500ms

### Quality Comparison

| Feature | Realtime API | Traditional |
|---------|--------------|-------------|
| Emotion Preservation | ✓ Full | ✗ Limited |
| Natural Pauses | ✓ Yes | ✗ No |
| Accent/Tone | ✓ Preserved | ✗ Lost |
| Interruption | ✓ Natural | ~ Delayed |
| Conversation Flow | ✓ Human-like | ~ Robotic |

## Advanced Configuration

### Complete Configuration Example
```python
from livekit.agents import APIConnectOptions

realtime_model = openai.realtime.RealtimeModel(
    model="gpt-4o-realtime-preview",
    voice="alloy",
    temperature=0.8,
    modalities=["text", "audio"],
    
    # Input audio transcription (optional)
    input_audio_transcription={
        "model": "whisper-1"
    },
    
    # Turn detection
    turn_detection=TurnDetection(
        type="server_vad",
        threshold=0.5,
        prefix_padding_ms=300,
        silence_duration_ms=500,
        create_response=True,
        interrupt_response=True,
    ),
    
    # Connection options
    conn_options=APIConnectOptions(
        max_retry=3,
        retry_interval=2.0,
        timeout=10.0
    ),
    
    # Tool configuration
    tool_choice="auto",
)
```

### Function Tools with Realtime
```python
class RealtimeAgent(Agent):
    @function_tool
    async def get_weather(self, context: RunContext, location: str):
        """Get weather information"""
        # Implementation
        return f"Weather in {location}: Sunny"
    
    @function_tool
    async def book_appointment(self, context: RunContext, date: str):
        """Book an appointment"""
        # Implementation
        return f"Appointment booked for {date}"
```

## Best Practices

### Do's
- ✓ Use audio-only modalities for lowest latency
- ✓ Configure VAD based on environment
- ✓ Handle session limits gracefully
- ✓ Monitor performance metrics
- ✓ Use mini model for cost optimization

### Don'ts
- ✗ Don't mix STT/TTS with Realtime model
- ✗ Don't ignore interruption configuration
- ✗ Don't assume unlimited session duration
- ✗ Don't use high temperature for consistent responses
- ✗ Don't skip error handling

## Monitoring and Debugging

### Performance Monitoring
```python
@session.on("metrics_collected")
def on_metrics(ev):
    metrics = ev.metrics
    logger.info(f"Latency: {metrics.ttfb}ms")
    logger.info(f"Processing: {metrics.processing_time}ms")
```

### Debug Logging
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("realtime-agent")

# Log all Realtime API events
@session.on("realtime_event")
def on_realtime_event(event):
    logger.debug(f"Realtime event: {event.type}")
```

## Migration Guide

### From STT→LLM→TTS to Realtime

**Before** (Traditional Pipeline):
```python
session = AgentSession(
    stt=deepgram.STT(),
    llm=openai.LLM(),
    tts=openai.TTS(),
    vad=silero.VAD.load(),
)
```

**After** (Realtime API):
```python
session = AgentSession(
    llm=openai.realtime.RealtimeModel(
        model="gpt-4o-realtime-preview",
        voice="alloy",
        turn_detection=TurnDetection(type="server_vad")
    )
)
```

### Key Differences
1. No separate STT/TTS components
2. Voice selection in model config
3. Turn detection built into model
4. Single API for all processing

## Cost Considerations

### Pricing Comparison
- **Realtime API**: Single charge for audio processing
- **Traditional**: Separate charges for STT + LLM + TTS
- **Mini Model**: 90% cost reduction from full model

### Optimization Strategies
1. Use `gpt-4o-mini-realtime-preview` when possible
2. Implement usage caps per session
3. Monitor token/audio usage
4. Set appropriate session limits

This comprehensive guide provides everything needed to implement and optimize OpenAI's Realtime API with LiveKit Agents for production-ready, low-latency voice interactions.