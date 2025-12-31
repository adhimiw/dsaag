#!/bin/bash

# Setup script for MCP Code Executor
# This script clones and builds the bazinga012/mcp_code_executor

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_DIR="$SCRIPT_DIR/mcp_code_executor"

echo "==================================="
echo "MCP Code Executor Setup"
echo "==================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js first: https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js version: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm is not installed"
    exit 1
fi

echo "✓ npm version: $(npm --version)"

# Clone repository if it doesn't exist
if [ -d "$MCP_DIR" ]; then
    echo "Directory $MCP_DIR already exists"
    read -p "Do you want to remove and re-clone? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing directory..."
        rm -rf "$MCP_DIR"
    else
        echo "Using existing directory"
    fi
fi

if [ ! -d "$MCP_DIR" ]; then
    echo "Cloning mcp_code_executor repository..."
    git clone https://github.com/bazinga012/mcp_code_executor.git "$MCP_DIR"
    echo "✓ Repository cloned"
fi

# Navigate to the directory
cd "$MCP_DIR"

# Install dependencies
echo "Installing npm dependencies..."
npm install
echo "✓ Dependencies installed"

# Build the project
echo "Building the project..."
npm run build
echo "✓ Build complete"

# Create code storage directory
CODE_STORAGE_DIR="$SCRIPT_DIR/code_storage"
mkdir -p "$CODE_STORAGE_DIR"
echo "✓ Created code storage directory: $CODE_STORAGE_DIR"

echo ""
echo "==================================="
echo "✓ Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Set up environment variables in .env file:"
echo "   CODE_EXECUTOR_SERVER_PATH=$MCP_DIR/build/index.js"
echo "   CODE_STORAGE_DIR=$CODE_STORAGE_DIR"
echo "   CONDA_ENV_NAME=your_conda_env_name"
echo ""
echo "2. Test the server:"
echo "   cd $MCP_DIR"
echo "   node build/index.js"
echo ""
echo "3. Use CodeExecutionManager in your agents for automatic fallback"
echo ""
