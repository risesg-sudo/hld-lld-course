# LMS Backend API

Flask-based REST API for the Learning Management System (LMS) that powers the HLD/LLD course platform.

## Features

- RESTful API for course content and progress tracking
- SQLite database with automatic initialization
- Course content auto-seeding from markdown files
- Progress tracking with completion status and time spent
- Personal notes and bookmarks
- Daily activity tracking with streak calculation
- CORS enabled for Next.js frontend integration
- Comprehensive error handling and logging

## Project Structure

```
backend/
├── app.py              # Main Flask application with API endpoints
├── database.py         # SQLite database operations
├── models.py           # Database schema definitions
├── config.py           # Configuration settings
├── seed_content.py     # Content scanner and seeder
├── requirements.txt    # Python dependencies
├── data/              # Database storage (auto-created)
│   └── lms.db         # SQLite database
└── README.md          # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Navigate to the backend directory:
```bash
cd /home/user/hld-lld-course/lms/backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000` and automatically:
- Create the SQLite database
- Initialize database schema
- Scan and seed course content from markdown files
- Enable CORS for the frontend (port 3000)

## Database Schema

### Lessons Table
Stores all course lessons with metadata.

```sql
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_num INTEGER NOT NULL,
    week_type TEXT NOT NULL,          -- 'LLD' or 'HLD'
    topic TEXT NOT NULL,
    title TEXT NOT NULL,
    content_path TEXT NOT NULL,       -- Path to markdown file
    video_url TEXT,                   -- Optional video URL
    estimated_minutes INTEGER NOT NULL,
    order_num INTEGER NOT NULL
);
```

### Progress Table
Tracks user progress for each lesson.

```sql
CREATE TABLE progress (
    lesson_id INTEGER PRIMARY KEY,
    is_completed BOOLEAN DEFAULT 0,
    time_spent_seconds INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    last_accessed TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
);
```

### Notes Table
Stores user notes for lessons.

```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
);
```

### Bookmarks Table
Tracks bookmarked lessons.

```sql
CREATE TABLE bookmarks (
    lesson_id INTEGER PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
);
```

### Activity Table
Tracks daily learning activity.

```sql
CREATE TABLE activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    lessons_completed INTEGER DEFAULT 0,
    time_spent_seconds INTEGER DEFAULT 0,
    UNIQUE(date)
);
```

## API Endpoints

### Health Check

#### GET /api/health
Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T10:30:00"
}
```

---

### Course Structure

#### GET /api/course-structure
Get the complete course structure organized by week type, week number, and topics.

**Response:**
```json
{
  "LLD": {
    "1": {
      "title": "Week 1",
      "topics": [
        {
          "name": "Oop Fundamentals",
          "lessons": [
            {
              "id": 1,
              "title": "Encapsulation Concept",
              "estimated_minutes": 15,
              "is_completed": true,
              "is_bookmarked": false,
              "video_url": null,
              "time_spent_seconds": 900
            }
          ]
        }
      ]
    }
  },
  "HLD": { ... }
}
```

#### GET /api/weeks
Get a summary of all weeks with completion statistics.

**Response:**
```json
{
  "LLD": [
    {
      "week_num": 1,
      "total_lessons": 20,
      "completed_lessons": 5,
      "completion_percentage": 25,
      "total_minutes": 300
    }
  ],
  "HLD": [ ... ]
}
```

#### GET /api/week/:week_type/:week_num
Get detailed information for a specific week.

**Parameters:**
- `week_type`: "LLD" or "HLD"
- `week_num`: Week number (1-5)

**Example:** `GET /api/week/LLD/1`

**Response:**
```json
{
  "week_type": "LLD",
  "week_num": 1,
  "topics": [
    {
      "name": "Oop Fundamentals",
      "lessons": [ ... ]
    }
  ]
}
```

---

### Lessons

#### GET /api/lesson/:id
Get detailed information about a specific lesson.

**Example:** `GET /api/lesson/1`

**Response:**
```json
{
  "id": 1,
  "week_num": 1,
  "week_type": "LLD",
  "topic": "Oop Fundamentals",
  "title": "Encapsulation Concept",
  "content_path": "LLD/week1/oop-fundamentals/encapsulation/concept.md",
  "video_url": null,
  "estimated_minutes": 15,
  "order_num": 1,
  "is_completed": true,
  "is_bookmarked": false,
  "time_spent_seconds": 900,
  "started_at": "2025-11-17T10:00:00",
  "last_accessed": "2025-11-17T10:15:00",
  "completed_at": "2025-11-17T10:15:00",
  "notes": "Important concepts to remember..."
}
```

#### GET /api/lesson/:id/content
Get the markdown content of a lesson.

**Example:** `GET /api/lesson/1/content`

**Response:**
```json
{
  "lesson_id": 1,
  "title": "Encapsulation Concept",
  "content": "# Encapsulation\n\n## The Hook...",
  "content_path": "LLD/week1/oop-fundamentals/encapsulation/concept.md"
}
```

---

### Progress Tracking

#### GET /api/progress
Get comprehensive progress statistics.

**Response:**
```json
{
  "overall": {
    "total_lessons": 150,
    "completed_lessons": 12,
    "completion_percentage": 8,
    "total_estimated_minutes": 2700,
    "total_time_spent_seconds": 28800,
    "estimated_completion_date": "2025-02-15"
  },
  "by_week": [
    {
      "week_type": "LLD",
      "week_num": 1,
      "total_lessons": 20,
      "completed": 5,
      "percentage": 25
    }
  ],
  "streak": {
    "current_days": 3,
    "best_days": 7
  }
}
```

#### GET /api/progress/weekly
Get week-by-week progress breakdown.

**Response:**
```json
[
  {
    "week_type": "LLD",
    "week_num": 1,
    "total_lessons": 20,
    "completed": 5,
    "percentage": 25
  }
]
```

#### POST /api/lesson/:id/complete
Toggle the completion status of a lesson.

**Example:** `POST /api/lesson/1/complete`

**Response:**
```json
{
  "lesson_id": 1,
  "is_completed": true,
  "message": "Lesson marked as completed"
}
```

#### POST /api/lesson/:id/time
Update time spent on a lesson.

**Example:** `POST /api/lesson/1/time`

**Request Body:**
```json
{
  "seconds": 300
}
```

**Response:**
```json
{
  "lesson_id": 1,
  "seconds_added": 300,
  "message": "Time updated successfully"
}
```

#### GET /api/activity/recent
Get recent daily activity.

**Query Parameters:**
- `days` (optional): Number of days to retrieve (default: 30)

**Example:** `GET /api/activity/recent?days=7`

**Response:**
```json
[
  {
    "id": 1,
    "date": "2025-11-17",
    "lessons_completed": 3,
    "time_spent_seconds": 2700
  }
]
```

---

### Notes

#### GET /api/notes/:lesson_id
Get notes for a specific lesson.

**Example:** `GET /api/notes/1`

**Response:**
```json
{
  "id": 1,
  "lesson_id": 1,
  "content": "Important points to remember...",
  "created_at": "2025-11-17T10:00:00",
  "updated_at": "2025-11-17T10:30:00"
}
```

#### POST /api/notes/:lesson_id
Save or update notes for a lesson.

**Example:** `POST /api/notes/1`

**Request Body:**
```json
{
  "content": "Updated notes content..."
}
```

**Response:**
```json
{
  "lesson_id": 1,
  "message": "Notes saved successfully"
}
```

#### DELETE /api/notes/:lesson_id
Delete notes for a lesson.

**Example:** `DELETE /api/notes/1`

**Response:**
```json
{
  "lesson_id": 1,
  "message": "Notes deleted successfully"
}
```

---

### Bookmarks

#### GET /api/bookmarks
Get all bookmarked lessons.

**Response:**
```json
[
  {
    "id": 1,
    "week_num": 1,
    "week_type": "LLD",
    "topic": "Oop Fundamentals",
    "title": "Encapsulation Concept",
    "content_path": "LLD/week1/...",
    "estimated_minutes": 15,
    "is_completed": true,
    "bookmarked_at": "2025-11-17T10:00:00"
  }
]
```

#### POST /api/bookmark/:lesson_id
Toggle bookmark status for a lesson.

**Example:** `POST /api/bookmark/1`

**Response:**
```json
{
  "lesson_id": 1,
  "is_bookmarked": true,
  "message": "Lesson bookmarked"
}
```

---

### Admin / Utility

#### POST /api/admin/reseed
Reseed the database by scanning course content again.

**Response:**
```json
{
  "message": "Database reseeded successfully",
  "timestamp": "2025-11-17T10:30:00"
}
```

**Note:** This will clear existing lessons but preserve progress, notes, and bookmarks.

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "error": "Error Type",
  "message": "Detailed error message"
}
```

## Configuration

Edit `config.py` to customize:

- **Database path**: `DB_PATH`
- **Server port**: `PORT`
- **CORS origins**: `CORS_ORIGINS`
- **Course root directory**: `COURSE_ROOT`
- **Default lesson time**: `DEFAULT_LESSON_TIME`
- **Daily study hours**: `DAILY_STUDY_HOURS`

## Content Seeding

The API automatically scans the course directory structure and creates lessons from markdown files:

1. **Directory Structure:** `/course-root/{LLD|HLD}/week{N}/{topic}/{lesson}.md`
2. **Auto-Detection:** Finds all markdown files (except README.md)
3. **Metadata Extraction:** Generates titles from filenames
4. **Time Estimation:** Calculates reading time based on word count
5. **Ordering:** Maintains hierarchical order

To reseed content after adding new lessons:
```bash
curl -X POST http://localhost:5000/api/admin/reseed
```

## Development

### Running in Debug Mode

Debug mode is enabled by default in `config.py`:
```python
DEBUG = True
```

This provides:
- Auto-reload on code changes
- Detailed error messages
- Request/response logging

### Database Management

View database contents:
```bash
sqlite3 data/lms.db
.tables
SELECT * FROM lessons LIMIT 5;
```

Reset database:
```bash
rm data/lms.db
python app.py  # Will recreate and reseed
```

### Adding Custom Endpoints

Add new endpoints to `app.py`:
```python
@app.route('/api/custom-endpoint', methods=['GET'])
def custom_endpoint():
    try:
        # Your logic here
        return jsonify({'data': 'value'})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
```

## Production Deployment

For production use:

1. **Disable Debug Mode:**
   ```python
   # config.py
   DEBUG = False
   ```

2. **Use Production Server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Add Authentication:**
   Consider adding JWT tokens or session management for user-specific data.

4. **Database Backup:**
   Regularly backup `data/lms.db`

5. **Logging:**
   Configure production logging to file:
   ```python
   logging.basicConfig(
       filename='lms.log',
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   ```

## Troubleshooting

### Database Locked
If you get "database is locked" errors:
- Close any open SQLite connections
- Restart the server

### CORS Issues
Ensure frontend origin is in `CORS_ORIGINS`:
```python
CORS_ORIGINS = ['http://localhost:3000']
```

### Content Not Loading
Check:
- Course directory paths in `config.py`
- File permissions
- Markdown file encoding (should be UTF-8)

### Performance Issues
- Add database indexes for frequently queried columns
- Implement caching for course structure
- Use database connection pooling

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:5000/api/health

# Get course structure
curl http://localhost:5000/api/course-structure

# Get a specific lesson
curl http://localhost:5000/api/lesson/1

# Mark lesson as complete
curl -X POST http://localhost:5000/api/lesson/1/complete

# Update time spent
curl -X POST http://localhost:5000/api/lesson/1/time \
  -H "Content-Type: application/json" \
  -d '{"seconds": 300}'

# Save notes
curl -X POST http://localhost:5000/api/notes/1 \
  -H "Content-Type: application/json" \
  -d '{"content": "My notes here"}'
```

### Using Python

```python
import requests

# Get course structure
response = requests.get('http://localhost:5000/api/course-structure')
data = response.json()
print(data)

# Mark lesson complete
response = requests.post('http://localhost:5000/api/lesson/1/complete')
print(response.json())
```

## License

This is part of the HLD-LLD course repository.

## Support

For issues or questions, check the logs. The API logs all requests, errors, and important operations for debugging.
