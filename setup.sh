#!/bin/bash

# Microservice Template Setup Script
echo "🚀 Setting up microservice-template..."

# Check if Python 3.13 is available
echo "📋 Checking Python version..."
if ! python3 --version | grep -q "3.13"; then
    echo "❌ Python 3.13 is required but not found."
    echo "Please install Python 3.13:"
    echo "  - Using pyenv: pyenv install 3.13.5 && pyenv local 3.13.5"
    echo "  - Or install from https://python.org"
    exit 1
fi

echo "✅ Python $(python3 --version) found"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔨 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install base dependencies
echo "📦 Installing base dependencies..."
pip install wheel setuptools

echo "✅ Setup completed!"
echo "👉 Next steps:"
echo "   1. Run: source .venv/bin/activate"
echo "   2. Install all dependencies: pip install -r requirements.txt" 