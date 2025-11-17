#!/bin/bash

echo "=========================================="
echo "Starting LMS Frontend Server"
echo "=========================================="
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/frontend" || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Error: Dependencies not installed"
    echo "Please run ./setup_frontend.sh first"
    exit 1
fi

# Start Next.js development server
echo "Starting Next.js development server on http://localhost:3000"
echo "Press Ctrl+C to stop"
echo ""
npm run dev
