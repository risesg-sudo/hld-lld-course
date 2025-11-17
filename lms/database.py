"""
Database management for the LMS
Handles SQLite operations, schema creation, and queries
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lms.db')

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize the database with required tables"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    with get_db() as conn:
        cursor = conn.cursor()

        # Lessons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_num INTEGER NOT NULL,
                week_type TEXT NOT NULL,
                topic TEXT NOT NULL,
                title TEXT NOT NULL,
                content_path TEXT NOT NULL,
                video_url TEXT,
                estimated_minutes INTEGER DEFAULT 5,
                order_num INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Progress tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                lesson_id INTEGER PRIMARY KEY,
                is_completed BOOLEAN DEFAULT 0,
                time_spent_seconds INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lessons(id)
            )
        ''')

        # Notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_id INTEGER NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lessons(id)
            )
        ''')

        # Bookmarks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                lesson_id INTEGER PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lessons(id)
            )
        ''')

        # Learning goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_goals (
                id INTEGER PRIMARY KEY,
                daily_minutes_goal INTEGER DEFAULT 30,
                weekly_lessons_goal INTEGER DEFAULT 10
            )
        ''')

        # Initialize learning goals if not exists
        cursor.execute('SELECT COUNT(*) as count FROM learning_goals')
        if cursor.fetchone()['count'] == 0:
            cursor.execute('INSERT INTO learning_goals (id, daily_minutes_goal, weekly_lessons_goal) VALUES (1, 30, 10)')

def insert_lesson(lesson_data):
    """Insert a new lesson into the database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO lessons (week_num, week_type, topic, title, content_path, video_url, estimated_minutes, order_num)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lesson_data['week_num'],
            lesson_data['week_type'],
            lesson_data['topic'],
            lesson_data['title'],
            lesson_data['content_path'],
            lesson_data.get('video_url', ''),
            lesson_data['estimated_minutes'],
            lesson_data['order_num']
        ))
        return cursor.lastrowid

def get_all_lessons():
    """Get all lessons with progress information"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                l.*,
                COALESCE(p.is_completed, 0) as is_completed,
                COALESCE(p.time_spent_seconds, 0) as time_spent_seconds,
                p.last_accessed,
                p.completed_at,
                CASE WHEN b.lesson_id IS NOT NULL THEN 1 ELSE 0 END as is_bookmarked
            FROM lessons l
            LEFT JOIN progress p ON l.id = p.lesson_id
            LEFT JOIN bookmarks b ON l.id = b.lesson_id
            ORDER BY l.order_num
        ''')
        return [dict(row) for row in cursor.fetchall()]

def get_lesson(lesson_id):
    """Get a specific lesson with all related data"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                l.*,
                COALESCE(p.is_completed, 0) as is_completed,
                COALESCE(p.time_spent_seconds, 0) as time_spent_seconds,
                p.last_accessed,
                p.completed_at,
                CASE WHEN b.lesson_id IS NOT NULL THEN 1 ELSE 0 END as is_bookmarked,
                n.content as note_content
            FROM lessons l
            LEFT JOIN progress p ON l.id = p.lesson_id
            LEFT JOIN bookmarks b ON l.id = b.lesson_id
            LEFT JOIN notes n ON l.id = n.lesson_id
            WHERE l.id = ?
        ''', (lesson_id,))
        return dict(cursor.fetchone()) if cursor.fetchone() else None

def update_progress(lesson_id, is_completed=None, time_spent_seconds=None):
    """Update progress for a lesson"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Check if progress record exists
        cursor.execute('SELECT lesson_id FROM progress WHERE lesson_id = ?', (lesson_id,))
        exists = cursor.fetchone()

        now = datetime.now().isoformat()

        if exists:
            updates = ['last_accessed = ?']
            params = [now]

            if is_completed is not None:
                updates.append('is_completed = ?')
                params.append(1 if is_completed else 0)
                if is_completed:
                    updates.append('completed_at = ?')
                    params.append(now)
                else:
                    updates.append('completed_at = NULL')

            if time_spent_seconds is not None:
                updates.append('time_spent_seconds = time_spent_seconds + ?')
                params.append(time_spent_seconds)

            params.append(lesson_id)
            cursor.execute(f'UPDATE progress SET {", ".join(updates)} WHERE lesson_id = ?', params)
        else:
            cursor.execute('''
                INSERT INTO progress (lesson_id, is_completed, time_spent_seconds, last_accessed, completed_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                lesson_id,
                1 if is_completed else 0,
                time_spent_seconds or 0,
                now,
                now if is_completed else None
            ))

def get_progress_stats():
    """Get overall progress statistics"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Total lessons
        cursor.execute('SELECT COUNT(*) as total FROM lessons')
        total_lessons = cursor.fetchone()['total']

        # Completed lessons
        cursor.execute('SELECT COUNT(*) as completed FROM progress WHERE is_completed = 1')
        completed_lessons = cursor.fetchone()['completed']

        # Total estimated time
        cursor.execute('SELECT SUM(estimated_minutes) as total_time FROM lessons')
        total_estimated_minutes = cursor.fetchone()['total_time'] or 0

        # Time spent
        cursor.execute('SELECT SUM(time_spent_seconds) as total_time FROM progress')
        total_time_spent_seconds = cursor.fetchone()['total_time'] or 0

        # Completed estimated time
        cursor.execute('''
            SELECT SUM(l.estimated_minutes) as completed_time
            FROM lessons l
            JOIN progress p ON l.id = p.lesson_id
            WHERE p.is_completed = 1
        ''')
        completed_estimated_minutes = cursor.fetchone()['completed_time'] or 0

        # Progress by week
        cursor.execute('''
            SELECT
                l.week_type,
                l.week_num,
                COUNT(*) as total,
                SUM(CASE WHEN p.is_completed = 1 THEN 1 ELSE 0 END) as completed
            FROM lessons l
            LEFT JOIN progress p ON l.id = p.lesson_id
            GROUP BY l.week_type, l.week_num
            ORDER BY l.week_num
        ''')
        week_progress = [dict(row) for row in cursor.fetchall()]

        # Last accessed lesson
        cursor.execute('''
            SELECT l.id, l.title, p.last_accessed
            FROM lessons l
            JOIN progress p ON l.id = p.lesson_id
            WHERE p.last_accessed IS NOT NULL
            ORDER BY p.last_accessed DESC
            LIMIT 1
        ''')
        last_accessed = cursor.fetchone()
        last_accessed = dict(last_accessed) if last_accessed else None

        # Streak calculation (consecutive days with completed lessons)
        cursor.execute('''
            SELECT DISTINCT DATE(completed_at) as completion_date
            FROM progress
            WHERE completed_at IS NOT NULL
            ORDER BY completion_date DESC
        ''')
        completion_dates = [row['completion_date'] for row in cursor.fetchall()]

        streak = 0
        if completion_dates:
            from datetime import date, timedelta
            today = date.today()
            current_date = today

            for completion_date_str in completion_dates:
                completion_date = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
                if completion_date == current_date or (current_date - completion_date).days == 1:
                    streak += 1
                    current_date = completion_date
                else:
                    break

        return {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'completion_percentage': round((completed_lessons / total_lessons * 100) if total_lessons > 0 else 0, 1),
            'total_estimated_minutes': total_estimated_minutes,
            'total_time_spent_seconds': total_time_spent_seconds,
            'completed_estimated_minutes': completed_estimated_minutes,
            'remaining_estimated_minutes': total_estimated_minutes - completed_estimated_minutes,
            'week_progress': week_progress,
            'last_accessed': last_accessed,
            'streak_days': streak
        }

def toggle_bookmark(lesson_id):
    """Toggle bookmark for a lesson"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT lesson_id FROM bookmarks WHERE lesson_id = ?', (lesson_id,))
        exists = cursor.fetchone()

        if exists:
            cursor.execute('DELETE FROM bookmarks WHERE lesson_id = ?', (lesson_id,))
            return False
        else:
            cursor.execute('INSERT INTO bookmarks (lesson_id, created_at) VALUES (?, ?)',
                         (lesson_id, datetime.now().isoformat()))
            return True

def get_bookmarked_lessons():
    """Get all bookmarked lessons"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, b.created_at as bookmarked_at
            FROM lessons l
            JOIN bookmarks b ON l.id = b.lesson_id
            ORDER BY b.created_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

def save_note(lesson_id, content):
    """Save or update a note for a lesson"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM notes WHERE lesson_id = ?', (lesson_id,))
        exists = cursor.fetchone()

        now = datetime.now().isoformat()

        if exists:
            cursor.execute('UPDATE notes SET content = ?, updated_at = ? WHERE lesson_id = ?',
                         (content, now, lesson_id))
        else:
            cursor.execute('INSERT INTO notes (lesson_id, content, created_at, updated_at) VALUES (?, ?, ?, ?)',
                         (lesson_id, content, now, now))

def get_note(lesson_id):
    """Get note for a specific lesson"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT content FROM notes WHERE lesson_id = ?', (lesson_id,))
        result = cursor.fetchone()
        return result['content'] if result else ''

def clear_all_lessons():
    """Clear all lessons from the database (for re-import)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM lessons')

def get_next_lesson(current_lesson_id):
    """Get the next lesson in the sequence"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT order_num FROM lessons WHERE id = ?', (current_lesson_id,))
        current = cursor.fetchone()
        if not current:
            return None

        cursor.execute('''
            SELECT id, title FROM lessons
            WHERE order_num > ?
            ORDER BY order_num
            LIMIT 1
        ''', (current['order_num'],))
        result = cursor.fetchone()
        return dict(result) if result else None

def get_previous_lesson(current_lesson_id):
    """Get the previous lesson in the sequence"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT order_num FROM lessons WHERE id = ?', (current_lesson_id,))
        current = cursor.fetchone()
        if not current:
            return None

        cursor.execute('''
            SELECT id, title FROM lessons
            WHERE order_num < ?
            ORDER BY order_num DESC
            LIMIT 1
        ''', (current['order_num'],))
        result = cursor.fetchone()
        return dict(result) if result else None
