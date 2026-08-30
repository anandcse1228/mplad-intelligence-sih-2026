import urllib.request
import urllib.parse
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def make_req(url, method="GET", body=None):
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8')
        return resp.status, json.loads(content) if content else {}

def test_notes_isolation():
    print("==================================================")
    print("  TESTING MULTI-DATASET INVESTIGATION NOTES ISOLATION")
    print("==================================================")

    # 1. Activate Dataset A (Ludhiana)
    status, res_a = make_req(f"{BASE_URL}/datasets/dataset_ludhiana_demo/activate", method="POST")
    assert status == 200
    print(f"1. Dataset A Active: {res_a['name']} ({res_a['dataset_id']})")

    # Use a unique timestamped shared Work ID to test collision safety
    ts = int(time.time())
    shared_work_id = f"WS/SHARED/2024-2025/{ts}"
    encoded_id = urllib.parse.quote(shared_work_id, safe='')
    unique_text_a = f"OFFICIAL NOTE UNDER DATASET A - TS {ts}"
    unique_text_b = f"OFFICIAL NOTE UNDER DATASET B - TS {ts}"

    # Add Note A under Dataset A
    status, note_a = make_req(
        f"{BASE_URL}/projects/{encoded_id}/notes",
        method="POST",
        body={"note_text": unique_text_a, "officer_name": "Punjab Officer"}
    )
    assert status == 201
    print(f"2. Saved Note A under Dataset A: ID #{note_a['id']}")

    # Verify Note A is returned under Dataset A
    status, notes_in_a = make_req(f"{BASE_URL}/projects/{encoded_id}/notes")
    print(f"3. Notes in Dataset A: {len(notes_in_a)} note(s)")
    assert len(notes_in_a) == 1
    assert notes_in_a[0]["note_text"] == unique_text_a

    # 2. Switch to Dataset B (Varanasi)
    status, lib = make_req(f"{BASE_URL}/datasets")
    varanasi_ds = next((d for d in lib["items"] if "varanasi" in d["dataset_id"].lower()), None)
    assert varanasi_ds is not None, "Varanasi dataset missing from library"

    status, res_b = make_req(f"{BASE_URL}/datasets/{varanasi_ds['dataset_id']}/activate", method="POST")
    assert status == 200
    print(f"\n4. Switched to Dataset B: {res_b['name']} ({res_b['dataset_id']})")

    # Verify Note A DOES NOT appear under Dataset B!
    status, notes_in_b = make_req(f"{BASE_URL}/projects/{encoded_id}/notes")
    print(f"5. Notes query in Dataset B for shared Work ID: {len(notes_in_b)} note(s) (Expected: 0)")
    assert len(notes_in_b) == 0, f"Cross-dataset leakage detected! Found {len(notes_in_b)} notes in Dataset B"

    # Add Note B under Dataset B
    status, note_b = make_req(
        f"{BASE_URL}/projects/{encoded_id}/notes",
        method="POST",
        body={"note_text": unique_text_b, "officer_name": "UP Officer"}
    )
    assert status == 201
    print(f"6. Saved Note B under Dataset B: ID #{note_b['id']}")

    # Verify only Note B is returned in Dataset B
    status, notes_in_b_after = make_req(f"{BASE_URL}/projects/{encoded_id}/notes")
    print(f"7. Notes in Dataset B: {len(notes_in_b_after)} note(s)")
    assert len(notes_in_b_after) == 1
    assert notes_in_b_after[0]["note_text"] == unique_text_b

    # 3. Switch back to Dataset A (Ludhiana)
    status, res_a_back = make_req(f"{BASE_URL}/datasets/dataset_ludhiana_demo/activate", method="POST")
    assert status == 200
    print(f"\n8. Switched back to Dataset A: {res_a_back['name']}")

    # Verify Note A is back and Note B DOES NOT appear!
    status, notes_in_a_back = make_req(f"{BASE_URL}/projects/{encoded_id}/notes")
    print(f"9. Notes in Dataset A after switchback: {len(notes_in_a_back)} note(s) (Expected: 1)")
    assert len(notes_in_a_back) == 1
    assert notes_in_a_back[0]["note_text"] == unique_text_a
    assert not any(n["note_text"] == unique_text_b for n in notes_in_a_back)

    print("\n==================================================")
    print("  MULTI-DATASET NOTES ISOLATION TEST: 100% PASSED! ")
    print("==================================================")

if __name__ == '__main__':
    test_notes_isolation()
