# LMS Quick Start Guide

## One-Command Setup and Start

### First Time Setup

Run this once to set up everything:

```bash
cd /home/user/hld-lld-course/lms
./setup_all.sh
```

This will:
- Install Python dependencies
- Create virtual environment for backend
- Parse course content and create database
- Add YouTube videos to lessons
- Install Node.js dependencies
- Configure environment variables

### Starting the LMS

After setup, start the LMS with:

```bash
cd /home/user/hld-lld-course/lms
./start_lms.sh
```

This will start both backend and frontend automatically.

Then open your browser to: **http://localhost:3000**

## Alternative: Manual Start (Two Terminals)

If you prefer to run backend and frontend separately:

**Terminal 1 - Backend:**
```bash
cd /home/user/hld-lld-course/lms
./run_backend.sh
```

**Terminal 2 - Frontend:**
```bash
cd /home/user/hld-lld-course/lms
./run_frontend.sh
```

## Scripts Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `setup_all.sh` | Complete setup | First time only |
| `setup_backend.sh` | Setup backend only | If backend setup failed |
| `setup_frontend.sh` | Setup frontend only | If frontend setup failed |
| `start_lms.sh` | Start both servers | Every time you want to use LMS |
| `run_backend.sh` | Start backend only | Manual two-terminal approach |
| `run_frontend.sh` | Start frontend only | Manual two-terminal approach |

## Stopping the LMS

### If using start_lms.sh with tmux:
```bash
tmux kill-session -t lms
```

### If using start_lms.sh without tmux:
Press `Ctrl+C` in the terminal

### If using separate terminals:
Press `Ctrl+C` in each terminal

## Troubleshooting

### Backend won't start

```bash
cd /home/user/hld-lld-course/lms
./setup_backend.sh
```

### Frontend won't start

```bash
cd /home/user/hld-lld-course/lms
./setup_frontend.sh
```

### Database is empty

```bash
cd /home/user/hld-lld-course/lms/backend
source venv/bin/activate
python content_parser.py
python update_videos.py
```

### Port already in use

If port 5000 or 3000 is in use, stop the process using it:

```bash
# Find what's using the port
lsof -i :5000
lsof -i :3000

# Kill the process (replace PID with actual process ID)
kill -9 PID
```

## Using tmux (Recommended)

tmux allows you to run both servers in one terminal window:

**Start with tmux:**
```bash
./start_lms.sh
```

**Switch between backend and frontend:**
- `Ctrl+b` then `0` for backend
- `Ctrl+b` then `1` for frontend

**Detach from tmux (keeps servers running):**
- `Ctrl+b` then `d`

**Reattach to tmux:**
```bash
tmux attach -t lms
```

**Stop everything:**
```bash
tmux kill-session -t lms
```

## Next Steps

1. Open http://localhost:3000
2. Start with LLD Week 1 - Encapsulation
3. Mark lessons complete as you learn
4. Watch reference YouTube videos
5. Take notes in the editor
6. Track your progress on the dashboard

Happy Learning!
