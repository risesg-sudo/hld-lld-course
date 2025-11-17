"""
Content parser for the LMS
Scans course directories and extracts lesson information
"""

import os
import re
from pathlib import Path
from database import init_database, clear_all_lessons, insert_lesson

COURSE_ROOT = os.path.dirname(os.path.dirname(__file__))
LLD_DIR = os.path.join(COURSE_ROOT, 'LLD')
HLD_DIR = os.path.join(COURSE_ROOT, 'HLD')

def extract_title_from_markdown(file_path):
    """Extract title from the first heading in markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for first # heading
            match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if match:
                return match.group(1).strip()
            # Fallback to filename
            return Path(file_path).stem.replace('_', ' ').replace('-', ' ').title()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return Path(file_path).stem.replace('_', ' ').replace('-', ' ').title()

def calculate_reading_time(file_path):
    """Calculate estimated reading time in minutes"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Count words (excluding code blocks for now)
            words = len(content.split())
            reading_minutes = words / 200  # 200 words per minute

            # Count code blocks (add 2 minutes per code block)
            code_blocks = len(re.findall(r'```', content))
            code_minutes = (code_blocks / 2) * 2  # Each pair of ``` is one block

            # Count images/diagrams (add 1 minute per image)
            images = len(re.findall(r'!\[.*?\]\(.*?\)', content))
            image_minutes = images * 1

            total_minutes = reading_minutes + code_minutes + image_minutes

            # Minimum 3 minutes, maximum capped at reasonable value
            return max(3, min(int(total_minutes), 60))
    except Exception as e:
        print(f"Error calculating time for {file_path}: {e}")
        return 5

def parse_week_number(path):
    """Extract week number from path"""
    # Look for weekN pattern
    match = re.search(r'week[_\-]?(\d+)', path.lower())
    if match:
        return int(match.group(1))

    # Look for wN pattern
    match = re.search(r'w(\d+)', path.lower())
    if match:
        return int(match.group(1))

    return 0

def get_topic_from_path(file_path, week_type):
    """Extract topic name from file path"""
    path = Path(file_path)

    # For structured content (e.g., LLD/week1/oop-fundamentals/encapsulation/concept.md)
    parts = path.parts

    # Find the week directory index
    week_idx = -1
    for i, part in enumerate(parts):
        if 'week' in part.lower():
            week_idx = i
            break

    if week_idx >= 0 and week_idx + 1 < len(parts):
        # Get the topic (directory after week)
        topic_parts = parts[week_idx + 1:-1]  # Exclude filename
        if topic_parts:
            return ' > '.join(part.replace('-', ' ').replace('_', ' ').title() for part in topic_parts)

    # Fallback: use parent directory name
    parent = path.parent.name
    return parent.replace('-', ' ').replace('_', ' ').title()

def scan_directory_structured(base_dir, week_type):
    """Scan a directory for structured markdown lessons"""
    lessons = []

    # Find all concept.md and dry_run.md files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.md') and file in ['concept.md', 'dry_run.md', 'overview.md',
                                                   'architecture.md', 'when-to-use.md',
                                                   'comparison.md', 'walkthrough.md',
                                                   'capacity-estimation.md', 'data-models.md',
                                                   'trade-offs.md']:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, COURSE_ROOT)

                week_num = parse_week_number(file_path)
                topic = get_topic_from_path(file_path, week_type)
                title = extract_title_from_markdown(file_path)
                estimated_minutes = calculate_reading_time(file_path)

                # Create a descriptive title
                file_type = file.replace('.md', '').replace('_', ' ').replace('-', ' ').title()
                full_title = f"{topic} - {file_type}"

                lessons.append({
                    'week_num': week_num,
                    'week_type': week_type,
                    'topic': topic,
                    'title': full_title,
                    'content_path': relative_path,
                    'video_url': '',
                    'estimated_minutes': estimated_minutes
                })

    return lessons

def scan_directory_legacy(base_dir, week_type):
    """Scan directory for legacy monolithic markdown files"""
    lessons = []

    # Pattern for main week files (e.g., week1_oop_principles_patterns.md)
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.startswith('week') and file.endswith('.md') and '_' in file:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, COURSE_ROOT)

                week_num = parse_week_number(file)
                title = extract_title_from_markdown(file_path)
                estimated_minutes = calculate_reading_time(file_path)

                lessons.append({
                    'week_num': week_num,
                    'week_type': week_type,
                    'topic': f'Week {week_num} Overview',
                    'title': title,
                    'content_path': relative_path,
                    'video_url': '',
                    'estimated_minutes': estimated_minutes
                })

    # Pattern for examples and additional content
    examples_dir = os.path.join(base_dir, 'examples')
    if os.path.exists(examples_dir):
        for root, dirs, files in os.walk(examples_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, COURSE_ROOT)

                    week_num = parse_week_number(file_path)
                    topic = get_topic_from_path(file_path, week_type)
                    title = extract_title_from_markdown(file_path)
                    estimated_minutes = calculate_reading_time(file_path)

                    lessons.append({
                        'week_num': week_num,
                        'week_type': week_type,
                        'topic': topic,
                        'title': title,
                        'content_path': relative_path,
                        'video_url': '',
                        'estimated_minutes': estimated_minutes
                    })

    return lessons

def parse_course_content():
    """Parse all course content and populate database"""
    print("Initializing database...")
    init_database()

    print("Clearing existing lessons...")
    clear_all_lessons()

    print("Scanning course content...")

    all_lessons = []

    # Scan LLD content
    print("Scanning LLD directory...")
    lld_lessons = scan_directory_structured(LLD_DIR, 'LLD')
    lld_lessons_legacy = scan_directory_legacy(LLD_DIR, 'LLD')
    all_lessons.extend(lld_lessons)
    all_lessons.extend(lld_lessons_legacy)

    # Scan HLD content
    print("Scanning HLD directory...")
    hld_lessons = scan_directory_structured(HLD_DIR, 'HLD')
    hld_lessons_legacy = scan_directory_legacy(HLD_DIR, 'HLD')
    all_lessons.extend(hld_lessons)
    all_lessons.extend(hld_lessons_legacy)

    # Sort lessons by week and topic
    all_lessons.sort(key=lambda x: (x['week_num'], x['week_type'], x['topic'], x['title']))

    # Assign order numbers
    for idx, lesson in enumerate(all_lessons, start=1):
        lesson['order_num'] = idx

    # Insert into database
    print(f"Inserting {len(all_lessons)} lessons into database...")
    for lesson in all_lessons:
        insert_lesson(lesson)

    print(f"✓ Successfully imported {len(all_lessons)} lessons!")
    print(f"  - LLD lessons: {len([l for l in all_lessons if l['week_type'] == 'LLD'])}")
    print(f"  - HLD lessons: {len([l for l in all_lessons if l['week_type'] == 'HLD'])}")

    # Calculate total time
    total_minutes = sum(l['estimated_minutes'] for l in all_lessons)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    print(f"  - Total estimated time: {hours}h {minutes}m")

if __name__ == '__main__':
    parse_course_content()
