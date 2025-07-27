# OpenAI Realtime API Agent Example

This example demonstrates a low-latency speech-to-speech agent using OpenAI's Realtime API with LiveKit.

## Features

- **Direct Audio Processing**: No intermediate text conversion
- **Sub-second Latency**: Typically 100-500ms response time
- **Natural Speech**: Preserves emotion, tone, and inflection
- **Interruption Handling**: Natural conversation flow with interruptions
- **Function Tools**: Weather lookup and joke telling

## Key Differences from STT→LLM→TTS

### Traditional Pipeline
- Multiple API calls (STT, LLM, TTS)
- 2-4 second typical latency
- Loses emotional context
- Robotic feel

### Realtime API
- Single API for all processing
- Sub-second responses
- Preserves voice characteristics
- Natural conversation flow

## Setup

1. Copy environment template from basic_voice_agent
2. Ensure you have OpenAI API access to Realtime models
3. Install dependencies:
```bash
pip install "livekit-agents[openai]~=1.0"
```

## Configuration

### Voice Options
The realtime model supports 6 voices:
- `alloy`: Neutral, balanced
- `echo`: Warm, engaging  
- `fable`: Expressive, animated
- `onyx`: Deep, authoritative
- `nova`: Bright, enthusiastic
- `shimmer`: Gentle, soothing

### Turn Detection
Two types available:
- `server_vad`: Silence-based detection (used here)
- `semantic_vad`: Context-aware detection

### Model Selection
- `gpt-4o-realtime-preview`: Full capabilities
- `gpt-4o-mini-realtime-preview`: 90% cost reduction

## Architecture

```python
# Key components:
- No separate STT/TTS components
- Single realtime model handles all audio
- Server-side VAD for turn detection
- Direct audio modalities
```

## Performance Optimization

### For Lowest Latency
1. Use `modalities=["audio"]` (audio-only)
2. Deploy close to OpenAI servers (US)
3. Use `gpt-4o-mini-realtime-preview`
4. Optimize VAD parameters

### VAD Tuning
- Lower `silence_duration_ms` for faster turns
- Adjust `threshold` based on environment noise
- Reduce `prefix_padding_ms` for minimal delay

## Common Issues

### Function Tool Compatibility
If you encounter errors with function tools, ensure you're using the latest LiveKit version:
```bash
pip install --upgrade "livekit-agents[openai]"
```

### Session Limits
- Maximum session duration: 30 minutes
- Plan for session rotation in production

## Monitoring

The agent logs:
- User and agent state changes
- Function tool calls
- Connection events

Use these logs to monitor conversation flow and debug issues.