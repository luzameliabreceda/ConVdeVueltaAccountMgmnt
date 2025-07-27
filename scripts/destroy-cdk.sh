#!/bin/bash

# Script to destroy the infrastructure using AWS CDK

# Default values
SERVICE_NAME="microservice-template"
ENVIRONMENT="dev"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--service-name)
            SERVICE_NAME="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -s, --service-name    Service name (default: microservice-template)"
            echo "  -e, --environment     Environment: dev|prod (default: dev)"
            echo "  -h, --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h for help"
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    echo "❌ Environment must be 'dev' or 'prod'"
    exit 1
fi

echo "🗑️  Destroying infrastructure with AWS CDK..."
echo "   📦 Service: $SERVICE_NAME"
echo "   🏷️  Environment: $ENVIRONMENT"

# Make sure we're in the project root
cd "$(dirname "$0")/.."

# Go to infrastructure directory
cd infrastructure

# Ensure CDK environment is activated and dependencies are installed
if [ ! -d ".venv" ] || [ ! -f ".venv/pyvenv.cfg" ]; then
    echo "🔨 Setting up CDK environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    echo "🔄 Activating CDK environment..."
    source .venv/bin/activate
    
    # Check if CDK is installed, if not install dependencies
    if ! python -c "import aws_cdk" &> /dev/null; then
            echo "📦 Installing CDK dependencies..."
    pip install -r requirements.txt
    fi
fi

# Destroy the stack
echo "🗑️  Destroying AWS resources..."
cdk destroy -c service_name="$SERVICE_NAME" -c environment="$ENVIRONMENT" --force

echo "✅ Destruction completed!"
echo "🔗 All resources for $SERVICE_NAME ($ENVIRONMENT) have been removed" 