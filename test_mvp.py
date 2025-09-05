#!/usr/bin/env python3
"""
Test script for the MVP functionality

This script tests the core components without requiring actual Telegram setup.
"""

import os
import sys
import sqlite3
import tempfile

def test_database():
    """Test database initialization and operations"""
    print("🧪 Testing database functionality...")

    # Use temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        test_db = tmp.name

    try:
        from server.database import init_database
        init_database(test_db)

        # Test database structure
        with sqlite3.connect(test_db) as conn:
            cursor = conn.cursor()

            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            required_tables = ['users', 'notifications', 'processes']
            for table in required_tables:
                if table in tables:
                    print(f"  ✅ Table '{table}' exists")
                else:
                    print(f"  ❌ Table '{table}' missing")
                    return False

        print("  ✅ Database test passed")
        return True

    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False

    finally:
        # Clean up
        if os.path.exists(test_db):
            os.unlink(test_db)

def test_client_library():
    """Test client library initialization"""
    print("🧪 Testing client library...")

    try:
        # Test import
        sys.path.insert(0, 'client')
        from experiment_bot import ExperimentBot

        # Test initialization with dummy key
        bot = ExperimentBot(api_key="test_key", api_url="http://localhost:8000")

        print("  ✅ Client library imports correctly")
        print("  ✅ ExperimentBot initializes with parameters")
        return True

    except Exception as e:
        print(f"  ❌ Client library test failed: {e}")
        return False

def test_api_server():
    """Test API server initialization"""
    print("🧪 Testing API server...")

    try:
        # Set dummy environment variable
        os.environ['TELEGRAM_BOT_TOKEN'] = 'dummy_token_for_testing'

        from server.api import app, APIServer

        # Test API server initialization
        api_server = APIServer()

        print("  ✅ API server imports correctly")
        print("  ✅ APIServer initializes")
        print("  ✅ FastAPI app created")
        return True

    except Exception as e:
        print(f"  ❌ API server test failed: {e}")
        return False

def test_bot():
    """Test Telegram bot initialization"""
    print("🧪 Testing Telegram bot...")

    try:
        # Set dummy environment variable
        os.environ['TELEGRAM_BOT_TOKEN'] = 'dummy_token_for_testing'

        from bot.telegram_bot import ExperimentBot as TelegramBot

        # Test bot initialization
        bot = TelegramBot()

        print("  ✅ Telegram bot imports correctly")
        print("  ✅ Bot initializes with token")
        return True

    except Exception as e:
        print(f"  ❌ Telegram bot test failed: {e}")
        return False

def test_project_structure():
    """Test project structure"""
    print("🧪 Testing project structure...")

    required_files = [
        'bot/telegram_bot.py',
        'server/api.py',
        'server/database.py',
        'client/experiment_bot/__init__.py',
        'client/setup.py',
        'start_bot.py',
        'start_server.py',
        'requirements.txt',
        '.env.example'
    ]

    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} missing")
            all_exist = False

    return all_exist

def main():
    print("🚀 ExperimentBot MVP Test Suite")
    print("=" * 50)

    tests = [
        ("Project Structure", test_project_structure),
        ("Database", test_database),
        ("Client Library", test_client_library),
        ("API Server", test_api_server),
        ("Telegram Bot", test_bot),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        result = test_func()
        results.append((test_name, result))

    print("\n" + "=" * 50)
    print("📊 Test Results:")

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! MVP is ready.")
        print("\nNext steps:")
        print("1. Get a Telegram bot token from @BotFather")
        print("2. Set TELEGRAM_BOT_TOKEN environment variable")
        print("3. Run: python start_bot.py")
        print("4. Run: python start_server.py")
        print("5. Message your bot with /start")
    else:
        print("❌ Some tests failed. Please fix the issues above.")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)