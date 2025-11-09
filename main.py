"""
X.com Followers Tracker
Automatically tracks follower count daily and calculates growth metrics.
"""
import requests
import os
import time
from dotenv import load_dotenv
from storage import get_storage_backend

# Load environment variables
load_dotenv()

BEARER_TOKEN = os.getenv('X_BEARER_TOKEN')
USERNAME = os.getenv('X_USERNAME')


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

    # Initialize storage backend
    try:
        storage = get_storage_backend()
        storage.initialize()
    except Exception as e:
        print(f"✗ Storage initialization failed: {e}")
        return

    # Load last record
    last_count = storage.load_last_record()

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
    storage.save_record(current_count, delta, growth_rate)

    print("=" * 60)
    print("✓ Tracking completed successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()
