# Immoweb Scraper

This Python script (`immo.py`) fetches housing data from Immoweb, performs data aggregation and analysis, and sends an email notification with the results.

## How it Works

1. The script fetches housing data from Immoweb's API, paginating through the results.
2. Fetched data is processed, normalized, and aggregated to perform analysis.
3. The aggregated data is saved to CSV files and uploaded to a DuckDB database.
4. An email notification is sent with the count of housing offers extracted.

## Usage

The script is triggered by a GitHub Actions workflow (`main.yml`) which runs daily at 15:30 UTC.

## Requirements

- Python 3.9
- Required Python packages are listed in `requirements.txt`.
- Environment variables:
  - `EMAIL_ME`: Sender email address for notification.
  - `EMAIL_PASSWORD_ME`: Sender email password.
  - `SERVICETOKENMD`: Service token for accessing DuckDB.
