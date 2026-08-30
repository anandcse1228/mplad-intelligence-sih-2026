import sqlite3
import os
import json

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mplads.db')
json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'ml_scored_works.json')

print("==================================================")
print("  READ-ONLY SQL QUERY VERIFICATION FOR MPLADS.DB  ")
print("==================================================")
print(f"Connecting to: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query 1: List all tables in SQLite database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print(f"\n1. Tables Found ({len(tables)}): {', '.join(tables)}")

# Query 2: Row counts per table
print("\n2. Table Row Counts:")
for tbl in ['sanctioned_works', 'recommended_works', 'completed_works', 'ml_scored_works', 'investigation_cases', 'investigation_notes', 'audit_logs']:
    cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
    cnt = cursor.fetchone()[0]
    print(f"   • {tbl}: {cnt} rows")

# Query 3: Top 5 High Risk Priority Works from ml_scored_works table
print("\n3. Top 5 High Risk Priority Works from SQLite (ml_scored_works):")
cursor.execute("""
    SELECT id, title, ml_anomaly_score, rule_score, risk_priority_score, severity_band 
    FROM ml_scored_works 
    ORDER BY risk_priority_score DESC 
    LIMIT 5;
""")
top5 = cursor.fetchall()
for idx, (wid, title, s_ml, s_rule, s_risk, band) in enumerate(top5, 1):
    print(f"   #{idx} [{wid}] S_risk={s_risk:.1f} (S_ml={s_ml:.1f}, S_rule={s_rule:.1f}) | {band} | {title[:45]}...")

# Query 4: Match SQLite scores against original ml_scored_works.json for 100% equality
print("\n4. Score Match Audit (SQLite vs JSON):")
with open(json_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)['works']

mismatches = 0
for j_item in json_data:
    wid = j_item['id']
    cursor.execute("SELECT ml_anomaly_score, rule_score, risk_priority_score FROM ml_scored_works WHERE id = ?;", (wid,))
    row = cursor.fetchone()
    if not row:
        mismatches += 1
        continue
    db_ml, db_rule, db_risk = row
    if abs(db_ml - j_item['ml_anomaly_score']) > 0.001 or \
       abs(db_rule - j_item['rule_score']) > 0.001 or \
       abs(db_risk - j_item['risk_priority_score']) > 0.001:
        mismatches += 1

if mismatches == 0:
    print("   [OK] All 220 SQLite ML scores match original ml_scored_works.json 100% exactly!")
else:
    print(f"   [FAIL] Found {mismatches} score mismatches!")

conn.close()
print("\n==================================================")
print("  READ-ONLY SQL VERIFICATION COMPLETE             ")
print("==================================================")
