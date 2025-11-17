#!/bin/bash

# Start script for LMS Backend API

echo "========================================="
echo "  LMS Backend API Starting..."
echo "========================================="
echo ""

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    echo ""
fi

# Run the Flask app
echo "Starting Flask server on http://localhost:5000"
echo "Press CTRL+C to stop"
echo ""

python app.py
