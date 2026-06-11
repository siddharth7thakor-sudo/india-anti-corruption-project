# Surat SMC Anti-Corruption Tracker

A focused investigative data module within the [India Anti-Corruption Project](https://github.com/siddharth7thakor-sudo/india-anti-corruption-project) targeting the **Surat Municipal Corporation (SMC)** — one of India's largest urban local bodies.

---

## Objective

Collect, analyze, and rank publicly available SMC data to surface potential corruption signals in:
- Tender awards and work orders
- Town Planning (TP) scheme approvals
- Development project expenditures
- Works Committee resolutions
- Budget allocations vs. actual spending

---

## Folder Structure

```
surat-smc-tracker/
|-- scrape_surat_smc.py       # Web scraper for SMC public portals
|-- analyze_evidence.py       # Evidence analyzer and risk scorer
|-- README.md                 # This file
|
|-- pages.csv                 # Scraped page metadata
|-- links.csv                 # All links extracted from pages
|-- projects.csv              # Development project listings
|-- tp_details.csv            # Town Planning scheme details
|-- downloaded_files.csv      # Inventory of downloaded documents
|
|-- evidence_hits.csv         # Records flagged by risk keywords
|-- ranked_evidence.csv       # All records ranked by risk score
|-- keyword_summary.csv       # Keyword frequency and severity
|-- case_timeline.csv         # Chronological case event timeline
```

---

## Data Sources

| Source | URL | Type |
|---|---|---|
| SMC E-Tender Portal | https://smc.gov.in/SMC_ONL/E-Tender/ | Tenders |
| SMC Projects | https://smc.gov.in/SMC_ONL/Projects/ | Development |
| SMC TP Schemes | https://smc.gov.in/SMC_ONL/TP/ | Town Planning |
| SMC Works Committee | https://smc.gov.in/SMC_ONL/WorksCommittee/ | Resolutions |
| SMC Budget | https://smc.gov.in/SMC_ONL/Budget/ | Finance |

---

## Risk Keywords

Records are flagged when they contain any of these terms:

- `amendment`, `revised estimate`, `direct award`
- `single source`, `urgent`, `without tender`
- `extension of time`, `supplementary`, `cost escalation`
- `variation order`, `splitting`, `cartel`, `kickback`
- `irregularity`, `inflated`, `fake certificate`
- `sub-standard`, `quality failure`

---

## How to Run

### 1. Install dependencies
```bash
pip install requests beautifulsoup4
```

### 2. Run the scraper
```bash
python scrape_surat_smc.py
```
This generates: `pages.csv`, `links.csv`

### 3. Add project/TP data manually or via scraper extension
Populate: `projects.csv`, `tp_details.csv`, `downloaded_files.csv`

### 4. Run the evidence analyzer
```bash
python analyze_evidence.py
```
This generates: `evidence_hits.csv`, `ranked_evidence.csv`, `keyword_summary.csv`, `case_timeline.csv`

---

## CSV Schema Reference

### pages.csv
| Field | Description |
|---|---|
| page_id | Unique identifier for the scraped page |
| page_name | Human-readable name |
| url | Full URL |
| status_code | HTTP response code |
| content_length | Response size in bytes |
| fetched_at | ISO timestamp |
| tables_found | Number of HTML tables found |
| links_found | Number of links found |

### evidence_hits.csv
| Field | Description |
|---|---|
| source | Source CSV file |
| record_id | Original record identifier |
| title | Record title or description |
| keywords_found | Semicolon-separated list of matched keywords |
| risk_score | Numeric score (10 per keyword) |
| flagged_at | ISO timestamp when flagged |

---

## Disclaimer

All data used in this project is sourced from **publicly available government portals**. This project is for **civic transparency and research purposes only**. No personal data is collected.

---

## License

MIT License — see root [LICENSE](../LICENSE) file.
