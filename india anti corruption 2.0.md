# India Anti-Corruption Project 2.0

> **Upgraded. Live. Multi-Portal. Real-Time Fraud Detection.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Data Sources](https://img.shields.io/badge/Data%20Sources-10%2B%20Portals-orange.svg)](#supported-portals)

---

## What's New in Version 2.0

Version 2.0 is a major upgrade over the static 1.0 system. Instead of working only with local CSV files, the system now **connects live to real Indian government portals** and performs multi-scheme welfare fraud detection across 10+ data sources.

### Key Upgrades

| Feature | Version 1.0 | Version 2.0 |
|---|---|---|
| Data Source | Local CSV files | Live government portals |
| Schemes Covered | Tenders only | 8+ welfare schemes |
| Detection Methods | Asset growth + tenders | Ghost beneficiaries, duplicate payments, wage anomalies, PDS leakage |
| Architecture | Single script | Modular connector package |
| Extensibility | Manual CSV updates | Add new portals dynamically |

---

## Project Overview

This project builds a **professional-grade, multi-portal corruption and welfare fraud detection system** for India. It connects to real government data portals, extracts beneficiary and procurement data, and applies automated fraud detection algorithms across schemes.

### What It Detects

- **Ghost Beneficiaries** - Inactive or deceased persons still receiving pension payments (NSAP)
- **Ghost Workers** - Fake workers logged in MGNREGA muster rolls
- **PDS Leakage** - Ration cards lifting more grain than allocated, or ghost cards with zero lifting
- **PM-KISAN Duplicates** - Same farmer receiving multiple instalments under different IDs
- **Wage Anomalies** - Workers paid far above average daily wage rates (MGNREGA)
- **Cross-Scheme Fraud** - Same entity claiming benefits from multiple schemes simultaneously
- **Tender Conflicts** - Politicians linked to ministry tenders (carried forward from v1.0)
- **Asset Growth Anomalies** - Suspicious 30%+ annual asset growth in politician declarations

---

## Supported Portals

| Portal | Scheme | Type | Status |
|---|---|---|---|
| [data.gov.in](https://data.gov.in) | Open Government Data | API | Active |
| [NSAP](https://nsap.dord.gov.in) | National Social Assistance Programme | HTML | Active |
| [MGNREGA MIS](https://nreganarep.nic.in) | Rural Employment | HTML | Active |
| [PDS Portal](https://pdsportal.gov.in) | Public Distribution System | HTML | Active |
| [PM-KISAN](https://pmkisan.gov.in) | Farmer Income Support | HTML | Active |
| [Jan Soochna](https://jansoochna.rajasthan.gov.in) | Rajasthan State Schemes | HTML | Active |
| [Union Budget](https://indiabudget.gov.in) | Budget Portal | HTML | Active |
| [CAG Reports](https://cag.gov.in) | Audit Reports | HTML | Active |
| [MoSPI](https://mospi.gov.in) | Project Monitoring | HTML | Active |
| [Social Justice](https://socialjustice.gov.in) | Scholarship Schemes | HTML | Active |

---

## Project Structure

```
india-anti-corruption-project/
├── connectors/                        # Live data connector package
│   ├── __init__.py                    # Package init, exports http_get
│   ├── base.py                        # Base HTTP connector (http_get, http_post)
│   └── example_open_data.py           # data.gov.in connector with datagovindia
│
├── welfare_fraud_connector.py         # Main 2.0 fraud detection engine
├── advanced_detection.py              # Tender & politician conflict detection
├── data_linker.py                     # Core corruption linking logic
├── education_ministry_extractor.py    # Education ministry data extractor
├── police_complaints_extractor.py     # Police complaint data extractor
│
├── surat-smc-tracker/                 # Surat Municipal Corporation case tracker
├── .github/workflows/                 # CI/CD pipeline
│
├── generate_massive_data.py           # Generates 1000+ realistic test records
├── setup_database.py                  # SQLite database setup
├── asset_growth.py                    # Asset growth analysis
├── risk_scoring.py                    # Risk score calculator
│
├── politicians.csv                    # Politician records
├── assets.csv                         # Declared assets by year
├── tenders.csv                        # Government tender records
└── family_registry.csv                # Family relationship data
```

---

## Architecture: Dynamic Connector System

### connectors/base.py
Provides reusable `http_get()` and `http_post()` functions used by all portal connectors. Every call hits the **live endpoint** - no caching, no static files.

```python
from connectors.base import http_get, HttpError

resp = http_get("https://data.gov.in/api/resource/...")
data = resp.json()
```

### welfare_fraud_connector.py
The core 2.0 engine. Provides:
- `DataSourceRegistry` - Central registry of all portal connections
- `FraudDetectionEngine` - Runs fraud checks across all active sources
- `WelfareFraudConnector` - Unified interface for scanning and reporting

```python
from welfare_fraud_connector import WelfareFraudConnector

connector = WelfareFraudConnector()
connector.connect_all()   # Test all portals
indicators = connector.scan()   # Run fraud detection
print(connector.report())   # Print full report
```

### Adding a New Portal

```python
# Register a new state transparency portal
connector.add_custom_source(
    name="mp_transparency",
    url="https://mpinfo.org/transparency",
    scheme_type=WelfareSchemeType.GENERAL
)
```

---

## Installation

```bash
# Clone the repo
git clone https://github.com/siddharth7thakor-sudo/india-anti-corruption-project.git
cd india-anti-corruption-project

# Install dependencies
pip install requests pandas datagovindia

# Set your data.gov.in API key
export DATAGOVINDIA_API_KEY="your_api_key_here"
# Get your free API key at: https://data.gov.in/user/register
```

---

## Quick Start

### Run Welfare Fraud Detection (Version 2.0)

```bash
python welfare_fraud_connector.py
```

Sample output:
```
Testing data source connections...
  nsap: CONNECTED
  mgnrega: CONNECTED
  pds: CONNECTED
  pmkisan: CONNECTED

Running fraud detection scan...

============================================================
WELFARE FRAUD DETECTION REPORT
Generated: 2025-06-15 10:30:00
============================================================
[HIGH] NSAP_GHOST_BENEFICIARY
  Source: NSAP
  Description: Found 1 inactive ghost beneficiaries still in system
  Confidence: 0.85

[MEDIUM] MGNREGA_WAGE_ANOMALY
  Source: MGNREGA
  Description: Found 1 workers with anomalous wage patterns
  Confidence: 0.70

[CRITICAL] PDS_GHOST_CARD
  Source: PDS
  Description: Found 1 ghost ration cards with zero lifting
  Confidence: 0.90

============================================================
SUMMARY
Total Indicators: 3
  Critical: 1
  High: 1
  Medium: 1
  Low: 0
============================================================
```

### Run Tender & Politician Detection (Version 1.0)

```bash
# Generate test data
python generate_massive_data.py

# Setup database
python setup_database.py

# Run full corruption analysis
python data_linker.py

# View findings
python read_politicians.py
```

---

## Fraud Detection Methods

### 1. Ghost Beneficiary Detection (NSAP)
Flags beneficiaries with `status = inactive` still listed as active recipients. These are persons who have died or moved but are still receiving pension payments.

### 2. Muster Roll Anomaly Detection (MGNREGA)
Detects workers with:
- More than 100 days worked (legal maximum is 100 days/year)
- Wages paid at more than 1.5x the average daily rate

### 3. PDS Leakage Detection
- **Ghost Cards**: Ration cards with zero grain lifting for multiple months
- **Over-lifting**: Cards lifting more grain than their allocated quota
- **Duplicate Households**: Same household head appearing on multiple cards

### 4. Cross-Scheme Duplicate Detection
Matches beneficiaries across NSAP, MGNREGA, PDS, and PM-KISAN using name and Aadhaar number to detect:
- Same person enrolled in multiple pension schemes
- Active farmer claiming both PM-KISAN and landless labour MGNREGA wages

### 5. Tender-Politician Linking (v1.0)
Links politicians to government tenders through ministry connections:
- Asset growth >30% annually flagged as corruption indicator
- Tender clustering by ministry detects conflicts of interest
- Risk scores (1-100) generated for each linked politician

---

## Real Data Integration

To connect to real government APIs:

```python
from connectors.example_open_data import fetch_sample_dataset

# Fetch live data from any data.gov.in dataset
records = fetch_sample_dataset(
    api_index="your_dataset_index",  # From data.gov.in catalog
    results_per_req=100
)
for row in records[:5]:
    print(row)
```

### Get a data.gov.in API Key
1. Register at [data.gov.in](https://data.gov.in/user/register)
2. Get your API key from your profile
3. Set it: `export DATAGOVINDIA_API_KEY="your_key"`
4. Browse datasets at [data.gov.in/catalogs](https://data.gov.in/catalog)

---

## Surat SMC Tracker

The `surat-smc-tracker/` folder is a live case-tracking module for Surat Municipal Corporation corruption cases. It tracks case timelines, complaints, and investigation status for real municipal-level cases.

---

## CI/CD Pipeline

The `.github/workflows/` directory contains automated workflows for:
- Linting Python scripts
- Testing connector imports
- Validating CSV schemas
- Running detection logic with synthetic data

---

## Roadmap

- [ ] Web dashboard for real-time visualization (Flask/Streamlit)
- [ ] Machine learning risk scoring (Random Forest model)
- [ ] Geospatial corruption mapping (district-level heatmaps)
- [ ] News article NLP analysis (flag politicians in corruption news)
- [ ] Beneficial ownership tracking (shell company detection)
- [ ] Property registry integration (sub-registrar data linking)
- [ ] WhatsApp/Telegram alert bot for new fraud indicators
- [ ] API endpoint for external integrations

---

## Data Sources & References

- [data.gov.in](https://data.gov.in) - Government of India Open Data Platform
- [NSAP MIS](https://nsap.dord.gov.in) - Ministry of Rural Development
- [MGNREGA MIS](https://nreganarep.nic.in) - Ministry of Rural Development  
- [PM-KISAN](https://pmkisan.gov.in) - Ministry of Agriculture
- [Transparency International](https://transparency.org) - Corruption Perceptions Index
- [World Bank Integrity](https://worldbank.org/integrity) - Procurement fraud research
- [CAG India](https://cag.gov.in) - Comptroller and Auditor General reports

---

## Author

**Siddharth Thakor-sudo**  
India Anti-Corruption Project  
Version 2.0 - Dynamic Multi-Portal Data Integration

---

*This project is for transparency research, anti-corruption investigation, and civic technology purposes.*
