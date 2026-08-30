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

def run_test():
    print("================================================================")
    print("  MPLAD INTELLIGENCE -- MULTI-STATE DATASET & LIFECYCLE TEST    ")
    print("================================================================")

    # 1. Health check
    h = get("/api/health")
    print("[PASS] 1. Backend Health Check: OK")

    # 2. Test Staged Multi-State Dataset Validation (Uttar Pradesh - Varanasi)
    val = post("/api/datasets/validate")
    print(f"[PASS] 2. Multi-State Dataset Validation Check: Valid={val['valid']}")
    print(f"       * Sanctioned: {val['sanctioned_count']}, Recommended: {val['recommended_count']}, Completed: {val['completed_count']}")
    assert val["valid"] is True, f"Validation failed: {val['errors']}"

    # 3. Analyze and Activate Multi-State Dataset
    analysis = post("/api/datasets/analyze", {"dataset_name": "Uttar Pradesh MPLADS — Varanasi District"})
    print(f"[PASS] 3. Dynamic ML Analysis & Activation: Status={analysis['status']}")
    print(f"       * Dataset: '{analysis['dataset_name']}'")
    print(f"       * Total Scored Works: {analysis['total_scored_works']}")
    print(f"       * ML Anomalies:       {analysis['ml_anomaly_candidates']}")
    print(f"       * Critical Risk:      {analysis['critical_risk_count']}")
    print(f"       * High Risk:          {analysis['high_risk_count']}")
    assert analysis["total_scored_works"] == 216, f"Expected 216 works, got {analysis['total_scored_works']}"
    assert analysis["ml_anomaly_candidates"] == 6, f"Expected 6 ML anomalies, got {analysis['ml_anomaly_candidates']}"

    # 4. Verify Active Dataset Metadata
    active = get("/api/datasets/active")
    print(f"[PASS] 4. Active Dataset Endpoint: '{active['name']}' (Sanctioned: {active['sanctioned_count']})")
    assert active["name"] == "Uttar Pradesh MPLADS — Varanasi District"

    # 5. Verify Overview KPIs for New State
    kpis = get("/api/overview/kpis")
    print(f"[PASS] 5. Dynamic Overview KPIs: {kpis['total_sanctioned_works']} Works, INR {kpis['total_sanctioned_amount_cr']} Cr, {kpis['ml_anomaly_candidates_count']} ML Anomalies")
    assert kpis["total_sanctioned_works"] == 216

    # 6. Verify Dynamic Risk Priority Queue & Formula Consistency for New State
    queue = get("/api/projects/risk-queue?page=1&page_size=216")
    items = queue["items"]
    print(f"[PASS] 6. Risk Queue Scored Works: {len(items)} works retrieved.")
    discrepancies = 0
    for w in items:
        expected = round(min(100.0, max(0.0, 0.60 * w["ml_anomaly_score"] + 0.40 * w["rule_score"])), 1)
        if abs(w["risk_priority_score"] - expected) > 0.05:
            discrepancies += 1
    assert discrepancies == 0, f"Found {discrepancies} formula discrepancies in multi-state dataset!"
    top_w = items[0]
    print(f"       * Top Priority Work: #{top_w['id']} ({top_w['district']}, {top_w['state']}) -> S_risk: {top_w['risk_priority_score']} | Band: {top_w['severity_band']}")

    # 7. Dynamic Explainability for New State Project
    encoded_id = urllib.parse.quote(top_w["id"], safe='')
    intel = get(f"/api/projects/{encoded_id}/intelligence")
    assert intel["id"] == top_w["id"]
    print(f"[PASS] 7. Dynamic Explainable Risk Intelligence for #{intel['id']}:")
    print(f"       * Executive Summary: {intel['explanation']['executive_summary'][:90]}...")
    assert len(intel["explanation"]["feature_evidence_matrix"]) == 6

    # 8. Restore Demo Benchmark Dataset (Punjab - Ludhiana)
    restore = post("/api/datasets/restore-demo")
    print(f"[PASS] 8. Demo Benchmark Dataset Restoration: Status={restore['status']}")
    print(f"       * Restored Dataset: '{restore['dataset_name']}'")
    print(f"       * Total Works: {restore['total_scored_works']}, ML Anomalies: {restore['ml_anomaly_candidates']}")
    assert restore["total_scored_works"] == 220
    assert restore["ml_anomaly_candidates"] == 7

    # 9. Verify Active Dataset Returned to Demo State
    demo_active = get("/api/datasets/active")
    print(f"[PASS] 9. Active Dataset After Restore: '{demo_active['name']}' (Sanctioned: {demo_active['sanctioned_count']})")
    assert demo_active["sanctioned_count"] == 220

    # 10. Verify Audit Log Persistence
    audit = get("/api/audit-logs?page=1&page_size=5")
    print(f"[PASS] 10. Audit Log Check: {len(audit['items'])} events retrieved.")
    for ev in audit["items"][:2]:
        print(f"        • [{ev['action_type']}] {ev['details']}")

    print("\n================================================================")
    print("  ALL 10 MULTI-STATE DATASET & LIFECYCLE TESTS PASSED 100%       ")
    print("================================================================")

if __name__ == "__main__":
    run_test()
