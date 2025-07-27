# LiveKit Appointment Confirmation Agent - Development Guidelines

This file contains project-specific guidelines for the LiveKit appointment confirmation voice agent. These rules work in conjunction with the global Archon workflow defined in `/Users/andrep/Documents/code/CLAUDE.md`.

## 🎯 Project Overview

**Archon Project ID**: `49edfe6d-f6d1-4338-9222-97d5679da1a3`

This project implements a human-like voice agent that makes appointment confirmation calls 24 hours in advance. The agent uses LiveKit's voice pipeline with natural conversation features to sound convincingly human.

## 🔄 Archon Task Management

### Active Development Workflow

**ALWAYS check current tasks before coding:**

```python
# View all project tasks
archon:manage_task(
  action="list",
  filter_by="project",
  filter_value="49edfe6d-f6d1-4338-9222-97d5679da1a3",
  include_closed=false
)

# Get highest priority task
# Look for highest task_order value in "todo" status
```

### Task Status Flow
1. **todo** → Unstarted tasks
2. **doing** → Currently working (only ONE at a time)
3. **review** → Implementation complete, needs testing
4. **done** → Tested and verified

### Before Starting Any Task

```python
# 1. Get task details
archon:manage_task(action="get", task_id="[task_id]")

# 2. Research patterns
archon:perform_rag_query(
  query="LiveKit voice pipeline natural conversation",
  match_count=5
)

# 3. Search code examples
archon:search_code_examples(
  query="voice agent filler phrases implementation",
  match_count=3
)

# 4. Update to in-progress
archon:manage_task(
  action="update",
  task_id="[task_id]",
  update_fields={"status": "doing"}
)
```

## 🏗️ Project Structure

```
appointment-confirmation-agent/
├── appointment_agent.py      # Main agent implementation
├── natural_speech.py        # Natural conversation utilities
├── response_templates.py    # Response variations
├── metrics.py              # Monitoring implementation
├── tests/                  # Test suite
├── deployment/             # Docker and deployment configs
├── PRPs/                   # Project requirements
│   └── livekit-appointment-confirmation.md
├── INITIAL.md              # Original requirements
├── CLAUDE.md               # This file
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
└── .env.example            # Environment template
```

## 🎙️ Voice Pipeline Standards

### Component Configuration
- **STT**: Deepgram Nova-2 with `language="multi"`
- **LLM**: GPT-4o-mini with `temperature=0.8`
- **TTS**: OpenAI Nova voice at `speed=1.0`
- **Turn Detection**: `MultilingualModel()` from LiveKit

### Natural Conversation Requirements
Every implementation MUST include:
1. **Filler phrases** during thinking
2. **Acknowledgment sounds** when listening
3. **Response variation** to avoid repetition
4. **Natural pauses** using SSML markup
5. **Progressive clarification** for errors

## 🧪 Testing Requirements

### Before Marking Task as "review"
- [ ] Agent connects successfully
- [ ] Voice sounds natural (not robotic)
- [ ] Filler phrases occur appropriately
- [ ] Handles interruptions gracefully
- [ ] Latency < 200ms (when possible)
- [ ] All test scenarios pass

### Test Scenarios
1. **Happy Path**: Confirm appointment
2. **Reschedule**: Request different time
3. **Confusion**: Don't remember appointment
4. **Wrong Person**: Someone else answers
5. **Poor Audio**: Background noise
6. **Interruption**: Mid-sentence interruption

## 📊 Task-Specific Guidelines

### Environment Setup Tasks
- Use Python 3.11 specifically
- Install exact versions from requirements.txt
- Create comprehensive .env.example

### Core Agent Tasks
- Follow personality guidelines exactly
- Implement ALL natural speech features
- Use appointment details structure

### Voice Pipeline Tasks
- Configure all components as specified
- Test latency measurements
- Verify turn detection sensitivity

### Testing Tasks
- Use pytest with async support
- Mock LiveKit sessions properly
- Test each conversation scenario

### Deployment Tasks
- Include ffmpeg in Docker image
- Set PYTHONUNBUFFERED=1
- Configure health checks

## 🔍 Research Guidelines

### For Each Task, Research:

**Architecture Patterns:**
```python
archon:perform_rag_query(
  query="LiveKit agents voice pipeline architecture",
  match_count=5
)
```

**Implementation Examples:**
```python
archon:search_code_examples(
  query="turn detection configuration LiveKit",
  match_count=3
)
```

**Best Practices:**
```python
archon:perform_rag_query(
  query="voice agent natural conversation patterns",
  match_count=3
)
```

## 📝 Code Standards

### Import Order
```python
# Standard library
import logging
import asyncio

# Third-party
from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession

# Local
from natural_speech import ResponseVariations
```

### Async Patterns
- Always use `async/await` properly
- Never block the event loop
- Handle connection errors gracefully

### Natural Speech Implementation
```python
# ALWAYS include variation
response = random.choice(RESPONSES[intent])

# ALWAYS add filler for thinking
if thinking:
    response = f"{random.choice(FILLERS)}... {response}"

# ALWAYS use SSML for pauses
response = add_natural_pauses(response)
```

## 🚫 Common Mistakes to Avoid

1. **Starting without checking Archon tasks**
2. **Skipping natural conversation features**
3. **Using wrong voice pipeline components**
4. **Not testing all scenarios**
5. **Forgetting to update task status**
6. **Hard-coding responses without variation**
7. **Missing error recovery implementation**

## 🎯 Success Criteria

A task is complete when:
- Implementation matches PRP specifications
- All natural conversation features work
- Tests pass for all scenarios
- Documentation is updated
- Task status updated to "review"
- User has tested and approved

## 🔗 Key Resources

- **PRP**: `/PRPs/livekit-appointment-confirmation.md`
- **Archon Project**: `49edfe6d-f6d1-4338-9222-97d5679da1a3`
- **LiveKit Docs**: https://docs.livekit.io/agents/
- **Global Archon Rules**: `/Users/andrep/Documents/code/CLAUDE.md`

## 💡 Remember

> "The goal is to create a voice agent that sounds so natural, customers won't realize they're talking to an AI."

Always prioritize naturalness over efficiency. A slightly slower but more human-like response is better than a fast robotic one.