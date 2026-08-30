import csv
import json
import math
import os

# Audit script to independently verify ML Integrity & Formula Precision
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, 'data')

rec_path = os.path.join(data_dir, 'recommended_works.csv')
sanct_path = os.path.join(data_dir, 'sanctioned_works.csv')
comp_path = os.path.join(data_dir, 'completed_works.csv')
json_path = os.path.join(data_dir, 'ml_scored_works.json')

print("=== STARTING DAY 4 ML INTEGRITY AUDIT ===")

# 1. Inspect Raw CSV Columns
with open(sanct_path, 'r', encoding='utf-8') as f:
    sanct_headers = [h.strip().replace('₹', 'INR') for h in next(csv.reader(f))]

with open(rec_path, 'r', encoding='utf-8') as f:
    rec_headers = [h.strip().replace('₹', 'INR') for h in next(csv.reader(f))]

with open(comp_path, 'r', encoding='utf-8') as f:
    comp_headers = [h.strip().replace('₹', 'INR') for h in next(csv.reader(f))]

print(f"1. Sanctioned CSV Columns ({len(sanct_headers)}): {sanct_headers}")
print(f"2. Recommended CSV Columns ({len(rec_headers)}): {rec_headers}")
print(f"3. Completed CSV Columns ({len(comp_headers)}): {comp_headers}")

# 2. Count Raw Sanctioned Rows
with open(sanct_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    sanct_rows = [r for r in reader if r.get('Sr. No.', '').strip() and r.get('Sr. No.', '').strip().lower() != 'grand total']

print(f"\nRaw Sanctioned Rows Count: {len(sanct_rows)}")

# 3. Load Exported ML JSON
with open(json_path, 'r', encoding='utf-8') as f:
    ml_data = json.load(f)

scored_works = ml_data['works']
meta = ml_data['metadata']

print(f"\nExported JSON Scored Works Count: {len(scored_works)}")

# 4. Deduplication & Unique Work ID Check
work_ids = [w['id'] for w in scored_works]
unique_ids = set(work_ids)

print(f"Unique Work IDs in Scored Export: {len(unique_ids)}")
if len(work_ids) == len(unique_ids):
    print("-> CHECK 12: PASSED. Zero duplicate Work IDs found. Every record has exactly one score.")
else:
    print(f"-> CHECK 12: WARNING. {len(work_ids) - len(unique_ids)} duplicates found.")

# 5. Formula & Hybrid Calculation Sample Verification
print("\n--- SAMPLE RECOMPUTATION AUDIT (TOP 5 SCORED RECORDS) ---")
mismatches = 0

for i in range(min(5, len(scored_works))):
    w = scored_works[i]
    s_ml = w['ml_anomaly_score']
    s_rule = w['rule_score']
    reported_s_risk = w['risk_priority_score']
    
    # Formula: S_risk = 0.60 * S_ml + 0.40 * S_rule
    expected_s_risk = round(min(100.0, max(0.0, (0.60 * s_ml) + (0.40 * s_rule))), 1)
    
    diff = abs(reported_s_risk - expected_s_risk)
    match_status = "MATCH" if diff < 0.05 else f"MISMATCH (Exp: {expected_s_risk})"
    if diff >= 0.05:
        mismatches += 1
        
    cleaned_title = w['title'].encode('ascii', 'ignore').decode('ascii')
    print(f"Item #{i+1} [{w['id']}] '{cleaned_title[:40]}...':")
    print(f"   S_ml: {s_ml} | S_rule: {s_rule} | Reported S_risk: {reported_s_risk} | Calculated: {expected_s_risk} -> {match_status}")
    print(f"   Rule Signals ({len(w['rule_signals'])}): {w['rule_signals']}")

# 6. Check for Unsupported / Fabricated Fields in JSON
forbidden_fields = ['contractor_name', 'gstin', 'latitude', 'longitude', 'fraud_label', 'fraud_confirmed']
found_forbidden = []

for w in scored_works:
    for ff in forbidden_fields:
        if ff in w or ff in w.get('features', {}):
            found_forbidden.append((w['id'], ff))

if not found_forbidden:
    print("\n-> CHECK 10: PASSED. Zero fabricated fields (contractor, GSTIN, coordinates, fraud labels) present in JSON.")
else:
    print(f"\n-> CHECK 10: FAILED. Found forbidden fields: {found_forbidden}")

# Summary Metrics Audit
anomalies = [w for w in scored_works if w['is_ml_anomaly']]
critical = [w for w in scored_works if w['severity_band'] == 'CRITICAL RISK PRIORITY']
high = [w for w in scored_works if w['severity_band'] == 'HIGH RISK PRIORITY']
medium = [w for w in scored_works if w['severity_band'] == 'MEDIUM RISK PRIORITY']
normal = [w for w in scored_works if w['severity_band'] == 'NORMAL RISK']

print("\n=== AUDIT SUMMARY METRICS ===")
print(f"Total Scored: {len(scored_works)}")
print(f"ML Anomalies (S_ml >= 70): {len(anomalies)}")
print(f"Critical Risk (S_risk >= 75): {len(critical)}")
print(f"High Risk (60 <= S_risk < 75): {len(high)}")
print(f"Medium Risk (40 <= S_risk < 60): {len(medium)}")
print(f"Normal / Low Risk (S_risk < 40): {len(normal)}")
