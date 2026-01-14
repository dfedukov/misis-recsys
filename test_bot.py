#!/usr/bin/env python3
"""
Test script to validate the FAQ bot functionality
"""

import json
import sys
from pathlib import Path

def test_json_structure():
    """Test FAQ JSON structure"""
    print("=" * 60)
    print("TEST 1: FAQ JSON Structure")
    print("=" * 60)

    faq_path = Path("faq.json")
    if not faq_path.exists():
        print("❌ FAIL: faq.json not found!")
        return False

    try:
        with open(faq_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "dataset" not in data:
            print("❌ FAIL: 'dataset' key not found in JSON")
            return False

        dataset = data["dataset"]
        print(f"✅ PASS: Found {len(dataset)} FAQ entries")

        # Validate structure of first entry
        required_fields = ["id", "block", "subblock", "question", "answer", "tags"]
        if dataset:
            first_item = dataset[0]
            missing = [f for f in required_fields if f not in first_item]
            if missing:
                print(f"❌ FAIL: Missing fields in FAQ items: {missing}")
                return False
            print(f"✅ PASS: All required fields present")

        # Check for unique IDs
        ids = [item["id"] for item in dataset]
        if len(ids) != len(set(ids)):
            print("⚠️  WARNING: Duplicate IDs found in dataset")
        else:
            print("✅ PASS: All IDs are unique")

        # Check blocks
        blocks = set(item["block"] for item in dataset)
        print(f"✅ INFO: Found {len(blocks)} unique blocks:")
        for block in sorted(blocks):
            count = sum(1 for item in dataset if item["block"] == block)
            print(f"   - {block}: {count} questions")

        return True

    except json.JSONDecodeError as e:
        print(f"❌ FAIL: Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Error reading JSON: {e}")
        return False


def test_config():
    """Test configuration"""
    print("\n" + "=" * 60)
    print("TEST 2: Configuration")
    print("=" * 60)

    try:
        import config

        if not config.BOT_TOKEN:
            print("⚠️  WARNING: BOT_TOKEN not set (required for running bot)")
        else:
            print("✅ PASS: BOT_TOKEN is configured")

        print(f"✅ INFO: FAQ_JSON_PATH = {config.FAQ_JSON_PATH}")
        print(f"✅ INFO: FAQ_INDEX_PATH = {config.FAQ_INDEX_PATH}")

        # Check if FAQ file exists at configured path
        faq_path = Path(config.FAQ_JSON_PATH)
        if not faq_path.exists():
            print(f"❌ FAIL: FAQ file not found at {config.FAQ_JSON_PATH}")
            print(f"   Current file location: faq.json")
            return False

        return True

    except ImportError as e:
        print(f"❌ FAIL: Cannot import config: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Config error: {e}")
        return False


def test_embeddings_db():
    """Test embeddings database functionality"""
    print("\n" + "=" * 60)
    print("TEST 3: Embeddings Database")
    print("=" * 60)

    try:
        from faq_embeddings_db import FAQEmbeddingsDB, FAQItem

        print("✅ PASS: Successfully imported FAQEmbeddingsDB")

        # Test with direct path
        db = FAQEmbeddingsDB("faq.json")
        print(f"✅ PASS: Database initialized with {len(db.items)} items")

        # Test methods
        blocks = db.get_blocks()
        print(f"✅ PASS: get_blocks() returned {len(blocks)} blocks")

        questions = db.get_all_questions()
        print(f"✅ PASS: get_all_questions() returned {len(questions)} questions")

        # Test search without building index
        try:
            db.search("test query", top_k=1)
            print("⚠️  WARNING: search() should fail before build_index()")
        except RuntimeError:
            print("✅ PASS: search() correctly fails before index is built")

        return True

    except ImportError as e:
        print(f"❌ FAIL: Cannot import faq_embeddings_db: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Embeddings DB error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """Test required dependencies"""
    print("\n" + "=" * 60)
    print("TEST 4: Dependencies")
    print("=" * 60)

    required = [
        ("aiogram", "Telegram bot framework"),
        ("sentence_transformers", "Text embeddings"),
        ("faiss", "Vector search"),
        ("numpy", "Numerical operations"),
        ("dotenv", "Environment variables")
    ]

    all_ok = True
    for module, description in required:
        try:
            __import__(module)
            print(f"✅ PASS: {module:25s} - {description}")
        except ImportError:
            print(f"❌ FAIL: {module:25s} - {description} (not installed)")
            all_ok = False

    return all_ok


def test_path_issues():
    """Test for common path configuration issues"""
    print("\n" + "=" * 60)
    print("TEST 5: Path Configuration Issues")
    print("=" * 60)

    issues = []

    # Check if data directory exists
    data_dir = Path("data")
    if not data_dir.exists():
        issues.append("❌ ISSUE: 'data/' directory does not exist")
        print(issues[-1])
        print("   SOLUTION: The bot will create this directory, but FAQ file needs to be in correct location")
    else:
        print("✅ OK: 'data/' directory exists")

    # Check FAQ file location
    import config
    expected_faq = Path(config.FAQ_JSON_PATH)
    actual_faq = Path("faq.json")

    if not expected_faq.exists() and actual_faq.exists():
        issues.append(f"❌ ISSUE: FAQ file is at {actual_faq} but config expects {expected_faq}")
        print(issues[-1])
        print(f"   SOLUTION: Move faq.json to {expected_faq} or update config.py")
    elif expected_faq.exists():
        print(f"✅ OK: FAQ file found at expected location: {expected_faq}")

    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        issues.append("❌ ISSUE: .env file not found")
        print(issues[-1])
        print("   SOLUTION: Create .env file with: BOT_TOKEN=your_telegram_bot_token")
    else:
        print("✅ OK: .env file exists")

    return len(issues) == 0


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "MISIS FAQ BOT - VALIDATION TEST" + " " * 16 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    results = {
        "JSON Structure": test_json_structure(),
        "Configuration": test_config(),
        "Embeddings DB": test_embeddings_db(),
        "Dependencies": test_dependencies(),
        "Path Issues": test_path_issues()
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Ensure BOT_TOKEN is set in .env file")
        print("2. Run: python build_index.py")
        print("3. Run: python bot.py")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nPlease fix the issues above before running the bot.")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
