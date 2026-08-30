import urllib.request
import json
import os

BASE_URL = "http://127.0.0.1:8000"

def make_request(url, method="GET", body=None):
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
            return resp.status, json.loads(content)
    except urllib.error.HTTPError as e:
        content = e.read().decode('utf-8')
        try:
            return e.code, json.loads(content)
        except Exception:
            return e.code, content

print("==================================================")
print("  MPLAD INTELLIGENCE — FASTAPI REST API SUITE AUDIT")
print("==================================================")

real_work_id = "WS/MP18157/2024-2025/163249"

# Test 1: GET /api/health
status_code, data = make_request(f"{BASE_URL}/api/health")
print(f"\n1. GET /api/health -> Status: {status_code} | Response: {data}")

# Test 2: GET /api/overview/kpis
status_code, data = make_request(f"{BASE_URL}/api/overview/kpis")
print(f"\n2. GET /api/overview/kpis -> Status: {status_code}")
print(f"   • Total Sanctioned Works: {data['total_sanctioned_works']} (INR {data['total_sanctioned_amount_cr']} Cr)")
print(f"   • Total Recommended Works: {data['total_recommended_works']} (INR {data['total_recommended_amount_cr']} Cr)")
print(f"   • Total Completed Works: {data['total_completed_works']} (INR {data['total_disbursed_amount_cr']} Cr)")
print(f"   • ML Anomalies: {data['ml_anomaly_candidates_count']} | High Risk: {data['high_risk_count']} | Medium: {data['medium_risk_count']} | Normal: {data['normal_risk_count']}")

# Test 3: GET /api/projects/risk-queue?page=1&page_size=15
status_code, data = make_request(f"{BASE_URL}/api/projects/risk-queue?page=1&page_size=15")
print(f"\n3. GET /api/projects/risk-queue (page_size=15) -> Status: {status_code}")
print(f"   • Returned Items: {len(data['items'])} | Page: {data['page']}/{data['total_pages']} | Total: {data['total']}")

# Test 4: GET /api/projects/risk-queue?page=1&page_size=50
status_code, data = make_request(f"{BASE_URL}/api/projects/risk-queue?page=1&page_size=50")
print(f"\n4. GET /api/projects/risk-queue (page_size=50) -> Status: {status_code}")
print(f"   • Returned Items: {len(data['items'])} | Page: {data['page']}/{data['total_pages']} | Total: {data['total']}")
print(f"   • Rank #1 Work: [{data['items'][0]['id']}] S_risk={data['items'][0]['risk_priority_score']} (S_ml={data['items'][0]['ml_anomaly_score']}, S_rule={data['items'][0]['rule_score']})")

# Test 5: GET /api/projects/{real_work_id}/intelligence
status_code, data = make_request(f"{BASE_URL}/api/projects/{real_work_id}/intelligence")
print(f"\n5. GET /api/projects/{real_work_id}/intelligence -> Status: {status_code}")
print(f"   • Title: {data['title'][:50]}...")
print(f"   • S_risk: {data['risk_priority_score']} | S_ml: {data['ml_anomaly_score']} | S_rule: {data['rule_score']}")
print(f"   • Features count: {len(data['features'])} | Rule signals: {len(data['rule_signals'])}")

# Test 6: GET /api/projects/{real_work_id}/investigation
status_code, data = make_request(f"{BASE_URL}/api/projects/{real_work_id}/investigation")
print(f"\n6. GET /api/projects/{real_work_id}/investigation -> Status: {status_code}")
print(f"   • Work ID: {data['work_id']} | Status: {data['current_status']}")

# Test 7: POST /api/projects/{real_work_id}/investigation-action
status_code, data = make_request(
    f"{BASE_URL}/api/projects/{real_work_id}/investigation-action",
    method="POST",
    body={"action": "MARK_FOR_FIELD_VERIFICATION", "actor": "State Nodal Officer", "details": "Field audit assigned"}
)
print(f"\n7. POST /api/projects/{real_work_id}/investigation-action -> Status: {status_code}")
print(f"   • Updated Status: {data.get('previous_status')} -> {data.get('new_status')} | Action: {data.get('action')}")

# Test 8: GET /api/audit-logs
status_code, data = make_request(f"{BASE_URL}/api/audit-logs")
print(f"\n8. GET /api/audit-logs -> Status: {status_code}")
print(f"   • Total Audit Logs: {data['total']} | Returned Items: {len(data['items'])}")
if data['items']:
    print(f"   • Event #1: [{data['items'][0]['work_id']}] {data['items'][0]['action_type']} | {data['items'][0]['timestamp']}")

# Test 9: POST /api/projects/{real_work_id}/notes
status_code, data = make_request(
    f"{BASE_URL}/api/projects/{real_work_id}/notes",
    method="POST",
    body={"note_text": "Site measurement verified with local engineer.", "officer_name": "State Nodal Officer"}
)
print(f"\n9. POST /api/projects/{real_work_id}/notes -> Status: {status_code}")
print(f"   • Saved Note ID: {data.get('id')} | Text: '{data.get('note_text')}'")

# Test 10: GET /api/projects/{real_work_id}/notes
status_code, data = make_request(f"{BASE_URL}/api/projects/{real_work_id}/notes")
print(f"\n10. GET /api/projects/{real_work_id}/notes -> Status: {status_code}")
print(f"    • Total Notes for Work: {len(data)}")

# Test 11: DELETE /api/audit-logs
status_code, data = make_request(f"{BASE_URL}/api/audit-logs", method="DELETE")
print(f"\n11. DELETE /api/audit-logs -> Status: {status_code}")
print(f"    • Cleared Audit Records: {data.get('deleted_audit_records')}")

# Test 12: GET /api/audit-logs (After clearing)
status_code, data = make_request(f"{BASE_URL}/api/audit-logs")
print(f"\n12. GET /api/audit-logs (After Clear) -> Status: {status_code}")
print(f"    • Total Audit Logs Remaining: {data['total']}")

# Test 13: Invalid Work ID -> 404
status_code, data = make_request(f"{BASE_URL}/api/projects/INVALID_WORK_ID/intelligence")
print(f"\n13. Invalid Work ID Test -> Status: {status_code} (Expected 404) | Detail: {data}")

# Test 14: Invalid Action -> 400
status_code, data = make_request(
    f"{BASE_URL}/api/projects/{real_work_id}/investigation-action",
    method="POST",
    body={"action": "INVALID_ACTION_NAME"}
)
print(f"\n14. Invalid Action Test -> Status: {status_code} (Expected 400) | Detail: {data}")

# Test 15: Empty Note -> 422
status_code, data = make_request(
    f"{BASE_URL}/api/projects/{real_work_id}/notes",
    method="POST",
    body={"note_text": "   "}
)
print(f"\n15. Empty Note Test -> Status: {status_code} (Expected 422) | Detail: {data}")

print("\n==================================================")
print("  ALL 15 REST API ENDPOINT AUDIT TESTS COMPLETED  ")
print("==================================================")
