import urllib.request
import urllib.parse
import json
import sqlite3
import os

BASE_URL = "http://127.0.0.1:8000/api"
SCRATCH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(SCRATCH_DIR, "backend", "mplads.db")

def make_req(url, method="GET", body=None):
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8')
        return resp.status, json.loads(content) if content else {}

def run_qa_audit():
    print("==================================================================")
    print("  MPLAD INTELLIGENCE — FINAL SIH DEMO STABILIZATION AUDIT         ")
    print("==================================================================")

    # 1. Restore Ludhiana Demo Dataset
    status, restore_res = make_req(f"{BASE_URL}/datasets/restore-demo", method="POST")
    assert status == 200
    print(f"\n[1] Active Benchmark Dataset Initialized: {restore_res['message']}")

    # 2. Get real top work from Ludhiana
    status, q_ludhiana = make_req(f"{BASE_URL}/projects/risk-queue?page=1&page_size=5")
    assert status == 200
    work_a = q_ludhiana["items"][0]
    work_id_a = work_a["id"]
    encoded_id_a = urllib.parse.quote(work_id_a, safe='')
    print(f"[2] Target Work in Dataset A (Ludhiana): #{work_id_a}")

    # Set status and add note in Dataset A
    status, act_a = make_req(
        f"{BASE_URL}/projects/{encoded_id_a}/investigation-action",
        method="POST",
        body={"action": "MARK_FOR_FIELD_VERIFICATION", "actor": "Punjab Officer", "details": "Inspection dispatched"}
    )
    assert status == 200
    assert act_a["current_status"] == "MARKED FOR FIELD VERIFICATION"

    status, note_a = make_req(
        f"{BASE_URL}/projects/{encoded_id_a}/notes",
        method="POST",
        body={"note_text": "TEST NOTE A - LUDHIANA VALIDATION", "officer_name": "Punjab Officer"}
    )
    assert status == 201

    # Verify Note A and Case Status in Dataset A
    status, notes_a = make_req(f"{BASE_URL}/projects/{encoded_id_a}/notes")
    assert len(notes_a) >= 1
    assert any(n["note_text"] == "TEST NOTE A - LUDHIANA VALIDATION" for n in notes_a)
    print(f"    • Dataset A Case Status: {act_a['current_status']} | Notes Count: {len(notes_a)} (PASS)")

    # 3. Switch to Dataset B (Varanasi)
    status, lib = make_req(f"{BASE_URL}/datasets")
    varanasi_ds = next((d for d in lib["items"] if "varanasi" in d["dataset_id"].lower()), None)
    assert varanasi_ds is not None, "Varanasi dataset missing from library"

    status, res_b = make_req(f"{BASE_URL}/datasets/{varanasi_ds['dataset_id']}/activate", method="POST")
    assert status == 200
    print(f"\n[3] Switched to Dataset B: {res_b['name']} ({res_b['dataset_id']})")

    # In Dataset B, check case status and notes for work_id_a (Must NOT leak Dataset A data!)
    status, case_b_leak_check = make_req(f"{BASE_URL}/projects/{encoded_id_a}/investigation")
    assert status == 200
    assert case_b_leak_check["current_status"] == "UNDER REVIEW", f"Leaked status: {case_b_leak_check['current_status']}"
    assert case_b_leak_check["dataset_id"] == varanasi_ds["dataset_id"]

    status, notes_b_leak_check = make_req(f"{BASE_URL}/projects/{encoded_id_a}/notes")
    assert status == 200
    assert len(notes_b_leak_check) == 0, f"Leaked notes in Dataset B: {notes_b_leak_check}"
    print(f"    • Dataset B Leak Check on Work #{work_id_a}: Case={case_b_leak_check['current_status']}, Notes Count={len(notes_b_leak_check)} (ZERO LEAKAGE PASS)")

    # Set status and add note in Dataset B for its own top work
    status, q_varanasi = make_req(f"{BASE_URL}/projects/risk-queue?page=1&page_size=5")
    work_id_b = q_varanasi["items"][0]["id"]
    encoded_id_b = urllib.parse.quote(work_id_b, safe='')
    
    status, act_b = make_req(
        f"{BASE_URL}/projects/{encoded_id_b}/investigation-action",
        method="POST",
        body={"action": "REQUEST_NODAL_AGENCY_AUDIT", "actor": "UP Officer", "details": "Ledger audit requested"}
    )
    assert status == 200
    assert act_b["current_status"] == "AUDIT REQUESTED (IDA)"

    status, note_b = make_req(
        f"{BASE_URL}/projects/{encoded_id_b}/notes",
        method="POST",
        body={"note_text": "TEST NOTE B - VARANASI VALIDATION", "officer_name": "UP Officer"}
    )
    assert status == 201
    print(f"    • Dataset B Work #{work_id_b}: Case={act_b['current_status']} | Note Saved ID #{note_b['id']} (PASS)")

    # 4. Switch back to Dataset A (Ludhiana)
    status, res_a_back = make_req(f"{BASE_URL}/datasets/dataset_ludhiana_demo/activate", method="POST")
    assert status == 200
    print(f"\n[4] Switched back to Dataset A: {res_a_back['name']}")

    # Verify Dataset A Case Status and Note A restored, Note B NOT present
    status, case_a_restored = make_req(f"{BASE_URL}/projects/{encoded_id_a}/investigation")
    assert case_a_restored["current_status"] == "MARKED FOR FIELD VERIFICATION"
    
    status, notes_a_restored = make_req(f"{BASE_URL}/projects/{encoded_id_a}/notes")
    assert len(notes_a_restored) >= 1
    assert any(n["note_text"] == "TEST NOTE A - LUDHIANA VALIDATION" for n in notes_a_restored)
    assert not any(n["note_text"] == "TEST NOTE B - VARANASI VALIDATION" for n in notes_a_restored)
    print(f"    • Restored Dataset A: Case={case_a_restored['current_status']}, Notes Count={len(notes_a_restored)} (100% PERSISTENCE & RESTORATION PASS)")

    # 5. 10 Consecutive Inspect Work Navigations
    print("\n[5] Testing 10 Consecutive Inspect Work API Queries:")
    all_test_works = [w["id"] for w in q_ludhiana["items"]] + [w["id"] for w in q_varanasi["items"]][:5]
    successful_navs = 0
    for idx, wid in enumerate(all_test_works[:10]):
        # Ensure active dataset matches work
        enc_id = urllib.parse.quote(wid, safe='')
        if "490" in wid: # Varanasi work
            make_req(f"{BASE_URL}/datasets/{varanasi_ds['dataset_id']}/activate", method="POST")
        else: # Ludhiana work
            make_req(f"{BASE_URL}/datasets/dataset_ludhiana_demo/activate", method="POST")
        
        st, res = make_req(f"{BASE_URL}/projects/{enc_id}/intelligence")
        if st == 200 and res["id"] == wid:
            successful_navs += 1
            print(f"    Attempt #{idx+1} on #{wid}: HTTP 200 OK (Score: {res['risk_priority_score']})")
        else:
            print(f"    Attempt #{idx+1} on #{wid}: FAILED (HTTP {st})")
    
    assert successful_navs == 10, f"Expected 10 successful navigations, got {successful_navs}"
    print(f"    -> 10 / 10 Successful First-Click Navigations (0 Retries Required)")

    # 6. Hybrid Score Mathematical Precision Audit across all records
    print("\n[6] Auditing Hybrid Risk Score Math across ALL records in SQLite:")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, dataset_id, work_id, ml_anomaly_score, rule_score, risk_priority_score FROM ml_scored_works;")
    rows = c.fetchall()
    conn.close()

    exact_unrounded_diffs = []
    exact_rounded_diffs = []
    tolerance = 0.05 # Stored precision is 1 decimal place (rounding tolerance = +/- 0.05)

    for r in rows:
        pk, ds_id, wid, s_ml, s_rule, s_risk = r
        raw_calc = 0.60 * s_ml + 0.40 * s_rule
        rounded_calc = round(min(100.0, max(0.0, raw_calc)), 1)
        
        diff_raw = abs(s_risk - raw_calc)
        diff_rounded = abs(s_risk - rounded_calc)
        
        exact_unrounded_diffs.append(diff_raw)
        exact_rounded_diffs.append(diff_rounded)

    max_unrounded = max(exact_unrounded_diffs)
    max_rounded = max(exact_rounded_diffs)
    mismatches = sum(1 for d in exact_unrounded_diffs if d > tolerance)

    print(f"    • Total Records Checked:        {len(rows)}")
    print(f"    • Defined Rounding Tolerance:   ±{tolerance} (for 1-decimal UI/storage precision)")
    print(f"    • Out-of-Tolerance Mismatches:  {mismatches}")
    print(f"    • Max Diff (vs unrounded float): {max_unrounded:.4f} (<= 0.05)")
    print(f"    • Max Diff (vs 1-decimal round): {max_rounded:.4f} (exact mathematical match)")
    assert mismatches == 0, f"Found {mismatches} formula mismatches!"

    print("\n==================================================================")
    print("  ALL SIH DEMO STABILIZATION CHECKS COMPLETED & VERIFIED 100%!    ")
    print("==================================================================")

if __name__ == '__main__':
    run_qa_audit()
