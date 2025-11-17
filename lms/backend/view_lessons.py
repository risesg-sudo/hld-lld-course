"""
Quick script to view lessons in the database
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db

def main():
    print("\n" + "=" * 80)
    print("LESSONS DATABASE OVERVIEW")
    print("=" * 80)

    # Get all lessons
    lessons = db.get_all_lessons()

    print(f"\nTotal Lessons: {len(lessons)}\n")

    # Group by week type and week number
    by_week = {}
    for lesson in lessons:
        key = (lesson['week_type'], lesson['week_num'])
        if key not in by_week:
            by_week[key] = []
        by_week[key].append(lesson)

    # Display grouped lessons
    for (week_type, week_num), lessons_list in sorted(by_week.items()):
        print(f"\n{week_type} - Week {week_num} ({len(lessons_list)} lessons)")
        print("-" * 80)

        # Group by topic
        by_topic = {}
        for lesson in lessons_list:
            topic = lesson['topic']
            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(lesson)

        for topic, topic_lessons in sorted(by_topic.items()):
            print(f"\n  Topic: {topic}")
            for lesson in topic_lessons:
                print(f"    - {lesson['title']} ({lesson['estimated_minutes']} min)")

    # Show progress stats
    print("\n" + "=" * 80)
    print("PROGRESS STATISTICS")
    print("=" * 80)

    stats = db.get_progress_stats()
    overall = stats['overall']

    print(f"\nTotal Lessons: {overall['total_lessons']}")
    print(f"Completed: {overall['completed_lessons'] or 0}")
    print(f"Completion: {overall['completion_percentage']}%")
    print(f"Total Estimated Time: {overall['total_estimated_minutes']} minutes")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
