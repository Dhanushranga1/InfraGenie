#!/bin/bash
# InfraGenie Backend Startup Script
# Ensures proper environment and starts the server

cd "$(dirname "$0")"

echo "🚀 Starting InfraGenie Backend..."
echo "📍 Working directory: $(pwd)"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "   Copy .env.example to .env and configure your API keys"
    exit 1
fi

# Check if venv exists
if [ ! -d venv ]; then
    echo "❌ ERROR: Virtual environment not found!"
    echo "   Run: python3 -m venv venv && venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Export PYTHONPATH
export PYTHONPATH=$(pwd)

# Start server
echo "✓ Environment ready"
echo "✓ Starting Uvicorn server..."
echo ""

venv/bin/python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
