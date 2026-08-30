import csv
from datetime import datetime
import os

def parse_date(d_str):
    if not d_str or d_str.upper() == 'NA':
        return None
    for fmt in ('%d-%b-%Y', '%d-%b-%y', '%Y-%m-%d'):
        try:
            return datetime.strptime(d_str.strip(), fmt)
        except ValueError:
            pass
    return None

def parse_amount(a_str):
    if not a_str or a_str.upper() == 'NA':
        return 0.0
    cleaned = a_str.replace(',', '').replace('₹', '').replace(' ', '').strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def get_work_code(row):
    w = row.get('Work') or row.get('WORK') or ''
    w = w.strip()
    if not w:
        return ""
    if "WS/MP" in w:
        idx = w.find("WS/MP")
        sub = w[idx:]
        parts = sub.split('-')
        return parts[0].strip()
    return w.split('-')[0].strip()

# Path detection for execution from root or scripts folder
data_dir = 'data' if os.path.exists('data') else '../data'

# 1. Audit Recommended Works
rec_rows = []
with open(os.path.join(data_dir, 'recommended_works.csv'), 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sr = row.get('Sr. No.', '').strip()
        if not sr or sr.lower() == 'grand total':
            continue
        amt = parse_amount(row.get('RECOMMENDED AMOUNT   ( ₹ )', '0'))
        r_date = parse_date(row.get('Recommended date', ''))
        code = get_work_code(row)
        rec_rows.append({
            'sr': sr,
            'code': code,
            'amt': amt,
            'rec_date': r_date,
            'ida': row.get('IDA', '').strip(),
            'title': row.get('Work description', '').strip(),
            'category': row.get('Work category', '').strip()
        })

# 2. Audit Sanctioned Works
sanct_rows = []
with open(os.path.join(data_dir, 'sanctioned_works.csv'), 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sr = row.get('Sr. No.', '').strip()
        if not sr or sr.lower() == 'grand total':
            continue
        amt = parse_amount(row.get('Sanction Amount ( ₹ )', '0'))
        s_date = parse_date(row.get('Sanction Date', ''))
        r_date = parse_date(row.get('Recommended date', ''))
        status = row.get('Work Status', '').strip()
        code = get_work_code(row)
        sanct_rows.append({
            'sr': sr,
            'code': code,
            'amt': amt,
            'sanct_date': s_date,
            'rec_date': r_date,
            'status': status,
            'ida': row.get('IDA', '').strip(),
            'title': row.get('Work description', '').strip(),
            'category': row.get('Work Category', '') or row.get('Work category', '')
        })

# 3. Audit Completed Works
comp_rows = []
with open(os.path.join(data_dir, 'completed_works.csv'), 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sr = row.get('Sr. No.', '').strip()
        if not sr or sr.lower() == 'grand total':
            continue
        amt = parse_amount(row.get('Amount Disbursed ( ₹ )', '0'))
        c_date = parse_date(row.get('Completion Date', ''))
        code = get_work_code(row)
        comp_rows.append({
            'sr': sr,
            'code': code,
            'amt': amt,
            'comp_date': c_date,
            'image': row.get('Image', '').strip(),
            'ida': row.get('IDA', '').strip(),
            'title': row.get('Work Description', '').strip()
        })

print("=== EMPIRICAL DATA AUDIT REPORT ===")
print(f"1. Recommended Works Rows Count: {len(rec_rows)}")
total_rec_amt = sum(r['amt'] for r in rec_rows)
print(f"   Total Recommended Amount: INR {total_rec_amt:,.2f} (INR {total_rec_amt/1e7:.4f} Cr)")

print(f"\n2. Sanctioned Works Rows Count: {len(sanct_rows)}")
total_sanct_amt = sum(r['amt'] for r in sanct_rows)
print(f"   Total Sanctioned Amount: INR {total_sanct_amt:,.2f} (INR {total_sanct_amt/1e7:.4f} Cr)")

print(f"\n3. Completed Works Rows Count: {len(comp_rows)}")
total_comp_amt = sum(r['amt'] for r in comp_rows)
print(f"   Total Disbursed Amount: INR {total_comp_amt:,.2f} (INR {total_comp_amt/1e7:.4f} Cr)")

# Matching logic
delays = []
matched_count = 0
sanction_only_count = 0

for s in sanct_rows:
    r_dt = s['rec_date']
    s_dt = s['sanct_date']
    if r_dt is not None:
        matched_count += 1
        if s_dt is not None:
            diff = (s_dt - r_dt).days
            if diff >= 0:
                delays.append(diff)
    else:
        sanction_only_count += 1

print(f"\n4. Match & Delay Metrics:")
print(f"   - Sanctioned Works with Recommended Date: {matched_count}")
print(f"   - Sanctioned-Only Works: {sanction_only_count}")
if delays:
    avg_delay = sum(delays) / len(delays)
    delays_sorted = sorted(delays)
    median_delay = delays_sorted[len(delays_sorted)//2]
    print(f"   - Calculated Delay Records Count: {len(delays)}")
    print(f"   - Mean Sanction Delay: {avg_delay:.2f} Days")
    print(f"   - Median Sanction Delay: {median_delay} Days")

# IDA Breakdown
ida_counts = {}
ida_amts = {}
for s in sanct_rows:
    ida = s['ida']
    ida_counts[ida] = ida_counts.get(ida, 0) + 1
    ida_amts[ida] = ida_amts.get(ida, 0.0) + s['amt']

print(f"\n5. Sanctioned Works IDA Breakdown:")
for ida, count in ida_counts.items():
    pct = (count / len(sanct_rows)) * 100
    amt_cr = ida_amts[ida] / 1e7
    print(f"   - {ida}: {count} Works ({pct:.1f}%) | INR {amt_cr:.4f} Cr")
