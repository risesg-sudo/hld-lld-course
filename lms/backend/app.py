"""
Flask Backend API for the LMS
Main application with REST API endpoints
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from pathlib import Path
import logging
from datetime import datetime

from config import PORT, DEBUG, HOST, CORS_ORIGINS, COURSE_ROOT
from database import db
from seed_content import seed_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=CORS_ORIGINS)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {error}", exc_info=True)
    return jsonify({
        'error': 'Server Error',
        'message': str(error)
    }), 500


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


# ==================== COURSE STRUCTURE ====================

@app.route('/api/course-structure', methods=['GET'])
def get_course_structure():
    """Get the complete course structure with progress"""
    try:
        structure = db.get_course_structure()
        return jsonify(structure)
    except Exception as e:
        logger.error(f"Error getting course structure: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/weeks', methods=['GET'])
def get_weeks():
    """Get summary of all weeks"""
    try:
        weeks = db.get_weeks_summary()
        return jsonify(weeks)
    except Exception as e:
        logger.error(f"Error getting weeks summary: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/week/<week_type>/<int:week_num>', methods=['GET'])
def get_week(week_type, week_num):
    """Get details for a specific week"""
    try:
        if week_type not in ['LLD', 'HLD']:
            return jsonify({'error': 'Invalid week type. Must be LLD or HLD'}), 400

        lessons = db.get_lessons_by_week(week_type, week_num)

        if not lessons:
            return jsonify({'error': f'Week {week_num} not found for {week_type}'}), 404

        # Organize by topic
        topics = {}
        for lesson in lessons:
            topic = lesson['topic']
            if topic not in topics:
                topics[topic] = {
                    'name': topic,
                    'lessons': []
                }

            topics[topic]['lessons'].append({
                'id': lesson['id'],
                'title': lesson['title'],
                'estimated_minutes': lesson['estimated_minutes'],
                'is_completed': bool(lesson['is_completed']),
                'is_bookmarked': bool(lesson['is_bookmarked']),
                'video_url': lesson['video_url'],
                'time_spent_seconds': lesson['time_spent_seconds']
            })

        return jsonify({
            'week_type': week_type,
            'week_num': week_num,
            'topics': list(topics.values())
        })
    except Exception as e:
        logger.error(f"Error getting week {week_type}/{week_num}: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== LESSONS ====================

@app.route('/api/lesson/<int:lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    """Get lesson metadata and details"""
    try:
        lesson = db.get_lesson_by_id(lesson_id)

        if not lesson:
            return jsonify({'error': f'Lesson {lesson_id} not found'}), 404

        return jsonify(lesson)
    except Exception as e:
        logger.error(f"Error getting lesson {lesson_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/lesson/<int:lesson_id>/content', methods=['GET'])
def get_lesson_content(lesson_id):
    """Get the markdown content for a lesson"""
    try:
        lesson = db.get_lesson_by_id(lesson_id)

        if not lesson:
            return jsonify({'error': f'Lesson {lesson_id} not found'}), 404

        content_path = COURSE_ROOT / lesson['content_path']

        if not content_path.exists():
            logger.error(f"Content file not found: {content_path}")
            return jsonify({'error': 'Content file not found'}), 404

        # Read and return the markdown content
        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return jsonify({
                'lesson_id': lesson_id,
                'title': lesson['title'],
                'content': content,
                'content_path': lesson['content_path']
            })
        except Exception as e:
            logger.error(f"Error reading content file {content_path}: {e}")
            return jsonify({'error': 'Error reading content file'}), 500

    except Exception as e:
        logger.error(f"Error getting lesson content {lesson_id}: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== PROGRESS ====================

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Get overall progress statistics"""
    try:
        stats = db.get_progress_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting progress stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress/weekly', methods=['GET'])
def get_weekly_progress():
    """Get week-by-week progress"""
    try:
        stats = db.get_progress_stats()
        return jsonify(stats['by_week'])
    except Exception as e:
        logger.error(f"Error getting weekly progress: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/lesson/<int:lesson_id>/complete', methods=['POST'])
def toggle_lesson_completion(lesson_id):
    """Toggle lesson completion status"""
    try:
        # Verify lesson exists
        lesson = db.get_lesson_by_id(lesson_id)
        if not lesson:
            return jsonify({'error': f'Lesson {lesson_id} not found'}), 404

        # Toggle completion
        new_status = db.toggle_lesson_completion(lesson_id)

        return jsonify({
            'lesson_id': lesson_id,
            'is_completed': new_status,
            'message': f'Lesson marked as {"completed" if new_status else "incomplete"}'
        })
    except Exception as e:
        logger.error(f"Error toggling lesson completion {lesson_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/lesson/<int:lesson_id>/time', methods=['POST'])
def update_lesson_time(lesson_id):
    """Update time spent on a lesson"""
    try:
        # Verify lesson exists
        lesson = db.get_lesson_by_id(lesson_id)
        if not lesson:
            return jsonify({'error': f'Lesson {lesson_id} not found'}), 404

        # Get seconds from request
        data = request.get_json()
        if not data or 'seconds' not in data:
            return jsonify({'error': 'Missing "seconds" in request body'}), 400

        seconds = data['seconds']
        if not isinstance(seconds, (int, float)) or seconds < 0:
            return jsonify({'error': 'Invalid seconds value. Must be a positive number'}), 400

        # Update time
        db.update_lesson_time(lesson_id, int(seconds))

        return jsonify({
            'lesson_id': lesson_id,
            'seconds_added': int(seconds),
            'message': 'Time updated successfully'
        })
    except Exception as e:
        logger.error(f"Error updating lesson time {lesson_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/activity/recent', methods=['GET'])
def get_recent_activity():
    """Get recent activity (last 30 days)"""
    try:
        days = request.args.get('days', 30, type=int)
        activity = db.get_recent_activity(days)
        return jsonify(activity)
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== NOTES ====================

@app.route('/api/notes/<int:lesson_id>', methods=['GET'])
def get_notes(lesson_id):
    """Get notes for a lesson"""
    try:
        notes = db.get_notes(lesson_id)
        if notes:
            return jsonify(notes)
        else:
            return jsonify({
                'lesson_id': lesson_id,
                'content': '',
                'message': 'No notes found'
            })
    except Exception as e:
        logger.error(f"Error getting notes for lesson {lesson_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes/<int:lesson_id>', methods=['POST'])
def save_notes(lesson_id):
    """Save or update notes for a lesson"""
    try:
        # Verify lesson exists
        lesson = db.get_lesson_by_id(lesson_id)
        if not lesson:
            return jsonify({'error': f'Lesson {lesson_id} not found'}), 404

        # Get content from request
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Missing "content" in request body'}), 400

        content = data['content']

        # Save notes
        db.save_notes(lesson_id, content)

        return jsonify({
            'lesson_id': lesson_id,
            'message': 'Notes saved successfully'
        })
    except Exception as e:
        logger.error(f"Error saving notes for lesson {lesson_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes/<int:lesson_id>', methods=['DELETE'])
def delete_notes(lesson_id):
    """Delete notes for a lesson"""
    try:
        db.delete_notes(lesson_id)
        return jsonify({
            'lesson_id': lesson_id,
            'message': 'Notes deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting notes for lesson {lesson_id}: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== BOOKMARKS ====================

@app.route('/api/bookmarks', methods=['GET'])
def get_bookmarks():
    """Get all bookmarked lessons"""
    try:
        bookmarks = db.get_bookmarks()
        return jsonify(bookmarks)
    except Exception as e:
        logger.error(f"Error getting bookmarks: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/bookmark/<int:lesson_id>', methods=['POST'])
def toggle_bookmark(lesson_id):
    """Toggle bookmark status for a lesson"""
    try:
        # Verify lesson exists
        lesson = db.get_lesson_by_id(lesson_id)
        if not lesson:
            return jsonify({'error': f'Lesson {lesson_id} not found'}), 404

        # Toggle bookmark
        is_bookmarked = db.toggle_bookmark(lesson_id)

        return jsonify({
            'lesson_id': lesson_id,
            'is_bookmarked': is_bookmarked,
            'message': f'Lesson {"bookmarked" if is_bookmarked else "unbookmarked"}'
        })
    except Exception as e:
        logger.error(f"Error toggling bookmark for lesson {lesson_id}: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== ADMIN / UTILITY ====================

@app.route('/api/admin/reseed', methods=['POST'])
def reseed_database():
    """Reseed the database with content (admin only)"""
    try:
        logger.info("Reseeding database...")
        seed_database()
        return jsonify({
            'message': 'Database reseeded successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error reseeding database: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== INITIALIZATION ====================

def initialize_app():
    """Initialize the application on first run"""
    logger.info("Initializing LMS Backend API...")

    # Check if database has any lessons
    try:
        lessons = db.get_all_lessons()
        if not lessons:
            logger.info("No lessons found. Seeding database...")
            seed_database()
            logger.info("Database seeded successfully")
        else:
            logger.info(f"Database already has {len(lessons)} lessons")
    except Exception as e:
        logger.error(f"Error during initialization: {e}")


# ==================== MAIN ====================

if __name__ == '__main__':
    # Initialize on startup
    initialize_app()

    # Start server
    logger.info(f"Starting Flask server on {HOST}:{PORT}")
    logger.info(f"CORS enabled for: {CORS_ORIGINS}")
    logger.info(f"Course root: {COURSE_ROOT}")

    app.run(host=HOST, port=PORT, debug=DEBUG)
