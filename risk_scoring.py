import csv

def calculate_risk_scores():
    # Load data (simulated for simplicity)
    # In a real app, this would load from CSVs/Database
    politicians = [
        {'id': 1, 'name': 'Asha Verma', 'growth': 1.13, 'tenders': 0, 'conflicts': 0},
        {'id': 2, 'name': 'Rahul Singh', 'growth': 0.80, 'tenders': 4, 'conflicts': 4},
        {'id': 3, 'name': 'Meera Iyer', 'growth': 0.50, 'tenders': 0, 'conflicts': 0},
        {'id': 4, 'name': 'Arjun Patel', 'growth': 0.05, 'tenders': 0, 'conflicts': 0},
    ]

    # Weights for risk factors
    WEIGHTS = {
        'growth': 40,    # 40% weight to suspicious asset growth
        'tenders': 30,   # 30% weight to tender wins
        'conflicts': 30  # 30% weight to own-ministry conflicts
    }

    print("=== CORRUPTION RISK SCORING ===")

    for p in politicians:
        # Normalize scores (0-100)
        # Growth > 30% is high risk
        growth_score = min(100, (p['growth'] / 0.3) * 100) if p['growth'] > 0 else 0
        
        # More than 2 tenders is high risk
        tender_score = min(100, (p['tenders'] / 2) * 100)
        
        # Any conflict is high risk
        conflict_score = 100 if p['conflicts'] > 0 else 0

        # Calculate final weighted score
        final_score = (
            (growth_score * (WEIGHTS['growth'] / 100)) +
            (tender_score * (WEIGHTS['tenders'] / 100)) +
            (conflict_score * (WEIGHTS['conflicts'] / 100))
        )

        risk_level = "LOW"
        if final_score > 70:
            risk_level = "CRITICAL 🚨"
        elif final_score > 40:
            risk_level = "MEDIUM ⚠️"

        print(f"\nPolitician: {p['name']}")
        print(f" Risk Score: {final_score:.1f}/100")
        print(f" Risk Level: {risk_level}")

if __name__ == "__main__":
    calculate_risk_scores()
