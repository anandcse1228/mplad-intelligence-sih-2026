import csv
import json
import math
import os
import random
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from sqlalchemy.orm import Session

# ----------------------------------------------------
# ROBUST STRING, KEY & VALUE EXTRACTION HELPERS
# ----------------------------------------------------

def clean_str(s: Any) -> str:
    if s is None:
        return ''
    return str(s).replace('\ufeff', '').strip(' \t\r\n"\'')

def normalize_key(k: Any) -> str:
    if not k:
        return ''
    k = clean_str(k)
    k = re.sub(r'[\(\)\[\]\{\}₹\$\,\.\'\"`:\-_/\\]', ' ', k)
    k = re.sub(r'\s+', ' ', k).strip().lower()
    return k

def get_field_val(row_dict: Dict[str, Any], candidate_keys: List[str], default: str = '') -> str:
    if not row_dict:
        return default
    norm_map = {}
    for k, v in row_dict.items():
        if k is not None:
            nk = normalize_key(k)
            if nk and nk not in norm_map:
                norm_map[nk] = v

    for cand in candidate_keys:
        cand_norm = normalize_key(cand)
        if cand_norm in norm_map and norm_map[cand_norm] is not None:
            val = clean_str(norm_map[cand_norm])
            if val != '':
                return val

    for cand in candidate_keys:
        cand_norm = normalize_key(cand)
        for k, v in norm_map.items():
            if (cand_norm in k or k in cand_norm) and v is not None:
                val = clean_str(v)
                if val != '':
                    return val

    return default

def parse_date(d_str: Any) -> Optional[datetime]:
    s = clean_str(d_str)
    if not s or s.upper() in ('NA', 'NULL', 'NONE', 'N/A', '-'):
        return None
    for fmt in ('%d-%b-%Y', '%d-%b-%y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None

def parse_amount(a_str: Any) -> float:
    s = clean_str(a_str)
    if not s or s.upper() in ('NA', 'NULL', 'NONE', 'N/A', '-'):
        return 0.0
    cleaned = re.sub(r'[₹\$,\s]', '', s)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def get_work_code(row_dict: Dict[str, Any]) -> str:
    w = get_field_val(row_dict, ['work', 'work description', 'work title', 'recommended work', 'project code', 'work code', 'work id'])
    s = clean_str(w)
    
    m = re.search(r'([A-Za-z0-9\-_]+/[A-Za-z0-9\-_]+/\d{4}-\d{4}/\d+)', s)
    if m:
        return m.group(1)
    
    m2 = re.search(r'(WS/[A-Za-z0-9\-_]+/\d+)', s)
    if m2:
        return m2.group(1)

    first_token = s.split()[0].rstrip('-') if s else ''
    if first_token and len(first_token) >= 5 and first_token.upper() not in ('NA', 'NULL', 'PROVIDING', 'CONSTRUCTION', 'INTERLOCKING'):
        return first_token

    sr = get_field_val(row_dict, ['sr no', 'sr_no', 's no', 'sno', 'serial no'], '0')
    return f"WORK-SR-{sr}"

def extract_district(row_dict: Dict[str, Any], default: str = 'District') -> str:
    d = get_field_val(row_dict, ['district', 'district name'])
    if d and d.upper() not in ('NA', 'NULL', '-'):
        return d.strip().capitalize()

    ida = get_field_val(row_dict, ['ida', 'implementing agency', 'agency'])
    if ida:
        clean_ida = re.sub(r'\(.*?\)', '', ida).replace('_IDA', '').replace('DC ', '').strip()
        first_word = clean_ida.split()[0] if clean_ida else ''
        if len(first_word) >= 3:
            return first_word.capitalize()

    constituency = get_field_val(row_dict, ['constituency'])
    if constituency and constituency.upper() not in ('NA', 'NULL', '-'):
        return constituency.strip().capitalize()

    state = get_field_val(row_dict, ['state'])
    if state and state.upper() not in ('NA', 'NULL', '-'):
        return f"{state.strip()}"

    return default

# ----------------------------------------------------
# PURE PYTHON ISOLATION FOREST ML ENGINE
# ----------------------------------------------------

def c_factor(n: int) -> float:
    if n <= 1:
        return 1.0
    if n == 2:
        return 1.0
    return 2.0 * (math.log(n - 1) + 0.5772156649) - (2.0 * (n - 1) / n)

class IsolationTreeNode:
    def __init__(self, size: int):
        self.size = size
        self.split_feat = None
        self.split_val = None
        self.left = None
        self.right = None
        self.is_leaf = True

def build_itree(data: List[List[float]], current_height: int, height_limit: int) -> IsolationTreeNode:
    n = len(data)
    node = IsolationTreeNode(n)
    if current_height >= height_limit or n <= 1:
        return node
    
    n_feats = len(data[0])
    valid_feats = []
    for f in range(n_feats):
        vals = [d[f] for d in data]
        if max(vals) > min(vals):
            valid_feats.append(f)
            
    if not valid_feats:
        return node
        
    feat_idx = random.choice(valid_feats)
    vals = [d[feat_idx] for d in data]
    min_val = min(vals)
    max_val = max(vals)
    
    split_val = random.uniform(min_val, max_val)
    
    left_data = [d for d in data if d[feat_idx] < split_val]
    right_data = [d for d in data if d[feat_idx] >= split_val]
    
    node.is_leaf = False
    node.split_feat = feat_idx
    node.split_val = split_val
    node.left = build_itree(left_data, current_height + 1, height_limit)
    node.right = build_itree(right_data, current_height + 1, height_limit)
    return node

def path_length(x: List[float], node: IsolationTreeNode, current_height: int) -> float:
    if node.is_leaf or node.size <= 1:
        return current_height + c_factor(node.size)
    if x[node.split_feat] < node.split_val:
        return path_length(x, node.left, current_height + 1)
    else:
        return path_length(x, node.right, current_height + 1)

class IsolationForestModel:
    def __init__(self, n_estimators: int = 100, max_samples: int = 256, random_state: int = 42):
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.random_state = random_state
        self.trees = []
        
    def fit(self, X: List[List[float]]):
        random.seed(self.random_state)
        n_samples = len(X)
        sample_size = min(self.max_samples, n_samples)
        height_limit = math.ceil(math.log2(max(2, sample_size)))
        
        self.trees = []
        for _ in range(self.n_estimators):
            sample = random.sample(X, sample_size)
            tree = build_itree(sample, 0, height_limit)
            self.trees.append(tree)
            
    def compute_anomaly_scores(self, X: List[List[float]]) -> List[float]:
        n_samples = len(X)
        c_n = c_factor(n_samples)
        scores = []
        for x in X:
            paths = [path_length(x, tree, 0) for tree in self.trees]
            avg_path = sum(paths) / len(paths)
            score = 2.0 ** (- (avg_path / c_n))
            scores.append(score)
        return scores

# ----------------------------------------------------
# 1. REAL DYNAMIC CSV SCHEMA & RECORD VALIDATION
# ----------------------------------------------------

def validate_dataset_files(sanct_path: str, rec_path: str, comp_path: str) -> Dict[str, Any]:
    checks = []
    errors = []
    warnings = []
    
    for label, path in [('Sanctioned Works', sanct_path), ('Recommended Works', rec_path), ('Completed Works', comp_path)]:
        if not path or not os.path.exists(path):
            errors.append(f"{label} CSV file is missing or path does not exist.")
            checks.append({"name": f"{label} File Exists", "status": "FAIL", "message": "File not found on server."})
        elif os.path.getsize(path) == 0:
            errors.append(f"{label} CSV file is empty (0 bytes).")
            checks.append({"name": f"{label} File Non-Empty", "status": "FAIL", "message": "File is empty (0 bytes)."})
        else:
            checks.append({"name": f"{label} File Exists & Non-Empty", "status": "PASS", "message": f"Size: {os.path.getsize(path)} bytes"})

    if errors:
        return {
            "valid": False,
            "sanctioned_count": 0,
            "recommended_count": 0,
            "completed_count": 0,
            "duplicate_ids_count": 0,
            "checks": checks,
            "errors": errors,
            "warnings": warnings
        }

    # 2. Schema check & record parsing: Sanctioned Works
    sanct_records = []
    sanct_ids = []
    duplicate_ids = []
    sanct_headers = []
    
    try:
        with open(sanct_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            sanct_headers = [clean_str(h) for h in (reader.fieldnames or [])]
            
            sample_row = next(reader, None)
            if sample_row is not None:
                work_sample = get_field_val(sample_row, ['work', 'work description', 'work title', 'recommended work', 'project code', 'work code'])
                amt_sample = get_field_val(sample_row, ['sanction amount', 'sanctioned amount', 'amount sanctioned', 'amount'])
                
                if not work_sample and not any('work' in normalize_key(h) for h in sanct_headers):
                    errors.append(f"Sanctioned Works CSV is missing a required Work Description or Work Identifier column. Detected columns: {', '.join(sanct_headers)}")
                    checks.append({"name": "Sanctioned Schema: Work Identifier", "status": "FAIL", "message": "Could not identify Work/Project column."})
                else:
                    checks.append({"name": "Sanctioned Schema: Work Identifier", "status": "PASS", "message": "Work identification column verified."})
                    
                if not amt_sample and not any('amount' in normalize_key(h) for h in sanct_headers):
                    errors.append(f"Sanctioned Works CSV is missing a required Sanction Amount column. Detected columns: {', '.join(sanct_headers)}")
                    checks.append({"name": "Sanctioned Schema: Sanction Amount", "status": "FAIL", "message": "Could not identify Sanction Amount column."})
                else:
                    checks.append({"name": "Sanctioned Schema: Sanction Amount", "status": "PASS", "message": "Sanction Amount column verified."})

                sr_sample = get_field_val(sample_row, ['sr no', 'sr_no', 's no', 'sno', 'serial no'])
                if sr_sample and sr_sample.lower() not in ('grand total', 'total', 'summary'):
                    code = get_work_code(sample_row)
                    sanct_ids.append(code)
                    sanct_records.append(sample_row)

            for r in reader:
                sr = get_field_val(r, ['sr no', 'sr_no', 's no', 'sno', 'serial no'])
                if not sr or sr.lower() in ('grand total', 'total', 'summary'):
                    continue
                code = get_work_code(r)
                if code in sanct_ids:
                    duplicate_ids.append(code)
                sanct_ids.append(code)
                sanct_records.append(r)
                
    except Exception as e:
        errors.append(f"Failed to parse Sanctioned Works CSV: {str(e)}")
        checks.append({"name": "Sanctioned Works CSV Parsing", "status": "FAIL", "message": str(e)})

    # 3. Schema check & record parsing: Recommended Works
    rec_records = []
    try:
        with open(rec_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            rec_headers = [clean_str(h) for h in (reader.fieldnames or [])]
            
            sample_row = next(reader, None)
            if sample_row is not None:
                rec_work_sample = get_field_val(sample_row, ['recommended work', 'work description', 'work', 'work title'])
                rec_amt_sample = get_field_val(sample_row, ['recommended amount', 'amount recommended', 'amount', 'sanction amount'])
                
                if not rec_work_sample and not any('work' in normalize_key(h) or 'recommend' in normalize_key(h) for h in rec_headers):
                    errors.append(f"Recommended Works CSV is missing a required Recommended Work Description column. Detected columns: {', '.join(rec_headers)}")
                    checks.append({"name": "Recommended Schema: Work Title", "status": "FAIL", "message": "Could not identify Work column."})
                else:
                    checks.append({"name": "Recommended Schema: Work Title", "status": "PASS", "message": "Recommended Work column verified."})

                if not rec_amt_sample and not any('amount' in normalize_key(h) for h in rec_headers):
                    errors.append(f"Recommended Works CSV is missing a required Recommended Amount column. Detected columns: {', '.join(rec_headers)}")
                    checks.append({"name": "Recommended Schema: Recommended Amount", "status": "FAIL", "message": "Could not identify Amount column."})
                else:
                    checks.append({"name": "Recommended Schema: Recommended Amount", "status": "PASS", "message": "Recommended Amount column verified."})

                sr_sample = get_field_val(sample_row, ['sr no', 'sr_no', 's no', 'sno', 'serial no'])
                if sr_sample and sr_sample.lower() not in ('grand total', 'total', 'summary'):
                    rec_records.append(sample_row)

            for r in reader:
                sr = get_field_val(r, ['sr no', 'sr_no', 's no', 'sno', 'serial no'])
                if not sr or sr.lower() in ('grand total', 'total', 'summary'):
                    continue
                rec_records.append(r)
    except Exception as e:
        errors.append(f"Failed to parse Recommended Works CSV: {str(e)}")
        checks.append({"name": "Recommended Works CSV Parsing", "status": "FAIL", "message": str(e)})

    # 4. Schema check & record parsing: Completed Works
    comp_records = []
    try:
        with open(comp_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            comp_headers = [clean_str(h) for h in (reader.fieldnames or [])]
            
            sample_row = next(reader, None)
            if sample_row is not None:
                comp_work_sample = get_field_val(sample_row, ['work description', 'work', 'work title', 'completed work'])
                comp_amt_sample = get_field_val(sample_row, ['amount disbursed', 'disbursed amount', 'amount', 'disbursed'])
                
                if not comp_work_sample and not any('work' in normalize_key(h) for h in comp_headers):
                    errors.append(f"Completed Works CSV is missing a required Work Description column. Detected columns: {', '.join(comp_headers)}")
                    checks.append({"name": "Completed Schema: Work Title", "status": "FAIL", "message": "Could not identify Work Description column."})
                else:
                    checks.append({"name": "Completed Schema: Work Title", "status": "PASS", "message": "Work Description column verified."})

                if not comp_amt_sample and not any('amount' in normalize_key(h) or 'disbursed' in normalize_key(h) for h in comp_headers):
                    errors.append(f"Completed Works CSV is missing a required Disbursed Amount column. Detected columns: {', '.join(comp_headers)}")
                    checks.append({"name": "Completed Schema: Disbursed Amount", "status": "FAIL", "message": "Could not identify Disbursed Amount column."})
                else:
                    checks.append({"name": "Completed Schema: Disbursed Amount", "status": "PASS", "message": "Disbursed Amount column verified."})

                sr_sample = get_field_val(sample_row, ['sr no', 'sr_no', 's no', 'sno', 'serial no'])
                if sr_sample and sr_sample.lower() not in ('grand total', 'total', 'summary'):
                    comp_records.append(sample_row)

            for r in reader:
                sr = get_field_val(r, ['sr no', 'sr_no', 's no', 'sno', 'serial no'])
                if not sr or sr.lower() in ('grand total', 'total', 'summary'):
                    continue
                comp_records.append(r)
    except Exception as e:
        errors.append(f"Failed to parse Completed Works CSV: {str(e)}")
        checks.append({"name": "Completed Works CSV Parsing", "status": "FAIL", "message": str(e)})

    # 5. Record Checks
    if len(sanct_records) == 0:
        errors.append("Sanctioned Works CSV contains 0 valid work rows after filtering totals and headers.")
        checks.append({"name": "Sanctioned Records Count", "status": "FAIL", "message": "0 valid records found."})
    else:
        checks.append({"name": "Sanctioned Records Count", "status": "PASS", "message": f"{len(sanct_records)} valid records parsed."})

    if len(duplicate_ids) > 0:
        warnings.append(f"Duplicate Work IDs detected in Sanctioned Works ({len(duplicate_ids)} duplicates). System will assign unique sequence suffixes.")
        checks.append({"name": "Duplicate Work IDs Check", "status": "WARN", "message": f"{len(duplicate_ids)} duplicate Work IDs found."})
    else:
        checks.append({"name": "Duplicate Work IDs Check", "status": "PASS", "message": "100% unique Work IDs."})

    # Cross-dataset join check preview
    matched_completed = 0
    sanct_id_set = set(sanct_ids)
    for c_row in comp_records:
        c_code = get_work_code(c_row)
        if c_code in sanct_id_set:
            matched_completed += 1
            
    checks.append({
        "name": "Cross-Dataset Completion Linkage",
        "status": "PASS",
        "message": f"{matched_completed} of {len(comp_records)} completed works link directly to sanctioned records."
    })

    is_valid = (len(errors) == 0)

    return {
        "valid": is_valid,
        "sanctioned_count": len(sanct_records),
        "recommended_count": len(rec_records),
        "completed_count": len(comp_records),
        "duplicate_ids_count": len(duplicate_ids),
        "checks": checks,
        "errors": errors,
        "warnings": warnings
    }

# ----------------------------------------------------
# 2. RUN TRULY DYNAMIC ML PIPELINE & HYBRID RISK SCORING
# ----------------------------------------------------

def run_ml_pipeline(sanct_path: str, rec_path: str, comp_path: str, output_json_path: Optional[str] = None) -> Dict[str, Any]:
    rec_works = {}
    with open(rec_path, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        for r in reader:
            sr = get_field_val(r, ['sr no', 'sr_no', 's no', 'sno', 'serial no'])
            if not sr or sr.lower() in ('grand total', 'total', 'summary'):
                continue
            code = get_work_code(r)
            amt = parse_amount(get_field_val(r, ['recommended amount', 'amount recommended', 'amount', 'sanction amount'], '0'))
            date_val = parse_date(get_field_val(r, ['recommended date', 'date of recommendation', 'recommendation date', 'rec date', 'sanction date']))
            desc_val = get_field_val(r, ['recommended work', 'work description', 'work', 'work title'])
            cat_val = get_field_val(r, ['work category', 'category', 'sector'], 'Normal/Others')
            
            if code:
                rec_works[code] = {
                    'code': code,
                    'amt': amt,
                    'date': date_val,
                    'desc': desc_val,
                    'cat': cat_val
                }

    comp_works = {}
    with open(comp_path, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        for r in reader:
            sr = get_field_val(r, ['sr no', 'sr_no', 's no', 'sno', 'serial no'])
            if not sr or sr.lower() in ('grand total', 'total', 'summary'):
                continue
            code = get_work_code(r)
            disb_amt = parse_amount(get_field_val(r, ['amount disbursed', 'disbursed amount', 'amount', 'disbursed'], '0'))
            comp_date = parse_date(get_field_val(r, ['completion date', 'date of completion', 'comp date']))
            desc_val = get_field_val(r, ['work description', 'work', 'work title', 'completed work'])
            
            if code:
                comp_works[code] = {
                    'code': code,
                    'amt_disbursed': disb_amt,
                    'comp_date': comp_date,
                    'desc': desc_val
                }

    sanct_records = []
    observed_delays = []
    seen_codes = set()
    
    with open(sanct_path, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        for idx, r in enumerate(reader):
            sr = get_field_val(r, ['sr no', 'sr_no', 's no', 'sno', 'serial no'])
            if not sr or sr.lower() in ('grand total', 'total', 'summary'):
                continue
            
            raw_code = get_work_code(r)
            code = raw_code
            if code in seen_codes:
                code = f"{raw_code}-{idx+1}"
            seen_codes.add(code)
            
            s_amt = parse_amount(get_field_val(r, ['sanction amount', 'sanctioned amount', 'amount sanctioned', 'amount'], '0'))
            s_date = parse_date(get_field_val(r, ['sanction date', 'date of sanction', 'sanct date']))
            
            r_date = parse_date(get_field_val(r, ['recommended date', 'date of recommendation', 'recommendation date', 'rec date']))
            is_rec_date_observed = (r_date is not None)
            
            r_item = rec_works.get(raw_code)
            if not r_date and r_item and r_item['date']:
                r_date = r_item['date']
                is_rec_date_observed = True
                
            r_amt = r_item['amt'] if r_item else s_amt
            
            if s_date and r_date:
                delay_days = max(0, (s_date - r_date).days)
                observed_delays.append(delay_days)
            else:
                delay_days = None
                
            c_item = comp_works.get(raw_code)
            is_completed = (c_item is not None)
            disbursed_amt = c_item['amt_disbursed'] if is_completed else 0.0
            
            cat = get_field_val(r, ['work category', 'category', 'sector', 'work type'], 'Normal/Others')
            ida = get_field_val(r, ['ida', 'implementing agency', 'agency', 'nodal agency'], 'Nodal Agency')
            mp_name = get_field_val(r, ["hon'ble members of parliament", "mp name", "member of parliament", "representative"], 'Nodal Representative')
            constituency = get_field_val(r, ['constituency', 'parliamentary constituency'], 'Constituency')
            state = get_field_val(r, ['state', 'state name'], 'State')
            district = extract_district(r, default=constituency.capitalize() if constituency else 'District')
            status = get_field_val(r, ['work status', 'status', 'project status'], 'Sanction Issued')
            title = get_field_val(r, ['work description', 'work', 'work title', 'recommended work'], code)
            
            sanct_records.append({
                'sr': sr,
                'code': code,
                'title': str(title).strip(),
                'category': str(cat).strip(),
                'ida': str(ida).strip(),
                'district': str(district).strip(),
                'mp_name': str(mp_name).strip(),
                'constituency': str(constituency).strip(),
                'state': str(state).strip(),
                'sanct_amount': s_amt,
                'rec_amount': r_amt,
                'sanct_date': s_date.strftime('%Y-%m-%d') if s_date else None,
                'rec_date': r_date.strftime('%Y-%m-%d') if r_date else None,
                'is_rec_date_observed': is_rec_date_observed,
                'delay_days': delay_days,
                'status': str(status).strip(),
                'is_completed': is_completed,
                'disbursed_amount': disbursed_amt
            })

    mean_delay_baseline = (sum(observed_delays) / len(observed_delays)) if observed_delays else 45.0
    
    for rec in sanct_records:
        if rec['delay_days'] is None:
            rec['delay_days'] = round(mean_delay_baseline, 1)
            rec['is_delay_imputed'] = True
        else:
            rec['is_delay_imputed'] = False

    category_amounts = {}
    ida_counts = {}
    desc_counts = {}

    for rec in sanct_records:
        cat = rec['category']
        category_amounts.setdefault(cat, []).append(rec['sanct_amount'])
        ida_counts[rec['ida']] = ida_counts.get(rec['ida'], 0) + 1
        desc = rec['title'].lower()
        desc_counts[desc] = desc_counts.get(desc, 0) + 1

    category_stats = {}
    for cat, amts in category_amounts.items():
        mean_val = sum(amts) / len(amts)
        variance = sum((x - mean_val) ** 2 for x in amts) / len(amts) if len(amts) > 1 else 0.0
        std_val = math.sqrt(variance)
        category_stats[cat] = {'mean': mean_val, 'std': std_val if std_val > 0 else 1.0}

    X = []
    total_sanct = len(sanct_records) if len(sanct_records) > 0 else 1
    
    for rec in sanct_records:
        cat = rec['category']
        stats = category_stats[cat]
        zscore = (rec['sanct_amount'] - stats['mean']) / stats['std']
        ida_pct = (ida_counts[rec['ida']] / total_sanct) * 100.0
        log_amt = math.log(1.0 + max(0.0, rec['sanct_amount']))
        
        variance_pct = 0.0
        if rec['is_completed'] and rec['sanct_amount'] > 0:
            variance_pct = abs(1.0 - (rec['disbursed_amount'] / rec['sanct_amount'])) * 100.0
            
        row_feat = [
            float(rec['delay_days']),
            float(log_amt),
            float(zscore),
            float(ida_pct),
            1.0 if rec['is_completed'] else 0.0,
            float(variance_pct)
        ]
        rec['features'] = {
            'sanction_delay_days': rec['delay_days'],
            'is_recommendation_date_imputed': rec['is_delay_imputed'],
            'log_sanction_amount': round(log_amt, 4),
            'category_cost_zscore': round(zscore, 4),
            'ida_concentration_pct': round(ida_pct, 2),
            'is_completed_flag': 1 if rec['is_completed'] else 0,
            'disbursed_variance_pct': round(variance_pct, 2)
        }
        X.append(row_feat)

    iso_model = IsolationForestModel(n_estimators=100, max_samples=256, random_state=42)
    iso_model.fit(X)
    raw_if_scores = iso_model.compute_anomaly_scores(X)

    min_if = min(raw_if_scores) if raw_if_scores else 0.5
    max_if = max(raw_if_scores) if raw_if_scores else 0.5

    s_ml_scores = []
    for score in raw_if_scores:
        if max_if != min_if:
            s_ml = ((score - min_if) / (max_if - min_if)) * 100.0
        else:
            s_ml = 50.0
        s_ml_scores.append(round(s_ml, 1))

    scored_output = []
    for idx, rec in enumerate(sanct_records):
        s_ml = s_ml_scores[idx]
        is_ml_anomaly = (s_ml >= 70.0)
        
        rule_pts = 0
        rule_signals = []
        
        # Rule 1: Administrative Delay
        if rec['delay_days'] > 180:
            rule_pts += 40
            tag = f"Administrative Delay: {rec['delay_days']} Days (>180d threshold)"
            if rec['is_delay_imputed']:
                tag += " [Imputed Mean Fallback]"
            rule_signals.append(tag)
        elif rec['delay_days'] > 120:
            rule_pts += 25
            tag = f"Administrative Delay: {rec['delay_days']} Days (>120d threshold)"
            if rec['is_delay_imputed']:
                tag += " [Imputed Mean Fallback]"
            rule_signals.append(tag)
        elif rec['delay_days'] > 90:
            rule_pts += 10
            tag = f"Administrative Delay: {rec['delay_days']} Days (>90d threshold)"
            if rec['is_delay_imputed']:
                tag += " [Imputed Mean Fallback]"
            rule_signals.append(tag)
            
        # Rule 2: Category Cost Outlier
        z_val = rec['features']['category_cost_zscore']
        if z_val > 2.5:
            rule_pts += 35
            rule_signals.append(f"Category Cost Outlier: Z-Score +{z_val:.2f} in '{rec['category']}'")
        elif z_val > 1.5:
            rule_pts += 20
            rule_signals.append(f"Category Cost Deviation: Z-Score +{z_val:.2f} in '{rec['category']}'")
            
        # Rule 3: High Value Allocation
        if rec['sanct_amount'] >= 15000000:
            rule_pts += 25
            rule_signals.append(f"High-Value Project Allocation: ₹{rec['sanct_amount']/1e5:.1f} Lakhs")
        elif rec['sanct_amount'] >= 5000000:
            rule_pts += 15
            rule_signals.append(f"Significant Project Allocation: ₹{rec['sanct_amount']/1e5:.1f} Lakhs")
            
        # Rule 4: Title Cluster Duplicate Match
        desc_key = rec['title'].lower()
        if desc_counts.get(desc_key, 0) > 1:
            rule_pts += 15
            rule_signals.append(f"Duplicate Work Title Cluster ({desc_counts[desc_key]} matching records)")
            
        # Rule 5: Disbursed Variance
        var_val = rec['features']['disbursed_variance_pct']
        if var_val > 20.0:
            rule_pts += 20
            rule_signals.append(f"Disbursed Amount Variance: {var_val:.1f}% deviation from sanction")

        s_rule = min(100.0, float(rule_pts))
        
        # Hybrid Formula: S_risk = 0.60 * S_ml + 0.40 * S_rule
        s_risk = (0.60 * s_ml) + (0.40 * s_rule)
        s_risk = round(min(100.0, max(0.0, s_risk)), 1)
        
        if s_risk >= 75.0:
            band = "CRITICAL RISK PRIORITY"
        elif s_risk >= 60.0:
            band = "HIGH RISK PRIORITY"
        elif s_risk >= 40.0:
            band = "MEDIUM RISK PRIORITY"
        else:
            band = "NORMAL RISK"
            
        explanation = {
            'ml_anomaly_evidence': {
                'is_ml_anomaly': is_ml_anomaly,
                'ml_anomaly_score': s_ml,
                'isolation_forest_raw_score': round(float(raw_if_scores[idx]), 4),
                'anomaly_threshold_rule': "S_ml >= 70.0 (Top 30% Anomaly Intensity Range)"
            },
            'deterministic_rule_evidence': {
                'rule_score': s_rule,
                'triggered_rule_count': len(rule_signals),
                'rule_signals': rule_signals if rule_signals else ["Standard Compliance Line"]
            },
            'composite_risk': {
                'risk_priority_score': s_risk,
                'severity_band': band,
                'weights_applied': {'w_ml': 0.60, 'w_rule': 0.40}
            }
        }
        
        item_scored = {
            'id': rec['code'],
            'sr_no': rec['sr'],
            'title': rec['title'],
            'category': rec['category'],
            'ida': rec['ida'],
            'district': rec['district'],
            'mp_name': rec['mp_name'],
            'constituency': rec['constituency'],
            'state': rec['state'],
            'sanctioned_amount_lakhs': round(rec['sanct_amount'] / 1e5, 2),
            'recommended_amount_lakhs': round(rec['rec_amount'] / 1e5, 2),
            'sanction_delay_days': rec['delay_days'],
            'is_recommendation_date_imputed': rec['is_delay_imputed'],
            'status': rec['status'],
            'is_completed': rec['is_completed'],
            'disbursed_amount_lakhs': round(rec['disbursed_amount'] / 1e5, 2),
            'features': rec['features'],
            'ml_anomaly_score': s_ml,
            'rule_score': s_rule,
            'risk_priority_score': s_risk,
            'severity_band': band,
            'is_ml_anomaly': is_ml_anomaly,
            'rule_signals': rule_signals if rule_signals else ["Standard Compliance Line"],
            'explanation': explanation
        }
        scored_output.append(item_scored)

    scored_output.sort(key=lambda x: x['risk_priority_score'], reverse=True)

    anomalies_count = sum(1 for w in scored_output if w['is_ml_anomaly'])
    critical_count = sum(1 for w in scored_output if w['severity_band'] == 'CRITICAL RISK PRIORITY')
    high_count = sum(1 for w in scored_output if w['severity_band'] == 'HIGH RISK PRIORITY')
    medium_count = sum(1 for w in scored_output if w['severity_band'] == 'MEDIUM RISK PRIORITY')
    normal_count = sum(1 for w in scored_output if w['severity_band'] == 'NORMAL RISK')

    result_payload = {
        'metadata': {
            'model_name': 'IsolationForest (Pure Python Kernel)',
            'n_estimators': 100,
            'total_scored': len(scored_output),
            'anomaly_count': anomalies_count,
            'critical_count': critical_count,
            'high_count': high_count,
            'medium_count': medium_count,
            'normal_count': normal_count,
            'mean_delay_baseline': round(mean_delay_baseline, 1),
            'weights': {'w_ml': 0.60, 'w_rule': 0.40},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M IST')
        },
        'works': scored_output,
        'raw_sanctioned': sanct_records,
        'raw_recommended': [
            {
                'sr_no': v.get('sr_no', '1'),
                'title': v['desc'],
                'recommended_amount': v['amt'],
                'recommended_amount_lakhs': round(v['amt'] / 1e5, 2),
                'rec_date': v['date'].strftime('%Y-%m-%d') if v['date'] else None,
                'district': sanct_records[0]['district'] if sanct_records else 'District'
            }
            for k, v in rec_works.items()
        ] if rec_works else [],
        'raw_completed': [
            {
                'sr_no': v.get('sr_no', '1'),
                'work_id_matched': k,
                'title': v['desc'],
                'disbursed_amount': v['amt_disbursed'],
                'disbursed_amount_lakhs': round(v['amt_disbursed'] / 1e5, 2),
                'completion_date': v['comp_date'].strftime('%Y-%m-%d') if v['comp_date'] else None,
                'district': sanct_records[0]['district'] if sanct_records else 'District'
            }
            for k, v in comp_works.items()
        ] if comp_works else []
    }

    if output_json_path:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(result_payload, f, indent=2)

    return result_payload

# ----------------------------------------------------
# 3. ATOMIC MULTI-DATASET ACTIVATION (NO DESTRUCTION)
# ----------------------------------------------------

def activate_dataset_in_db(
    db: Session,
    ml_result: Dict[str, Any],
    dataset_name: str = "Active MPLADS Dataset",
    source_type: str = "UPLOADED",
    dataset_id: Optional[str] = None,
    validation_report: Optional[Dict[str, Any]] = None
) -> Any:
    from models import (
        SanctionedWork, 
        RecommendedWork, 
        CompletedWork, 
        MlScoredWork, 
        InvestigationCase, 
        InvestigationNote, 
        AuditLog,
        DatasetMetadata
    )

    scored_works = ml_result['works']
    meta = ml_result['metadata']

    first_w = scored_works[0] if scored_works else {}
    st_val = first_w.get('state', 'State')
    dist_val = first_w.get('district', 'District')
    const_val = first_w.get('constituency', 'Constituency')

    if not dataset_id:
        if source_type == "DEMO_RESTORE":
            dataset_id = "dataset_ludhiana_demo"
        else:
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', dist_val.lower())
            timestamp_str = datetime.now().strftime('%Y%m%d%H%M%S')
            dataset_id = f"dataset_{safe_name}_{timestamp_str}"

    # 1. Clear ONLY records belonging to this specific dataset_id (keeps other datasets intact!)
    db.query(MlScoredWork).filter(MlScoredWork.dataset_id == dataset_id).delete()
    db.query(SanctionedWork).filter(SanctionedWork.dataset_id == dataset_id).delete()
    db.query(RecommendedWork).filter(RecommendedWork.dataset_id == dataset_id).delete()
    db.query(CompletedWork).filter(CompletedWork.dataset_id == dataset_id).delete()
    db.query(InvestigationCase).filter(InvestigationCase.dataset_id == dataset_id).delete()

    # 2. Insert Sanctioned Works
    sanct_objects = []
    for w in scored_works:
        amt = float(w['sanctioned_amount_lakhs']) * 100000.0
        obj = SanctionedWork(
            id=f"{dataset_id}:{w['id']}",
            dataset_id=dataset_id,
            work_id=w['id'],
            sr_no=w.get('sr_no'),
            title=w['title'],
            category=w['category'],
            ida=w['ida'],
            district=w['district'],
            mp_name=w['mp_name'],
            constituency=w['constituency'],
            state=w['state'],
            sanctioned_amount=amt,
            sanctioned_amount_lakhs=w['sanctioned_amount_lakhs'],
            sanct_date=w.get('sanct_date'),
            status=w['status']
        )
        sanct_objects.append(obj)
    db.bulk_save_objects(sanct_objects)

    # 3. Insert Recommended Works
    rec_objects = []
    for r in ml_result.get('raw_recommended', []):
        obj = RecommendedWork(
            dataset_id=dataset_id,
            sr_no=r.get('sr_no'),
            title=r['title'],
            recommended_amount=r['recommended_amount'],
            recommended_amount_lakhs=r['recommended_amount_lakhs'],
            rec_date=r.get('rec_date'),
            district=r.get('district', dist_val)
        )
        rec_objects.append(obj)
    if rec_objects:
        db.bulk_save_objects(rec_objects)

    # 4. Insert Completed Works
    comp_objects = []
    for c in ml_result.get('raw_completed', []):
        obj = CompletedWork(
            dataset_id=dataset_id,
            sr_no=c.get('sr_no'),
            work_id_matched=c.get('work_id_matched'),
            title=c['title'],
            disbursed_amount=c['disbursed_amount'],
            disbursed_amount_lakhs=c['disbursed_amount_lakhs'],
            completion_date=c.get('completion_date'),
            district=c.get('district', dist_val)
        )
        comp_objects.append(obj)
    if comp_objects:
        db.bulk_save_objects(comp_objects)

    # 5. Insert ML Scored Works
    ml_objects = []
    for w in scored_works:
        obj = MlScoredWork(
            id=f"{dataset_id}:{w['id']}",
            dataset_id=dataset_id,
            work_id=w['id'],
            sr_no=w.get('sr_no'),
            title=w['title'],
            category=w['category'],
            ida=w['ida'],
            district=w['district'],
            mp_name=w['mp_name'],
            constituency=w['constituency'],
            state=w['state'],
            sanctioned_amount_lakhs=w['sanctioned_amount_lakhs'],
            recommended_amount_lakhs=w['recommended_amount_lakhs'],
            sanction_delay_days=int(round(w['sanction_delay_days'] or 0)),
            is_recommendation_date_imputed=w.get('is_recommendation_date_imputed', False),
            status=w['status'],
            is_completed=w['is_completed'],
            disbursed_amount_lakhs=w.get('disbursed_amount_lakhs', 0.0),
            features=w['features'],
            ml_anomaly_score=w['ml_anomaly_score'],
            rule_score=w['rule_score'],
            risk_priority_score=w['risk_priority_score'],
            severity_band=w['severity_band'],
            is_ml_anomaly=w['is_ml_anomaly'],
            rule_signals=w['rule_signals'],
            explanation=w['explanation']
        )
        ml_objects.append(obj)
    db.bulk_save_objects(ml_objects)

    # 6. Insert InvestigationCase records for this dataset's works
    cases = [InvestigationCase(dataset_id=dataset_id, work_id=w['id'], current_status="UNDER REVIEW") for w in scored_works]
    db.bulk_save_objects(cases)

    # 7. Update DatasetMetadata Library (Set all other datasets is_active=False)
    db.query(DatasetMetadata).filter(DatasetMetadata.dataset_id != dataset_id).update({"is_active": False, "status": "STORED"})

    unique_idas = len(set(w['ida'] for w in scored_works)) if scored_works else 1

    existing_meta = db.query(DatasetMetadata).filter(DatasetMetadata.dataset_id == dataset_id).first()
    if existing_meta:
        existing_meta.name = dataset_name
        existing_meta.state = st_val
        existing_meta.district = dist_val
        existing_meta.constituency = const_val
        existing_meta.status = "ACTIVE"
        existing_meta.is_active = True
        existing_meta.activated_at = datetime.utcnow()
        existing_meta.sanctioned_count = len(scored_works)
        existing_meta.recommended_count = len(rec_objects) if rec_objects else len(scored_works)
        existing_meta.completed_count = len(comp_objects)
        existing_meta.ida_count = unique_idas
        existing_meta.ml_anomaly_count = meta['anomaly_count']
        existing_meta.critical_risk_count = meta['critical_count']
        existing_meta.high_risk_count = meta['high_count']
        existing_meta.medium_risk_count = meta['medium_count']
        existing_meta.normal_risk_count = meta['normal_count']
        existing_meta.validation_status = "VALIDATED"
        existing_meta.analysis_status = "COMPLETED"
        if validation_report:
            existing_meta.validation_report = validation_report
        db_meta = existing_meta
    else:
        new_meta = DatasetMetadata(
            dataset_id=dataset_id,
            name=dataset_name,
            state=st_val,
            district=dist_val,
            constituency=const_val,
            status="ACTIVE",
            is_active=True,
            uploaded_at=datetime.utcnow(),
            activated_at=datetime.utcnow(),
            sanctioned_count=len(scored_works),
            recommended_count=len(rec_objects) if rec_objects else len(scored_works),
            completed_count=len(comp_objects),
            ida_count=unique_idas,
            ml_anomaly_count=meta['anomaly_count'],
            critical_risk_count=meta['critical_count'],
            high_risk_count=meta['high_count'],
            medium_risk_count=meta['medium_count'],
            normal_risk_count=meta['normal_count'],
            validation_status="VALIDATED",
            analysis_status="COMPLETED",
            validation_report=validation_report
        )
        db.add(new_meta)
        db_meta = new_meta

    # 8. Record Audit Log Event
    audit_action = "DEMO_DATASET_RESTORED" if source_type == "DEMO_RESTORE" else "DATASET_ACTIVATED"
    audit_entry = AuditLog(
        dataset_id=dataset_id,
        work_id=scored_works[0]['id'] if scored_works else "SYSTEM_DATASET",
        action_type=audit_action,
        previous_status="STORED",
        new_status=f"ACTIVE ({dataset_name})",
        actor="State Nodal Officer",
        details=f"Dataset '{dataset_name}' [{dataset_id}] activated: {len(scored_works)} Sanctioned Works, {meta['anomaly_count']} ML Anomalies.",
        timestamp=datetime.utcnow()
    )
    db.add(audit_entry)

    db.commit()
    db.refresh(db_meta)

    return db_meta
