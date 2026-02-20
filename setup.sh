#!/bin/bash

# Define the virtual environment directory
VENV_DIR=".venv"

# Check if python3 is installed and get path
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "🚀 Setting up Python environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    $PYTHON_CMD -m venv $VENV_DIR
else
    echo "Virtual environment already exists in $VENV_DIR."
fi

# Activate virtual environment
source $VENV_DIR/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found!"
fi

echo ""
echo "✅ Setup complete!"
echo ""

# Activate the virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "env" ]; then
    source env/bin/activate
else
    echo "⚠️ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

echo "🚀 Running data generator..."
python3 generate_data.py
echo ""
echo "To start the application:"
echo "    streamlit run app.py"
