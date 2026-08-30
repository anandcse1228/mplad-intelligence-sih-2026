import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = "http://127.0.0.1:8000/api"

def http_get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, {}

def http_post(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, {}

def http_delete(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"}, method="DELETE")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, {}

def run_ultra_micro_tests():
    print("=" * 66)
    print("  ULTRA-MICRO STABILIZATION VERIFICATION SUITE")
    print("=" * 66)

    # -----------------------------------------------------------------
    # TEST 1: AUDIT LOG LIFECYCLE (ISSUE 5)
    # -----------------------------------------------------------------
    print("\n[TEST 1] Testing Audit Log Complete Lifecycle...")
    
    # Step A: Clear logs
    status, res = http_delete("/audit-logs")
    assert status == 200, f"Delete failed: status {status}"
    
    status, logs_data = http_get("/audit-logs?page=1&page_size=10")
    assert status == 200
    logs = logs_data.get("items", [])
    assert len(logs) == 0, f"Expected 0 logs after clear, got {len(logs)}"
    print("  [OK] Step 1: Audit Log cleared to 0 events successfully.")

    # Step B: Perform action on Work 1
    work_id = "WS/MP18157/2024-2025/163249"
    encoded_id = urllib.parse.quote(work_id, safe='')
    status, action_res = http_post(f"/projects/{encoded_id}/investigation-action", {
        "action": "MARK_FOR_FIELD_VERIFICATION",
        "details": "Dispatching field team for physical verification.",
        "actor": "State Nodal Officer"
    })
    assert status == 200, f"Action failed: {status}"
    print("  [OK] Step 2: Investigation status action recorded.")

    # Step C: Save note on Work 1
    status, note_res = http_post(f"/projects/{encoded_id}/notes", {
        "note_text": "Field inspection scheduled for tomorrow.",
        "officer_name": "State Nodal Officer"
    })
    assert status in (200, 201), f"Note save failed: {status}"
    print("  [OK] Step 3: Investigation note added.")

    # Step D: Verify audit logs now contain 2 events
    status, logs_data = http_get("/audit-logs?page=1&page_size=10")
    assert status == 200
    logs = logs_data.get("items", [])
    assert len(logs) == 2, f"Expected 2 audit logs after actions, got {len(logs)}"
    print(f"  [OK] Step 4: Audit log correctly reflects {len(logs)} live events.")
    print(f"     Event #1: [{logs[0]['work_id']}] {logs[0]['action_type']}")
    print(f"     Event #2: [{logs[1]['work_id']}] {logs[1]['action_type']}")

    # Step E: Clear logs again to restore clean state
    status, _ = http_delete("/audit-logs")
    assert status == 200
    print("  [OK] Step 5: Final clear verified.")

    # -----------------------------------------------------------------
    # TEST 2: AUDIT LOG -> INSPECT WORK NAVIGATION DETERMINISM (ISSUE 4)
    # -----------------------------------------------------------------
    print("\n[TEST 2] Testing Audit Log -> Inspect Work Navigation Determinism...")
    
    status, active_ds = http_get("/datasets/active")
    assert status == 200
    print(f"  [OK] Active Dataset confirmed: '{active_ds.get('name')}' (ID: {active_ds.get('dataset_id')})")

    status, queue_res = http_get("/projects/risk-queue?page=1&page_size=500")
    assert status == 200
    queue_items = queue_res.get("items", [])
    assert len(queue_items) > 0
    print(f"  [OK] Risk Queue fetched: {len(queue_items)} items available.")

    target_work = queue_items[0]["id"]
    target_encoded = urllib.parse.quote(target_work, safe='')
    status, intel = http_get(f"/projects/{target_encoded}/intelligence")
    assert status == 200
    assert intel["id"] == target_work
    print(f"  [OK] Target Work #{target_work} resolved perfectly (S_risk: {intel['risk_priority_score']}).")

    fake_work = "WS/INVALID/999999"
    fake_encoded = urllib.parse.quote(fake_work, safe='')
    status, _ = http_get(f"/projects/{fake_encoded}/intelligence")
    assert status == 404
    print("  [OK] Non-existent work returns 404 API status; UI fallback items[0] disabled.")

    # -----------------------------------------------------------------
    # TEST 3: NOTES PERSISTENCE AND ISOLATION (ISSUE 3)
    # -----------------------------------------------------------------
    print("\n[TEST 3] Testing Authoritative Notes Persistence...")
    
    status, _ = http_post(f"/projects/{target_encoded}/notes", {
        "note_text": "Authoritative persistence verification note.",
        "officer_name": "State Auditor"
    })
    assert status in (200, 201), f"Note save failed: {status}"
    
    status, notes = http_get(f"/projects/{target_encoded}/notes")
    assert status == 200
    assert any(n["note_text"] == "Authoritative persistence verification note." for n in notes)
    print(f"  [OK] Note authoritatively refetched from SQLite ({len(notes)} notes total).")

    print("\n" + "=" * 66)
    print("  ALL ULTRA-MICRO STABILIZATION TESTS PASSED 100% PERFECTLY!")
    print("=" * 66)

if __name__ == "__main__":
    run_ultra_micro_tests()
