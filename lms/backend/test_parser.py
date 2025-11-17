"""
Quick test script to verify content parser output
"""
from database import Database

db = Database()

# Get sample lessons
lessons = db.get_all_lessons()

print(f"\n{'='*80}")
print("DATABASE VERIFICATION")
print(f"{'='*80}\n")

print(f"Total lessons in database: {len(lessons)}\n")

print(f"{'ID':<4} {'Type':<6} {'Week':<5} {'Topic':<35} {'Title':<35} {'Time':<5}")
print("-" * 110)

# Show first 15 lessons
for lesson in lessons[:15]:
    topic_short = lesson['topic'][:32] + '...' if len(lesson['topic']) > 32 else lesson['topic']
    title_short = lesson['title'][:32] + '...' if len(lesson['title']) > 32 else lesson['title']
    print(f"{lesson['id']:<4} {lesson['week_type']:<6} {lesson['week_num']:<5} {topic_short:<35} {title_short:<35} {lesson['estimated_minutes']:<5}")

if len(lessons) > 15:
    print(f"... and {len(lessons) - 15} more lessons\n")

# Test getting a specific lesson
lesson_1 = db.get_lesson_by_id(1)
if lesson_1:
    print(f"\nSample Lesson Details (ID: 1):")
    print(f"  Title: {lesson_1['title']}")
    print(f"  Week: {lesson_1['week_type']} Week {lesson_1['week_num']}")
    print(f"  Topic: {lesson_1['topic']}")
    print(f"  Content Path: {lesson_1['content_path']}")
    print(f"  Estimated Time: {lesson_1['estimated_minutes']} minutes")
    print(f"  Video URL: {lesson_1['video_url'] or 'Not set'}")

print(f"\n{'='*80}\n")
