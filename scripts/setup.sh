#!/bin/bash

# =============================================================================
# MICROSERVICE TEMPLATE - SETUP SCRIPT
# =============================================================================
# This script sets up the complete development environment for the microservice template.
# It uses pyenv to manage Python versions and installs all necessary dependencies.

set -e  # Exit on any error

echo "🚀 Setting up Microservice Template Development Environment"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if pyenv is installed
check_pyenv() {
    if ! command -v pyenv &> /dev/null; then
        print_error "pyenv is not installed. Please install pyenv first:"
        echo "  macOS: brew install pyenv"
        echo "  Linux: curl https://pyenv.run | bash"
        echo "  Windows: Use pyenv-win"
        exit 1
    fi
    print_success "pyenv is installed"
}

# Install Python version with pyenv
install_python() {
    print_status "Checking Python version requirements..."
    
    # Read Python version from .python-version file
    if [ ! -f ".python-version" ]; then
        print_error ".python-version file not found"
        exit 1
    fi
    
    REQUIRED_VERSION=$(cat .python-version)
    print_status "Required Python version: $REQUIRED_VERSION"
    
    # Check if the required version is installed
    if pyenv versions | grep -q "$REQUIRED_VERSION"; then
        print_success "Python $REQUIRED_VERSION is already installed"
    else
        print_status "Installing Python $REQUIRED_VERSION with pyenv..."
        pyenv install "$REQUIRED_VERSION"
        print_success "Python $REQUIRED_VERSION installed successfully"
    fi
    
    # Set local Python version
    pyenv local "$REQUIRED_VERSION"
    print_success "Local Python version set to $REQUIRED_VERSION"
}

# Clean up old virtual environments
cleanup_venv() {
    print_status "Cleaning up old virtual environments..."
    
    # Remove old .venv directories
    if [ -d ".venv" ]; then
        print_status "Removing old .venv directory..."
        rm -rf .venv
        print_success "Old .venv removed"
    fi
    
    if [ -d "infrastructure/.venv" ]; then
        print_status "Removing old infrastructure/.venv directory..."
        rm -rf infrastructure/.venv
        print_success "Old infrastructure/.venv removed"
    fi
    
    print_success "Cleanup completed"
}

# Create and activate virtual environment
setup_venv() {
    print_status "Creating virtual environment..."
    
    # Create virtual environment
    python -m venv .venv
    print_success "Virtual environment created"
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source .venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    print_success "pip upgraded"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Check if requirements files exist
    if [ ! -f "src/requirements.txt" ]; then
        print_error "src/requirements.txt not found"
        exit 1
    fi
    
    if [ ! -f "infrastructure/requirements.txt" ]; then
        print_error "infrastructure/requirements.txt not found"
        exit 1
    fi
    
    # Install Lambda dependencies (for local development)
    print_status "Installing Lambda dependencies..."
    pip install -r src/requirements.txt
    print_success "Lambda dependencies installed"
    
    # Install CDK/Development dependencies
    print_status "Installing CDK and development dependencies..."
    pip install -r infrastructure/requirements.txt
    print_success "CDK and development dependencies installed"
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check if key packages are installed
    if python -c "import fastapi" &> /dev/null; then
        print_success "FastAPI is installed"
    else
        print_error "FastAPI installation failed"
        exit 1
    fi
    
    if python -c "import aws_cdk" &> /dev/null; then
        print_success "AWS CDK is installed"
    else
        print_error "AWS CDK installation failed"
        exit 1
    fi
    
    if command -v cdk &> /dev/null; then
        print_success "CDK CLI is available"
    else
        print_error "CDK CLI not found"
        exit 1
    fi
    
    if command -v sam &> /dev/null; then
        print_success "SAM CLI is available"
    else
        print_warning "SAM CLI not found. Install it for local Lambda testing:"
        echo "  macOS: brew install aws-sam-cli"
        echo "  Linux: pip install aws-sam-cli"
    fi
    
    print_success "Installation verification completed"
}

# Setup environment variables
setup_env() {
    print_status "Setting up environment variables..."
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
# Environment Configuration
ENVIRONMENT=dev
SERVICE_NAME=microservice-template
AWS_REGION=us-west-2

# Database Configuration (for local development)
DATABASE_TYPE=memory

# AWS Configuration
AWS_PROFILE=cvdv
EOF
        print_success ".env file created"
    else
        print_success ".env file already exists"
    fi
}

# Main setup function
main() {
    echo ""
    print_status "Starting setup process..."
    
    # Check prerequisites
    check_pyenv
    
    # Install Python version
    install_python
    
    # Clean up old environments
    cleanup_venv
    
    # Setup virtual environment
    setup_venv
    
    # Install dependencies
    install_dependencies
    
    # Verify installation
    verify_installation
    
    # Setup environment
    setup_env
    
    echo ""
    print_success "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Activate the virtual environment:"
    echo "      source .venv/bin/activate"
    echo ""
    echo "   2. For local FastAPI development:"
    echo "      python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "   3. For local Lambda testing with SAM:"
    echo "      ./scripts/run_sam.sh"
    echo ""
    echo "   4. For AWS deployment:"
    echo "      ./scripts/deploy-cdk.sh -s 'your-service-name' -e 'dev'"
    echo ""
    echo "   5. View API documentation:"
    echo "      http://localhost:8000/docs"
    echo ""
    print_status "Happy coding! 🚀"
}

# Run main function
main "$@" 