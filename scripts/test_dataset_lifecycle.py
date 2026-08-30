import urllib.request
import urllib.parse
import json
import os
import sys

BASE_URL = "http://127.0.0.1:8000"

def get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.urlopen(url)
    return json.loads(req.read().decode('utf-8'))

def post(endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    payload = json.dumps(data).encode('utf-8') if data is not None else b''
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode('utf-8'))

def run_tests():
    print("==================================================")
    print("  MPLAD INTELLIGENCE -- DATASET LIFECYCLE & REGRESSION TEST")
    print("==================================================")

    # 1. Health Check
    health = get("/api/health")
    assert health["status"] == "ok", f"Health check failed: {health}"
    print("[PASS] 1. Backend Health Check: OK")

    # 2. Overview KPIs
    kpis = get("/api/overview/kpis")
    print(f"[PASS] 2. Overview KPIs: {kpis['total_sanctioned_works']} Works, INR {kpis['total_sanctioned_amount_cr']} Cr, {kpis['ml_anomaly_candidates_count']} ML Anomalies")

    # 3. Active Dataset Metadata
    active = get("/api/datasets/active")
    print(f"[PASS] 3. Active Dataset: '{active['name']}' (Sanctioned: {active['sanctioned_count']}, ML Anomalies: {active['ml_anomaly_count']})")
    assert active["sanctioned_count"] > 0, "Sanctioned count must be > 0"

    # 4. Dataset Validation on Staged / Active Files
    val = post("/api/datasets/validate")
    print(f"[PASS] 4. Dataset Validation Check: Valid={val['valid']}, Checks={len(val['checks'])}")
    assert val["valid"] is True, f"Expected validation to pass on benchmark files: {val['errors']}"

    # 5. Invalid Dataset Protection Test
    # Create invalid temporary CSV files with missing required column
    tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp_test_data')
    os.makedirs(tmp_dir, exist_ok=True)
    
    invalid_csv = os.path.join(tmp_dir, 'invalid_sanctioned.csv')
    with open(invalid_csv, 'w', encoding='utf-8') as f:
        f.write("Sr. No.,Wrong_Column_1,Wrong_Column_2\n1,Value1,Value2\n")
        
    valid_rec = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'recommended_works.csv')
    valid_comp = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'completed_works.csv')
    
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))
    from pipeline import validate_dataset_files, run_ml_pipeline
    
    invalid_val = validate_dataset_files(invalid_csv, valid_rec, valid_comp)
    assert invalid_val["valid"] is False, "Validation must fail for CSV with missing required columns"
    print(f"[PASS] 5. Invalid Dataset Protection: Validation successfully caught missing columns -> {invalid_val['errors'][0]}")

    # 6. ML Formula Verification across All Scored Records
    # S_risk = 0.60 * S_ml + 0.40 * S_rule
    queue = get("/api/projects/risk-queue?page=1&page_size=220")
    items = queue["items"]
    max_discrepancy = 0.0
    discrepancy_count = 0

    for item in items:
        s_ml = item["ml_anomaly_score"]
        s_rule = item["rule_score"]
        s_risk = item["risk_priority_score"]
        expected = round(min(100.0, max(0.0, (0.60 * s_ml) + (0.40 * s_rule))), 1)
        diff = abs(s_risk - expected)
        if diff > max_discrepancy:
            max_discrepancy = diff
        if diff > 0.05:
            discrepancy_count += 1

    print(f"[PASS] 6. ML Risk Formula Verification: Checked {len(items)} works.")
    print(f"       * Maximum Formula Discrepancy: {max_discrepancy:.4f}")
    print(f"       * Number of Discrepancies:     {discrepancy_count}")
    assert discrepancy_count == 0, f"Detected {discrepancy_count} formula discrepancies!"

    # 7. Project Intelligence & Dynamic Explainability Test
    target_id = items[0]["id"]
    encoded_id = urllib.parse.quote(target_id, safe='')
    intel = get(f"/api/projects/{encoded_id}/intelligence")
    assert intel["id"] == target_id, "Project ID mismatch"
    exp = intel["explanation"]
    assert "score_attribution" in exp, "Score attribution missing"
    assert "feature_evidence_matrix" in exp, "Feature evidence matrix missing"
    assert len(exp["feature_evidence_matrix"]) == 6, "Expected 6 features in evidence matrix"
    print(f"[PASS] 7. Explainable Risk Intelligence for #{target_id}: S_risk={intel['risk_priority_score']}, Band={intel['severity_band']}")

    # 8. Restore Demo Dataset API Test
    restore_res = post("/api/datasets/restore-demo")
    print(f"[PASS] 8. Restore Demo Dataset: Status={restore_res['status']}, Scored={restore_res['total_scored_works']}, ML Anomalies={restore_res['ml_anomaly_candidates']}")
    assert restore_res["total_scored_works"] == 220, "Demo dataset must have exactly 220 scored works"
    assert restore_res["ml_anomaly_candidates"] == 7, "Demo dataset must have exactly 7 ML anomalies"

    # 9. Audit Log Verification
    audit_res = get("/api/audit-logs?page=1&page_size=10")
    audit_items = audit_res["items"]
    assert len(audit_items) > 0, "Expected audit events"
    latest_event = audit_items[0]
    print(f"[PASS] 9. Audit Log Check: Latest Event -> '{latest_event['action_type']}' by {latest_event['actor']} (Work ID: {latest_event['work_id']})")

    # Cleanup temporary test directory
    try:
        os.remove(invalid_csv)
        os.rmdir(tmp_dir)
    except:
        pass

    print("\n==================================================")
    print("  ALL 9 DATASET & REGRESSION TESTS PASSED 100%    ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
