"""
Database operations for the LMS
"""
import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import os

from config import DB_PATH, COURSE_ROOT, CONTENT_PATHS, DEFAULT_LESSON_TIME, DAILY_STUDY_HOURS
from models import SCHEMA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Database manager for LMS operations"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database and tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        conn.executescript(SCHEMA)
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    # ==================== LESSON OPERATIONS ====================

    def get_all_lessons(self) -> List[Dict]:
        """Get all lessons with their progress"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    l.*,
                    COALESCE(p.is_completed, 0) as is_completed,
                    COALESCE(p.time_spent_seconds, 0) as time_spent_seconds,
                    COALESCE(p.last_accessed, NULL) as last_accessed,
                    EXISTS(SELECT 1 FROM bookmarks b WHERE b.lesson_id = l.id) as is_bookmarked
                FROM lessons l
                LEFT JOIN progress p ON l.id = p.lesson_id
                ORDER BY l.order_num
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_lesson_by_id(self, lesson_id: int) -> Optional[Dict]:
        """Get a specific lesson by ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    l.*,
                    COALESCE(p.is_completed, 0) as is_completed,
                    COALESCE(p.time_spent_seconds, 0) as time_spent_seconds,
                    p.started_at,
                    p.last_accessed,
                    p.completed_at,
                    EXISTS(SELECT 1 FROM bookmarks b WHERE b.lesson_id = l.id) as is_bookmarked,
                    (SELECT content FROM notes WHERE lesson_id = l.id) as notes
                FROM lessons l
                LEFT JOIN progress p ON l.id = p.lesson_id
                WHERE l.id = ?
            """, (lesson_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_lessons_by_week(self, week_type: str, week_num: int) -> List[Dict]:
        """Get all lessons for a specific week"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    l.*,
                    COALESCE(p.is_completed, 0) as is_completed,
                    COALESCE(p.time_spent_seconds, 0) as time_spent_seconds,
                    EXISTS(SELECT 1 FROM bookmarks b WHERE b.lesson_id = l.id) as is_bookmarked
                FROM lessons l
                LEFT JOIN progress p ON l.id = p.lesson_id
                WHERE l.week_type = ? AND l.week_num = ?
                ORDER BY l.order_num
            """, (week_type, week_num))
            return [dict(row) for row in cursor.fetchall()]

    def insert_lesson(self, week_num: int, week_type: str, topic: str, title: str,
                     content_path: str, video_url: Optional[str], estimated_minutes: int,
                     order_num: int) -> int:
        """Insert a new lesson"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO lessons
                (week_num, week_type, topic, title, content_path, video_url, estimated_minutes, order_num)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (week_num, week_type, topic, title, content_path, video_url, estimated_minutes, order_num))
            return cursor.lastrowid

    def clear_lessons(self):
        """Clear all lessons (for reseeding)"""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM lessons")
            logger.info("All lessons cleared")

    # ==================== PROGRESS OPERATIONS ====================

    def get_progress_stats(self) -> Dict:
        """Get overall progress statistics"""
        with self.get_connection() as conn:
            # Overall stats
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as total_lessons,
                    SUM(CASE WHEN p.is_completed = 1 THEN 1 ELSE 0 END) as completed_lessons,
                    SUM(l.estimated_minutes) as total_estimated_minutes,
                    SUM(COALESCE(p.time_spent_seconds, 0)) as total_time_spent_seconds
                FROM lessons l
                LEFT JOIN progress p ON l.id = p.lesson_id
            """)
            overall = dict(cursor.fetchone())

            # Calculate completion percentage
            total = overall['total_lessons']
            completed = overall['completed_lessons'] or 0
            overall['completion_percentage'] = round((completed / total * 100) if total > 0 else 0)

            # Calculate estimated completion date
            remaining_lessons = total - completed
            avg_minutes_per_lesson = DEFAULT_LESSON_TIME
            if total > 0:
                avg_minutes_per_lesson = overall['total_estimated_minutes'] / total

            remaining_minutes = remaining_lessons * avg_minutes_per_lesson
            daily_minutes = DAILY_STUDY_HOURS * 60
            days_needed = remaining_minutes / daily_minutes if daily_minutes > 0 else 0

            estimated_completion = date.today() + timedelta(days=int(days_needed))
            overall['estimated_completion_date'] = estimated_completion.isoformat()

            # Week-by-week stats
            cursor = conn.execute("""
                SELECT
                    l.week_type,
                    l.week_num,
                    COUNT(*) as total_lessons,
                    SUM(CASE WHEN p.is_completed = 1 THEN 1 ELSE 0 END) as completed
                FROM lessons l
                LEFT JOIN progress p ON l.id = p.lesson_id
                GROUP BY l.week_type, l.week_num
                ORDER BY l.week_type, l.week_num
            """)
            by_week = []
            for row in cursor.fetchall():
                week_data = dict(row)
                completed = week_data['completed'] or 0
                total = week_data['total_lessons']
                week_data['percentage'] = round((completed / total * 100) if total > 0 else 0)
                by_week.append(week_data)

            # Streak calculation
            streak = self._calculate_streak()

            return {
                'overall': overall,
                'by_week': by_week,
                'streak': streak
            }

    def _calculate_streak(self) -> Dict:
        """Calculate current and best study streak"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT date, lessons_completed
                FROM activity
                WHERE lessons_completed > 0
                ORDER BY date DESC
                LIMIT 90
            """)
            activity_data = cursor.fetchall()

            if not activity_data:
                return {'current_days': 0, 'best_days': 0}

            # Calculate current streak
            current_streak = 0
            today = date.today()

            for row in activity_data:
                activity_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                expected_date = today - timedelta(days=current_streak)

                if activity_date == expected_date:
                    current_streak += 1
                else:
                    break

            # Calculate best streak
            best_streak = 0
            temp_streak = 0
            prev_date = None

            for row in reversed(activity_data):
                activity_date = datetime.strptime(row['date'], '%Y-%m-%d').date()

                if prev_date is None or (prev_date - activity_date).days == 1:
                    temp_streak += 1
                    best_streak = max(best_streak, temp_streak)
                else:
                    temp_streak = 1

                prev_date = activity_date

            return {
                'current_days': current_streak,
                'best_days': best_streak
            }

    def toggle_lesson_completion(self, lesson_id: int) -> bool:
        """Toggle completion status of a lesson"""
        with self.get_connection() as conn:
            # Check current status
            cursor = conn.execute("""
                SELECT is_completed FROM progress WHERE lesson_id = ?
            """, (lesson_id,))
            row = cursor.fetchone()

            now = datetime.now().isoformat()

            if row is None:
                # Create new progress entry (mark as completed)
                conn.execute("""
                    INSERT INTO progress (lesson_id, is_completed, started_at, last_accessed, completed_at)
                    VALUES (?, 1, ?, ?, ?)
                """, (lesson_id, now, now, now))
                new_status = True
            else:
                # Toggle existing status
                new_status = not row['is_completed']
                completed_at = now if new_status else None
                conn.execute("""
                    UPDATE progress
                    SET is_completed = ?,
                        completed_at = ?,
                        last_accessed = ?
                    WHERE lesson_id = ?
                """, (new_status, completed_at, now, lesson_id))

            # Update daily activity if completed
            if new_status:
                self._update_activity(conn, lessons_completed=1)

            return new_status

    def update_lesson_time(self, lesson_id: int, seconds: int) -> bool:
        """Update time spent on a lesson"""
        with self.get_connection() as conn:
            now = datetime.now().isoformat()

            # Check if progress record exists
            cursor = conn.execute("""
                SELECT time_spent_seconds FROM progress WHERE lesson_id = ?
            """, (lesson_id,))
            row = cursor.fetchone()

            if row is None:
                # Create new progress entry
                conn.execute("""
                    INSERT INTO progress (lesson_id, time_spent_seconds, started_at, last_accessed)
                    VALUES (?, ?, ?, ?)
                """, (lesson_id, seconds, now, now))
            else:
                # Update existing entry
                new_time = row['time_spent_seconds'] + seconds
                conn.execute("""
                    UPDATE progress
                    SET time_spent_seconds = ?,
                        last_accessed = ?
                    WHERE lesson_id = ?
                """, (new_time, now, lesson_id))

            # Update daily activity
            self._update_activity(conn, time_spent_seconds=seconds)

            return True

    def _update_activity(self, conn, lessons_completed: int = 0, time_spent_seconds: int = 0):
        """Update today's activity record"""
        today = date.today().isoformat()

        cursor = conn.execute("""
            SELECT lessons_completed, time_spent_seconds
            FROM activity
            WHERE date = ?
        """, (today,))
        row = cursor.fetchone()

        if row is None:
            conn.execute("""
                INSERT INTO activity (date, lessons_completed, time_spent_seconds)
                VALUES (?, ?, ?)
            """, (today, lessons_completed, time_spent_seconds))
        else:
            new_lessons = row['lessons_completed'] + lessons_completed
            new_time = row['time_spent_seconds'] + time_spent_seconds
            conn.execute("""
                UPDATE activity
                SET lessons_completed = ?,
                    time_spent_seconds = ?
                WHERE date = ?
            """, (new_lessons, new_time, today))

    def get_recent_activity(self, days: int = 30) -> List[Dict]:
        """Get activity for the last N days"""
        with self.get_connection() as conn:
            start_date = (date.today() - timedelta(days=days)).isoformat()
            cursor = conn.execute("""
                SELECT * FROM activity
                WHERE date >= ?
                ORDER BY date DESC
            """, (start_date,))
            return [dict(row) for row in cursor.fetchall()]

    # ==================== NOTES OPERATIONS ====================

    def get_notes(self, lesson_id: int) -> Optional[Dict]:
        """Get notes for a specific lesson"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM notes WHERE lesson_id = ?
            """, (lesson_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def save_notes(self, lesson_id: int, content: str) -> bool:
        """Save or update notes for a lesson"""
        with self.get_connection() as conn:
            now = datetime.now().isoformat()

            cursor = conn.execute("""
                SELECT id FROM notes WHERE lesson_id = ?
            """, (lesson_id,))
            row = cursor.fetchone()

            if row is None:
                conn.execute("""
                    INSERT INTO notes (lesson_id, content, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (lesson_id, content, now, now))
            else:
                conn.execute("""
                    UPDATE notes
                    SET content = ?, updated_at = ?
                    WHERE lesson_id = ?
                """, (content, now, lesson_id))

            return True

    def delete_notes(self, lesson_id: int) -> bool:
        """Delete notes for a lesson"""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM notes WHERE lesson_id = ?", (lesson_id,))
            return True

    # ==================== BOOKMARK OPERATIONS ====================

    def get_bookmarks(self) -> List[Dict]:
        """Get all bookmarked lessons"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    l.*,
                    b.created_at as bookmarked_at,
                    COALESCE(p.is_completed, 0) as is_completed
                FROM bookmarks b
                JOIN lessons l ON b.lesson_id = l.id
                LEFT JOIN progress p ON l.id = p.lesson_id
                ORDER BY b.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def toggle_bookmark(self, lesson_id: int) -> bool:
        """Toggle bookmark status of a lesson"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT lesson_id FROM bookmarks WHERE lesson_id = ?
            """, (lesson_id,))
            row = cursor.fetchone()

            if row is None:
                # Add bookmark
                now = datetime.now().isoformat()
                conn.execute("""
                    INSERT INTO bookmarks (lesson_id, created_at)
                    VALUES (?, ?)
                """, (lesson_id, now))
                return True
            else:
                # Remove bookmark
                conn.execute("""
                    DELETE FROM bookmarks WHERE lesson_id = ?
                """, (lesson_id,))
                return False

    # ==================== COURSE STRUCTURE ====================

    def get_course_structure(self) -> Dict:
        """Get the full course structure organized by week and topic"""
        lessons = self.get_all_lessons()

        structure = {}

        for lesson in lessons:
            week_type = lesson['week_type']
            week_num = lesson['week_num']
            topic = lesson['topic']

            # Initialize week type if not exists
            if week_type not in structure:
                structure[week_type] = {}

            # Initialize week number if not exists
            if week_num not in structure[week_type]:
                structure[week_type][week_num] = {
                    'title': f'Week {week_num}',
                    'topics': {}
                }

            # Initialize topic if not exists
            if topic not in structure[week_type][week_num]['topics']:
                structure[week_type][week_num]['topics'][topic] = {
                    'name': topic,
                    'lessons': []
                }

            # Add lesson to topic
            lesson_data = {
                'id': lesson['id'],
                'title': lesson['title'],
                'estimated_minutes': lesson['estimated_minutes'],
                'is_completed': bool(lesson['is_completed']),
                'is_bookmarked': bool(lesson['is_bookmarked']),
                'video_url': lesson['video_url'],
                'time_spent_seconds': lesson['time_spent_seconds']
            }
            structure[week_type][week_num]['topics'][topic]['lessons'].append(lesson_data)

        # Convert topics dict to list
        for week_type in structure:
            for week_num in structure[week_type]:
                topics_dict = structure[week_type][week_num]['topics']
                structure[week_type][week_num]['topics'] = list(topics_dict.values())

        return structure

    def get_weeks_summary(self) -> Dict:
        """Get a summary of all weeks"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    week_type,
                    week_num,
                    COUNT(*) as total_lessons,
                    SUM(CASE WHEN p.is_completed = 1 THEN 1 ELSE 0 END) as completed_lessons,
                    SUM(estimated_minutes) as total_minutes
                FROM lessons l
                LEFT JOIN progress p ON l.id = p.lesson_id
                GROUP BY week_type, week_num
                ORDER BY week_type, week_num
            """)

            weeks = {}
            for row in cursor.fetchall():
                week_type = row['week_type']
                week_num = row['week_num']

                if week_type not in weeks:
                    weeks[week_type] = []

                completed = row['completed_lessons'] or 0
                total = row['total_lessons']

                weeks[week_type].append({
                    'week_num': week_num,
                    'total_lessons': total,
                    'completed_lessons': completed,
                    'completion_percentage': round((completed / total * 100) if total > 0 else 0),
                    'total_minutes': row['total_minutes']
                })

            return weeks


# Singleton instance
db = Database()
