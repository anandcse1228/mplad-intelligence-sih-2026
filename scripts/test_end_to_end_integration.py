import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000/api"

def make_request(url, method="GET", body=None):
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8')
        return resp.status, json.loads(content) if content else {}

print("==================================================")
print("  FULL REACT -> FASTAPI -> SQLITE INTEGRATION TEST")
print("==================================================")

# 0. Dynamically discover a valid Work ID from the active dataset's risk queue
status, queue_res = make_request(f"{BASE_URL}/projects/risk-queue?page=1&page_size=5")
assert status == 200, f"Failed to query risk queue: {queue_res}"
assert len(queue_res.get("items", [])) > 0, "Risk queue is empty"

target_work = queue_res["items"][0]
work_id = target_work["id"]
encoded_work_id = urllib.parse.quote(work_id, safe='')
print(f"0. Dynamically Selected Target Work: #{work_id} (Score: {target_work['risk_priority_score']})")

# 1. Clear initial audit logs via DELETE /api/audit-logs
status, clear_res = make_request(f"{BASE_URL}/audit-logs", method="DELETE")
print(f"1. Audit Logs Cleared: HTTP {status} -> {clear_res}")
assert status == 200, f"Expected HTTP 200, got {status}"
assert clear_res.get("status") == "cleared", f"Unexpected status: {clear_res}"
assert "deleted_count" in clear_res, f"Missing deleted_count: {clear_res}"

status, logs_start = make_request(f"{BASE_URL}/audit-logs")
print(f"   Audit Logs Verified Empty: {logs_start['total']} events")
assert logs_start['total'] == 0, f"Expected 0 audit logs after clear, got {logs_start['total']}"

# 2. Perform Investigation Status Change on Page 4
status, action_res = make_request(
    f"{BASE_URL}/projects/{encoded_work_id}/investigation-action",
    method="POST",
    body={"action": "MARK_FOR_FIELD_VERIFICATION", "actor": "State Nodal Officer", "details": "Physical verification team dispatched"}
)
print(f"2. Page 4 Investigation Status Updated: {action_res.get('previous_status', 'UNDER REVIEW')} -> {action_res.get('current_status') or action_res.get('new_status')}")
assert status == 200, f"Failed to update investigation status: {action_res}"

# 3. Check Page 6 Audit Logs (Must be EXACTLY 1 event)
status, logs_after_action = make_request(f"{BASE_URL}/audit-logs")
print(f"3. Page 6 Audit Logs Query: Total = {logs_after_action['total']} (Expected: 1)")
assert logs_after_action['total'] == 1, f"Expected 1 audit event, got {logs_after_action['total']}"
event1 = logs_after_action['items'][0]
print(f"   • Event #1: [{event1['work_id']}] {event1['action_type']} | Timestamp: {event1['timestamp']}")

# 4. Save Investigation Note on Page 4
status, note_res = make_request(
    f"{BASE_URL}/projects/{encoded_work_id}/notes",
    method="POST",
    body={"note_text": "Site measurements confirmed with Assistant Engineer.", "officer_name": "State Nodal Officer"}
)
print(f"4. Page 4 Investigation Note Saved: ID #{note_res['id']} ('{note_res['note_text']}')")
assert status == 201, f"Failed to save investigation note: {note_res}"

# 5. Check Page 6 Audit Logs (Must be EXACTLY 2 events)
status, logs_after_note = make_request(f"{BASE_URL}/audit-logs")
print(f"5. Page 6 Audit Logs Query: Total = {logs_after_note['total']} (Expected: 2)")
assert logs_after_note['total'] == 2, f"Expected 2 audit events, got {logs_after_note['total']}"
event2 = logs_after_note['items'][0]
print(f"   • Event #2: [{event2['work_id']}] {event2['action_type']} | Details: '{event2['details']}'")

# 6. Verify Final Audit Log Clear & Accurate Count
status, clear_final = make_request(f"{BASE_URL}/audit-logs", method="DELETE")
print(f"6. Final Audit Log Clear: HTTP {status} -> {clear_final}")
assert status == 200, f"Expected HTTP 200, got {status}"
assert clear_final.get("status") == "cleared"
assert clear_final.get("deleted_count") == 2, f"Expected deleted_count=2, got {clear_final.get('deleted_count')}"

print("\n==================================================")
print("  END-TO-END INTEGRATION TEST PASSED 100% PERFECTLY ")
print("==================================================")
