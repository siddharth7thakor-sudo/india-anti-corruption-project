# analyze_evidence.py - Surat SMC Anti-Corruption Tracker
"""
Reads scraped data files and produces ranked evidence,
evidence hits, keyword summaries, and case timelines.
"""

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("surat-smc-tracker")

RISK_KEYWORDS = [
    "amendment", "revised estimate", "direct award",
    "single source", "urgent", "without tender",
    "extension of time", "supplementary", "cost escalation",
    "variation order", "splitting", "cartel", "kickback",
    "irregularity", "inflated", "fake certificate",
    "sub-standard", "quality failure",
]


def read_csv(filename):
    filepath = OUTPUT_DIR / filename
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return []
    with open(filepath, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(rows, filename, fieldnames):
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows -> {filepath}")


def keyword_scan(text, keywords):
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def risk_score(hits):
    return len(hits) * 10


def analyze_projects():
    projects = read_csv("projects.csv")
    evidence_hits = []
    ranked = []
    for p in projects:
        combined_text = " ".join(p.values())
        hits = keyword_scan(combined_text, RISK_KEYWORDS)
        score = risk_score(hits)
        if hits:
            evidence_hits.append({
                "source": "projects.csv",
                "record_id": p.get("project_id", p.get("id", "")),
                "title": p.get("title", p.get("name", "")),
                "keywords_found": "; ".join(hits),
                "risk_score": score,
                "flagged_at": datetime.now().isoformat(),
            })
        ranked.append({
            "source": "projects.csv",
            "record_id": p.get("project_id", p.get("id", "")),
            "title": p.get("title", p.get("name", "")),
            "risk_score": score,
            "keywords_found": "; ".join(hits),
        })
    return evidence_hits, ranked


def analyze_tp_details():
    tp_rows = read_csv("tp_details.csv")
    hits = []
    for row in tp_rows:
        combined = " ".join(row.values())
        found = keyword_scan(combined, RISK_KEYWORDS)
        if found:
            hits.append({
                "source": "tp_details.csv",
                "record_id": row.get("tp_id", row.get("id", "")),
                "title": row.get("title", row.get("description", "")),
                "keywords_found": "; ".join(found),
                "risk_score": risk_score(found),
                "flagged_at": datetime.now().isoformat(),
            })
    return hits


def build_keyword_summary(all_hits):
    counter = Counter()
    for hit in all_hits:
        for kw in hit.get("keywords_found", "").split("; "):
            if kw:
                counter[kw] += 1
    return [
        {"keyword": kw, "count": count, "severity": "HIGH" if count >= 3 else "MEDIUM"}
        for kw, count in counter.most_common()
    ]


def build_case_timeline(all_hits):
    timeline = []
    for idx, hit in enumerate(all_hits, start=1):
        timeline.append({
            "event_no": idx,
            "date": hit.get("flagged_at", "")[:10],
            "source": hit.get("source", ""),
            "record_id": hit.get("record_id", ""),
            "title": hit.get("title", ""),
            "keywords_found": hit.get("keywords_found", ""),
            "risk_score": hit.get("risk_score", 0),
        })
    timeline.sort(key=lambda x: (x["date"], -int(x["risk_score"])))
    return timeline


def main():
    print("=" * 60)
    print("Evidence Analyzer - Surat SMC Tracker")
    print("=" * 60)
    all_hits = []
    ranked_all = []
    project_hits, project_ranked = analyze_projects()
    all_hits.extend(project_hits)
    ranked_all.extend(project_ranked)
    tp_hits = analyze_tp_details()
    all_hits.extend(tp_hits)
    print(f"\nTotal evidence hits: {len(all_hits)}")
    ranked_all.sort(key=lambda x: -int(x["risk_score"]))
    keyword_summary = build_keyword_summary(all_hits)
    case_timeline = build_case_timeline(all_hits)
    write_csv(all_hits, "evidence_hits.csv",
              ["source", "record_id", "title", "keywords_found", "risk_score", "flagged_at"])
    write_csv(ranked_all, "ranked_evidence.csv",
              ["source", "record_id", "title", "risk_score", "keywords_found"])
    write_csv(keyword_summary, "keyword_summary.csv",
              ["keyword", "count", "severity"])
    write_csv(case_timeline, "case_timeline.csv",
              ["event_no", "date", "source", "record_id", "title", "keywords_found", "risk_score"])
    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
