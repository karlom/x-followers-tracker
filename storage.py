"""
Storage backends for followers data.
Supports CSV (local file), Google Sheets (online), and Notion (database).
"""
import csv
import os
import datetime
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def initialize(self):
        """Initialize storage (create file/sheet if needed)."""
        pass

    @abstractmethod
    def load_last_record(self):
        """
        Load the last recorded followers count.

        Returns:
            int: Last followers count, or 0 if no history
        """
        pass

    @abstractmethod
    def save_record(self, current_count, delta, growth_rate):
        """
        Save a new record.

        Args:
            current_count (int): Current followers count
            delta (int): Change from previous count
            growth_rate (float): Growth percentage
        """
        pass


class CSVStorage(StorageBackend):
    """CSV file storage backend."""

    def __init__(self, file_path='followers_log.csv'):
        """
        Initialize CSV storage.

        Args:
            file_path (str): Path to CSV file
        """
        self.file_path = file_path

    def initialize(self):
        """Create CSV file with header if it doesn't exist."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['date', 'followers_count', 'delta', 'rate'])
            print(f"✓ Created new CSV file: {self.file_path}")

    def load_last_record(self):
        """Load last record from CSV file."""
        try:
            with open(self.file_path, 'r') as f:
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

    def save_record(self, current_count, delta, growth_rate):
        """Append record to CSV file."""
        today = datetime.date.today().isoformat()
        with open(self.file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([today, current_count, delta, f"{growth_rate:.2f}%"])
        print(f"✓ Saved record: {today}, {current_count} followers, Δ{delta:+d} ({growth_rate:+.2f}%)")


class SheetsStorage(StorageBackend):
    """Google Sheets storage backend."""

    def __init__(self, spreadsheet_id, credentials_json):
        """
        Initialize Google Sheets storage.

        Args:
            spreadsheet_id (str): Google Sheets ID
            credentials_json (str): Service account credentials (JSON string)
        """
        self.spreadsheet_id = spreadsheet_id
        self.credentials_json = credentials_json
        self.worksheet = None
        self._connect()

    def _connect(self):
        """Connect to Google Sheets."""
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            import json

            # Parse credentials
            creds_dict = json.loads(self.credentials_json)
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)

            # Connect to spreadsheet
            client = gspread.authorize(credentials)
            spreadsheet = client.open_by_key(self.spreadsheet_id)
            self.worksheet = spreadsheet.sheet1  # Use first sheet

            print(f"✓ Connected to Google Sheets: {spreadsheet.title}")

        except ImportError:
            raise ImportError(
                "Google Sheets support requires: pip install gspread google-auth"
            )
        except Exception as e:
            raise Exception(f"Failed to connect to Google Sheets: {e}")

    def initialize(self):
        """Initialize Google Sheets with header if empty."""
        if not self.worksheet:
            raise Exception("Not connected to Google Sheets")

        # Check if sheet is empty
        values = self.worksheet.get_all_values()
        if not values or len(values) == 0:
            # Add header
            self.worksheet.append_row(['date', 'followers_count', 'delta', 'rate'])
            print("✓ Initialized Google Sheets with header")
        elif values[0] != ['date', 'followers_count', 'delta', 'rate']:
            # Verify header
            print("⚠ Warning: Sheet header doesn't match expected format")

    def load_last_record(self):
        """Load last record from Google Sheets."""
        if not self.worksheet:
            raise Exception("Not connected to Google Sheets")

        values = self.worksheet.get_all_values()
        if len(values) > 1:  # Has data beyond header
            last_row = values[-1]
            last_count = int(last_row[1])
            print(f"✓ Loaded last record: {last_count} followers on {last_row[0]}")
            return last_count
        else:
            print("ℹ No historical data found (first run)")
            return 0

    def save_record(self, current_count, delta, growth_rate):
        """Append record to Google Sheets."""
        if not self.worksheet:
            raise Exception("Not connected to Google Sheets")

        today = datetime.date.today().isoformat()
        row = [today, current_count, delta, f"{growth_rate:.2f}%"]
        self.worksheet.append_row(row)
        print(f"✓ Saved record to Sheets: {today}, {current_count} followers, Δ{delta:+d} ({growth_rate:+.2f}%)")


class NotionStorage(StorageBackend):
    """Notion database storage backend."""

    def __init__(self, token, database_id):
        """
        Initialize Notion storage.

        Args:
            token (str): Notion Integration Token
            database_id (str): Notion Database ID
        """
        self.token = token.strip() if token else token
        self.database_id = database_id.strip() if database_id else database_id
        self.client = None
        self._connect()

    def _connect(self):
        """Connect to Notion API."""
        try:
            from notion_client import Client

            self.client = Client(auth=self.token)

            # Test connection by retrieving database info
            database = self.client.databases.retrieve(database_id=self.database_id)
            print(f"✓ Connected to Notion Database: {database.get('title', [{}])[0].get('plain_text', 'Untitled')}")

        except ImportError:
            raise ImportError(
                "Notion support requires: pip install notion-client"
            )
        except Exception as e:
            raise Exception(f"Failed to connect to Notion: {e}")

    def initialize(self):
        """Verify Notion database connection."""
        if not self.client:
            raise Exception("Not connected to Notion")

        try:
            # Verify database exists and is accessible
            database = self.client.databases.retrieve(database_id=self.database_id)
            print("✓ Notion database connection verified")

        except Exception as e:
            raise Exception(f"Failed to verify Notion database: {e}")

    def load_last_record(self):
        """Load last record from Notion database (excluding today's records)."""
        if not self.client:
            raise Exception("Not connected to Notion")

        try:
            # Get today's date to exclude today's records
            today = datetime.date.today().isoformat()
            print(f"🔍 Debug: Today's date = {today}")

            # Use search API to find all pages
            # Note: In newer Notion API, we use search instead of database query
            response = self.client.search(
                filter={
                    "property": "object",
                    "value": "page"
                },
                sort={
                    "direction": "descending",
                    "timestamp": "last_edited_time"
                },
                page_size=100  # Get more pages to filter by database
            )

            results = response.get('results', [])
            print(f"🔍 Debug: Search returned {len(results)} total pages")

            # Filter pages that belong to our database and have Date property
            database_pages = []
            for page in results:
                # Check if page belongs to our database
                parent = page.get('parent', {})
                parent_type = parent.get('type')
                # In Notion API 2025, type changed from 'database_id' to 'data_source_id'
                if parent_type in ['database_id', 'data_source_id']:
                    parent_db_id = parent.get('database_id') or parent.get('data_source_id')
                    if parent_db_id == self.database_id:
                        database_pages.append(page)

            print(f"🔍 Debug: Found {len(database_pages)} pages in our database")
            print(f"🔍 Debug: Expected database_id = {self.database_id}")
            print(f"🔍 Debug: Expected ID length = {len(self.database_id)}, repr = {repr(self.database_id)}")

            # Debug: Show what we're actually getting
            if len(results) > 0 and len(database_pages) == 0:
                print("🔍 Debug: No matches found. Checking first few pages:")
                for i, page in enumerate(results[:3]):
                    parent = page.get('parent', {})
                    parent_type = parent.get('type')
                    parent_db_id = parent.get('database_id') or parent.get('data_source_id')
                    print(f"  Page {i+1}: type={parent_type}, id={parent_db_id}")
                    if parent_db_id:
                        print(f"          length={len(parent_db_id)}, repr={repr(parent_db_id)}")
                        print(f"          Match: {parent_db_id == self.database_id}")

            if not database_pages:
                print("ℹ No historical data found in Notion (first run)")
                return 0

            # Sort pages by Date property and filter out today's records
            dated_pages = []
            for page in database_pages:
                properties = page.get('properties', {})
                date_property = properties.get('Date', {})
                date_obj = date_property.get('date', {})
                if date_obj and date_obj.get('start'):
                    record_date = date_obj.get('start')
                    print(f"🔍 Debug: Found record with date {record_date}")
                    # Only include records from before today
                    if record_date < today:
                        dated_pages.append((page, record_date))
                        print(f"  ✓ Included (before today)")
                    else:
                        print(f"  ✗ Excluded (today or future)")

            print(f"🔍 Debug: After filtering, {len(dated_pages)} records from before today")

            if not dated_pages:
                print("ℹ No historical data found in Notion (first run)")
                return 0

            # Sort by date descending and get the latest (most recent date before today)
            dated_pages.sort(key=lambda x: x[1], reverse=True)
            latest_page, latest_date = dated_pages[0]

            # Extract followers count
            properties = latest_page.get('properties', {})
            followers_property = properties.get('Followers Count', {})
            last_count = followers_property.get('number', 0)

            print(f"✓ Loaded last record from Notion: {last_count} followers on {latest_date}")
            return last_count

        except Exception as e:
            print(f"⚠ Error loading last record from Notion: {e}")
            return 0

    def save_record(self, current_count, delta, growth_rate):
        """Create new page in Notion database."""
        if not self.client:
            raise Exception("Not connected to Notion")

        today = datetime.date.today().isoformat()

        try:
            # Create new page with properties
            self.client.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "Date": {
                        "date": {
                            "start": today
                        }
                    },
                    "Followers Count": {
                        "number": current_count
                    },
                    "Delta": {
                        "number": delta
                    },
                    "Rate": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": f"{growth_rate:.2f}%"
                                }
                            }
                        ]
                    }
                }
            )

            print(f"✓ Saved record to Notion: {today}, {current_count} followers, Δ{delta:+d} ({growth_rate:+.2f}%)")

        except Exception as e:
            raise Exception(f"Failed to save record to Notion: {e}")


def get_storage_backend():
    """
    Factory function to get appropriate storage backend based on environment.

    Returns:
        StorageBackend: Configured storage backend instance
    """
    storage_type = os.getenv('STORAGE_TYPE', 'csv').lower()

    if storage_type == 'notion':
        token = os.getenv('NOTION_TOKEN')
        database_id = os.getenv('NOTION_DATABASE_ID')

        if not token or not database_id:
            raise ValueError(
                "Notion mode requires NOTION_TOKEN and NOTION_DATABASE_ID "
                "environment variables"
            )

        print("📝 Using Notion storage")
        return NotionStorage(token, database_id)

    elif storage_type == 'sheets':
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        credentials_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')

        if not spreadsheet_id or not credentials_json:
            raise ValueError(
                "Google Sheets mode requires GOOGLE_SHEETS_ID and "
                "GOOGLE_SERVICE_ACCOUNT_JSON environment variables"
            )

        print("📊 Using Google Sheets storage")
        return SheetsStorage(spreadsheet_id, credentials_json)
    else:
        csv_file_path = os.getenv('CSV_FILE_PATH', 'followers_log.csv')
        print(f"📁 Using CSV storage: {csv_file_path}")
        return CSVStorage(csv_file_path)
