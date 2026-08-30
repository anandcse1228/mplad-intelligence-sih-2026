import urllib.request
import json

filters = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'NORMAL', 'ML_ANOMALY']

print("==================================================")
print("  API SEVERITY FILTER COUNT VERIFICATION          ")
print("==================================================")

total_sum = 0
for f in filters:
    url = f"http://127.0.0.1:8000/api/projects/risk-queue?page=1&page_size=500&severity={f}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        count = data['total']
        print(f"Filter {f:<12}: {count} records")
        if f in ['CRITICAL', 'HIGH', 'MEDIUM', 'NORMAL']:
            total_sum += count

print(f"\nSum of severity bands (CRITICAL + HIGH + MEDIUM + NORMAL): {total_sum} / 220")
assert total_sum == 220, "Total severity sum must equal 220"
print("==================================================")
print("  SEVERITY FILTER VERIFICATION PASSED 100%        ")
print("==================================================")
