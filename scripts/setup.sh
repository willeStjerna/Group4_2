#!/bin/bash

echo "Setting up the project..."

# Get the absolute path of the script directory
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Get the project root directory (parent of scripts/)
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python3 and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/venv"
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$PROJECT_ROOT/venv/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r "$PROJECT_ROOT/requirements.txt"
else
    echo "No requirements.txt found in $PROJECT_ROOT. Skipping dependency installation."
fi

echo "Setup complete!"
echo "To start working, run: source venv/bin/activate"
