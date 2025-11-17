"""
Content seeder - scans course directories and populates the database
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import logging

from config import COURSE_ROOT, CONTENT_PATHS, DEFAULT_LESSON_TIME
from database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentSeeder:
    """Scans course content and seeds the database"""

    def __init__(self):
        self.order_counter = 0

    def seed_all(self):
        """Scan and seed all course content"""
        logger.info("Starting content seeding...")

        # Clear existing lessons
        db.clear_lessons()

        # Seed LLD content
        self._seed_course_type('LLD')

        # Seed HLD content
        self._seed_course_type('HLD')

        logger.info(f"Content seeding complete. Total lessons: {self.order_counter}")

    def _seed_course_type(self, course_type: str):
        """Seed content for a specific course type (LLD or HLD)"""
        base_path = CONTENT_PATHS[course_type]

        if not base_path.exists():
            logger.warning(f"Course path not found: {base_path}")
            return

        # Find all week directories
        week_dirs = sorted([d for d in base_path.iterdir() if d.is_dir() and d.name.startswith('week')])

        for week_dir in week_dirs:
            week_num = self._extract_week_number(week_dir.name)
            if week_num is not None:
                self._seed_week(course_type, week_num, week_dir)

    def _extract_week_number(self, dirname: str) -> int:
        """Extract week number from directory name"""
        match = re.search(r'week(\d+)', dirname)
        return int(match.group(1)) if match else None

    def _seed_week(self, course_type: str, week_num: int, week_dir: Path):
        """Seed content for a specific week"""
        logger.info(f"Seeding {course_type} Week {week_num} from {week_dir}")

        # Get all subdirectories (topics)
        topic_dirs = sorted([d for d in week_dir.iterdir() if d.is_dir()])

        for topic_dir in topic_dirs:
            topic_name = self._format_topic_name(topic_dir.name)
            self._seed_topic(course_type, week_num, topic_name, topic_dir)

    def _format_topic_name(self, dirname: str) -> str:
        """Format topic name from directory name"""
        # Convert kebab-case or snake_case to Title Case
        name = dirname.replace('-', ' ').replace('_', ' ')
        return ' '.join(word.capitalize() for word in name.split())

    def _seed_topic(self, course_type: str, week_num: int, topic_name: str, topic_dir: Path):
        """Seed lessons for a specific topic"""
        # Get all markdown files in the topic directory
        md_files = sorted(topic_dir.glob('*.md'))

        for md_file in md_files:
            # Skip README files
            if md_file.name.upper() == 'README.MD':
                continue

            lesson_title = self._format_lesson_title(md_file.stem)
            content_path = str(md_file.relative_to(COURSE_ROOT))

            # Estimate reading time based on file size
            estimated_minutes = self._estimate_reading_time(md_file)

            # Insert lesson
            self.order_counter += 1
            lesson_id = db.insert_lesson(
                week_num=week_num,
                week_type=course_type,
                topic=topic_name,
                title=lesson_title,
                content_path=content_path,
                video_url=None,  # Can be added later
                estimated_minutes=estimated_minutes,
                order_num=self.order_counter
            )

            logger.info(f"  Added: {lesson_title} (ID: {lesson_id})")

    def _format_lesson_title(self, filename: str) -> str:
        """Format lesson title from filename"""
        # Convert snake_case or kebab-case to Title Case
        title = filename.replace('_', ' ').replace('-', ' ')
        return ' '.join(word.capitalize() for word in title.split())

    def _estimate_reading_time(self, file_path: Path) -> int:
        """Estimate reading time based on file content"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Count words (average reading speed: 200-250 words per minute)
            words = len(content.split())
            minutes = max(5, int(words / 200))  # Minimum 5 minutes

            # Add time for code blocks (assume they take longer to read)
            code_blocks = content.count('```')
            minutes += code_blocks * 2  # 2 minutes per code block

            return min(minutes, 60)  # Cap at 60 minutes
        except Exception as e:
            logger.warning(f"Error estimating reading time for {file_path}: {e}")
            return DEFAULT_LESSON_TIME


def seed_database():
    """Main function to seed the database"""
    seeder = ContentSeeder()
    seeder.seed_all()


if __name__ == '__main__':
    seed_database()
