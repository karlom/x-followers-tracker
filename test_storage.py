"""
Test script for storage backends
Tests both CSV and Sheets storage (mock mode for Sheets)
"""
import os
import sys
from storage import CSVStorage, get_storage_backend

# Test CSV Storage
def test_csv_storage():
    """Test CSV storage backend"""
    print("\n" + "=" * 60)
    print("Test: CSV Storage Backend")
    print("=" * 60)

    test_file = 'test_storage.csv'

    # Clean up if exists
    if os.path.exists(test_file):
        os.remove(test_file)

    # Initialize storage
    storage = CSVStorage(test_file)
    storage.initialize()

    # Test first run
    print("\n1. First run (no history):")
    last_count = storage.load_last_record()
    assert last_count == 0, f"Expected 0, got {last_count}"
    print(f"   ✓ Correct: {last_count}")

    # Save first record
    storage.save_record(1000, 1000, 0.0)

    # Test second run
    print("\n2. Second run (with history):")
    last_count = storage.load_last_record()
    assert last_count == 1000, f"Expected 1000, got {last_count}"
    print(f"   ✓ Correct: {last_count}")

    # Save second record
    storage.save_record(1050, 50, 5.0)

    # Test third run
    print("\n3. Third run (verify latest):")
    last_count = storage.load_last_record()
    assert last_count == 1050, f"Expected 1050, got {last_count}"
    print(f"   ✓ Correct: {last_count}")

    # Verify file contents
    with open(test_file, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"
        print(f"   ✓ File has correct number of records")

    # Cleanup
    os.remove(test_file)
    print("\n✓ CSV Storage test passed")
    return True


def test_storage_factory():
    """Test storage factory function"""
    print("\n" + "=" * 60)
    print("Test: Storage Factory Function")
    print("=" * 60)

    # Test CSV mode (default)
    print("\n1. Testing CSV mode (default):")
    os.environ.pop('STORAGE_TYPE', None)  # Remove if exists
    storage = get_storage_backend()
    assert isinstance(storage, CSVStorage), "Should return CSVStorage"
    print("   ✓ Returns CSVStorage instance")

    # Test CSV mode (explicit)
    print("\n2. Testing CSV mode (explicit):")
    os.environ['STORAGE_TYPE'] = 'csv'
    storage = get_storage_backend()
    assert isinstance(storage, CSVStorage), "Should return CSVStorage"
    print("   ✓ Returns CSVStorage instance")

    # Test Sheets mode (should fail without credentials)
    print("\n3. Testing Sheets mode (missing credentials):")
    os.environ['STORAGE_TYPE'] = 'sheets'
    try:
        storage = get_storage_backend()
        print("   ✗ Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"   ✓ Correctly raised ValueError: {str(e)[:50]}...")

    # Cleanup
    os.environ.pop('STORAGE_TYPE', None)
    print("\n✓ Storage factory test passed")
    return True


def run_all_tests():
    """Run all storage tests"""
    print("=" * 60)
    print("Storage Backend - Test Suite")
    print("=" * 60)

    tests = [
        test_csv_storage,
        test_storage_factory
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Passed: {passed}/{len(tests)}")
    print(f"  Failed: {failed}/{len(tests)}")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
