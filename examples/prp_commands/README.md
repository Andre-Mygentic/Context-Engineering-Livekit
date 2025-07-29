# PRP Custom Commands

This directory contains the custom Claude commands used to generate and execute Product Requirements Prompts (PRPs) for LiveKit voice agents.

## Commands

### 1. `/generate-livekit-prp`
Generates a comprehensive Product Requirements Prompt document for a LiveKit voice agent based on your specifications.

**Usage:**
```
/generate-livekit-prp Create a customer service agent that handles returns and exchanges
```

This command will create a structured PRP document with:
- Agent personality and instructions
- Voice pipeline configuration
- Function definitions
- Testing scenarios
- Deployment specifications

### 2. `/execute-livekit-prp`
Executes a PRP document to build the complete LiveKit agent implementation.

**Usage:**
```
/execute-livekit-prp path/to/your-prp.md
```

This command will:
- Parse the PRP document
- Create the agent implementation
- Set up the voice pipeline
- Implement all specified functions
- Generate tests and documentation

## How These Commands Work

These commands are part of the context engineering approach used in this project:

1. **generate-livekit-prp** takes natural language requirements and structures them into an AI-friendly format
2. **execute-livekit-prp** takes that structured format and generates the complete implementation

## Setting Up Custom Commands

To use these commands in your own Claude Code setup:

1. Copy these files to your `~/.claude/commands/` directory
2. Restart Claude Code to load the commands
3. Use them with the `/` prefix in your conversations

## Example Workflow

```bash
# 1. Generate a PRP for your use case
/generate-livekit-prp Create a voice agent for restaurant reservations

# 2. Review and edit the generated PRP
# 3. Execute the PRP to build the agent
/execute-livekit-prp restaurant-reservation-prp.md

# 4. The command will create:
#    - Agent implementation
#    - Voice pipeline setup
#    - Function tools
#    - Tests
#    - Documentation
```

## Benefits

- **Consistency**: Every agent follows the same patterns
- **Speed**: Generate complete implementations in minutes
- **Best Practices**: Built-in LiveKit best practices
- **Extensibility**: Easy to modify for your needs

These commands were instrumental in building this appointment confirmation agent in just 5 hours!