"""
Database models and schema definitions for the LMS
"""

# SQL schema for creating database tables
SCHEMA = """
-- Lessons table
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_num INTEGER NOT NULL,
    week_type TEXT NOT NULL,  -- 'LLD' or 'HLD'
    topic TEXT NOT NULL,
    title TEXT NOT NULL,
    content_path TEXT NOT NULL,
    video_url TEXT,
    estimated_minutes INTEGER NOT NULL DEFAULT 15,
    order_num INTEGER NOT NULL,
    UNIQUE(week_type, week_num, topic, title)
);

-- Progress tracking
CREATE TABLE IF NOT EXISTS progress (
    lesson_id INTEGER PRIMARY KEY,
    is_completed BOOLEAN DEFAULT 0,
    time_spent_seconds INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    last_accessed TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
);

-- User notes
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    UNIQUE(lesson_id)
);

-- Bookmarks
CREATE TABLE IF NOT EXISTS bookmarks (
    lesson_id INTEGER PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
);

-- Daily activity tracking
CREATE TABLE IF NOT EXISTS activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    lessons_completed INTEGER DEFAULT 0,
    time_spent_seconds INTEGER DEFAULT 0,
    UNIQUE(date)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_lessons_week ON lessons(week_type, week_num);
CREATE INDEX IF NOT EXISTS idx_lessons_order ON lessons(order_num);
CREATE INDEX IF NOT EXISTS idx_progress_completed ON progress(is_completed);
CREATE INDEX IF NOT EXISTS idx_activity_date ON activity(date DESC);
"""

# Initial indexes
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_lessons_week ON lessons(week_type, week_num)",
    "CREATE INDEX IF NOT EXISTS idx_lessons_order ON lessons(order_num)",
    "CREATE INDEX IF NOT EXISTS idx_progress_completed ON progress(is_completed)",
    "CREATE INDEX IF NOT EXISTS idx_activity_date ON activity(date DESC)",
]
