#!/bin/bash

echo "=========================================="
echo "Setting up LMS Frontend"
echo "=========================================="
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/frontend" || exit 1

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    echo "Please install Node.js 18 or higher from https://nodejs.org/"
    exit 1
fi

echo "Node.js version:"
node --version
echo ""

echo "npm version:"
npm --version
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."
echo ""
npm install
echo ""

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:5000
EOF
    echo ".env.local created"
fi
echo ""

echo "=========================================="
echo "Frontend setup complete!"
echo "=========================================="
echo ""
echo "To start the frontend development server, run:"
echo "  ./run_frontend.sh"
echo ""
echo "Or manually:"
echo "  cd lms/frontend"
echo "  npm run dev"
echo ""
