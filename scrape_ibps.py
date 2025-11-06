"""
Scrape IBPS recruitment listings and save to timestamped CSV.
Fields extracted: Job Title, Location, PostDate, Link
"""

from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin
import requests
import pandas as pd
import logging
import sys
import re
import os
import certifi
import urllib3
from bs4 import BeautifulSoup

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

BASE_URL = "https://www.ibps.in"
RECRUITMENT_PATH = "/index.php/recruitment/"
RECRUITMENT_URL = urljoin(BASE_URL, RECRUITMENT_PATH)
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

def fetch_page(url: str, timeout: int = 10, verify_ssl: bool = False) -> Optional[str]:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = {"User-Agent": USER_AGENT}
    try:
        logging.info("Fetching %s", url)
        resp = requests.get(url, headers=headers, timeout=timeout, verify=verify_ssl)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        logging.error("Error fetching %s : %s", url, e)
        return None

def parse_recruitment_list(html: str, base_url: str = BASE_URL) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []

    possible_containers = []
    for keyword in ("recruit", "career", "notice", "vacancy", "advertisement", "notification"):
        possible_containers.extend(soup.find_all(
            lambda tag: tag.name in ("div", "section", "ul", "tbody") and tag.get("class") and
            any(keyword in c.lower() for c in " ".join(tag.get("class")).split())
        ))

    if not possible_containers:
        main = soup.find("main") or soup.find("body") or soup
        possible_containers = [main]

    anchors = []
    for container in possible_containers:
        anchors.extend(container.find_all("a", href=True))
    anchors = list({(a.get_text(strip=True), a['href']): a for a in anchors}.values())

    keyword_pattern = re.compile(r"(recruit|apply|notification|advertisement|vacancy|register|click here|recruitment|notice)", re.I)

    for a in anchors:
        text = a.get_text(" ", strip=True)
        href = urljoin(base_url, a['href'])
        parent = a.parent
        date_text = None
        location_text = None

        search_nodes = [parent] + list(parent.find_all_next(limit=3)) + list(parent.find_all_previous(limit=3))
        for node in search_nodes:
            if node:
                txt = node.get_text(" ", strip=True)
                date_match = re.search(r"\b(\d{1,2}[ \-\/][A-Za-z0-9]{1,3}[ \-\/]\d{2,4})\b|\b([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})\b", txt)
                if date_match:
                    date_text = date_match.group(0)
                    break

        for node in search_nodes:
            if node:
                txt = node.get_text(" ", strip=True)
                loc_match = re.search(r"(Location[:\s]*[A-Za-z,\s\-]+)|([A-Za-z\s]+(?:District|State|Region|City|Town))", txt)
                if loc_match:
                    location_text = loc_match.group(0)
                    break

        title = text or "IBPS Notice"

        if not (keyword_pattern.search(title) or title.lower().count("ibps") > 0 or a['href'].lower().endswith((".pdf", ".doc", ".docx"))):
            if not (("wp-content" in a['href']) or ("recruit" in a['href'].lower()) or ("notification" in a['href'].lower())):
                continue

        results.append({
            "title": title,
            "location": location_text or "",
            "post_date": date_text or "",
            "link": href,
        })

    if not results:
        for a in soup.find_all("a", href=True):
            href = a['href']
            if href.lower().endswith(".pdf"):
                title = a.get_text(" ", strip=True) or "IBPS PDF Notice"
                results.append({
                    "title": title,
                    "location": "",
                    "post_date": "",
                    "link": urljoin(base_url, href),
                })

    seen = set()
    unique = []
    for r in results:
        if r["link"] in seen:
            continue
        seen.add(r["link"])
        unique.append(r)

    logging.info("Parsed %d entries", len(unique))
    return unique

def save_to_csv(items: List[Dict], out_dir: str = "data", prefix: str = "ibps_recruitments"):
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
    logging.info("Saved %d rows to %s", len(df), out_path)

def main():
    html = fetch_page(RECRUITMENT_URL, verify_ssl=False)
    if not html:
        logging.error("Failed to fetch recruitment page. Exiting.")
        return
    items = parse_recruitment_list(html, base_url=BASE_URL)
    if not items:
        logging.warning("No job listings found on page. You may need to adjust selectors.")
    save_to_csv(items)

if __name__ == "__main__":
    main()
