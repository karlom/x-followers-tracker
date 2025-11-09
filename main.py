"""
X.com Followers Tracker
Automatically tracks follower count daily and calculates growth metrics.
"""
import requests
import datetime
import csv
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BEARER_TOKEN = os.getenv('X_BEARER_TOKEN')
USERNAME = os.getenv('X_USERNAME')
CSV_FILE = os.getenv('CSV_FILE_PATH', 'followers_log.csv')


def get_followers_count():
    """
    Fetch current followers count from X API.

    Returns:
        int: Current followers count

    Raises:
        Exception: If API call fails after retry
    """
    url = f"https://api.twitter.com/2/users/by/username/{USERNAME}?user.fields=public_metrics"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

    # Retry logic: try up to 2 times
    for attempt in range(2):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                followers_count = data['data']['public_metrics']['followers_count']
                print(f"✓ Successfully fetched followers count: {followers_count}")
                return followers_count
            else:
                print(f"✗ API error (attempt {attempt + 1}/2): {response.status_code} - {response.text}")
                if attempt == 0:
                    time.sleep(2)  # Wait before retry
        except requests.exceptions.RequestException as e:
            print(f"✗ Request exception (attempt {attempt + 1}/2): {e}")
            if attempt == 0:
                time.sleep(2)

    raise Exception("Failed to fetch followers count after 2 attempts")


def initialize_csv():
    """
    Initialize CSV file with header if it doesn't exist.
    """
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'followers_count', 'delta', 'rate'])
        print(f"✓ Created new CSV file: {CSV_FILE}")


def load_last_record():
    """
    Load the last recorded followers count from CSV.

    Returns:
        int: Last followers count, or 0 if no history exists
    """
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) > 1:  # Has data beyond header
                last_row = rows[-1]
                last_count = int(last_row[1])
                print(f"✓ Loaded last record: {last_count} followers on {last_row[0]}")
                return last_count
            else:
                print("ℹ No historical data found (first run)")
                return 0
    except FileNotFoundError:
        print("ℹ No CSV file found (first run)")
        return 0


def save_record(current_count, delta, growth_rate):
    """
    Append new record to CSV file.

    Args:
        current_count (int): Current followers count
        delta (int): Change from previous count
        growth_rate (float): Growth percentage
    """
    today = datetime.date.today().isoformat()
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([today, current_count, delta, f"{growth_rate:.2f}%"])
    print(f"✓ Saved record: {today}, {current_count} followers, Δ{delta:+d} ({growth_rate:+.2f}%)")


def main():
    """
    Main execution logic.
    """
    print("=" * 60)
    print("X Followers Tracker - Starting")
    print("=" * 60)

    # Validate environment variables
    if not BEARER_TOKEN or not USERNAME:
        print("✗ Error: Missing required environment variables")
        print("  Please set X_BEARER_TOKEN and X_USERNAME")
        return

    # Initialize CSV if needed
    initialize_csv()

    # Load last record
    last_count = load_last_record()

    # Fetch current count
    try:
        current_count = get_followers_count()
    except Exception as e:
        print(f"✗ Failed to fetch followers count: {e}")
        return

    # Calculate growth
    delta = current_count - last_count
    growth_rate = (delta / last_count * 100) if last_count > 0 else 0.0

    # Save record
    save_record(current_count, delta, growth_rate)

    print("=" * 60)
    print("✓ Tracking completed successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()
