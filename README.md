# Price Scraper with Change Detection

A simple Python tool that collects product data from a website, saves it to CSV, and tells you when a price changes.

Demo target: books.toscrape.com (a public practice site). The same structure can be adapted to other sites.

## Features

- Scrapes multiple pages (you choose how many)
- Saves title, price, link and time to CSV
- Detects price changes between runs and logs them in `changes.csv`
- Retries automatically on network errors
- Polite delay between requests

## Install

    pip install -r requirements.txt

## Usage

    python scraper.py --pages 3
    python scraper.py --pages 5 --out my_data.csv

Run it again later. If any price changed, you will see it in the terminal and in `changes.csv`.

## Example output

See `sample_output.csv` and `sample_changes.csv`.

## Need something similar?

I build custom Python scrapers and automation scripts: price monitoring, data collection, reports, and Telegram alerts.
Contact: Telegram @amir0_418
