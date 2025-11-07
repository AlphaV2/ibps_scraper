#!/usr/bin/env python3
"""
IBPS Recruitment Scraper — Task Version (Final)
-----------------------------------------------
Scrapes public IBPS recruitment listings from https://www.ibps.in/index.php/recruitment/
Extracts:
    - Job Title
    - Location
    - Post/Publish Date
    - Link to detailed job page
Saves results into a timestamped CSV file using Pandas.
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import re
import os
import logging
import sys
from typing import List, Dict

# -------------------------------------------------------------------
# Basic Configuration
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

BASE_URL = "https://www.ibps.in"
RECRUITMENT_URL = urljoin(BASE_URL, "/index.php/recruitment/")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; IBPS-Scraper/1.0)"}
OUTPUT_DIR = "data"

# -------------------------------------------------------------------
# 1. Fetch HTML Page
# -------------------------------------------------------------------
def fetch_page(url: str) -> str | None:
    """Fetches the IBPS recruitment page HTML content."""
    try:
        logging.info(f"Fetching recruitment page: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None

# -------------------------------------------------------------------
# 2. Parse Job Listings
# -------------------------------------------------------------------
def parse_jobs(html: str) -> List[Dict]:
    """Extracts job details from the HTML content."""
    soup = BeautifulSoup(html, "html.parser")
    anchors = soup.find_all("a", href=True)
    jobs: List[Dict] = []

    for a in anchors:
        text = a.get_text(" ", strip=True)
        href = urljoin(BASE_URL, a["href"])
        if not text or not any(k in text.lower() for k in ["recruit", "vacancy", "notification", "advertisement"]):
            continue

        parent = a.parent
        date_text, location_text = "", ""

        # Extract nearby date or location info
        neighbors = [parent] + list(parent.find_all_next(limit=3)) + list(parent.find_all_previous(limit=3))
        for n in neighbors:
            txt = n.get_text(" ", strip=True)
            date_match = re.search(r"\b(\d{1,2}[-/ ][A-Za-z]{3,9}[-/ ]\d{2,4})\b", txt)
            if date_match:
                date_text = date_match.group(0)
                break

        for n in neighbors:
            txt = n.get_text(" ", strip=True)
            loc_match = re.search(r"(Location[:\s]*[A-Za-z\s,]+)", txt)
            if loc_match:
                location_text = loc_match.group(0)
                break

        jobs.append({
            "title": text.strip(),
            "location": location_text.strip(),
            "post_date": date_text.strip(),
            "link": href
        })

    logging.info(f"Extracted {len(jobs)} raw entries.")
    return deduplicate_jobs(jobs)

# -------------------------------------------------------------------
# 3. Deduplicate
# -------------------------------------------------------------------
def deduplicate_jobs(jobs: List[Dict]) -> List[Dict]:
    """Removes duplicate entries based on the job link."""
    seen, unique = set(), []
    for job in jobs:
        if job["link"] not in seen:
            seen.add(job["link"])
            unique.append(job)
    logging.info(f"Deduplicated to {len(unique)} unique entries.")
    return unique

# -------------------------------------------------------------------
# 4. Save to CSV
# -------------------------------------------------------------------
def save_to_csv(items: List[Dict], out_dir: str = "data", prefix: str = "ibps_recruitments"):
    """Saves job listings to a timestamped CSV."""
    if not items:
        logging.warning("No items to save.")
        return

    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{prefix}_{timestamp}.csv"
    out_path = os.path.join(out_dir, filename)

    df = pd.DataFrame(items)
    df = df[["title", "location", "post_date", "link"]]
    df.to_csv(out_path, index=False)
    logging.info(f"Saved {len(df)} rows to {out_path}")

# -------------------------------------------------------------------
# 5. Main Execution
# -------------------------------------------------------------------
def main():
    html = fetch_page(RECRUITMENT_URL)
    if not html:
        logging.error("Failed to fetch recruitment page. Exiting.")
        return

    jobs = parse_jobs(html)
    save_to_csv(jobs)

if __name__ == "__main__":
    main()
