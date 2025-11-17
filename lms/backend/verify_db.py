"""Quick script to verify database content"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import get_db

with get_db() as db:
    cursor = db.cursor()
    cursor.execute("SELECT id, week_type, week_num, topic, title, estimated_minutes FROM lessons LIMIT 10")

    print("Sample lessons from database:\n")
    print(f"{'ID':<4} {'Type':<6} {'Week':<5} {'Topic':<30} {'Title':<40} {'Time':<5}")
    print("-" * 110)

    for row in cursor.fetchall():
        print(f"{row['id']:<4} {row['week_type']:<6} {row['week_num']:<5} {row['topic']:<30} {row['title']:<40} {row['estimated_minutes']:<5}")

    cursor.execute("SELECT COUNT(*) as total FROM lessons")
    total = cursor.fetchone()['total']
    print(f"\nTotal lessons in database: {total}")
