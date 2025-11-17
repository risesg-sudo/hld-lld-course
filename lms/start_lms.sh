#!/bin/bash

echo "=========================================="
echo "Starting Complete LMS"
echo "=========================================="
echo ""

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check if tmux is available
if command -v tmux &> /dev/null; then
    echo "Using tmux to run both backend and frontend..."
    echo ""

    # Create a new tmux session
    SESSION_NAME="lms"

    # Kill existing session if it exists
    tmux kill-session -t $SESSION_NAME 2>/dev/null

    # Create new session with backend
    tmux new-session -d -s $SESSION_NAME -n backend "cd '$SCRIPT_DIR' && ./run_backend.sh"

    # Create new window for frontend
    tmux new-window -t $SESSION_NAME -n frontend "cd '$SCRIPT_DIR' && ./run_frontend.sh"

    # Select backend window
    tmux select-window -t $SESSION_NAME:0

    echo "LMS started in tmux session: $SESSION_NAME"
    echo ""
    echo "To view:"
    echo "  tmux attach -t $SESSION_NAME"
    echo ""
    echo "To switch windows in tmux:"
    echo "  Ctrl+b then 0 (backend)"
    echo "  Ctrl+b then 1 (frontend)"
    echo ""
    echo "To detach from tmux:"
    echo "  Ctrl+b then d"
    echo ""
    echo "To stop LMS:"
    echo "  tmux kill-session -t $SESSION_NAME"
    echo ""
    echo "Backend: http://localhost:5000"
    echo "Frontend: http://localhost:3000"
    echo ""

    # Attach to session
    tmux attach -t $SESSION_NAME

else
    echo "tmux not found. Starting servers sequentially..."
    echo ""
    echo "Starting backend in background..."
    cd "$SCRIPT_DIR"
    ./run_backend.sh > backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend started (PID: $BACKEND_PID)"
    echo "Backend logs: $SCRIPT_DIR/backend.log"
    echo ""

    # Wait for backend to start
    echo "Waiting for backend to start..."
    sleep 5
    echo ""

    echo "Starting frontend..."
    echo "Frontend will run in foreground. Press Ctrl+C to stop both servers."
    echo ""

    # Trap Ctrl+C to kill backend
    trap "echo 'Stopping servers...'; kill $BACKEND_PID 2>/dev/null; exit" INT TERM

    cd "$SCRIPT_DIR"
    ./run_frontend.sh

    # Kill backend on exit
    kill $BACKEND_PID 2>/dev/null
fi
