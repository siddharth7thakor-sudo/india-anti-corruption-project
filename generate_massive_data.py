#!/usr/bin/env python3
"""
GENERATE MASSIVE DATA: Creates comprehensive sample dataset for India Anti-Corruption Project
Generates 1000+ politicians across Indian states, their declared assets, and government tenders
Demonstrates data linking and corruption detection at scale
"""

import csv
import random
from datetime import datetime, timedelta

# Indian states and union territories
INDIAN_STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
    'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya',
    'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim',
    'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand',
    'West Bengal', 'Delhi', 'Jammu & Kashmir', 'Ladakh'
]

FIRST_NAMES = [
    'Rajesh', 'Priya', 'Amit', 'Neha', 'Vikram', 'Sanjay', 'Kavya', 'Arun',
    'Deepak', 'Anjali', 'Manoj', 'Ritika', 'Suresh', 'Pooja', 'Ramesh',
    'Nisha', 'Arjun', 'Meera', 'Akshay', 'Divya', 'Rohan', 'Shweta'
]

LAST_NAMES = [
    'Singh', 'Kumar', 'Sharma', 'Patel', 'Verma', 'Yadav', 'Gupta', 'Desai',
    'Reddy', 'Nair', 'Pandey', 'Tiwari', 'Joshi', 'Bhat', 'Menon', 'Chopra'
]

PARTIES = ['Party A', 'Party B', 'Party C', 'Party D', 'Party E']

MINISTRIES = [
    'Ministry of Roads', 'Ministry of Health', 'Ministry of Education',
    'Ministry of Defence', 'Ministry of Energy', 'Ministry of Agriculture',
    'Ministry of Commerce', 'Ministry of Finance', 'Ministry of Urban Development'
]

CONTRACTORS = [
    'Apex Infrastructure Ltd', 'Royal Builders', 'MedEquip Solutions',
    'Sunshine Constructions', 'HealthFirst Corp', 'Golden Projects Inc',
    'Tech Solutions Ltd', 'Build Strong Ltd', 'Premium Infrastructure'
]

def generate_politicians(count=1000):
    """Generate politician records with realistic Indian names"""
    politicians = []
    for i in range(1, count + 1):
        politician = {
            'politician_id': i,
            'name': f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            'party': random.choice(PARTIES),
            'role': random.choice(['Minister', 'MP', 'State Minister', 'MLA'])
        }
        politicians.append(politician)
    return politicians

def generate_assets(politicians, years_range=5):
    """Generate asset declarations for politicians across multiple years"""
    assets = []
    for politician in politicians:
        base_assets = random.randint(1000000, 50000000)
        for year in range(2019, 2019 + years_range):
            # Simulate asset growth pattern (can indicate corruption)
            growth_factor = random.uniform(1.1, 1.4) if random.random() > 0.7 else random.uniform(0.95, 1.1)
            declared = int(base_assets * (growth_factor ** (year - 2019)))
            asset_record = {
                'politician_id': politician['politician_id'],
                'year': year,
                'declared_assets': declared
            }
            assets.append(asset_record)
    return assets

def generate_tenders(politicians, count=5000):
    """Generate government tender records that may be linked to politicians"""
    tenders = []
    tender_id = 1
    
    for _ in range(count):
        tender = {
            'tender_id': f"T{tender_id:05d}",
            'ministry': random.choice(MINISTRIES),
            'contractor_name': random.choice(CONTRACTORS),
            'amount': random.randint(1000000, 100000000),
            'year': random.randint(2014, 2024)
        }
        tenders.append(tender)
        tender_id += 1
    
    return tenders

def write_csv(filename, data, fieldnames):
    """Write data to CSV file"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"\u2714 Generated {filename} with {len(data)} records")
    except Exception as e:
        print(f"\u2717 Error writing {filename}: {e}")

def main():
    print("\n" + "="*80)
    print("INDIA ANTI-CORRUPTION PROJECT: MASSIVE DATA GENERATOR")
    print("="*80 + "\n")
    
    # Generate data
    print("Generating politician records...")
    politicians = generate_politicians(count=1000)
    
    print("Generating asset declarations...")
    assets = generate_assets(politicians, years_range=6)  # 2019-2024
    
    print("Generating tender records...")
    tenders = generate_tenders(politicians, count=5000)
    
    # Write to CSV files
    print("\nWriting to CSV files...\n")
    
    write_csv('politicians.csv', politicians, 
              ['politician_id', 'name', 'party', 'role'])
    
    write_csv('assets.csv', assets, 
              ['politician_id', 'year', 'declared_assets'])
    
    write_csv('tenders.csv', tenders, 
              ['tender_id', 'ministry', 'contractor_name', 'amount', 'year'])
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\u2714 Total politicians: {len(politicians)}")
    print(f"\u2714 Total asset records: {len(assets)}")
    print(f"\u2714 Total tenders: {len(tenders)}")
    print(f"\u2714 Data points for analysis: {len(assets) + len(tenders)}")
    print(f"\u2714 Ready for data linking and corruption detection!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()