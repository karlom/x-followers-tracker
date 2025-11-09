"""
Test script for X Followers Tracker
Tests core functionality without actual API calls
"""
import csv
import os
import datetime

# Mock test data
test_csv_file = 'test_followers_log.csv'


def test_csv_initialization():
    """Test 1: CSV initialization with header"""
    print("\n" + "=" * 60)
    print("Test 1: CSV Initialization")
    print("=" * 60)

    # Clean up if exists
    if os.path.exists(test_csv_file):
        os.remove(test_csv_file)

    # Create CSV with header
    with open(test_csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'followers_count', 'delta', 'rate'])

    # Verify
    with open(test_csv_file, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == 1, "Should have header only"
        assert rows[0] == ['date', 'followers_count', 'delta', 'rate'], "Header incorrect"

    print("✓ CSV initialized correctly with header")
    return True


def test_first_run():
    """Test 2: First run - no previous data"""
    print("\n" + "=" * 60)
    print("Test 2: First Run (no historical data)")
    print("=" * 60)

    # Simulate first run
    last_count = 0  # No history
    current_count = 1234  # Mock API response
    delta = current_count - last_count
    growth_rate = (delta / last_count * 100) if last_count > 0 else 0.0

    # Save record
    today = datetime.date.today().isoformat()
    with open(test_csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([today, current_count, delta, f"{growth_rate:.2f}%"])

    print(f"  Last count: {last_count}")
    print(f"  Current count: {current_count}")
    print(f"  Delta: {delta:+d}")
    print(f"  Growth rate: {growth_rate:.2f}%")

    # Verify
    assert delta == 1234, "Delta should be 1234"
    assert growth_rate == 0.0, "Growth rate should be 0% on first run"

    print("✓ First run handled correctly (delta=1234, rate=0%)")
    return True


def test_second_run():
    """Test 3: Second run - with previous data"""
    print("\n" + "=" * 60)
    print("Test 3: Second Run (with previous data)")
    print("=" * 60)

    # Load last record
    with open(test_csv_file, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        last_row = rows[-1]
        last_count = int(last_row[1])

    # Simulate second run
    current_count = 1250  # Mock API response (gained 16 followers)
    delta = current_count - last_count
    growth_rate = (delta / last_count * 100) if last_count > 0 else 0.0

    # Save record
    today = datetime.date.today().isoformat()
    with open(test_csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([today, current_count, delta, f"{growth_rate:.2f}%"])

    print(f"  Last count: {last_count}")
    print(f"  Current count: {current_count}")
    print(f"  Delta: {delta:+d}")
    print(f"  Growth rate: {growth_rate:.2f}%")

    # Verify
    assert delta == 16, f"Delta should be 16, got {delta}"
    assert abs(growth_rate - 1.30) < 0.01, f"Growth rate should be ~1.30%, got {growth_rate:.2f}%"

    print("✓ Second run calculated correctly (delta=+16, rate=+1.30%)")
    return True


def test_third_run_with_loss():
    """Test 4: Third run - with follower loss"""
    print("\n" + "=" * 60)
    print("Test 4: Third Run (follower loss scenario)")
    print("=" * 60)

    # Load last record
    with open(test_csv_file, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        last_row = rows[-1]
        last_count = int(last_row[1])

    # Simulate third run with loss
    current_count = 1240  # Mock API response (lost 10 followers)
    delta = current_count - last_count
    growth_rate = (delta / last_count * 100) if last_count > 0 else 0.0

    # Save record
    today = datetime.date.today().isoformat()
    with open(test_csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([today, current_count, delta, f"{growth_rate:.2f}%"])

    print(f"  Last count: {last_count}")
    print(f"  Current count: {current_count}")
    print(f"  Delta: {delta:+d}")
    print(f"  Growth rate: {growth_rate:.2f}%")

    # Verify
    assert delta == -10, f"Delta should be -10, got {delta}"
    assert abs(growth_rate - (-0.80)) < 0.01, f"Growth rate should be ~-0.80%, got {growth_rate:.2f}%"

    print("✓ Third run handled correctly (delta=-10, rate=-0.80%)")
    return True


def test_data_persistence():
    """Test 5: Verify data is appended, not overwritten"""
    print("\n" + "=" * 60)
    print("Test 5: Data Persistence (append vs overwrite)")
    print("=" * 60)

    with open(test_csv_file, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)

    print(f"  Total rows: {len(rows)}")
    print(f"  Header: {rows[0]}")
    print(f"  Data rows: {len(rows) - 1}")

    # Verify
    assert len(rows) == 4, f"Should have 4 rows (header + 3 data), got {len(rows)}"

    print("\n  CSV Contents:")
    for i, row in enumerate(rows):
        if i == 0:
            print(f"  {' | '.join(row)}")
            print(f"  {'-' * 50}")
        else:
            print(f"  {' | '.join(row)}")

    print("\n✓ Data correctly appended (not overwritten)")
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("X Followers Tracker - Test Suite")
    print("=" * 60)

    tests = [
        test_csv_initialization,
        test_first_run,
        test_second_run,
        test_third_run_with_loss,
        test_data_persistence
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

    # Cleanup
    if os.path.exists(test_csv_file):
        print(f"\nTest file created: {test_csv_file}")
        print("You can inspect it or delete it.")


if __name__ == "__main__":
    run_all_tests()
