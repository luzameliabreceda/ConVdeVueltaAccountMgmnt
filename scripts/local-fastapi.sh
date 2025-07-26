#!/bin/bash

# Script to run FastAPI locally for development

echo "🚀 Starting FastAPI development server..."

# Make sure we're in the project root
cd "$(dirname "$0")/.."

# Activate virtual environment explicitly
if [ -d ".venv" ]; then
    echo "🔄 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Export environment variables (consistent with CDK dev mode)
export ENVIRONMENT=dev
export DEBUG=true
export SERVICE_NAME=microservice-template

# Run the FastAPI development server
python scripts/run_local.py 