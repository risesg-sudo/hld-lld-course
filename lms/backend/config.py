"""
Configuration settings for the LMS Flask API
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
COURSE_ROOT = Path('/home/user/hld-lld-course')
DATA_DIR = BASE_DIR / 'data'

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Database
DB_PATH = str(DATA_DIR / 'lms.db')

# Flask settings
PORT = 5000
DEBUG = True
HOST = '0.0.0.0'

# CORS settings
CORS_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# Course structure
COURSE_TYPES = ['LLD', 'HLD']

# Default time estimates (in minutes)
DEFAULT_LESSON_TIME = 15

# Activity tracking
ACTIVITY_RETENTION_DAYS = 90  # Keep activity data for 90 days
RECENT_ACTIVITY_DAYS = 30     # Show last 30 days in dashboard

# Estimated study hours per day for completion date calculation
DAILY_STUDY_HOURS = 2

# Video URL templates (if videos are added later)
VIDEO_BASE_URL = 'https://youtube.com/watch?v='

# Content paths relative to COURSE_ROOT
CONTENT_PATHS = {
    'LLD': COURSE_ROOT / 'LLD',
    'HLD': COURSE_ROOT / 'HLD',
}
