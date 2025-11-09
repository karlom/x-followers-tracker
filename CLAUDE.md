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
1. **track_followers.py** - Main Python script containing:
   - API client for X API v2 endpoint: `GET /2/users/by/username/:username?user.fields=public_metrics`
   - Growth calculation logic (delta and percentage)
   - Data storage handler (CSV and optional Google Sheets)
   - Error handling with retry logic

2. **.github/workflows/daily.yml** - GitHub Actions workflow for daily scheduling

3. **Data Storage:**
   - Default: Local CSV file committed to repo
   - Optional: Google Sheets integration via gspread

**Data Flow:**
1. Scheduled trigger (GitHub Actions cron)
2. Fetch current follower count from X API
3. Read last record from storage
4. Calculate delta and growth rate
5. Append new record to storage
6. Commit and push updated file (CSV mode)

## Development Commands

### Local Development
```bash
# Run tracker manually
python track_followers.py

# Install dependencies
pip install -r requirements.txt

# Install with Google Sheets support (optional)
pip install -r requirements.txt gspread google-auth
```

### Testing
```bash
# Run unit tests (when implemented)
python -m pytest tests/

# Test specific module
python -m pytest tests/test_api.py
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

**Modularization:**
- Separate functions for: API calls, growth calculation, CSV operations, Sheets operations
- Each function must have docstrings explaining purpose, parameters, and return values

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

**Workflow Steps:**
1. Checkout repository
2. Set up Python 3.8+
3. Install dependencies
4. Run tracker script
5. Commit and push updated CSV (if changed)

**Secrets Configuration:**
- Store `X_BEARER_TOKEN` in GitHub repository secrets
- Optional: `GOOGLE_SERVICE_ACCOUNT_JSON` for Sheets mode

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
3. Test locally before committing
4. Update this CLAUDE.md if architecture changes
5. Test GitHub Actions workflow in a fork before deploying

## Future Extensions (Not in Scope)

- Real-time monitoring
- Email/Slack notifications on errors
- Multi-user support
- Data visualization dashboard
- Additional metrics (likes, retweets, etc.)
