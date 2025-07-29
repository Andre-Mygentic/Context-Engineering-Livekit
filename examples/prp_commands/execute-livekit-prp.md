# Execute LiveKit Agents PRP

Implement a LiveKit Agents feature using the PRP file. This command is specialized for executing PRPs that build real-time voice and multimodal AI agents.

## PRP File: $ARGUMENTS

## Execution Process

1. **Load LiveKit PRP**
   - Read the specified LiveKit PRP file
   - Understand agent architecture and requirements
   - Review voice pipeline configuration
   - Note deployment and testing requirements

2. **ULTRATHINK - LiveKit Implementation**
   - Plan agent class structure and inheritance
   - Design voice pipeline with appropriate components
   - Map out function tools and their purposes
   - Consider multi-agent workflows if applicable
   - Plan testing and validation approach

3. **Environment Setup**
   - Create .env file with required API keys
   - Set up virtual environment with Python 3.11
   - Install LiveKit agents and provider plugins
   - Verify environment variables are loaded

4. **Execute LiveKit Implementation**
   - Implement entrypoint function
   - Create Agent class with instructions
   - Configure AgentSession with components
   - Implement function tools as needed
   - Set up proper error handling
   - Add metrics collection

5. **Voice Pipeline Configuration**
   - Select appropriate STT provider
   - Configure LLM (standard or realtime)
   - Choose TTS provider and voice
   - Set up VAD and turn detection
   - Test interruption handling

6. **Validate LiveKit Agent**
   - Run Python syntax checks
   - Test imports and dependencies
   - Verify environment configuration
   - Test with local LiveKit server (if available)
   - Check metrics collection
   - Validate error handling

7. **Complete Implementation**
   - Ensure all PRP requirements met
   - Run final validation suite
   - Document any deviations
   - Prepare deployment configuration

## LiveKit-Specific Validation

### Code Structure
```bash
# Verify agent structure
grep -q "async def entrypoint" agent.py
grep -q "class.*Agent" agent.py
grep -q "cli.run_app" agent.py
```

### Dependencies
```bash
# Check required imports
python -c "from livekit.agents import Agent, AgentSession, JobContext"
python -c "from livekit.plugins import openai, deepgram, silero"
```

### Environment
```bash
# Validate environment variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; assert os.getenv('LIVEKIT_URL')"
```

### Functionality
```bash
# Test agent initialization
python -c "from agent import MyAgent; a = MyAgent()"
```

## Common LiveKit Patterns to Implement

### Basic Voice Agent
- Inherit from Agent base class
- Configure all pipeline components
- Implement on_enter() method
- Set up metrics collection

### Realtime Agent
- Use openai.realtime.RealtimeModel
- Configure turn detection
- Handle pure audio pipeline
- Optimize for low latency

### Multi-Agent System
- Create specialized agent classes
- Implement handoff logic
- Preserve conversation context
- Share state between agents

### Function Tools
- Use @function_tool decorator
- Include comprehensive docstrings
- Handle errors with ToolError
- Validate inputs properly

## Troubleshooting

### Connection Issues
- Verify LIVEKIT_URL format (wss://)
- Check API credentials
- Ensure network connectivity

### Audio Issues
- Adjust VAD sensitivity
- Configure turn detection
- Check audio format compatibility

### Performance Issues
- Use prewarm for model loading
- Monitor CPU and memory usage
- Optimize component selection

Note: Always test with a local LiveKit server before production deployment.