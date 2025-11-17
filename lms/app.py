"""
Flask backend for the Learning Management System
Provides RESTful API for course content and progress tracking
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
import os
import markdown
from database import (
    init_database, get_all_lessons, get_lesson, update_progress,
    get_progress_stats, toggle_bookmark, get_bookmarked_lessons,
    save_note, get_note, get_next_lesson, get_previous_lesson
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

COURSE_ROOT = os.path.dirname(os.path.dirname(__file__))

# Initialize database on startup
init_database()

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/course-structure')
def get_course_structure():
    """Get all lessons organized by week and topic"""
    try:
        lessons = get_all_lessons()

        # Organize by week
        structure = {}
        for lesson in lessons:
            week_key = f"{lesson['week_type']}_Week_{lesson['week_num']}"

            if week_key not in structure:
                structure[week_key] = {
                    'week_num': lesson['week_num'],
                    'week_type': lesson['week_type'],
                    'topics': {},
                    'lessons': []
                }

            # Add to topics
            topic = lesson['topic']
            if topic not in structure[week_key]['topics']:
                structure[week_key]['topics'][topic] = []

            structure[week_key]['topics'][topic].append({
                'id': lesson['id'],
                'title': lesson['title'],
                'estimated_minutes': lesson['estimated_minutes'],
                'is_completed': bool(lesson['is_completed']),
                'is_bookmarked': bool(lesson['is_bookmarked']),
                'time_spent_seconds': lesson['time_spent_seconds']
            })

            structure[week_key]['lessons'].append(lesson['id'])

        # Convert to list and sort
        weeks = []
        for week_key, week_data in structure.items():
            week_data['key'] = week_key
            weeks.append(week_data)

        weeks.sort(key=lambda x: (x['week_num'], x['week_type']))

        return jsonify({
            'success': True,
            'weeks': weeks
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lesson/<int:lesson_id>')
def get_lesson_content(lesson_id):
    """Get lesson content and metadata"""
    try:
        lessons = get_all_lessons()
        lesson = next((l for l in lessons if l['id'] == lesson_id), None)

        if not lesson:
            return jsonify({
                'success': False,
                'error': 'Lesson not found'
            }), 404

        # Read markdown content
        content_path = os.path.join(COURSE_ROOT, lesson['content_path'])
        with open(content_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Convert to HTML
        md = markdown.Markdown(extensions=['extra', 'codehilite', 'fenced_code', 'tables'])
        html_content = md.convert(markdown_content)

        # Get note
        note = get_note(lesson_id)

        # Get next and previous lessons
        next_lesson = get_next_lesson(lesson_id)
        prev_lesson = get_previous_lesson(lesson_id)

        # Update last accessed time
        update_progress(lesson_id)

        return jsonify({
            'success': True,
            'lesson': {
                'id': lesson['id'],
                'title': lesson['title'],
                'topic': lesson['topic'],
                'week_num': lesson['week_num'],
                'week_type': lesson['week_type'],
                'estimated_minutes': lesson['estimated_minutes'],
                'is_completed': bool(lesson['is_completed']),
                'is_bookmarked': bool(lesson['is_bookmarked']),
                'time_spent_seconds': lesson['time_spent_seconds'],
                'video_url': lesson['video_url'],
                'markdown_content': markdown_content,
                'html_content': html_content,
                'note': note,
                'next_lesson': next_lesson,
                'prev_lesson': prev_lesson
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lesson/<int:lesson_id>/complete', methods=['POST'])
def mark_complete(lesson_id):
    """Toggle lesson completion status"""
    try:
        data = request.get_json()
        is_completed = data.get('is_completed', True)

        update_progress(lesson_id, is_completed=is_completed)

        return jsonify({
            'success': True,
            'is_completed': is_completed
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lesson/<int:lesson_id>/time', methods=['POST'])
def update_time(lesson_id):
    """Update time spent on a lesson"""
    try:
        data = request.get_json()
        time_spent_seconds = data.get('time_spent_seconds', 0)

        update_progress(lesson_id, time_spent_seconds=time_spent_seconds)

        return jsonify({
            'success': True,
            'time_spent_seconds': time_spent_seconds
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/progress')
def get_progress():
    """Get overall progress statistics"""
    try:
        stats = get_progress_stats()

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bookmark/<int:lesson_id>', methods=['POST'])
def toggle_lesson_bookmark(lesson_id):
    """Toggle bookmark for a lesson"""
    try:
        is_bookmarked = toggle_bookmark(lesson_id)

        return jsonify({
            'success': True,
            'is_bookmarked': is_bookmarked
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bookmarks')
def get_bookmarks():
    """Get all bookmarked lessons"""
    try:
        bookmarks = get_bookmarked_lessons()

        return jsonify({
            'success': True,
            'bookmarks': bookmarks
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/notes/<int:lesson_id>', methods=['GET', 'POST'])
def handle_notes(lesson_id):
    """Get or save notes for a lesson"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            content = data.get('content', '')
            save_note(lesson_id, content)

            return jsonify({
                'success': True,
                'content': content
            })
        else:
            note = get_note(lesson_id)

            return jsonify({
                'success': True,
                'content': note
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search')
def search_lessons():
    """Search lessons by keyword"""
    try:
        query = request.args.get('q', '').lower()
        filter_status = request.args.get('status', 'all')  # all, completed, incomplete

        lessons = get_all_lessons()

        # Filter by completion status
        if filter_status == 'completed':
            lessons = [l for l in lessons if l['is_completed']]
        elif filter_status == 'incomplete':
            lessons = [l for l in lessons if not l['is_completed']]

        # Search in title and topic
        if query:
            lessons = [
                l for l in lessons
                if query in l['title'].lower() or query in l['topic'].lower()
            ]

        return jsonify({
            'success': True,
            'lessons': lessons,
            'count': len(lessons)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("System Design Course - Learning Management System")
    print("=" * 60)
    print("\nStarting Flask server...")
    print("Access the LMS at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
