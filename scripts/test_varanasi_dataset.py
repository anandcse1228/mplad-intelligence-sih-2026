import sys
sys.path.append('backend')
from pipeline import validate_dataset_files, run_ml_pipeline

sanct = 'data/staging/sanctioned_works.csv'
rec = 'data/staging/recommended_works.csv'
comp = 'data/staging/completed_works.csv'

val = validate_dataset_files(sanct, rec, comp)
print("=== 1. VALIDATION RESULT FOR VARANASI (UP) DATASET ===")
print("Valid:", val["valid"])
print("Sanctioned count:", val["sanctioned_count"])
print("Recommended count:", val["recommended_count"])
print("Completed count:", val["completed_count"])
print("Warnings:", val["warnings"])
print("Errors:", val["errors"])

for c in val["checks"]:
    print(f"  [{c['status']}] {c['name']}: {c['message']}")

if val["valid"]:
    ml_res = run_ml_pipeline(sanct, rec, comp)
    meta = ml_res["metadata"]
    print("\n=== 2. REAL ML PIPELINE EXECUTION FOR VARANASI DATASET ===")
    print(f"• Total Scored Works: {meta['total_scored']}")
    print(f"• ML Anomalies (S_ml >= 70): {meta['anomaly_count']}")
    print(f"• Critical Risk Priority: {meta['critical_count']}")
    print(f"• High Risk Priority: {meta['high_count']}")
    print(f"• Medium Risk Priority: {meta['medium_count']}")
    print(f"• Normal Risk: {meta['normal_count']}")
    print(f"• Dataset Mean Delay: {meta['mean_delay_baseline']} Days")
    
    print("\n=== 3. TOP 5 SCORED WORKS FOR VARANASI ===")
    for w in ml_res["works"][:5]:
        print(f"  #{w['id']} | District: {w['district']}, {w['state']} | S_risk: {w['risk_priority_score']} (S_ml: {w['ml_anomaly_score']}, S_rule: {w['rule_score']}) | Band: {w['severity_band']}")
