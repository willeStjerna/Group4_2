Write-Output "Setting up the project..."

# Get the absolute path of the script directory
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Get the project root directory (parent of scripts/)
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR

# Check if Python is installed
$pythonExists = Get-Command python -ErrorAction SilentlyContinue
if (-Not $pythonExists) {
    Write-Output "Python is not installed. Please install Python and try again."
    Exit 1
}

# Create virtual environment if it doesn't exist
if (-Not (Test-Path "$PROJECT_ROOT\venv")) {
    Write-Output "Creating virtual environment..."
    python -m venv "$PROJECT_ROOT\venv"
} else {
    Write-Output "Virtual environment already exists."
}

# Activate the virtual environment
Write-Output "Activating virtual environment..."
& "$PROJECT_ROOT\venv\Scripts\Activate"

# Upgrade pip
Write-Output "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
if (Test-Path "$PROJECT_ROOT\requirements.txt") {
    Write-Output "Installing dependencies from requirements.txt..."
    pip install -r "$PROJECT_ROOT\requirements.txt"
} else {
    Write-Output "No requirements.txt found in $PROJECT_ROOT. Skipping dependency installation."
}

Write-Output "Setup complete!"
Write-Output "To start working, run: venv\Scripts\Activate"
