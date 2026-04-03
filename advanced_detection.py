import csv
import re

def fuzzy_match(name1, name2):
    \"\"\"Basic fuzzy matching for names.\"\"\"
    n1 = re.sub(r'[^a-zA-Z0-9]', '', name1.lower())
    n2 = re.sub(r'[^a-zA-Z0-9]', '', name2.lower())
    return n1 in n2 or n2 in n1

def load_data(file_path):
    data = []
    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f\"Warning: {file_path} not found.\")
    return data

def analyze_corruption_risk():
    politicians = load_data('politicians.csv')
    assets = load_data('assets.csv')
    tenders = load_data('tenders.csv')
    
    risk_reports = []

    for p in politicians:
        p_id = p['politician_id']
        p_name = p['name']
        
        # 1. Asset Growth Risk
        p_assets = [float(a['declared_assets']) for a in assets if a['politician_id'] == p_id]
        asset_growth_risk = False
        if len(p_assets) >= 2:
            growth = (p_assets[-1] - p_assets[0]) / p_assets[0]
            if growth > 0.3:  # 30% growth threshold
                asset_growth_risk = True

        # 2. Tender Concentration Risk
        p_tenders = [t for t in tenders if fuzzy_match(p_name, t['contractor'])]
        tender_count = len(p_tenders)
        total_tender_value = sum(float(t['amount']) for t in p_tenders)

        # 3. Conflict of Interest (Ministry Match)
        conflicts = []
        for t in p_tenders:
            if fuzzy_match(p['role'], t['ministry']):
                conflicts.append(t)

        if asset_growth_risk or tender_count > 0 or conflicts:
            risk_reports.append({
                'name': p_name,
                'asset_growth_risk': asset_growth_risk,
                'tender_count': tender_count,
                'total_tender_value': total_tender_value,
                'conflicts': len(conflicts)
            })

    print(\"\
=== ADVANCED CORRUPTION RISK REPORT ===\")
    for report in risk_reports:
        print(f\"\
Politician: {report['name']}\")
        if report['asset_growth_risk']:
            print(\"  🚩 HIGH ASSET GROWTH (>30%)\")
        if report['tender_count'] > 0:
            print(f\"  🚩 TENDER WINS DETECTED: {report['tender_count']} contract(s) total ₹{report['total_tender_value']}\")
        if report['conflicts'] > 0:
            print(f\"  🚨 CONFLICT OF INTEREST: {report['conflicts']} tender(s) from own ministry!\")

if __name__ == \"__main__\":
    analyze_corruption_risk()
