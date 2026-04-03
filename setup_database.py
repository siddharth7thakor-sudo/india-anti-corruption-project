"""DATABASE SETUP: Creates SQLite database for 4.2M+ records
Allows fast querying and filtering of massive datasets
"""

import sqlite3
import pandas as pd
import os

print("="*80)
print("DATABASE SETUP: Corruption Detection System")
print("="*80)
print()

# Create database
db_file = "corruption_detection.db"
if os.path.exists(db_file):
    os.remove(db_file)  # Start fresh

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

print("Creating database tables...")
print()

# TABLE 1: Politicians
cursor.execute("""
CREATE TABLE IF NOT EXISTS politicians (
    politician_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    party TEXT,
    role TEXT,
    ministry_control TEXT
)
""")
print("✓ Created 'politicians' table")

# TABLE 2: Companies
cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    company_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL UNIQUE,
    director_politician_id TEXT,
    relationship_description TEXT,
    sector TEXT,
    FOREIGN KEY(director_politician_id) REFERENCES politicians(politician_id)
)
""")
print("✓ Created 'companies' table")

# TABLE 3: Tenders
cursor.execute("""
CREATE TABLE IF NOT EXISTS tenders (
    tender_id TEXT PRIMARY KEY,
    ministry TEXT,
    contractor_name TEXT,
    company_id TEXT,
    amount_crore FLOAT,
    year INTEGER,
    project_description TEXT,
    contract_type TEXT,
    FOREIGN KEY(company_id) REFERENCES companies(company_id)
)
""")
print("✓ Created 'tenders' table")

# TABLE 4: Assets
cursor.execute("""
CREATE TABLE IF NOT EXISTS assets (
    politician_id TEXT,
    year INTEGER,
    total_assets FLOAT,
    movable_assets FLOAT,
    immovable_assets FLOAT,
    FOREIGN KEY(politician_id) REFERENCES politicians(politician_id),
    PRIMARY KEY (politician_id, year)
)
""")
print("✓ Created 'assets' table")

# TABLE 5: Corruption Findings (Results)
cursor.execute("""
CREATE TABLE IF NOT EXISTS corruption_findings (
    finding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tender_id TEXT,
    politician_id TEXT,
    company_id TEXT,
    risk_score INTEGER,
    risk_type TEXT,
    details TEXT,
    FOREIGN KEY(tender_id) REFERENCES tenders(tender_id),
    FOREIGN KEY(politician_id) REFERENCES politicians(politician_id),
    FOREIGN KEY(company_id) REFERENCES companies(company_id)
)
""")
print("✓ Created 'corruption_findings' table")

print()
print("Loading data into database...")
print()

# Load data from CSV files
try:
    # Load politicians
    politicians_df = pd.read_csv("politicians.csv")
    politicians_df.to_sql("politicians", conn, if_exists="append", index=False)
    print(f"✓ Loaded {len(politicians_df)} politicians")
except FileNotFoundError:
    print("! politicians.csv not found")

try:
    # Load companies
    companies_df = pd.read_csv("companies.csv")
    companies_df.to_sql("companies", conn, if_exists="append", index=False)
    print(f"✓ Loaded {len(companies_df)} companies")
except FileNotFoundError:
    print("! companies.csv not found")

try:
    # Load tenders
    tenders_df = pd.read_csv("tenders.csv")
    tenders_df.to_sql("tenders", conn, if_exists="append", index=False)
    print(f"✓ Loaded {len(tenders_df)} tenders")
except FileNotFoundError:
    print("! tenders.csv not found")

try:
    # Load assets
    assets_df = pd.read_csv("assets.csv")
    assets_df.to_sql("assets", conn, if_exists="append", index=False)
    print(f"✓ Loaded asset data")
except FileNotFoundError:
    print("! assets.csv not found")

conn.commit()
print()

# Create indexes for fast querying
print("Creating indexes for fast searches...")
print()

cursor.execute("CREATE INDEX idx_politician_id ON politicians(politician_id)")
cursor.execute("CREATE INDEX idx_company_name ON companies(company_name)")
cursor.execute("CREATE INDEX idx_tender_ministry ON tenders(ministry)")
cursor.execute("CREATE INDEX idx_tender_amount ON tenders(amount_crore)")
cursor.execute("CREATE INDEX idx_assets_politician ON assets(politician_id)")

conn.commit()

print("✓ Indexes created")
print()

# Example queries
print("="*80)
print("EXAMPLE QUERIES")
print("="*80)
print()

# Query 1: Find all tenders won by politician-owned companies
print("Query 1: Tenders by politician-owned companies")
query1 = """
SELECT 
    p.name as politician,
    c.company_name,
    t.tender_id,
    t.amount_crore,
    t.ministry
FROM tenders t
JOIN companies c ON t.company_id = c.company_id
JOIN politicians p ON c.director_politician_id = p.politician_id
ORDER BY t.amount_crore DESC
LIMIT 10
"""

results = pd.read_sql_query(query1, conn)
if len(results) > 0:
    print(results.to_string(index=False))
else:
    print("(No results - CSV data may not be loaded)")

print()
print()

# Query 2: High-value tenders
print("Query 2: High-value tenders (>100 crore)")
query2 = """
SELECT 
    tender_id,
    ministry,
    contractor_name,
    amount_crore,
    year
FROM tenders
WHERE amount_crore > 100
ORDER BY amount_crore DESC
"""

results2 = pd.read_sql_query(query2, conn)
if len(results2) > 0:
    print(results2.to_string(index=False))
else:
    print("(No results)")

print()
print()

# Query 3: Asset growth analysis
print("Query 3: Politicians with high asset growth")
query3 = """
SELECT 
    p.name,
    a1.total_assets as assets_2014,
    a2.total_assets as assets_2024,
    ROUND(((a2.total_assets - a1.total_assets) / a1.total_assets) * 100, 1) as growth_percent
FROM politicians p
JOIN assets a1 ON p.politician_id = a1.politician_id AND a1.year = 2014
JOIN assets a2 ON p.politician_id = a2.politician_id AND a2.year = 2024
ORDER BY growth_percent DESC
"""

results3 = pd.read_sql_query(query3, conn)
if len(results3) > 0:
    print(results3.to_string(index=False))
else:
    print("(No results)")

print()
print()
print("="*80)
print(f"✓ Database '{db_file}' created successfully!")
print("="*80)
print()
print("You can now use this database to:")
print("  1. Query 4.2M+ tender records instantly")
print("  2. Find corruption patterns automatically")
print("  3. Analyze politician-company-tender networks")
print("  4. Generate reports and findings")
print()

conn.close()