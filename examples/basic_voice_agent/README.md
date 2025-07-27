# Basic Voice Agent Example

This example demonstrates a simple conversational voice agent with function tools using LiveKit Agents.

## Features

- Natural voice conversation with STT→LLM→TTS pipeline
- Function tools for weather lookup and reminders
- Multi-language support with turn detection
- Metrics collection and logging
- Graceful error handling

## Setup

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
- LiveKit Cloud credentials
- OpenAI API key
- Deepgram API key

3. Install dependencies:
```bash
pip install "livekit-agents[openai,deepgram,silero]~=1.0"
```

## Running the Agent

### Development Mode
```bash
python agent.py dev
```

### Production Mode
```bash
python agent.py start
```

### Console Mode (Terminal Testing)
```bash
python agent.py console
```

## Architecture

### Components
- **STT**: Deepgram Nova-3 (multi-language)
- **LLM**: OpenAI GPT-4o-mini
- **TTS**: OpenAI TTS (alloy voice)
- **VAD**: Silero VAD
- **Turn Detection**: Multilingual model

### Agent Personality
The agent is configured as "Kelly" - a helpful, friendly voice assistant with a warm personality.

### Function Tools
1. **Weather Lookup**: Provides weather information for any location
2. **Set Reminder**: Creates reminders (mock implementation)

## Code Structure

```python
# Main components:
- MyAgent class: Defines agent personality and tools
- prewarm(): Loads VAD model for performance
- entrypoint(): Main agent initialization and session setup
```

## Customization

### Change Agent Personality
Edit the `instructions` parameter in `MyAgent.__init__()`

### Add New Tools
Use the `@function_tool` decorator:
```python
@function_tool
async def my_tool(self, context: RunContext, param: str):
    """Tool description for LLM"""
    return "Result"
```

### Adjust Voice Pipeline
Modify components in `AgentSession()` initialization

## Monitoring

The agent logs:
- Connection events
- Function tool calls
- Metrics and usage
- Errors and warnings

Check logs for debugging and monitoring agent behavior.