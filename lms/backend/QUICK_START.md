# Quick Start Guide - YouTube Video Integration

## Overview
This guide walks you through using the YouTube video reference system for the System Design course.

## Files Created
- `youtube_videos.json` - Database of 116 curated YouTube videos
- `update_videos.py` - Script to populate lesson videos in database
- `README.md` - Comprehensive documentation
- `QUICK_START.md` - This file

## Quick Setup (3 Steps)

### Step 1: Initialize the Database
If you haven't already, initialize the LMS database with course content:
```bash
cd /home/user/hld-lld-course/lms/backend
python3 content_parser.py
```

### Step 2: Preview Changes (Dry Run)
```bash
python3 update_videos.py --dry-run
```
This shows which lessons will get videos without making any changes.

### Step 3: Apply Updates
```bash
python3 update_videos.py
```
This updates the database with video URLs.

## Verify Installation

**Check video statistics:**
```bash
python3 update_videos.py --list-topics
```

**Validate JSON structure:**
```bash
python3 update_videos.py --validate
```

## What Got Created

### youtube_videos.json (116 videos)
Organized as:
```
LLD (Low Level Design):
├─ Week 1: SOLID Principles (13 topics, 19 videos)
├─ Week 2: Creational Patterns (7 topics, 14 videos)
├─ Week 3: Structural Patterns (8 topics, 15 videos)
├─ Week 4: Case Studies (3 topics, 6 videos)
└─ Week 5: Advanced Studies (2 topics, 1 video)

HLD (High Level Design):
├─ Week 1: Fundamentals (7 topics, 13 videos)
├─ Week 2: Scalability (9 topics, 17 videos)
├─ Week 3: Data Management (6 topics, 11 videos)
├─ Week 4: Production (6 topics, 12 videos)
└─ Week 5: Real-World Systems (4 topics, 8 videos)
```

### Video Quality Metrics
- **Total Videos**: 116
- **LLD Videos**: 55 (across 33 topics)
- **HLD Videos**: 61 (across 32 topics)
- **Channels**: 8 reputable educational channels
- **Average Duration**: 20-25 minutes
- **Recent Content**: 2023 productions

### Featured Channels
1. **ByteByteGo** - System design authority
2. **Gaurav Sen** - In-depth concepts
3. **Hussein Nasser** - Backend fundamentals
4. **freeCodeCamp** - Comprehensive tutorials
5. **Programming with Mosh** - OOP & patterns
6. **ArjanCodes** - Clean code practices
7. **Tech Dummies** - Pattern visualization
8. **System Design Interview** - Interview prep

## Database Integration

After running `update_videos.py`, the LMS API will include video URLs:

```bash
# Get lesson with video
curl http://localhost:5000/api/lesson/1

# Response includes:
{
  "success": true,
  "lesson": {
    "id": 1,
    "title": "Encapsulation in OOP",
    "topic": "encapsulation",
    "video_url": "https://www.youtube.com/watch?v=...",
    ...
  }
}
```

## Common Commands

**List all available topics:**
```bash
python3 update_videos.py --list-topics
```

**Check changes before applying:**
```bash
python3 update_videos.py --dry-run
```

**Update with custom JSON file:**
```bash
python3 update_videos.py --json-file /path/to/custom.json
```

**Check script help:**
```bash
python3 update_videos.py --help
```

## Troubleshooting

**Issue: "No lessons found in database"**
- Solution: Run `python3 content_parser.py` first

**Issue: "JSON structure is invalid"**
- Solution: Check youtube_videos.json with `python3 -m json.tool youtube_videos.json`

**Issue: Videos not updating**
- Solution: Ensure topic names in database match JSON keys
- Use `--list-topics` to see available topics

## File Locations

```
/home/user/hld-lld-course/
├─ lms/
│  ├─ backend/
│  │  ├─ youtube_videos.json    ← Video database
│  │  ├─ update_videos.py       ← Update script
│  │  ├─ README.md              ← Full documentation
│  │  ├─ QUICK_START.md         ← This file
│  │  ├─ content_parser.py      ← Content importer
│  │  └─ models.py              ← DB models
│  ├─ database.py               ← Database layer
│  ├─ app.py                    ← Flask app
│  └─ data/
│     └─ lms.db                 ← SQLite database
└─ LLD/                          ← Course content
└─ HLD/                          ← Course content
```

## Next Steps

1. **Initialize database**: `python3 content_parser.py`
2. **Add videos**: `python3 update_videos.py`
3. **Start LMS**: `python3 app.py`
4. **Access frontend**: http://localhost:5000

## Video Categories

### LLD Week 1 (19 videos)
- OOP Principles: Encapsulation, Inheritance, Polymorphism, Abstraction
- Design Principles: DRY, KISS, SOLID (5 principles)
- Creational Patterns: Factory, Abstract Factory

### LLD Week 2 (14 videos)
- Singleton, Builder, Prototype, Observer, Command, Chain, Iterator

### LLD Week 3 (15 videos)
- Strategy, Template, Adapter, Decorator, Bridge, Composite, Proxy, Facade

### LLD Week 4 (6 videos)
- Railway Reservation System
- Chess Game System
- Elevator System

### LLD Week 5 (1 video)
- Recommendation System, Meeting Scheduler

### HLD Week 1 (13 videos)
- Protocols: HTTP, WebSockets, SSE, gRPC
- Architecture: Client-Server, Monolith vs Microservices, REST vs GraphQL

### HLD Week 2 (17 videos)
- Performance: Latency, Throughput, CAP Theorem, Load Balancing
- Caching: Strategies, LRU, LFU, Consistent Hashing
- Messaging: Pub/Sub, Apache Kafka

### HLD Week 3 (11 videos)
- Databases: SQL vs NoSQL, Indexing, Replication, Sharding
- Consistency: ACID, BASE

### HLD Week 4 (12 videos)
- Design: Capacity, Rate Limiting, Circuit Breaker, API Design
- Security: JWT Authentication
- Operations: System Monitoring

### HLD Week 5 (8 videos)
- WhatsApp System Design
- YouTube System Design
- Uber System Design
- Stock Trading Platform Design

## Advanced Usage

### Adding Custom Videos
Edit `youtube_videos.json` to add new videos:
```json
"your_topic": [
  {
    "title": "Your Video Title",
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "channel": "Channel Name",
    "duration_minutes": 20,
    "language": "English",
    "year": 2024
  }
]
```

### Batch Updates
To update only specific courses:
1. Edit `youtube_videos.json` to include only desired courses
2. Run: `python3 update_videos.py --dry-run`
3. Review changes
4. Run: `python3 update_videos.py`

### Database Direct Access
Query videos directly from SQLite:
```bash
sqlite3 data/lms.db "SELECT topic, video_url FROM lessons WHERE video_url != '' LIMIT 5;"
```

## Support

For detailed information, see:
- `README.md` - Complete documentation
- Database schema in `database.py`
- Video structure in `youtube_videos.json`

## Statistics Summary

```
Video Database Snapshot
├─ Total Videos: 116
├─ LLD Topics: 33
├─ HLD Topics: 32
├─ Channels: 8
├─ Duration: 8-50 minutes
└─ Language: English
```

---
Last Updated: November 17, 2025
