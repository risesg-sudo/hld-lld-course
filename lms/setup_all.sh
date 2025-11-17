#!/bin/bash

echo "=========================================="
echo "Complete LMS Setup Script"
echo "=========================================="
echo ""
echo "This will set up both backend and frontend"
echo ""

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Setup backend
echo "Step 1/2: Setting up Backend..."
echo "=========================================="
./setup_backend.sh
if [ $? -ne 0 ]; then
    echo "Backend setup failed!"
    exit 1
fi
echo ""

# Setup frontend
echo "Step 2/2: Setting up Frontend..."
echo "=========================================="
./setup_frontend.sh
if [ $? -ne 0 ]; then
    echo "Frontend setup failed!"
    exit 1
fi
echo ""

echo "=========================================="
echo "Complete Setup Successful!"
echo "=========================================="
echo ""
echo "To start the LMS, run:"
echo "  ./start_lms.sh"
echo ""
echo "Or start servers separately:"
echo "  ./run_backend.sh   (in one terminal)"
echo "  ./run_frontend.sh  (in another terminal)"
echo ""
echo "Access the LMS at: http://localhost:3000"
echo ""
