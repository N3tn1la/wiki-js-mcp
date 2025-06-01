#!/bin/bash

# Wiki.js MCP Server Test Script
# This script is for interactive testing and debugging

set -e  # Exit on any error

echo "🚀 Testing Wiki.js MCP Server..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please copy config/example.env to .env and configure it."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if the main server file exists
if [ ! -f "src/wiki_mcp_server.py" ]; then
    echo "❌ Error: Server file src/wiki_mcp_server.py not found."
    exit 1
fi

# Load environment variables for validation
echo "⚙️  Loading configuration..."
source .env

# Validate required environment variables
if [ -z "$WIKIJS_API_URL" ]; then
    echo "❌ Error: WIKIJS_API_URL not set in .env file"
    exit 1
fi

if [ -z "$WIKIJS_TOKEN" ] && [ -z "$WIKIJS_USERNAME" ]; then
    echo "❌ Error: Either WIKIJS_TOKEN or WIKIJS_USERNAME must be set in .env file"
    exit 1
fi

echo "✅ Configuration validated"

# Create logs directory if it doesn't exist
mkdir -p logs

# Display server information
echo ""
echo "📊 Server Configuration:"
echo "   API URL: $WIKIJS_API_URL"
echo "   Database: ${WIKIJS_MCP_DB:-./wikijs_mappings.db}"
echo "   Log Level: ${LOG_LEVEL:-INFO}"
echo "   Log File: ${LOG_FILE:-wikijs_mcp.log}"
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down Wiki.js MCP Server..."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the server
echo "🌟 Starting MCP server for testing..."
echo "   Press Ctrl+C to stop the server"
echo ""

# Run the server with error handling
if python src/wiki_mcp_server.py; then
    echo "✅ Server started successfully"
else
    echo "❌ Server failed to start. Check the logs for details:"
    echo "   Log file: ${LOG_FILE:-wikijs_mcp.log}"
    echo ""
    echo "💡 Troubleshooting tips:"
    echo "   1. Verify Wiki.js is running and accessible"
    echo "   2. Check your API token is valid"
    echo "   3. Ensure all dependencies are installed (run ./setup.sh)"
    echo "   4. Check the log file for detailed error messages"
    exit 1
fi 