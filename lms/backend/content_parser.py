"""
Content Parser for LMS Backend
Scans course directories (LLD/HLD) and populates database with lessons
Includes time estimates, metadata extraction, and course structure generation
"""

import os
import re
import json
from pathlib import Path

from config import COURSE_ROOT, CONTENT_PATHS
from database import Database

# Course directories
LLD_DIR = str(CONTENT_PATHS['LLD'])
HLD_DIR = str(CONTENT_PATHS['HLD'])


def calculate_reading_time(markdown_content):
    """
    Calculate estimated reading time based on:
    - Word count (200 words per minute)
    - Code blocks (2 minutes per block)
    - Images/diagrams (1 minute each)
    """
    # Remove code blocks temporarily to count text words
    text_only = re.sub(r'```[\s\S]*?```', '', markdown_content)

    # Remove images
    text_only = re.sub(r'!\[.*?\]\(.*?\)', '', text_only)

    # Remove markdown links but keep the text
    text_only = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text_only)

    # Count words
    word_count = len(text_only.split())
    reading_minutes = word_count / 200

    # Count code blocks (each ``` pair is one block)
    code_blocks = markdown_content.count('```')
    code_minutes = (code_blocks / 2) * 2  # 2 min per code block

    # Count images/diagrams
    images = markdown_content.count('![')
    image_minutes = images * 1

    total_minutes = int(reading_minutes + code_minutes + image_minutes)

    # Minimum 5 minutes, maximum 60 minutes per file
    return max(5, min(total_minutes, 60))


def extract_title_from_markdown(file_path):
    """
    Extract title from the first # heading in markdown file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for first # heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()

        # Fallback to filename
        return Path(file_path).stem.replace('-', ' ').replace('_', ' ').title()

    except Exception as e:
        print(f"Warning: Error reading {file_path}: {e}")
        return Path(file_path).stem.replace('-', ' ').replace('_', ' ').title()


def extract_topic_from_path(directory_path, week_type, week_num):
    """
    Extract topic from directory path
    e.g., /LLD/week1/oop-fundamentals/encapsulation/ -> "OOP Fundamentals > Encapsulation"
    """
    parts = Path(directory_path).parts

    # Find the index of the week directory
    week_dir_name = f'week{week_num}'
    try:
        week_idx = [i for i, p in enumerate(parts) if week_dir_name in p.lower()][0]
    except IndexError:
        # Fallback: use last directory name
        return parts[-1].replace('-', ' ').replace('_', ' ').title()

    # Get all parts after week directory
    topic_parts = parts[week_idx + 1:]

    if not topic_parts:
        return f"Week {week_num} Overview"

    # Create hierarchical topic name
    topic = ' > '.join(part.replace('-', ' ').replace('_', ' ').title() for part in topic_parts)
    return topic


def parse_lesson(file_path, week_type, week_num, directory):
    """
    Extract lesson metadata from concept.md or other markdown file

    Returns dict with:
    - week_type: 'LLD' or 'HLD'
    - week_num: integer week number
    - topic: hierarchical topic name
    - title: lesson title from markdown
    - content_path: relative path to content file
    - estimated_minutes: calculated reading time
    - video_url: None (to be populated later)
    - has_example: boolean
    - has_dry_run: boolean
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    # Extract title from markdown
    title = extract_title_from_markdown(file_path)

    # Extract topic from directory path
    topic = extract_topic_from_path(directory, week_type, week_num)

    # Calculate base reading time
    estimated_minutes = calculate_reading_time(content)

    # Check for associated files in the same directory
    has_example = os.path.exists(os.path.join(directory, 'example.py'))
    has_dry_run = os.path.exists(os.path.join(directory, 'dry_run.md'))

    # Add extra time for dry_run if it exists
    if has_dry_run:
        dry_run_path = os.path.join(directory, 'dry_run.md')
        try:
            with open(dry_run_path, 'r', encoding='utf-8') as f:
                dry_run_content = f.read()
                estimated_minutes += calculate_reading_time(dry_run_content)
        except Exception as e:
            print(f"Warning: Error reading dry_run.md at {dry_run_path}: {e}")

    # Add extra time for example code if it exists
    if has_example:
        estimated_minutes += 3  # Add 3 minutes for code review

    # Get relative path from course root
    relative_path = os.path.relpath(file_path, COURSE_ROOT)

    # Determine file type for title suffix
    file_name = os.path.basename(file_path)
    if file_name == 'concept.md':
        full_title = title
    else:
        file_type = file_name.replace('.md', '').replace('_', ' ').replace('-', ' ').title()
        full_title = f"{title}"

    return {
        'week_type': week_type,
        'week_num': week_num,
        'topic': topic,
        'title': full_title,
        'content_path': relative_path,
        'estimated_minutes': estimated_minutes,
        'video_url': None,
        'has_example': has_example,
        'has_dry_run': has_dry_run
    }


def parse_week(week_path, week_type, week_num):
    """
    Parse a week directory and extract all concept.md files
    Returns list of lesson dictionaries
    """
    lessons = []

    if not os.path.exists(week_path):
        print(f"Warning: Week path does not exist: {week_path}")
        return lessons

    print(f"  Scanning {week_type}/week{week_num}...")

    # Find all concept.md files recursively
    for root, dirs, files in os.walk(week_path):
        if 'concept.md' in files:
            concept_path = os.path.join(root, 'concept.md')
            lesson = parse_lesson(concept_path, week_type, week_num, root)

            if lesson:
                lessons.append(lesson)
                print(f"    Found: {lesson['topic']} - {lesson['title']} ({lesson['estimated_minutes']} min)")

    return lessons


def scan_course_content():
    """
    Scan LLD and HLD directories and extract all lessons
    Returns list of all lessons with metadata
    """
    lessons = []

    print("\n=== Scanning Course Content ===\n")

    # Scan LLD weeks 1-5
    print("Scanning LLD content...")
    for week_num in range(1, 6):
        week_path = os.path.join(LLD_DIR, f'week{week_num}')
        week_lessons = parse_week(week_path, 'LLD', week_num)
        lessons.extend(week_lessons)

    # Scan HLD weeks 1-5
    print("\nScanning HLD content...")
    for week_num in range(1, 6):
        week_path = os.path.join(HLD_DIR, f'week{week_num}')
        week_lessons = parse_week(week_path, 'HLD', week_num)
        lessons.extend(week_lessons)

    print(f"\n=== Total lessons found: {len(lessons)} ===\n")

    return lessons


def populate_database(db):
    """
    Populate database with all lessons from course content
    Sorts lessons and assigns order numbers
    """
    print("Fetching course content...")
    lessons = scan_course_content()

    if not lessons:
        print("Warning: No lessons found!")
        return 0

    # Sort lessons by:
    # 1. Week type (LLD first, then HLD)
    # 2. Week number
    # 3. Topic (alphabetically)
    # 4. Title (alphabetically)
    lessons.sort(key=lambda x: (
        0 if x['week_type'] == 'LLD' else 1,
        x['week_num'],
        x['topic'],
        x['title']
    ))

    print(f"Populating database with {len(lessons)} lessons...")

    # Insert into database with order numbers
    with db.get_connection() as conn:
        cursor = conn.cursor()

        for order, lesson in enumerate(lessons, start=1):
            try:
                cursor.execute("""
                    INSERT INTO lessons (
                        week_num, week_type, topic, title,
                        content_path, video_url, estimated_minutes, order_num
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    lesson['week_num'],
                    lesson['week_type'],
                    lesson['topic'],
                    lesson['title'],
                    lesson['content_path'],
                    lesson['video_url'],
                    lesson['estimated_minutes'],
                    order
                ))
            except Exception as e:
                print(f"Error inserting lesson '{lesson['title']}': {e}")

    print(f"Successfully populated {len(lessons)} lessons into database\n")

    return len(lessons)


def generate_course_structure(db):
    """
    Generate hierarchical course structure for frontend

    Returns structure:
    {
        'LLD': {
            1: {
                'topics': {
                    'OOP Fundamentals': [
                        {'id': 1, 'title': 'Encapsulation', 'estimated_minutes': 15},
                        ...
                    ]
                }
            }
        },
        'HLD': {...}
    }
    """
    structure = {
        'LLD': {},
        'HLD': {}
    }

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT week_type, week_num, topic,
                   id, title, estimated_minutes, order_num
            FROM lessons
            ORDER BY order_num
        """)

        for row in cursor.fetchall():
            week_type = row['week_type']
            week_num = row['week_num']
            topic = row['topic']

            # Initialize week if not exists
            if week_num not in structure[week_type]:
                structure[week_type][week_num] = {'topics': {}}

            # Initialize topic if not exists
            if topic not in structure[week_type][week_num]['topics']:
                structure[week_type][week_num]['topics'][topic] = []

            # Add lesson to topic
            structure[week_type][week_num]['topics'][topic].append({
                'id': row['id'],
                'title': row['title'],
                'estimated_minutes': row['estimated_minutes']
            })

    return structure


def print_statistics(db):
    """
    Print detailed statistics about the course content
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()

        print("\n" + "=" * 60)
        print("COURSE CONTENT STATISTICS")
        print("=" * 60 + "\n")

        # Overall statistics
        cursor.execute("""
            SELECT
                COUNT(*) as total_lessons,
                SUM(estimated_minutes) as total_minutes
            FROM lessons
        """)
        row = cursor.fetchone()
        total_lessons = row['total_lessons']
        total_minutes = row['total_minutes']
        total_hours = total_minutes // 60
        remaining_minutes = total_minutes % 60

        print(f"Total Lessons: {total_lessons}")
        print(f"Total Estimated Time: {total_hours}h {remaining_minutes}m ({total_minutes} minutes)")
        print()

        # By week type
        for week_type in ['LLD', 'HLD']:
            cursor.execute("""
                SELECT
                    COUNT(*) as count,
                    SUM(estimated_minutes) as minutes
                FROM lessons
                WHERE week_type = ?
            """, (week_type,))
            row = cursor.fetchone()
            count = row['count']
            minutes = row['minutes'] or 0
            hours = minutes // 60
            mins = minutes % 60

            print(f"{week_type}:")
            print(f"  Lessons: {count}")
            print(f"  Time: {hours}h {mins}m")

            # By week
            cursor.execute("""
                SELECT
                    week_num,
                    COUNT(*) as count,
                    SUM(estimated_minutes) as minutes
                FROM lessons
                WHERE week_type = ?
                GROUP BY week_num
                ORDER BY week_num
            """, (week_type,))

            for week_row in cursor.fetchall():
                week_num = week_row['week_num']
                week_count = week_row['count']
                week_minutes = week_row['minutes'] or 0
                week_hours = week_minutes // 60
                week_mins = week_minutes % 60
                print(f"    Week {week_num}: {week_count} lessons, {week_hours}h {week_mins}m")

            print()

        print("=" * 60 + "\n")


def main():
    """
    Main function to scan content and populate database
    """
    print("\n" + "=" * 60)
    print("LMS CONTENT PARSER")
    print("=" * 60 + "\n")

    # Initialize database
    print("Initializing database...")
    db = Database()

    # Clear existing lessons
    print("Clearing existing lessons...")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lessons")

    # Populate with fresh data
    lesson_count = populate_database(db)

    if lesson_count == 0:
        print("No lessons were imported. Exiting.")
        return

    # Generate structure
    print("Generating course structure...")
    structure = generate_course_structure(db)

    # Save to JSON file for caching
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(exist_ok=True)

    json_path = data_dir / 'course_structure.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2)

    print(f"Course structure saved to: {json_path}")

    # Print statistics
    print_statistics(db)

    print("Course content parsing completed successfully!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
