#!/bin/bash

echo "=========================================="
echo "Starting LMS Backend Server"
echo "=========================================="
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/backend" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run ./setup_backend.sh first"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Check if database exists
if [ ! -f "data/lms.db" ]; then
    echo "Warning: Database not found"
    echo "Running content parser to create database..."
    python content_parser.py
    python update_videos.py
    echo ""
fi

# Start Flask server
echo "Starting Flask server on http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""
python app.py
