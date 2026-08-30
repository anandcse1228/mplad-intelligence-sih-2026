import urllib.request
import json

def test():
    req = urllib.request.urlopen('http://127.0.0.1:8000/api/datasets/active')
    active = json.loads(req.read().decode('utf-8'))
    print(f"Active Dataset: {active['dataset_id']} -> '{active['name']}'")
    print(f"State: {active['state']}, District: {active['district']}, Sanctioned: {active['sanctioned_count']}")

    req2 = urllib.request.urlopen('http://127.0.0.1:8000/api/datasets')
    lib = json.loads(req2.read().decode('utf-8'))
    print(f"Library Datasets count: {lib['total']}")
    for d in lib['items']:
        print(f"  • [{d['dataset_id']}] {d['name']} | Active: {d['is_active']} | Works: {d['sanctioned_count']}")

    pdf_url = f"http://127.0.0.1:8000/api/datasets/{active['dataset_id']}/report-pdf"
    req3 = urllib.request.urlopen(pdf_url)
    pdf_bytes = req3.read()
    print(f"Downloaded PDF Report Size: {len(pdf_bytes)} bytes (Content-Type: {req3.headers.get('Content-Type')})")
    assert len(pdf_bytes) > 1000

test()
