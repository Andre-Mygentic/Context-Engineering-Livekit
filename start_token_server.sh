#!/bin/bash

# Start the LiveKit token server

echo "Starting LiveKit token server..."

# Activate virtual environment
source venv/bin/activate

# Start the token server
python token_server.py