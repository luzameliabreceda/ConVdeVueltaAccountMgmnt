#!/bin/bash

# Script to run the Lambda function locally using SAM

echo "🚀 Starting SAM local API..."

# Make sure we're in the project root
cd "$(dirname "$0")/.."

# Activate virtual environment explicitly (SAM CLI is installed here)
if [ -d ".venv" ]; then
    echo "🔄 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Check if template.yaml exists
if [ ! -f "template.yaml" ]; then
    echo "❌ template.yaml not found. Please run this script from the project root."
    exit 1
fi

# Build the Lambda function first (this installs dependencies)
echo "🔨 Building Lambda function..."
sam build --use-container

# Start SAM local API
echo "🚀 Starting SAM local API server..."
sam local start-api \
    --host 0.0.0.0 \
    --port 3000 \
    --warm-containers EAGER \
    --log-file sam-local.log

echo "📝 Logs are being written to sam-local.log" 