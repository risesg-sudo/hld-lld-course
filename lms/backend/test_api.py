"""
Quick test script to verify API functionality
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        import config
        print("  ✓ config.py imported successfully")

        import models
        print("  ✓ models.py imported successfully")

        import database
        print("  ✓ database.py imported successfully")

        import seed_content
        print("  ✓ seed_content.py imported successfully")

        from app import app
        print("  ✓ app.py imported successfully")

        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    try:
        from database import db

        # Test connection
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

        expected_tables = ['lessons', 'progress', 'notes', 'bookmarks', 'activity']
        for table in expected_tables:
            if table in tables:
                print(f"  ✓ Table '{table}' exists")
            else:
                print(f"  ✗ Table '{table}' missing")
                return False

        return True
    except Exception as e:
        print(f"  ✗ Database test failed: {e}")
        return False


def test_seeding():
    """Test content seeding"""
    print("\nTesting content seeding...")
    try:
        from seed_content import seed_database
        from database import db

        # Seed database
        seed_database()

        # Check if lessons were created
        lessons = db.get_all_lessons()
        print(f"  ✓ Seeded {len(lessons)} lessons")

        if lessons:
            lesson = lessons[0]
            print(f"  ✓ Sample lesson: {lesson['title']} ({lesson['week_type']} Week {lesson['week_num']})")

        return len(lessons) > 0
    except Exception as e:
        print(f"  ✗ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_routes():
    """Test that API routes are defined"""
    print("\nTesting API routes...")
    try:
        from app import app

        # Get all routes
        routes = [str(rule) for rule in app.url_map.iter_rules()]

        expected_routes = [
            '/api/health',
            '/api/course-structure',
            '/api/weeks',
            '/api/progress',
            '/api/bookmarks'
        ]

        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"  ✓ Route '{route}' defined")
            else:
                print(f"  ✗ Route '{route}' missing")
                return False

        print(f"  ✓ Total routes defined: {len(routes)}")
        return True
    except Exception as e:
        print(f"  ✗ Route test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("LMS Backend API Test Suite")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Content Seeding", test_seeding),
        ("API Routes", test_api_routes)
    ]

    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED! ✓")
        print("The API is ready to run with: python app.py")
    else:
        print("SOME TESTS FAILED! ✗")
        print("Please check the errors above.")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
