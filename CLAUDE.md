# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

X Followers Tracker - An automated tool that tracks X.com (formerly Twitter) follower counts daily using GitHub Actions and the X API. The tool calculates daily growth (delta and percentage) and stores data in CSV or Google Sheets.

**Key Goals:**
- Zero-cost deployment using GitHub Actions free tier
- Daily automated execution at fixed time (UTC 8:00 by default)
- Data persistence with historical tracking
- Minimal manual intervention

## Architecture

**Core Components:**

1. **main.py** - Main entry point containing:
   - API client for X API v2: `GET /2/users/by/username/:username?user.fields=public_metrics`
   - Growth calculation logic (delta and percentage)
   - Retry mechanism for API failures
   - Integration with storage backends

2. **storage.py** - Storage abstraction layer:
   - `StorageBackend`: Abstract base class
   - `CSVStorage`: Local CSV file storage (default)
   - `SheetsStorage`: Google Sheets integration via gspread
   - `get_storage_backend()`: Factory function for mode selection

3. **.github/workflows/daily.yml** - GitHub Actions workflow:
   - Cron schedule (daily at UTC 8:00)
   - Python environment setup
   - Automatic git commit/push (CSV mode only)

**Data Flow:**
1. Scheduled trigger (GitHub Actions cron) or manual execution
2. Initialize storage backend based on STORAGE_TYPE
3. Fetch current follower count from X API (with retry)
4. Read last record from storage
5. Calculate delta and growth rate
6. Save new record to storage
7. Commit and push (CSV mode only)

## Development Commands

### Local Development
```bash
# Run tracker manually
python main.py

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_tracker.py  # Core functionality tests
python test_storage.py  # Storage backend tests
```

### Testing
```bash
# Run functionality tests
python test_tracker.py

# Run storage backend tests
python test_storage.py

# Both test suites should pass all tests
```

## Configuration

**Required Environment Variables:**
- `X_BEARER_TOKEN` - X API Bearer Token (store in GitHub Secrets)
- `X_USERNAME` - Target username to track

**Optional Environment Variables:**
- `STORAGE_TYPE` - "csv" (default) or "sheets"
- `CSV_FILE_PATH` - Path to CSV file (default: "followers_data.csv")
- `GOOGLE_SHEETS_ID` - Google Sheets ID (for Sheets mode)
- `GOOGLE_SERVICE_ACCOUNT_JSON` - Service account credentials (for Sheets mode)

**CSV Data Format:**
- Columns: `date` (YYYY-MM-DD), `followers_count`, `delta`, `rate`
- Rate format: "%.2f%%" (e.g., "2.50%")

## Code Structure Requirements

**File Organization:**
- `main.py`: Entry point and API integration
- `storage.py`: Storage backend abstraction
- `test_tracker.py`: Core functionality tests
- `test_storage.py`: Storage backend tests

**Storage Backend Pattern:**
- All storage backends inherit from `StorageBackend` ABC
- Implement three methods: `initialize()`, `load_last_record()`, `save_record()`
- Use factory pattern via `get_storage_backend()` for instantiation
- Mode selection via `STORAGE_TYPE` environment variable

**Error Handling:**
- API call failures: Retry once, then log error and exit gracefully
- Division by zero: Handle when previous count is 0 (rate = 0%)
- First run: When no historical data exists (delta = 0, rate = 0%)

**Calculation Logic:**
```python
delta = current_count - previous_count
rate = (delta / previous_count) * 100  # Handle division by zero
```

## GitHub Actions Setup

**Workflow Schedule:**
- Cron: "0 8 * * *" (daily at 8:00 UTC)
- Configurable in `.github/workflows/daily.yml`
- Manual trigger supported via `workflow_dispatch`

**Workflow Steps:**
1. Checkout repository
2. Set up Python 3.11 with pip caching
3. Install dependencies from requirements.txt
4. Run tracker script with environment variables
5. Commit and push updated CSV (CSV mode only, conditional)

**Secrets Configuration:**
- `X_BEARER_TOKEN`: Required
- `X_USERNAME`: Required
- `STORAGE_TYPE`: Optional (default: csv)
- `GOOGLE_SHEETS_ID`: Required for Sheets mode
- `GOOGLE_SERVICE_ACCOUNT_JSON`: Required for Sheets mode

## Technical Constraints

- Python 3.8+ required
- X API free tier: 1,500 requests/month (daily usage: ~30 requests/month)
- GitHub Actions free tier: 2,000 minutes/month
- Script execution target: < 10 seconds per run
- Data append-only mode (never overwrite historical records)

## X API Integration

**Endpoint:** `https://api.twitter.com/2/users/by/username/:username`
**Query Parameters:** `user.fields=public_metrics`
**Authentication:** Bearer Token in Authorization header
**Response:** Extract `data.public_metrics.followers_count`

## Development Workflow

When implementing new features:
1. Update requirements.txt if new dependencies are added
2. Ensure all functions have docstrings
3. Add tests to test_tracker.py or test_storage.py
4. Test locally before committing
5. Update README.md with usage instructions
6. Update this CLAUDE.md if architecture changes

## Project Status

✅ **Complete - Production Ready**
- Stage 1: Core CSV tracking ✓
- Stage 2: Project configuration ✓
- Stage 3: GitHub Actions automation ✓
- Stage 4: Google Sheets support ✓
- Stage 5: Final validation ✓
