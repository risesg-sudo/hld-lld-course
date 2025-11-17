# System Design LMS - Complete Setup Guide

## Overview

A complete Learning Management System (LMS) for the System Design course featuring:

- Next.js 14 frontend with Tailwind CSS and shadcn/ui
- Flask backend with SQLite database
- Progress tracking with time estimates
- 116 curated YouTube videos
- 31 lessons (17h 48m of content)
- Auto-save notes and bookmarks
- Dark mode support
- Responsive design

## Architecture

```
lms/
├── backend/                 # Flask API + SQLite
│   ├── app.py              # Main API server
│   ├── database.py         # Database operations
│   ├── content_parser.py   # Course content parser
│   ├── update_videos.py    # YouTube video integration
│   ├── youtube_videos.json # 116 curated videos
│   └── requirements.txt
│
└── frontend/               # Next.js application
    ├── app/               # App Router pages
    ├── components/        # React components
    ├── lib/              # API client & types
    └── package.json
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Step 1: Setup Backend

```bash
cd /home/user/hld-lld-course/lms/backend

# Install Python dependencies
pip install -r requirements.txt

# Parse course content and populate database
python content_parser.py

# Add YouTube videos to lessons
python update_videos.py

# Start the backend server
python app.py
```

Backend will run on: **http://localhost:5000**

### Step 2: Setup Frontend

```bash
cd /home/user/hld-lld-course/lms/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on: **http://localhost:3000**

### Step 3: Access the LMS

Open your browser and navigate to: **http://localhost:3000**

## Features

### Progress Tracking (Primary Feature)

- Overall completion percentage with donut chart
- Per-week progress bars
- Time estimates for each lesson (auto-calculated)
- Active timer while viewing lessons
- Completion streaks (days in a row)
- Estimated completion date
- Weekly learning goals

### Learning Features

- 31 lessons across LLD and HLD
- 116 curated YouTube reference videos
- Markdown content with syntax highlighting
- Code examples with proper formatting
- Auto-save personal notes
- Bookmark favorite lessons
- Search functionality
- Filter by completion status

### UI/UX

- Modern, clean interface with Tailwind CSS
- shadcn/ui component library
- Responsive design (mobile, tablet, desktop)
- Dark/light mode toggle
- Collapsible sidebar navigation
- Previous/Next lesson navigation
- Progress visualization with Chart.js

## Database Schema

```sql
-- Lessons (31 entries with time estimates)
lessons (
    id, week_num, week_type, topic, title,
    content_path, video_url, estimated_minutes, order_num
)

-- Progress tracking
progress (
    lesson_id, is_completed, time_spent_seconds,
    started_at, last_accessed, completed_at
)

-- Personal notes (auto-save)
notes (
    id, lesson_id, content, created_at, updated_at
)

-- Bookmarks
bookmarks (
    lesson_id, created_at
)

-- Daily activity
activity (
    id, date, lessons_completed, time_spent_seconds
)
```

## API Endpoints

### Course Structure
- `GET /api/course-structure` - Full course hierarchy
- `GET /api/weeks` - Week summaries
- `GET /api/week/:type/:num` - Specific week details

### Lessons
- `GET /api/lesson/:id` - Lesson metadata
- `GET /api/lesson/:id/content` - Markdown content

### Progress
- `GET /api/progress` - Overall statistics
- `GET /api/progress/weekly` - Week breakdown
- `POST /api/lesson/:id/complete` - Toggle completion
- `POST /api/lesson/:id/time` - Update time spent
- `GET /api/activity/recent` - Recent activity

### Notes & Bookmarks
- `GET/POST/DELETE /api/notes/:id` - Manage notes
- `GET /api/bookmarks` - All bookmarks
- `POST /api/bookmark/:id` - Toggle bookmark

## Course Content

### LLD (Low-Level Design) - 28 lessons, 15h 37m

**Week 1: OOP & SOLID** (13 lessons, 6h 42m)
- Encapsulation, Inheritance, Polymorphism, Abstraction
- DRY and KISS principles
- All 5 SOLID principles
- Factory and Abstract Factory patterns

**Week 2: Creational & Behavioral** (7 lessons, 4h 1m)
- Singleton, Builder, Prototype
- Observer, Command, Chain of Responsibility, Iterator

**Week 3: Structural Patterns** (8 lessons, 4h 54m)
- Strategy, Template, Adapter, Decorator
- Bridge, Composite, Proxy, Facade

**Week 4: System Designs**
- IRCTC, Chess, Elevator systems

**Week 5: Advanced Designs**
- Recommendation system, Meeting scheduler

### HLD (High-Level Design) - 3 lessons, 2h 11m

**Week 1: Networking**
- Client-server architecture

**Week 3: Databases**
- SQL and NoSQL concepts

## YouTube Videos

116 curated videos from top channels:

- **ByteByteGo** (18 videos) - System design interviews
- **Gaurav Sen** (30 videos) - Distributed systems
- **Hussein Nasser** (16 videos) - Backend engineering
- **freeCodeCamp** (10 videos) - Comprehensive tutorials
- **Programming with Mosh** (6 videos) - OOP concepts
- **ArjanCodes** (13 videos) - Design patterns
- **Tech Dummies** (13 videos) - System design
- **System Design Interview** (4 videos) - Interview prep

Videos cover 65 topics with average duration of 20-25 minutes.

## Time Estimates

The system automatically calculates reading time based on:

- Word count (200 words per minute)
- Code blocks (2 minutes each)
- Images/diagrams (1 minute each)
- Associated files (dry_run.md, example.py)

Current course stats:
- Total time: 17h 48m
- Average lesson: 34 minutes
- Shortest lesson: 17 minutes
- Longest lesson: 69 minutes

## Development

### Backend Development

```bash
cd lms/backend

# Run tests
python test_api.py

# View database contents
python view_lessons.py

# Reseed database
python content_parser.py

# Update videos
python update_videos.py
```

### Frontend Development

```bash
cd lms/frontend

# Development mode (hot reload)
npm run dev

# Build for production
npm run build

# Run production build
npm start

# Type check
npm run type-check

# Lint
npm run lint
```

## Troubleshooting

### Backend Issues

**Database not found:**
```bash
cd lms/backend
python content_parser.py  # Recreates database
```

**Videos not showing:**
```bash
cd lms/backend
python update_videos.py --validate  # Check JSON
python update_videos.py             # Apply to database
```

**Port 5000 in use:**
Edit `config.py` and change `PORT = 5000` to another port

### Frontend Issues

**API connection failed:**
Check that backend is running on http://localhost:5000

**Build errors:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**TypeScript errors:**
```bash
npm run type-check
```

## Project Structure

```
/home/user/hld-lld-course/
├── LLD/                    # Course content (markdown files)
├── HLD/                    # Course content (markdown files)
└── lms/
    ├── backend/
    │   ├── app.py         # Flask server
    │   ├── database.py    # SQLite operations
    │   ├── content_parser.py  # Content scanner
    │   ├── update_videos.py   # Video integration
    │   ├── youtube_videos.json  # Video database
    │   ├── data/
    │   │   └── lms.db     # SQLite database
    │   └── requirements.txt
    │
    └── frontend/
        ├── app/
        │   ├── layout.tsx      # Root layout
        │   ├── page.tsx        # Dashboard
        │   └── lesson/[id]/page.tsx  # Lesson viewer
        ├── components/
        │   ├── Sidebar.tsx           # Navigation
        │   ├── ProgressDashboard.tsx # Stats & charts
        │   ├── LessonContent.tsx     # Markdown renderer
        │   ├── VideoPlayer.tsx       # YouTube embed
        │   └── NotesEditor.tsx       # Auto-save notes
        ├── lib/
        │   ├── api.ts              # Backend client
        │   └── types.ts            # TypeScript types
        └── package.json
```

## Production Deployment

### Backend (Flask)

```bash
cd lms/backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend (Next.js)

```bash
cd lms/frontend
npm run build
npm start
```

Or deploy to Vercel:
```bash
npm install -g vercel
vercel deploy
```

## Environment Variables

### Backend (.env)
```
FLASK_ENV=development
DATABASE_PATH=data/lms.db
COURSE_ROOT=/home/user/hld-lld-course
PORT=5000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## Support

For issues, refer to:
- Backend README: `/lms/backend/README.md`
- Frontend README: `/lms/frontend/README.md`
- Content Parser: `/lms/backend/CONTENT_PARSER_README.md`
- Video System: `/lms/backend/VIDEO_INDEX.md`

## License

This LMS is part of the System Design course materials.

## Next Steps

1. Start both backend and frontend servers
2. Navigate to http://localhost:3000
3. Begin with LLD Week 1 - Encapsulation
4. Track your progress and take notes
5. Watch reference videos for each topic
6. Mark lessons complete as you learn
7. Aim for daily learning streaks

Happy Learning!
