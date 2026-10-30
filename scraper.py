import argparse
import csv
import os
import re
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://books.toscrape.com/catalogue/"


def make_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1,
                  status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers["User-Agent"] = "Mozilla/5.0 (price-scraper demo)"
    return session


def parse_price(text):
    match = re.search(r"\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


def scrape_page(session, page):
    url = f"{BASE}page-{page}.html"
    resp = session.get(url, timeout=15)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = []
    for item in soup.select("article.product_pod"):
        link_tag = item.h3.a
        rows.append({
            "title": link_tag["title"],
            "price": parse_price(item.select_one("p.price_color").text),
            "link": urljoin(url, link_tag["href"]),
        })
    return rows


def load_previous(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, newline="", encoding="utf-8") as f:
        return {r["link"]: parse_price(r["price"]) for r in csv.DictReader(f)}


def save(rows, filename):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "price", "link", "scraped_at"])
        for r in rows:
            writer.writerow([r["title"], r["price"], r["link"], stamp])


def save_changes(changes, filename="changes.csv"):
    new_file = not os.path.exists(filename)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["title", "old_price", "new_price", "link", "detected_at"])
        for title, old, new, link in changes:
            writer.writerow([title, old, new, link, stamp])


def main():
    parser = argparse.ArgumentParser(description="Book price scraper")
    parser.add_argument("--pages", type=int, default=3, help="how many pages")
    parser.add_argument("--out", default="output.csv", help="output CSV file")
    args = parser.parse_args()

    session = make_session()
    previous = load_previous(args.out)
    rows = []

    for page in range(1, args.pages + 1):
        try:
            page_rows = scrape_page(session, page)
        except requests.RequestException as err:
            print(f"Page {page}: error - {err}")
            break
        if page_rows is None:
            print(f"Page {page}: not found, stopping.")
            break
        rows.extend(page_rows)
        print(f"Page {page}: {len(page_rows)} products")
        time.sleep(0.5)

    if not rows:
        print("No data collected. Existing file left untouched.")
        return

    changes = []
    for r in rows:
        old = previous.get(r["link"])
        if old is not None and old != r["price"]:
            changes.append((r["title"], old, r["price"], r["link"]))

    save(rows, args.out)
    if changes:
        save_changes(changes)
    print(f"Saved {len(rows)} products to {args.out}")
    print(f"Price changes detected: {len(changes)}")
    for title, old, new, _ in changes:
        print(f"  {title}: {old} -> {new}")


if __name__ == "__main__":
    main()
