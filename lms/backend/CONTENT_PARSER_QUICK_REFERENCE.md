# Content Parser - Quick Reference

## File Location
```
/home/user/hld-lld-course/lms/backend/content_parser.py
```

## Quick Start

### Run the Parser
```bash
cd /home/user/hld-lld-course/lms/backend
python content_parser.py
```

### Test the Results
```bash
python test_parser.py
```

## What It Does

1. **Scans** all `concept.md` files in LLD/HLD directories
2. **Extracts** metadata (title, topic, week)
3. **Calculates** reading time estimates
4. **Populates** SQLite database with lessons
5. **Generates** JSON course structure
6. **Reports** detailed statistics

## Current Statistics

Based on latest run:
- **Total Lessons**: 31
- **Total Time**: 17h 48m
- **LLD Lessons**: 28 (15h 37m)
- **HLD Lessons**: 3 (2h 11m)

## Time Calculation

The parser calculates reading time based on:

| Element | Formula |
|---------|---------|
| Text | 200 words per minute |
| Code blocks | 2 minutes per block |
| Images | 1 minute per image |
| dry_run.md | Full calculation added |
| example.py | +3 minutes |

**Min**: 5 minutes
**Max**: 60 minutes per file

## Directory Structure Scanned

```
/home/user/hld-lld-course/
├── LLD/
│   ├── week1/  ✓ Scanned (13 lessons)
│   ├── week2/  ✓ Scanned (7 lessons)
│   ├── week3/  ✓ Scanned (8 lessons)
│   ├── week4/  ✓ Scanned (0 lessons)
│   └── week5/  ✓ Scanned (0 lessons)
└── HLD/
    ├── week1/  ✓ Scanned (1 lesson)
    ├── week2/  ✓ Scanned (0 lessons)
    ├── week3/  ✓ Scanned (2 lessons)
    ├── week4/  ⚠ Does not exist
    └── week5/  ✓ Scanned (0 lessons)
```

## Sample Lessons Found

| ID | Type | Week | Topic | Title | Time |
|----|------|------|-------|-------|------|
| 1 | LLD | 1 | Oop Fundamentals > Abstraction | Abstraction | 81 min |
| 2 | LLD | 1 | Oop Fundamentals > Encapsulation | Encapsulation | 63 min |
| 3 | LLD | 1 | Oop Fundamentals > Inheritance | Inheritance | 69 min |
| 4 | LLD | 1 | Oop Fundamentals > Polymorphism | Polymorphism | 66 min |
| 5 | LLD | 1 | Patterns > Abstract Factory | Abstract Factory Pattern | 13 min |

## Output Files

### 1. Database
**Location**: `/home/user/hld-lld-course/lms/backend/data/lms.db`

**Table**: `lessons`

**Columns**:
- `id` - Auto-incrementing ID
- `week_num` - Week number (1-5)
- `week_type` - 'LLD' or 'HLD'
- `topic` - Hierarchical topic path
- `title` - Lesson title
- `content_path` - Path to markdown file
- `video_url` - Video URL (NULL)
- `estimated_minutes` - Reading time
- `order_num` - Display order

### 2. Course Structure JSON
**Location**: `/home/user/hld-lld-course/lms/backend/data/course_structure.json`

**Format**:
```json
{
  "LLD": {
    "1": {
      "topics": {
        "Oop Fundamentals > Encapsulation": [
          {
            "id": 2,
            "title": "Encapsulation",
            "estimated_minutes": 63
          }
        ]
      }
    }
  },
  "HLD": {...}
}
```

## Key Functions Reference

| Function | Purpose | Returns |
|----------|---------|---------|
| `calculate_reading_time()` | Calculate time estimate | int (minutes) |
| `extract_title_from_markdown()` | Get lesson title | str |
| `extract_topic_from_path()` | Get hierarchical topic | str |
| `parse_lesson()` | Extract lesson metadata | dict |
| `parse_week()` | Scan week directory | list[dict] |
| `scan_course_content()` | Scan all content | list[dict] |
| `populate_database()` | Insert into DB | int (count) |
| `generate_course_structure()` | Create JSON structure | dict |
| `print_statistics()` | Show stats | None |

## Common Use Cases

### 1. Initial Setup
```bash
# First time setup
python content_parser.py
```

### 2. After Adding New Lessons
```bash
# Re-scan and update database
python content_parser.py
```

### 3. Verify Database
```bash
# Check what's in the database
python test_parser.py
```

### 4. Check JSON Structure
```bash
# View generated structure
cat data/course_structure.json | python -m json.tool | head -n 50
```

## Sorting Logic

Lessons are sorted by:
1. **Course Type**: LLD first, then HLD
2. **Week Number**: 1, 2, 3, 4, 5
3. **Topic**: Alphabetical
4. **Title**: Alphabetical

This ensures consistent ordering across all views.

## Example Output

```
============================================================
LMS CONTENT PARSER
============================================================

Scanning LLD content...
  Scanning LLD/week1...
    Found: Oop Fundamentals > Encapsulation - Encapsulation (63 min)
    Found: Oop Fundamentals > Inheritance - Inheritance (69 min)

=== Total lessons found: 31 ===

Populating database with 31 lessons...
Successfully populated 31 lessons into database

Course structure saved to: .../data/course_structure.json

============================================================
COURSE CONTENT STATISTICS
============================================================

Total Lessons: 31
Total Estimated Time: 17h 48m (1068 minutes)

LLD:
  Lessons: 28
  Time: 15h 37m
    Week 1: 13 lessons, 6h 42m
    Week 2: 7 lessons, 4h 1m
    Week 3: 8 lessons, 4h 54m
```

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| No lessons found | Check directory paths in config.py |
| Database locked | Close any other connections to lms.db |
| Import errors | Run from backend directory |
| Permission denied | Check data/ directory is writable |
| Missing files | Verify concept.md files exist |

## Dependencies

Required imports:
- `os` - File system operations
- `re` - Regular expressions for parsing
- `json` - JSON file generation
- `pathlib.Path` - Path handling
- `config` - Configuration settings
- `database.Database` - Database operations

## Integration Points

Works with:
- **database.py** - Database operations
- **config.py** - Path configuration
- **models.py** - Schema definitions
- **app.py** - Flask API (reads generated data)

## Performance

- Scans 31 lessons in < 1 second
- Database insertion: < 1 second
- JSON generation: < 0.1 second
- Total runtime: ~2-3 seconds

## Best Practices

1. Always run from `/home/user/hld-lld-course/lms/backend/`
2. Backup database before running
3. Review output for warnings
4. Run test script to verify
5. Check JSON structure after generation

## Next Steps After Running

1. Verify lesson count matches expectations
2. Check time estimates are reasonable
3. Review hierarchical topic structure
4. Test with frontend application
5. Add video URLs if needed (separate script)

## Related Files

- `content_parser.py` - Main parser (this file)
- `test_parser.py` - Test/verification script
- `database.py` - Database operations
- `config.py` - Configuration
- `CONTENT_PARSER_README.md` - Full documentation
