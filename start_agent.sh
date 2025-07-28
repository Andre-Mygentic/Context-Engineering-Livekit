#!/bin/bash

# Start the LiveKit appointment confirmation agent

echo "Starting LiveKit appointment confirmation agent..."

# Activate virtual environment
source venv/bin/activate

# Download models if needed
echo "Checking for required models..."
python agent/appointment_agent.py download-files

# Start the agent in development mode
echo "Starting agent in development mode..."
python agent/appointment_agent.py dev