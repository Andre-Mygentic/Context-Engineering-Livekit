#!/bin/bash

# Start the React frontend for testing the appointment confirmation agent

echo "Starting React frontend for appointment confirmation testing..."

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Go to frontend directory
cd "$SCRIPT_DIR"

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    pnpm install
fi

# Start the development server
echo "Starting Next.js development server on http://localhost:3000..."
pnpm dev