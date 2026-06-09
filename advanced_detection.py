import csv
import re

def fuzzy_match(name1, name2):
    """Basic fuzzy matching for names."""
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
        print(f"Warning: {file_path} not found.")
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
            if growth > 0.5:  # Arbitrary 50% growth threshold
                asset_growth_risk = True

        # 2. Procurement Risk
        procurement_risk = False
        linked_tenders = [t for t in tenders if fuzzy_match(t['contractor_name'], p_name)]
        if len(linked_tenders) > 3:
            procurement_risk = True

        if asset_growth_risk or procurement_risk:
            risk_reports.append({
                'politician_id': p_id,
                'name': p_name,
                'asset_growth_risk': asset_growth_risk,
                'procurement_risk': procurement_risk
            })

    return risk_reports

if __name__ == "__main__":
    reports = analyze_corruption_risk()
    for report in reports:
        print(report)
