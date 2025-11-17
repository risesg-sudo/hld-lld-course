# Content Parser Documentation

## Overview

The Content Parser is a comprehensive tool that scans the HLD/LLD course directories and populates the LMS database with lesson information. It automatically extracts metadata, calculates reading time estimates, and generates hierarchical course structures.

## File Location

**Path**: `/home/user/hld-lld-course/lms/backend/content_parser.py`

## Features

### 1. Automatic Content Discovery
- Recursively scans `LLD/` and `HLD/` directories (weeks 1-5)
- Finds all `concept.md` files in the course structure
- Extracts metadata from directory structure and markdown content

### 2. Intelligent Time Estimation
Calculates reading time based on:
- **Word count**: 200 words per minute
- **Code blocks**: 2 minutes per code block
- **Images/diagrams**: 1 minute per image
- **Additional files**:
  - Adds time for `dry_run.md` if present
  - Adds 3 minutes for `example.py` files

### 3. Metadata Extraction
For each lesson, extracts:
- **Title**: From first `#` heading in markdown
- **Topic**: Hierarchical path from directory structure
- **Week number**: From directory name
- **Week type**: LLD or HLD
- **Content path**: Relative path from course root
- **Estimated minutes**: Calculated reading time

### 4. Database Population
- Clears existing lessons (fresh import)
- Sorts lessons logically (LLD first, then by week/topic/title)
- Assigns sequential order numbers
- Inserts into SQLite database

### 5. Course Structure Generation
Creates JSON file with hierarchical structure:
```json
{
  "LLD": {
    "1": {
      "topics": {
        "OOP Fundamentals > Encapsulation": [
          {
            "id": 1,
            "title": "Encapsulation",
            "estimated_minutes": 63
          }
        ]
      }
    }
  }
}
```

### 6. Statistics & Reporting
Provides detailed statistics:
- Total lessons count
- Total estimated time
- Breakdown by LLD/HLD
- Breakdown by week
- Time estimates for each section

## Usage

### Basic Usage

Run the parser from the backend directory:

```bash
cd /home/user/hld-lld-course/lms/backend
python content_parser.py
```

### Expected Output

```
============================================================
LMS CONTENT PARSER
============================================================

Initializing database...
Clearing existing lessons...
Fetching course content...

=== Scanning Course Content ===

Scanning LLD content...
  Scanning LLD/week1...
    Found: Oop Fundamentals > Encapsulation - Encapsulation (63 min)
    Found: Oop Fundamentals > Inheritance - Inheritance (69 min)
    ...

=== Total lessons found: 31 ===

Populating database with 31 lessons...
Successfully populated 31 lessons into database

Generating course structure...
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

HLD:
  Lessons: 3
  Time: 2h 11m
    Week 1: 1 lessons, 1h 4m
    Week 3: 2 lessons, 1h 7m

============================================================

Course content parsing completed successfully!
```

## Directory Structure Expected

The parser expects the following structure:

```
/home/user/hld-lld-course/
├── LLD/
│   ├── week1/
│   │   ├── oop-fundamentals/
│   │   │   ├── encapsulation/
│   │   │   │   ├── concept.md       ← Main content
│   │   │   │   ├── example.py       ← Optional
│   │   │   │   └── dry_run.md       ← Optional
│   │   │   └── inheritance/...
│   │   ├── principles/...
│   │   ├── solid/...
│   │   └── patterns/...
│   ├── week2/...
│   ├── week3/...
│   ├── week4/...
│   └── week5/...
└── HLD/
    ├── week1/...
    ├── week2/...
    └── ...
```

## Functions

### Core Functions

#### `calculate_reading_time(markdown_content)`
Calculates estimated reading time for markdown content.

**Parameters**:
- `markdown_content` (str): Markdown file contents

**Returns**:
- `int`: Estimated minutes (min: 5, max: 60)

#### `extract_title_from_markdown(file_path)`
Extracts title from first heading in markdown file.

**Parameters**:
- `file_path` (str): Path to markdown file

**Returns**:
- `str`: Extracted title or formatted filename

#### `extract_topic_from_path(directory_path, week_type, week_num)`
Extracts hierarchical topic from directory structure.

**Parameters**:
- `directory_path` (str): Full directory path
- `week_type` (str): 'LLD' or 'HLD'
- `week_num` (int): Week number

**Returns**:
- `str`: Hierarchical topic (e.g., "OOP Fundamentals > Encapsulation")

#### `parse_lesson(file_path, week_type, week_num, directory)`
Parses a single lesson file and extracts all metadata.

**Parameters**:
- `file_path` (str): Path to concept.md
- `week_type` (str): 'LLD' or 'HLD'
- `week_num` (int): Week number
- `directory` (str): Lesson directory path

**Returns**:
- `dict`: Lesson metadata including title, topic, time estimate, etc.

#### `parse_week(week_path, week_type, week_num)`
Scans a week directory for all lessons.

**Parameters**:
- `week_path` (str): Path to week directory
- `week_type` (str): 'LLD' or 'HLD'
- `week_num` (int): Week number

**Returns**:
- `list`: List of lesson dictionaries

#### `scan_course_content()`
Scans all LLD and HLD directories.

**Returns**:
- `list`: Complete list of all lessons found

#### `populate_database(db)`
Populates database with lessons.

**Parameters**:
- `db` (Database): Database instance

**Returns**:
- `int`: Number of lessons inserted

#### `generate_course_structure(db)`
Generates hierarchical course structure.

**Parameters**:
- `db` (Database): Database instance

**Returns**:
- `dict`: Nested structure organized by type/week/topic

#### `print_statistics(db)`
Prints detailed statistics about course content.

**Parameters**:
- `db` (Database): Database instance

## Output Files

### 1. Database (`data/lms.db`)
SQLite database with populated `lessons` table containing:
- `id`: Auto-incrementing primary key
- `week_num`: Week number (1-5)
- `week_type`: 'LLD' or 'HLD'
- `topic`: Hierarchical topic path
- `title`: Lesson title
- `content_path`: Relative path to markdown file
- `video_url`: Video URL (initially NULL)
- `estimated_minutes`: Reading time estimate
- `order_num`: Sequential ordering

### 2. Course Structure JSON (`data/course_structure.json`)
Hierarchical JSON structure for frontend consumption:
- Organized by course type (LLD/HLD)
- Nested by week number
- Grouped by topic
- Contains lesson ID, title, and time estimate

## Error Handling

The parser handles various edge cases:

1. **Missing directories**: Warns but continues processing
2. **Unreadable files**: Logs error and uses fallback values
3. **Missing titles**: Uses formatted filename as fallback
4. **Invalid markdown**: Gracefully handles parsing errors
5. **Database errors**: Logs specific insertion errors

## Testing

Verify the parser output:

```bash
cd /home/user/hld-lld-course/lms/backend
python test_parser.py
```

This will show:
- Total lessons in database
- Sample lesson details
- First 15 lessons with metadata

## Integration

The content parser integrates with:

1. **Database Module** (`database.py`): Uses Database class for all operations
2. **Config Module** (`config.py`): Gets paths and configuration
3. **Models Module** (`models.py`): Uses schema definitions

## When to Run

Run the content parser when:

1. **Initial setup**: First time setting up the LMS
2. **Content updates**: After adding new lessons or weeks
3. **Metadata changes**: After modifying titles or structure
4. **Database reset**: After clearing the database

## Configuration

The parser uses configuration from `config.py`:

```python
COURSE_ROOT = Path('/home/user/hld-lld-course')
CONTENT_PATHS = {
    'LLD': COURSE_ROOT / 'LLD',
    'HLD': COURSE_ROOT / 'HLD',
}
```

## Customization

### Modify Time Calculation

Edit the `calculate_reading_time()` function:

```python
# Current: 200 words per minute
word_count = len(text_only.split())
reading_minutes = word_count / 200  # Adjust this value

# Current: 2 minutes per code block
code_minutes = (code_blocks / 2) * 2  # Adjust this value
```

### Add More File Types

Modify `parse_week()` to look for additional markdown files:

```python
for root, dirs, files in os.walk(week_path):
    # Add more file patterns here
    if 'concept.md' in files or 'overview.md' in files:
        # Process file
```

### Change Sorting Order

Modify the sort key in `populate_database()`:

```python
lessons.sort(key=lambda x: (
    0 if x['week_type'] == 'LLD' else 1,  # Change priority
    x['week_num'],                         # Week order
    x['topic'],                            # Topic order
    x['title']                             # Title order
))
```

## Troubleshooting

### Issue: "No lessons found"
- Check that course directories exist at expected paths
- Verify `concept.md` files are present
- Check directory naming matches `week1`, `week2`, etc.

### Issue: "Database error"
- Ensure `data/` directory exists and is writable
- Check database schema is initialized
- Verify no file permission issues

### Issue: "Incorrect time estimates"
- Review markdown file formatting
- Check for unusual code block patterns
- Adjust calculation constants if needed

### Issue: "Missing topics"
- Verify directory structure matches expected format
- Check for symlinks or unusual path structures
- Ensure directories are readable

## Best Practices

1. **Backup database** before running parser
2. **Review output** for any warnings or errors
3. **Verify statistics** match expected course content
4. **Test course structure JSON** with frontend
5. **Run test script** after parsing to verify results

## Future Enhancements

Potential improvements:

1. **Incremental updates**: Only update changed lessons
2. **Video URL detection**: Automatically find associated videos
3. **Dependency tracking**: Track prerequisite lessons
4. **Difficulty levels**: Extract or calculate lesson difficulty
5. **Tag extraction**: Parse tags from markdown metadata
6. **Multi-language support**: Handle different language versions
7. **Preview generation**: Create lesson previews/summaries
8. **Validation checks**: Verify markdown quality and completeness

## Support

For issues or questions:
1. Check this documentation
2. Review error messages in console output
3. Run test script to verify database state
4. Check database logs in `database.py`
