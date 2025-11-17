# LMS Backend API - Quick Reference

## Starting the Server

```bash
# Option 1: Use the start script
./start.sh

# Option 2: Direct Python command
python app.py

# Option 3: Install dependencies first
pip install -r requirements.txt
python app.py
```

Server runs on: **http://localhost:5000**

## Essential Endpoints

### Course Content

```bash
# Get full course structure
GET /api/course-structure

# Get weeks summary
GET /api/weeks

# Get specific week
GET /api/week/LLD/1
GET /api/week/HLD/2

# Get lesson details
GET /api/lesson/1

# Get lesson content (markdown)
GET /api/lesson/1/content
```

### Progress Tracking

```bash
# Get overall progress
GET /api/progress

# Get weekly progress
GET /api/progress/weekly

# Mark lesson complete/incomplete (toggle)
POST /api/lesson/1/complete

# Update time spent (in seconds)
POST /api/lesson/1/time
Content-Type: application/json
{
  "seconds": 300
}

# Get recent activity (last 30 days)
GET /api/activity/recent?days=30
```

### Notes

```bash
# Get notes for lesson
GET /api/notes/1

# Save/update notes
POST /api/notes/1
Content-Type: application/json
{
  "content": "My notes here..."
}

# Delete notes
DELETE /api/notes/1
```

### Bookmarks

```bash
# Get all bookmarks
GET /api/bookmarks

# Toggle bookmark
POST /api/bookmark/1
```

### Utility

```bash
# Health check
GET /api/health

# Reseed database (re-scan course content)
POST /api/admin/reseed
```

## Testing with curl

```bash
# Health check
curl http://localhost:5000/api/health

# Get course structure
curl http://localhost:5000/api/course-structure | jq

# Get lesson
curl http://localhost:5000/api/lesson/1 | jq

# Mark lesson complete
curl -X POST http://localhost:5000/api/lesson/1/complete

# Add time
curl -X POST http://localhost:5000/api/lesson/1/time \
  -H "Content-Type: application/json" \
  -d '{"seconds": 300}'

# Save notes
curl -X POST http://localhost:5000/api/notes/1 \
  -H "Content-Type: application/json" \
  -d '{"content": "Important points to remember"}'
```

## Response Examples

### Course Structure
```json
{
  "LLD": {
    "1": {
      "title": "Week 1",
      "topics": [{
        "name": "OOP Fundamentals",
        "lessons": [{
          "id": 1,
          "title": "Encapsulation",
          "estimated_minutes": 15,
          "is_completed": false,
          "is_bookmarked": false
        }]
      }]
    }
  }
}
```

### Progress Stats
```json
{
  "overall": {
    "total_lessons": 150,
    "completed_lessons": 12,
    "completion_percentage": 8,
    "estimated_completion_date": "2025-02-15"
  },
  "streak": {
    "current_days": 3,
    "best_days": 7
  }
}
```

## Database Location

**Path:** `/home/user/hld-lld-course/lms/backend/data/lms.db`

**Reset Database:**
```bash
rm data/lms.db
python app.py  # Will recreate and reseed
```

## Configuration

Edit `/home/user/hld-lld-course/lms/backend/config.py`:

- **PORT**: Server port (default: 5000)
- **DEBUG**: Debug mode (default: True)
- **CORS_ORIGINS**: Allowed origins (default: localhost:3000)
- **COURSE_ROOT**: Course directory path

## Common Tasks

### View all lessons
```bash
python view_lessons.py
```

### Run tests
```bash
python test_api.py
```

### Reseed content
```bash
curl -X POST http://localhost:5000/api/admin/reseed
```

## Error Codes

- **200**: Success
- **400**: Bad request (invalid parameters)
- **404**: Resource not found
- **500**: Server error

## CORS Configuration

The API allows requests from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

To add more origins, edit `config.py`.

## Logs

Logs are printed to console in debug mode. For production, configure file logging in `app.py`.

## Next Steps

1. Start the server: `./start.sh`
2. Test endpoints: `curl http://localhost:5000/api/health`
3. Build your frontend to consume the API
4. Configure production deployment when ready

For full documentation, see `README.md`.
