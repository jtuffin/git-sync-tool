#!/bin/bash

# Git Cloner Installation Script
# This script installs git-cloner in development mode

set -e

echo "🔧 Installing git-cloner in development mode..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.6 or higher."
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is required but not installed. Please install pip."
    exit 1
fi

# Determine pip command
PIP_CMD="pip"
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
fi

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is required but not installed. Please install git."
    exit 1
fi

# Install in development mode
echo "📦 Installing package in development mode..."
$PIP_CMD install -e .

# Verify installation
if command -v git-cloner &> /dev/null; then
    echo "✅ git-cloner installed successfully!"
    echo "🚀 Try running: git-cloner --help"
else
    echo "⚠️  Installation completed but git-cloner command not found in PATH."
    echo "   You may need to add ~/.local/bin to your PATH or use python -m git_cloner"
fi

echo ""
echo "📝 Installation complete!"
echo "   • Command: git-cloner"
echo "   • Module: python -m git_cloner"
echo "   • Help: git-cloner --help"