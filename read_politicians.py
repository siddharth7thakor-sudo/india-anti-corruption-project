import csv

# Open the CSV file
with open("politicians.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    print("List of politicians:")
    print("--------------------")
    for row in reader:
        pid = row["politician_id"]
        name = row["name"]
        party = row["party"]
        role = row["role"]
        print(f"ID: {pid} | Name: {name} | Party: {party} | Role: {role}")
