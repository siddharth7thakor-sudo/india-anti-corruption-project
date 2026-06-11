"""
Surat SMC Scraper
Scrapes Surat Municipal Corporation (SMC) data for anti-corruption analysis.
Target pages: tenders, projects, TP announcements, works committee.
"""

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
BASE_URL = "https://smc.gov.in"
OUTPUT_DIR = Path("surat-smc-tracker")
OUTPUT_DIR.mkdir(exist_ok=True)

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
TIMEOUT = 30

# ------------------------------------------------------------------------------
# Target URLs (SMC public sections)
# ------------------------------------------------------------------------------
TARGET_PAGES = [
    {
        "id": "tenders",
        "name": "Tenders & E-Marketplace",
        "url": f"{BASE_URL}/SMC_ONL/E-Tender/tenderHome.aspx",
        "keywords": ["tender", "work order", "NIT", "bid"],
    },
    {
        "id": "projects",
        "name": "Development Projects",
        "url": f"{BASE_URL}/SMC_ONL/Projects/default.aspx",
        "keywords": ["project", "development", "works"],
    },
    {
        "id": "tp",
        "name": "Town Planning (TP) Schemes",
        "url": f"{BASE_URL}/SMC_ONL/TP/default.aspx",
        "keywords": ["TP scheme", "town planning", "land acquisition"],
    },
    {
        "id": "works_committee",
        "name": "Works Committee",
        "url": f"{BASE_URL}/SMC_ONL/WorksCommittee/default.aspx",
        "keywords": ["resolution", "sanction", "committee"],
    },
    {
        "id": "budget",
        "name": "Budget Documents",
        "url": f"{BASE_URL}/SMC_ONL/Budget/default.aspx",
        "keywords": ["budget", "expenditure", "allocation"],
    },
]

# Risk keywords that suggest corruption signals
RISK_KEYWORDS = [
    "amendment", "revised", "direct award",
    "single source", "urgent", "without tender",
    "extension", "supplementary",
    "cost escalation", "variation order",
]

# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------
def normalize_text(text: str) -> str:
    return " ".join(text.split()).strip() if text else ""

def save_csv(rows: list[dict], filename: str, fieldnames: list[str]):
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {filepath}")

def save_json(data, filename: str):
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON to {filepath}")

# ------------------------------------------------------------------------------
# Scraper Functions
# ------------------------------------------------------------------------------
def scrape_page(page_info: dict):
    """Fetch and parse a single SMC target page."""
    print(f"Fetching: {page_info['name']} ({page_info['url']})")
    try:
        resp = requests.get(
            page_info["url"],
            headers=REQUEST_HEADERS,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  Error fetching: {e}")
        return None, []

    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract tables (common SMC pattern)
    rows = []
    tables = soup.find_all("table")
    for table in tables:
        for tr in table.find_all("tr"):
            cells = [norm
                    for c in tr.find_all(["td", "th"])
                    if norm := normalize_text(c.get_text())]
            if cells:
                rows.append({
                    "page_id": page_info["id"],
                    "page_name": page_info["name"],
                    "cell_count": len(cells),
                    "preview": cells[:5],
                })

    # Extract links
    links = [
        {
            "page_id": page_info["id"],
            "text": normalize_text(a.get_text()),
            "href": a.get("href", ""),
            "abs_url": (
                BASE_URL + a["href"]
                if a.get("href", "").startswith("/")
                else a.get("href", "")
            ),
        }
        for a in soup.find_all("a", href=True)
    ]

    return dict(
        page_id=page_info["id"],
        page_name=page_info["name"],
        url=page_info["url"],
        status_code=resp.status_code,
        content_length=len(resp.text),
        fetched_at=datetime.now().isoformat(),
        tables_found=len(tables),
        links_found=len(links),
    ), links


def analyze_tender_text(text: str, keywords: list[str]) -> list[str]:
    """Return risk keywords found in text."""
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


# ------------------------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Surat SMC Scraper - Anti-Corruption Data Collection")
    print("=" * 60)

    pages_data = []
    all_links = []

    for page in TARGET_PAGES:
        page_record, links = scrape_page(page)
        if page_record:
            pages_data.append(page_record)
            all_links.extend(links)
            print(
                f"  pages_data={len(pages_data)}, "
                f"tables={page_record['tables_found']}, "
                f"links={page_record['links_found']}"
            )

    # ----------------- Save pages.csv -----------------
    save_csv(
        pages_data,
        "pages.csv",
        [
            "page_id",
            "page_name",
            "url",
            "status_code",
            "content_length",
            "fetched_at",
            "tables_found",
            "links_found",
        ],
    )

    # ----------------- Save links.csv -----------------
    save_csv(
        all_links,
        "links.csv",
        ["page_id", "text", "href", "abs_url"],
    )

    print("\nScraping complete.")

    # ----------------- Evidence Analysis -------------
    print("\nRunning evidence analysis...")
    analyze_evidence()


def analyze_evidence():
    """Run evidence analysis on scraped data."""
    # Placeholder analysis logic
    print("Evidence analysis module called.")


if __name__ == "__main__":
    main()
