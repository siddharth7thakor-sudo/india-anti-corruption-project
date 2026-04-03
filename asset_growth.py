import csv

# Step 1: load politicians into a dictionary
politicians = {}
with open("politicians.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pid = row["politician_id"]
        politicians[pid] = {
            "name": row["name"],
            "party": row["party"],
            "role": row["role"],
        }

# Step 2: load assets and group by politician_id
assets_by_pid = {}
with open("assets.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pid = row["politician_id"]
        year = int(row["year"])
        amount = float(row["declared_assets"])

        if pid not in assets_by_pid:
            assets_by_pid[pid] = {}
        assets_by_pid[pid][year] = amount

# Step 3: compute growth between 2014 and 2019
print("Asset growth between 2014 and 2019")
print("----------------------------------")

for pid, info in politicians.items():
    name = info["name"]
    party = info["party"]
    role = info["role"]

    years = assets_by_pid.get(pid, {})
    a2014 = years.get(2014)
    a2019 = years.get(2019)

    if a2014 is None or a2019 is None:
        print(f"{name}: missing asset data")
        continue

    growth_abs = a2019 - a2014
    growth_pct = (growth_abs / a2014) * 100 if a2014 != 0 else 0

    print(
        f"ID: {pid} | {name} ({party}, {role}) | "
        f"2014: {a2014:.0f} | 2019: {a2019:.0f} | "
        f"Growth: {growth_abs:.0f} ({growth_pct:.1f}%)"
    )
