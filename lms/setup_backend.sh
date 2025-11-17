#!/bin/bash

echo "=========================================="
echo "Setting up LMS Backend"
echo "=========================================="
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/backend" || exit 1

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo ""

# Create data directory if it doesn't exist
mkdir -p data
echo "Data directory ready"
echo ""

# Parse course content and populate database
echo "Parsing course content..."
python content_parser.py
echo ""

# Update video URLs
echo "Adding YouTube videos..."
python update_videos.py
echo ""

echo "=========================================="
echo "Backend setup complete!"
echo "=========================================="
echo ""
echo "To start the backend server, run:"
echo "  ./run_backend.sh"
echo ""
echo "Or manually:"
echo "  cd lms/backend"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
