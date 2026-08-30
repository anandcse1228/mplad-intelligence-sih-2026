import csv
import re
import math
from datetime import datetime

def clean_str(s):
    if s is None:
        return ''
    return str(s).replace('\ufeff', '').strip(' \t\r\n"\'')

def normalize_key(k):
    if not k:
        return ''
    k = clean_str(k)
    k = re.sub(r'[\(\)\[\]₹\$\,\.]', ' ', k)
    k = re.sub(r'\s+', ' ', k).strip().lower()
    return k

def get_field_val(row_dict, candidate_keys, default=''):
    norm_dict = {normalize_key(k): v for k, v in row_dict.items() if k is not None}
    for cand in candidate_keys:
        cand_norm = normalize_key(cand)
        if cand_norm in norm_dict and norm_dict[cand_norm] is not None:
            val = clean_str(norm_dict[cand_norm])
            if val != '':
                return val
        for k, v in norm_dict.items():
            if cand_norm in k or k in cand_norm:
                val = clean_str(v)
                if val != '':
                    return val
    return default

def test_all():
    print("--- 1. Testing Sanctioned Works ---")
    with open('data/staging/sanctioned_works.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        sanct_rows = [r for r in reader if get_field_val(r, ['sr no', 's no', 'sno', 'serial no']).lower() not in ('', 'grand total', 'total', 'summary')]
        print(f"Sanctioned records parsed: {len(sanct_rows)}")

    print("\n--- 2. Testing Recommended Works ---")
    with open('data/staging/recommended_works.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        rec_rows = [r for r in reader if get_field_val(r, ['sr no', 's no', 'sno', 'serial no']).lower() not in ('', 'grand total', 'total', 'summary')]
        print(f"Recommended records parsed: {len(rec_rows)}")

    print("\n--- 3. Testing Completed Works ---")
    with open('data/staging/completed_works.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        comp_rows = [r for r in reader if get_field_val(r, ['sr no', 's no', 'sno', 'serial no']).lower() not in ('', 'grand total', 'total', 'summary')]
        print(f"Completed records parsed: {len(comp_rows)}")

test_all()
