"""DATA LINKER: Links massive amounts of data (politicians, companies, tenders, assets)
Handles 4.2M+ records and finds corruption patterns
"""

import csv
import pandas as pd
from collections import defaultdict

# ==============================================================================
# STEP 1: LOAD DATA
# ==============================================================================
print("Loading data files...")

politicians = {}
with open("politicians.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        politicians[row["politician_id"]] = row

companies = {}
with open("family_registry.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        companies[row["company_name"]] = row

tenders = []
with open("tenders.csv", encoding="utf-8") as f:
    tenders = list(csv.DictReader(f))

assets = defaultdict(dict)
with open("assets.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        pid = row["politician_id"]
        year = int(row["year"])
        assets[pid][year] = float(row["total_assets"])

print(f"✓ Loaded {len(politicians)} politicians")
print(f"✓ Loaded {len(companies)} companies")
print(f"✓ Loaded {len(tenders)} tenders")
print(f"✓ Loaded asset data for {len(assets)} politicians")
print()

# ==============================================================================
# STEP 2: LINK TENDERS TO POLITICIANS (via companies)
# ==============================================================================
print("Linking tenders to politicians...")

linked_tenders = []
for tender in tenders:
    contractor = tender["contractor_name"]
    
    if contractor in companies:
        company = companies[contractor]
        politician_id = company["director_politician_id"]
        
        if politician_id != "NULL" and politician_id in politicians:
            politician = politicians[politician_id]
            
            linked_tenders.append({
                "tender_id": tender["tender_id"],
                "amount": float(tender["amount"]),
                "ministry": tender["ministry"],
                "contractor": contractor,
                "politician_name": politician["name"],
                "politician_id": politician_id,
                "politician_role": politician["role"],
                "politician_ministry": politician["ministry_control"],
                "relationship": company["relationship"],
                "sector": company["sector"],
            })

print(f"✓ Found {len(linked_tenders)} tenders linked to politicians' companies")
print()

# ==============================================================================
# STEP 3: DETECT CORRUPTION SIGNALS
# ==============================================================================
print("Detecting corruption signals...")
print()

# SIGNAL 1: Same-Ministry Conflicts
print("="*80)
print("SIGNAL 1: SAME-MINISTRY CONFLICTS (CRITICAL RISK)")
print("="*80)
print()

same_ministry_tenders = []
for t in linked_tenders:
    if t["politician_ministry"] in t["ministry"]:
        same_ministry_tenders.append(t)
        print(f"🚩 CRITICAL: {t['politician_name']} ({t['politician_role']})")
        print(f"   Owns: {t['contractor']}")
        print(f"   Won ₹{t['amount']:.0f} crore from {t['ministry']} (THEIR ministry!)")
        print(f"   Relationship: {t['relationship']}")
        print()

print(f"Total same-ministry tenders: {len(same_ministry_tenders)}")
print(f"Total value: ₹{sum(t['amount'] for t in same_ministry_tenders):.0f} crore")
print()

# SIGNAL 2: High-Value Contracts
print("="*80)
print("SIGNAL 2: HIGH-VALUE CONTRACTS (>₹100 crore)")
print("="*80)
print()

high_value = [t for t in linked_tenders if t["amount"] > 100]
for t in sorted(high_value, key=lambda x: x["amount"], reverse=True):
    print(f"₹{t['amount']:.0f} crore | {t['politician_name']} | {t['contractor']}")

print()
print(f"Total high-value tenders: {len(high_value)}")
print()

# SIGNAL 3: Market Concentration
print("="*80)
print("SIGNAL 3: MARKET CONCENTRATION (One company dominates)")
print("="*80)
print()

concentration = defaultdict(lambda: {"total": 0, "count": 0})
for t in linked_tenders:
    key = t["contractor"]
    concentration[key]["total"] += t["amount"]
    concentration[key]["count"] += 1

for contractor, data in sorted(concentration.items(), key=lambda x: x[1]["total"], reverse=True)[:10]:
    print(f"{contractor}: ₹{data['total']:.0f} cr ({data['count']} contracts)")

print()

# SIGNAL 4: Asset Growth vs Tender Wins
print("="*80)
print("SIGNAL 4: ASSET GROWTH CORRELATION")
print("="*80)
print()

for pid in politicians:
    if pid in assets and 2014 in assets[pid] and 2024 in assets[pid]:
        politician = politicians[pid]
        asset_2014 = assets[pid][2014]
        asset_2024 = assets[pid][2024]
        growth = ((asset_2024 - asset_2014) / asset_2014) * 100 if asset_2014 > 0 else 0
        
        # How many tenders did they win?
        tender_value = sum(t["amount"] for t in linked_tenders if t["politician_id"] == pid)
        
        if growth > 200:
            print(f"⚠️  {politician['name']} ({politician['role']})")
            print(f"   Asset growth: {growth:.0f}% (₹{asset_2014/10000000:.1f}cr → ₹{asset_2024/10000000:.1f}cr)")
            print(f"   Tender wins: ₹{tender_value:.0f} crore")
            print()

# ==============================================================================
# STEP 5: SAVE FINDINGS
# ==============================================================================
print("="*80)
print("SUMMARY")
print("="*80)
print(f"Total politicians with tender links: {len(set(t['politician_id'] for t in linked_tenders))}")
print(f"Total tender value linked to politicians: ₹{sum(t['amount'] for t in linked_tenders):.0f} crore")
print(f"Critical same-ministry conflicts: {len(same_ministry_tenders)}")
print(f"Total value at risk: ₹{sum(t['amount'] for t in same_ministry_tenders):.0f} crore")
print()

# Save to CSV for analysis
with open("corruption_findings.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=linked_tenders[0].keys())
    writer.writeheader()
    writer.writerows(sorted(linked_tenders, key=lambda x: x["amount"], reverse=True))

print("✓ Saved findings to corruption_findings.csv")
print()
print("Analysis complete!")