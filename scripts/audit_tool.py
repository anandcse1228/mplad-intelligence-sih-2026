import sqlite3
import os
import json
import re

db_path = r'C:\Users\HP\.gemini\antigravity\scratch\mplads_intelligence\backend\mplads.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("--- SQLITE SCHEMA & TABLES ---")
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
for t in tables:
    t_name = t[0]
    if t_name == 'sqlite_sequence': continue
    c.execute(f"PRAGMA table_info({t_name});")
    cols = [col[1] for col in c.fetchall()]
    c.execute(f"SELECT count(*) FROM {t_name};")
    cnt = c.fetchone()[0]
    print(f"Table: {t_name} ({cnt} rows) -> Columns: {cols}")

print("\n--- DATASETS IN METADATA ---")
c.execute("SELECT dataset_id, name, state, district, sanctioned_count, ml_anomaly_count, is_active FROM dataset_metadata;")
for row in c.fetchall():
    print(" ", row)

print("\n--- FORMULA VERIFICATION ACROSS ALL STORED ML SCORED WORKS ---")
c.execute("SELECT id, dataset_id, work_id, ml_anomaly_score, rule_score, risk_priority_score, severity_band FROM ml_scored_works;")
rows = c.fetchall()
mismatches = 0
max_diff = 0.0
for r in rows:
    pk, ds_id, wid, s_ml, s_rule, s_risk, band = r
    expected = round(min(100.0, max(0.0, 0.60 * s_ml + 0.40 * s_rule)), 1)
    diff = abs(s_risk - expected)
    if diff > max_diff:
        max_diff = diff
    if diff > 0.05:
        mismatches += 1
        print(f"  MISMATCH: {pk} (ds: {ds_id}) -> s_ml={s_ml}, s_rule={s_rule}, stored={s_risk}, expected={expected}")

print(f"Total ML Scored Works: {len(rows)}")
print(f"Total Records Verified: {len(rows)}")
print(f"Formula Mismatches: {mismatches}")
print(f"Maximum Discrepancy: {max_diff:.4f}")

conn.close()
