import urllib.request
import urllib.parse
import json
import os

BASE_URL = "http://127.0.0.1:8000/api"
SCRATCH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_DIR = os.path.join(SCRATCH_DIR, "data", "demo_backup")
VARANASI_FILES = {
    "sanctioned": os.path.join(SCRATCH_DIR, "data", "staging", "sanctioned_works.csv"),
    "recommended": os.path.join(SCRATCH_DIR, "data", "staging", "recommended_works.csv"),
    "completed": os.path.join(SCRATCH_DIR, "data", "staging", "completed_works.csv")
}

def multipart_upload(url, files_dict):
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = bytearray()

    for field, file_path in files_dict.items():
        filename = os.path.basename(file_path)
        body.extend(f'--{boundary}\r\n'.encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="{field}"; filename="{filename}"\r\n'.encode('utf-8'))
        body.extend(b'Content-Type: text/csv\r\n\r\n')
        with open(file_path, 'rb') as f:
            body.extend(f.read())
        body.extend(b'\r\n')

    body.extend(f'--{boundary}--\r\n'.encode('utf-8'))

    req = urllib.request.Request(url, data=bytes(body))
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def post_json(url, data_dict=None):
    payload = json.dumps(data_dict or {}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def get_json(url):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode('utf-8'))

def test_full_lifecycle():
    print("==================================================================")
    print("  MPLAD INTELLIGENCE — MULTI-DATASET PLATFORM LIFECYCLE AUDIT     ")
    print("==================================================================")

    # 0. Ensure Demo Benchmark is Active
    post_json(f"{BASE_URL}/datasets/restore-demo")

    # 1. Check Initial Active Dataset
    active_1 = get_json(f"{BASE_URL}/datasets/active")
    print(f"\n[1] Initial Active Dataset: {active_1['name']} ({active_1['dataset_id']})")
    print(f"    State: {active_1['state']}, District: {active_1['district']}, Works: {active_1['sanctioned_count']}")
    assert active_1['dataset_id'] == 'dataset_ludhiana_demo'
    assert active_1['sanctioned_count'] == 220

    # 2. Upload Staged Files (Varanasi Dataset)
    upload_res = multipart_upload(f"{BASE_URL}/datasets/upload", {
        "sanctioned_file": VARANASI_FILES["sanctioned"],
        "recommended_file": VARANASI_FILES["recommended"],
        "completed_file": VARANASI_FILES["completed"]
    })
    print(f"\n[2] Upload 3 CSVs to Staging: {upload_res['status']} — {upload_res['message']}")
    assert upload_res['staging_ready'] is True

    # 3. Validate Staged Files
    val_res = post_json(f"{BASE_URL}/datasets/validate")
    print(f"\n[3] CSV Validation: valid={val_res['valid']}")
    print(f"    Sanctioned: {val_res['sanctioned_count']}, Rec: {val_res['recommended_count']}, Comp: {val_res['completed_count']}")
    assert val_res['valid'] is True
    assert val_res['sanctioned_count'] == 216

    # 4. Run ML Analysis Pipeline & Activate Varanasi Dataset
    ana_res = post_json(f"{BASE_URL}/datasets/analyze", {"dataset_name": "Uttar Pradesh MPLADS — Varanasi District"})
    print(f"\n[4] ML Analysis & Activation: {ana_res['status']} — {ana_res['message']}")
    print(f"    Dataset ID: {ana_res['dataset_id']}, ML Anomalies: {ana_res['ml_anomaly_candidates']}")
    assert ana_res['total_scored_works'] == 216
    varanasi_id = ana_res['dataset_id']

    # 5. Check Dataset Library (Must have at least 2 datasets preserved!)
    lib_res = get_json(f"{BASE_URL}/datasets")
    print(f"\n[5] Dataset Library Count: {lib_res['total']} datasets stored")
    for d in lib_res['items']:
        print(f"    • [{d['dataset_id']}] {d['name']} | Active: {d['is_active']} | Works: {d['sanctioned_count']}")
    assert lib_res['total'] >= 2
    assert any(d['dataset_id'] == 'dataset_ludhiana_demo' for d in lib_res['items'])
    assert any(d['dataset_id'] == varanasi_id for d in lib_res['items'])

    # 6. Check Active Dataset Metadata
    active_2 = get_json(f"{BASE_URL}/datasets/active")
    print(f"\n[6] New Active Dataset: {active_2['name']}")
    print(f"    State: {active_2['state']}, District: {active_2['district']}, Works: {active_2['sanctioned_count']}")
    assert active_2['state'] == 'Uttar Pradesh'
    assert active_2['district'] == 'Varanasi'
    assert active_2['sanctioned_count'] == 216

    # 7. Check Overview KPIs (Reflects Varanasi)
    kpis = get_json(f"{BASE_URL}/overview/kpis")
    print(f"\n[7] Command Center KPIs: {kpis['total_sanctioned_works']} works, District: {kpis['district']}, State: {kpis['state']}")
    assert kpis['total_sanctioned_works'] == 216
    assert kpis['district'] == 'Varanasi'

    # 8. Check Risk Queue
    queue = get_json(f"{BASE_URL}/projects/risk-queue?page=1&page_size=10")
    print(f"\n[8] Risk Queue Top Work: #{queue['items'][0]['id']} — Score: {queue['items'][0]['risk_priority_score']}")
    top_varanasi_id = queue['items'][0]['id']

    # 9. Check Project Intelligence Detail & Dynamic Explainability
    intel = get_json(f"{BASE_URL}/projects/{urllib.parse.quote(top_varanasi_id, safe='')}/intelligence")
    print(f"\n[9] Project Intelligence Detail for #{intel['id']}:")
    print(f"    S_risk: {intel['risk_priority_score']} (S_ml: {intel['ml_anomaly_score']}, S_rule: {intel['rule_score']})")
    print(f"    Narrative: {intel['explanation']['executive_summary'][:100]}...")
    assert abs(intel['risk_priority_score'] - round(0.60 * intel['ml_anomaly_score'] + 0.40 * intel['rule_score'], 1)) < 0.1

    # 10. Test Download PDF Report for Varanasi Dataset
    pdf_req = urllib.request.urlopen(f"{BASE_URL}/datasets/{varanasi_id}/report-pdf")
    pdf_bytes = pdf_req.read()
    print(f"\n[10] Downloaded Varanasi PDF Report: {len(pdf_bytes)} bytes")
    assert pdf_bytes.startswith(b'%PDF-')
    assert len(pdf_bytes) > 2000

    # 11. Switch Active Dataset back to Ludhiana Demo
    switched = post_json(f"{BASE_URL}/datasets/dataset_ludhiana_demo/activate")
    print(f"\n[11] Switched Active Dataset back to: {switched['name']}")
    assert switched['dataset_id'] == 'dataset_ludhiana_demo'

    # 12. Check Overview KPIs again (Reflects Ludhiana)
    kpis_back = get_json(f"{BASE_URL}/overview/kpis")
    print(f"\n[12] Restored Command Center KPIs: {kpis_back['total_sanctioned_works']} works, District: {kpis_back['district']}, State: {kpis_back['state']}")
    assert kpis_back['total_sanctioned_works'] == 220
    assert kpis_back['district'] == 'Ludhiana'

    # 13. Download PDF Report for Ludhiana Dataset
    pdf_ludhiana_req = urllib.request.urlopen(f"{BASE_URL}/datasets/dataset_ludhiana_demo/report-pdf")
    pdf_ludhiana_bytes = pdf_ludhiana_req.read()
    print(f"\n[13] Downloaded Ludhiana PDF Report: {len(pdf_ludhiana_bytes)} bytes")
    assert pdf_ludhiana_bytes.startswith(b'%PDF-')

    print("\n==================================================================")
    print("  ALL 13 MULTI-DATASET PLATFORM LIFECYCLE TESTS PASSED 100%!      ")
    print("==================================================================")

if __name__ == '__main__':
    test_full_lifecycle()
