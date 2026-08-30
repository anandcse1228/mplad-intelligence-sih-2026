import csv
import json
import math
import os
import random
import re
from datetime import datetime

# ----------------------------------------------------
# PURE PYTHON ISOLATION FOREST ML ANOMALY ENGINE
# ----------------------------------------------------

def parse_date(d_str):
    if not d_str or str(d_str).upper() == 'NA':
        return None
    for fmt in ('%d-%b-%Y', '%d-%b-%y', '%Y-%m-%d'):
        try:
            return datetime.strptime(str(d_str).strip(), fmt)
        except ValueError:
            pass
    return None

def parse_amount(a_str):
    if not a_str or str(a_str).upper() == 'NA':
        return 0.0
    cleaned = str(a_str).replace(',', '').replace('₹', '').replace(' ', '').strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def get_work_code(row):
    w = row.get('Work') or row.get('WORK') or ''
    s = str(w).strip()
    if not s:
        return f"WORK-{row.get('Sr. No.', '0').strip()}"
    m = re.search(r'(WS/MP\d+/\d{4}-\d{4}/\d+)', s)
    if m:
        return m.group(1)
    first_token = s.split()[0].rstrip('-')
    if first_token and first_token.upper() != 'NA':
        return first_token
    return f"WORK-SR-{row.get('Sr. No.', '0').strip()}"

# Average path length factor c(n) for sample size n
def c_factor(n):
    if n <= 1:
        return 1.0
    if n == 2:
        return 1.0
    # Euler-Mascheroni constant gamma = 0.5772156649
    return 2.0 * (math.log(n - 1) + 0.5772156649) - (2.0 * (n - 1) / n)

class IsolationTreeNode:
    def __init__(self, size):
        self.size = size
        self.split_feat = None
        self.split_val = None
        self.left = None
        self.right = None
        self.is_leaf = True

def build_itree(data, current_height, height_limit):
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

def path_length(x, node, current_height):
    if node.is_leaf or node.size <= 1:
        return current_height + c_factor(node.size)
    if x[node.split_feat] < node.split_val:
        return path_length(x, node.left, current_height + 1)
    else:
        return path_length(x, node.right, current_height + 1)

class IsolationForestModel:
    def __init__(self, n_estimators=100, max_samples=256, random_state=42):
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.random_state = random_state
        self.trees = []
        
    def fit(self, X):
        random.seed(self.random_state)
        n_samples = len(X)
        sample_size = min(self.max_samples, n_samples)
        height_limit = math.ceil(math.log2(max(2, sample_size)))
        
        self.trees = []
        for _ in range(self.n_estimators):
            sample = random.sample(X, sample_size)
            tree = build_itree(sample, 0, height_limit)
            self.trees.append(tree)
            
    def compute_anomaly_scores(self, X):
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
# MAIN EXECUTION: DATA LOADING & SCORED DATASET CREATION
# ----------------------------------------------------

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, 'data')

rec_path = os.path.join(data_dir, 'recommended_works.csv')
sanct_path = os.path.join(data_dir, 'sanctioned_works.csv')
comp_path = os.path.join(data_dir, 'completed_works.csv')

# 1. Load Recommended Works
rec_works = {}
with open(rec_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        sr = r.get('Sr. No.', '').strip()
        if not sr or sr.lower() == 'grand total':
            continue
        code = get_work_code(r)
        if code:
            rec_works[code] = {
                'code': code,
                'amt': parse_amount(r.get('RECOMMENDED AMOUNT   ( ₹ )', '0')),
                'date': parse_date(r.get('Recommended date', '')),
                'desc': r.get('Work description', '').strip(),
                'cat': r.get('Work category', '').strip()
            }

# 2. Load Completed Works
comp_works = {}
with open(comp_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        sr = r.get('Sr. No.', '').strip()
        if not sr or sr.lower() == 'grand total':
            continue
        code = get_work_code(r)
        if code:
            comp_works[code] = {
                'code': code,
                'amt_disbursed': parse_amount(r.get('Amount Disbursed ( ₹ )', '0')),
                'comp_date': parse_date(r.get('Completion Date', '')),
                'desc': r.get('Work Description', '').strip()
            }

# 3. Load Sanctioned Works
sanct_records = []
with open(sanct_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        sr = r.get('Sr. No.', '').strip()
        if not sr or sr.lower() == 'grand total':
            continue
        code = get_work_code(r)
        s_amt = parse_amount(r.get('Sanction Amount ( ₹ )', '0'))
        s_date = parse_date(r.get('Sanction Date', ''))
        r_date = parse_date(r.get('Recommended date', ''))
        
        # Check explicit observation status
        is_rec_date_observed = r_date is not None
        
        r_item = rec_works.get(code)
        if not r_date and r_item and r_item['date']:
            r_date = r_item['date']
            is_rec_date_observed = True
            
        r_amt = r_item['amt'] if r_item else s_amt
        
        if s_date and r_date:
            delay_days = max(0, (s_date - r_date).days)
            is_imputed = False
        else:
            delay_days = 75.35  # Empirical mean fallback
            is_imputed = True
        
        c_item = comp_works.get(code)
        is_completed = c_item is not None
        disbursed_amt = c_item['amt_disbursed'] if is_completed else 0.0
        
        sanct_records.append({
            'sr': sr,
            'code': code,
            'title': r.get('Work description', '').strip(),
            'category': r.get('Work category', '') or r.get('Work Category', 'Normal/Others'),
            'ida': r.get('IDA', '').strip(),
            'mp_name': r.get("Hon'ble Members of Parliament", '').strip(),
            'constituency': r.get('Constituency', '').strip(),
            'state': r.get('State', '').strip(),
            'sanct_amount': s_amt,
            'rec_amount': r_amt,
            'sanct_date': s_date.strftime('%Y-%m-%d') if s_date else None,
            'rec_date': r_date.strftime('%Y-%m-%d') if r_date else None,
            'is_rec_date_observed': is_rec_date_observed,
            'is_delay_imputed': is_imputed,
            'delay_days': round(delay_days, 1),
            'status': r.get('Work Status', '').strip(),
            'is_completed': is_completed,
            'disbursed_amount': disbursed_amt
        })

print(f"Loaded {len(sanct_records)} sanctioned works for ML Feature Extraction & Scoring.")

# Stats for Z-score & concentration
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
    variance = sum((x - mean_val) ** 2 for x in amts) / len(amts)
    std_val = math.sqrt(variance)
    category_stats[cat] = {'mean': mean_val, 'std': std_val if std_val > 0 else 1.0}

# Feature Names & Matrix Construction
feature_names = [
    'sanction_delay_days',
    'log_sanction_amount',
    'category_cost_zscore',
    'ida_concentration_pct',
    'is_completed_flag',
    'disbursed_variance_pct'
]

X = []
for rec in sanct_records:
    cat = rec['category']
    stats = category_stats[cat]
    zscore = (rec['sanct_amount'] - stats['mean']) / stats['std']
    ida_pct = (ida_counts[rec['ida']] / len(sanct_records)) * 100.0
    log_amt = math.log(1.0 + rec['sanct_amount'])
    
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

# Fit Isolation Forest Model
iso_model = IsolationForestModel(n_estimators=100, max_samples=256, random_state=42)
iso_model.fit(X)

# Compute Raw Isolation Forest Anomaly Scores
raw_if_scores = iso_model.compute_anomaly_scores(X)

# Rescale S_ml to [0, 100] via Min-Max Normalization
min_if = min(raw_if_scores)
max_if = max(raw_if_scores)

s_ml_scores = []
for score in raw_if_scores:
    if max_if != min_if:
        s_ml = ((score - min_if) / (max_if - min_if)) * 100.0
    else:
        s_ml = 50.0
    s_ml_scores.append(round(s_ml, 1))

# Deterministic Rule Engine & Hybrid Risk Priority Scoring
scored_output = []

for idx, rec in enumerate(sanct_records):
    s_ml = s_ml_scores[idx]
    # ML Anomaly Threshold S_ml >= 70.0 (Upper 30% anomaly intensity percentile in Min-Max space)
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
    
    # Hybrid Risk Priority Score S_risk = 0.60 * S_ml + 0.40 * S_rule
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
    
    district_clean = rec['ida'].split('(')[0].capitalize() if '(' in rec['ida'] else rec['ida']
    
    item_scored = {
        'id': rec['code'],
        'sr_no': rec['sr'],
        'title': rec['title'],
        'category': rec['category'],
        'ida': rec['ida'],
        'district': district_clean,
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

# Sort by Risk Priority Score descending
scored_output.sort(key=lambda x: x['risk_priority_score'], reverse=True)

# Metrics Summary
anomalies_count = sum(1 for w in scored_output if w['is_ml_anomaly'])
critical_count = sum(1 for w in scored_output if w['severity_band'] == 'CRITICAL RISK PRIORITY')
high_count = sum(1 for w in scored_output if w['severity_band'] == 'HIGH RISK PRIORITY')
medium_count = sum(1 for w in scored_output if w['severity_band'] == 'MEDIUM RISK PRIORITY')
normal_count = sum(1 for w in scored_output if w['severity_band'] == 'NORMAL RISK')

print("\n=== ISOLATION FOREST ML ANOMALY ENGINE FIT SUMMARY ===")
print(f"• Total Sanctioned Records Scored: {len(scored_output)}")
print(f"• ML Isolation Forest Anomaly Candidates (S_ml >= 70): {anomalies_count} ({anomalies_count/len(scored_output)*100:.1f}%)")
print(f"• Critical Risk Priority (S_risk >= 75): {critical_count}")
print(f"• High Risk Priority (60 <= S_risk < 75): {high_count}")
print(f"• Medium Risk Priority (40 <= S_risk < 60): {medium_count}")
print(f"• Normal / Low Risk (S_risk < 40): {normal_count}")

# Save JSON file to data/ml_scored_works.json
out_json_path = os.path.join(data_dir, 'ml_scored_works.json')
with open(out_json_path, 'w', encoding='utf-8') as f:
    json.dump({
        'metadata': {
            'model_name': 'IsolationForest (Pure Python Kernel)',
            'n_estimators': 100,
            'total_scored': len(scored_output),
            'anomaly_count': anomalies_count,
            'features_used': feature_names,
            'weights': {'w_ml': 0.60, 'w_rule': 0.40},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M IST')
        },
        'works': scored_output
    }, f, indent=2)

print(f"Successfully written ML scored dataset to: {out_json_path}")
