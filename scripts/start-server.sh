#!/bin/bash

# Wiki.js MCP Server Start Script
# This script activates the virtual environment and starts the MCP server

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run ./setup.sh first." >&2
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please copy config/example.env to .env and configure it." >&2
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if the main server file exists
if [ ! -f "src/wiki_mcp_server.py" ]; then
    echo "❌ Error: Server file src/wiki_mcp_server.py not found." >&2
    exit 1
fi

# Load environment variables for validation
source .env

# Validate required environment variables
if [ -z "$WIKIJS_API_URL" ]; then
    echo "❌ Error: WIKIJS_API_URL not set in .env file" >&2
    exit 1
fi

if [ -z "$WIKIJS_TOKEN" ] && [ -z "$WIKIJS_USERNAME" ]; then
    echo "❌ Error: Either WIKIJS_TOKEN or WIKIJS_USERNAME must be set in .env file" >&2
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the MCP server (this will handle stdin/stdout communication with Cursor)
exec python src/wiki_mcp_server.py 