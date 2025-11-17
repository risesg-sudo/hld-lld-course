# Getting Started with the LMS Backend API

## Quick Start (30 seconds)

```bash
cd /home/user/hld-lld-course/lms/backend
./start.sh
```

That's it! The API will be running on **http://localhost:5000**

## What You Just Created

A complete Flask REST API with:
- 18 API endpoints
- SQLite database with 5 tables
- 29 pre-seeded lessons from your course
- Progress tracking system
- Notes and bookmarks
- Daily activity tracking

## Verify It's Working

```bash
# Option 1: Run the test suite
python test_api.py

# Option 2: Check the health endpoint
curl http://localhost:5000/api/health

# Option 3: View seeded lessons
python view_lessons.py
```

## Try Your First API Calls

```bash
# Get course structure
curl http://localhost:5000/api/course-structure | python -m json.tool

# Get all weeks
curl http://localhost:5000/api/weeks | python -m json.tool

# Get a specific lesson
curl http://localhost:5000/api/lesson/1 | python -m json.tool

# Mark a lesson complete
curl -X POST http://localhost:5000/api/lesson/1/complete

# Get progress stats
curl http://localhost:5000/api/progress | python -m json.tool
```

## Key Files

- **app.py** - Main Flask application
- **database.py** - Database operations
- **config.py** - Configuration settings
- **README.md** - Complete API documentation
- **API_QUICK_REFERENCE.md** - Quick reference guide

## Next Steps

1. **Explore the API**: Try the endpoints listed above
2. **Read the docs**: Check out README.md for complete documentation
3. **Build your frontend**: Create a Next.js app to consume this API
4. **Customize**: Edit config.py to adjust settings

## Database Location

**Path**: `/home/user/hld-lld-course/lms/backend/data/lms.db`

To reset:
```bash
rm data/lms.db
python app.py  # Auto-recreates and reseeds
```

## Common Commands

```bash
# Start the server
./start.sh

# Run tests
python test_api.py

# View lessons
python view_lessons.py

# Reseed database
curl -X POST http://localhost:5000/api/admin/reseed
```

## CORS Configuration

The API allows requests from:
- http://localhost:3000 (Next.js default)
- http://127.0.0.1:3000

Perfect for local frontend development!

## Need Help?

- **Complete docs**: README.md
- **Quick reference**: API_QUICK_REFERENCE.md
- **Full summary**: BACKEND_SUMMARY.md

---

**You're all set!** 🚀

Your LMS backend API is ready to power your learning platform.
