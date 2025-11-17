#!/usr/bin/env python3
"""
Update video URLs in the LMS database based on youtube_videos.json
Maps course topics to lessons and populates video_url field
"""

import json
import os
import sys
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path to import database module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database import get_db


class VideoUpdater:
    """Handles updating video URLs in the database"""

    def __init__(self, json_file_path: str):
        """
        Initialize the VideoUpdater

        Args:
            json_file_path: Path to youtube_videos.json
        """
        self.json_file_path = json_file_path
        self.videos_data = self._load_videos_json()
        self.stats = {
            'total_lessons': 0,
            'updated_lessons': 0,
            'skipped_lessons': 0,
            'failed_lessons': []
        }

    def _load_videos_json(self) -> Dict:
        """Load and parse the youtube_videos.json file"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: File not found: {self.json_file_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {self.json_file_path}: {e}")
            sys.exit(1)

    def _normalize_topic_name(self, topic: str) -> str:
        """
        Normalize topic name for matching with JSON keys
        Converts spaces to underscores and lowercases
        """
        return topic.lower().replace(' ', '_').replace('/', '_')

    def _find_primary_video(self, videos_list: List[Dict]) -> str:
        """
        Select the primary video URL from a list of videos
        Prefers videos from top-tier channels
        """
        if not videos_list:
            return ''

        # Channel priority
        channel_priority = {
            'ByteByteGo': 0,
            'Gaurav Sen': 1,
            'Hussein Nasser': 2,
            'freeCodeCamp': 3,
            'Programming with Mosh': 4,
            'ArjanCodes': 5,
            'Tech Dummies': 6,
            'System Design Interview': 7
        }

        # Sort by channel priority
        sorted_videos = sorted(
            videos_list,
            key=lambda v: channel_priority.get(v.get('channel', ''), 999)
        )

        return sorted_videos[0].get('url', '')

    def _get_video_url_for_topic(self, course_type: str, week_num: int, topic: str) -> str:
        """
        Get the primary video URL for a given course, week, and topic

        Args:
            course_type: 'LLD' or 'HLD'
            week_num: Week number (1-5)
            topic: Topic name

        Returns:
            Video URL or empty string if not found
        """
        try:
            # Normalize topic name for matching
            normalized_topic = self._normalize_topic_name(topic)

            # Navigate to the correct section
            if course_type not in self.videos_data:
                return ''

            week_key = f'week{week_num}'
            if week_key not in self.videos_data[course_type]:
                return ''

            topic_videos = self.videos_data[course_type][week_key].get(
                normalized_topic, []
            )

            if not topic_videos:
                return ''

            return self._find_primary_video(topic_videos)

        except (KeyError, TypeError, AttributeError):
            return ''

    def update_database(self, dry_run: bool = False) -> None:
        """
        Update all lessons in the database with video URLs

        Args:
            dry_run: If True, don't actually update the database
        """
        print("\n" + "=" * 70)
        print("VIDEO URL UPDATE PROCESS")
        print("=" * 70)

        with get_db() as conn:
            cursor = conn.cursor()

            # Get all lessons
            cursor.execute('''
                SELECT id, week_type, week_num, topic, title
                FROM lessons
                ORDER BY week_type, week_num, id
            ''')
            lessons = cursor.fetchall()

            self.stats['total_lessons'] = len(lessons)

            if self.stats['total_lessons'] == 0:
                print("\nNo lessons found in the database.")
                print("Run content_parser.py first to import lessons.")
                return

            print(f"\nFound {self.stats['total_lessons']} lessons to process...")
            print("-" * 70)

            for lesson in lessons:
                lesson_id = lesson['id']
                course_type = lesson['week_type']
                week_num = lesson['week_num']
                topic = lesson['topic']
                title = lesson['title']

                # Get video URL for this topic
                video_url = self._get_video_url_for_topic(
                    course_type, week_num, topic
                )

                if video_url:
                    status = "✓"
                    self.stats['updated_lessons'] += 1

                    # Update the database
                    if not dry_run:
                        try:
                            cursor.execute(
                                'UPDATE lessons SET video_url = ? WHERE id = ?',
                                (video_url, lesson_id)
                            )
                        except Exception as e:
                            status = "✗"
                            self.stats['failed_lessons'].append({
                                'lesson_id': lesson_id,
                                'topic': topic,
                                'error': str(e)
                            })
                else:
                    status = "○"
                    self.stats['skipped_lessons'] += 1

                print(f"{status} [{course_type} Week {week_num}] {topic}: {title}")

            # Commit changes
            if not dry_run and self.stats['updated_lessons'] > 0:
                conn.commit()
                print("\n" + "-" * 70)
                print("Changes committed to database.")
            elif dry_run:
                print("\n" + "-" * 70)
                print("DRY RUN - No changes were made to the database.")

    def print_statistics(self) -> None:
        """Print update statistics"""
        print("\n" + "=" * 70)
        print("UPDATE STATISTICS")
        print("=" * 70)
        print(f"Total lessons processed:    {self.stats['total_lessons']}")
        print(f"Lessons updated:            {self.stats['updated_lessons']}")
        print(f"Lessons skipped:            {self.stats['skipped_lessons']}")
        print(f"Lessons with errors:        {len(self.stats['failed_lessons'])}")

        if self.stats['failed_lessons']:
            print("\nFailed updates:")
            for failed in self.stats['failed_lessons']:
                print(f"  - Lesson {failed['lesson_id']} ({failed['topic']}): {failed['error']}")

        success_rate = (
            (self.stats['updated_lessons'] / self.stats['total_lessons'] * 100)
            if self.stats['total_lessons'] > 0
            else 0
        )
        print(f"\nSuccess rate: {success_rate:.1f}%")
        print("=" * 70 + "\n")

    def validate_json_structure(self) -> bool:
        """Validate the structure of youtube_videos.json"""
        print("\nValidating JSON structure...")

        required_courses = ['LLD', 'HLD']
        errors = []

        for course in required_courses:
            if course not in self.videos_data:
                errors.append(f"Missing course type: {course}")
                continue

            if not isinstance(self.videos_data[course], dict):
                errors.append(f"{course} should be a dictionary")
                continue

            for week_num in range(1, 6):
                week_key = f'week{week_num}'
                if week_key not in self.videos_data[course]:
                    errors.append(f"{course} missing {week_key}")

        if errors:
            print("ERROR: JSON structure validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False

        print("✓ JSON structure is valid")
        return True

    def print_available_topics(self) -> None:
        """Print all available topics by course and week"""
        print("\n" + "=" * 70)
        print("AVAILABLE TOPICS IN youtube_videos.json")
        print("=" * 70)

        for course_type in ['LLD', 'HLD']:
            if course_type not in self.videos_data:
                continue

            print(f"\n{course_type}:")
            print("-" * 70)

            for week_num in range(1, 6):
                week_key = f'week{week_num}'
                if week_key not in self.videos_data[course_type]:
                    continue

                topics = self.videos_data[course_type][week_key]
                if topics:
                    print(f"  Week {week_num}:")
                    for topic in topics.keys():
                        video_count = len(topics[topic])
                        print(f"    - {topic}: {video_count} video(s)")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Update video URLs in the LMS database'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without making changes'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Only validate the JSON structure'
    )
    parser.add_argument(
        '--list-topics',
        action='store_true',
        help='List all available topics in the JSON file'
    )
    parser.add_argument(
        '--json-file',
        default=os.path.join(os.path.dirname(__file__), 'youtube_videos.json'),
        help='Path to youtube_videos.json file'
    )

    args = parser.parse_args()

    # Create updater instance
    updater = VideoUpdater(args.json_file)

    # Validate JSON structure
    if not updater.validate_json_structure():
        sys.exit(1)

    # If only listing topics, do that and exit
    if args.list_topics:
        updater.print_available_topics()
        return

    # If only validating, exit after validation
    if args.validate:
        print("\nValidation passed! Ready to update videos.")
        return

    # Update the database
    updater.update_database(dry_run=args.dry_run)

    # Print statistics
    updater.print_statistics()

    if args.dry_run:
        print("\nTo apply these changes, run without the --dry-run flag:")
        print(f"  python update_videos.py --json-file {args.json_file}")


if __name__ == '__main__':
    main()
