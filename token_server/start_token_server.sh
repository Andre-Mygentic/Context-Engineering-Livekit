#!/bin/bash

# Start the LiveKit token server

echo "Starting LiveKit token server..."

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Go to project root
cd "$SCRIPT_DIR/.."

# Activate virtual environment
source venv/bin/activate

# Start the token server
python token_server/token_server.py