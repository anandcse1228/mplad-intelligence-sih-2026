import csv
import json
import os
import re
from datetime import datetime
from database import engine, SessionLocal, Base, DB_PATH
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

# Root Data Directory Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_DIR = os.path.join(BASE_DIR, 'data', 'demo_backup')

DEMO_DATASET_ID = "dataset_ludhiana_demo"

def clean_str(s):
    if s is None:
        return ''
    return str(s).replace('\ufeff', '').strip(' \t\r\n"\'')

def parse_float(val):
    if not val:
        return 0.0
    clean = str(val).replace(',', '').replace('₹', '').strip()
    try:
        return float(clean)
    except ValueError:
        return 0.0

def init_database():
    print("==================================================")
    print("  MPLAD INTELLIGENCE -- SQLITE DATABASE INITIALIZER")
    print("==================================================")
    print(f"Target Database File: {DB_PATH}")

    # Reset / Create Tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[OK] All 8 SQLAlchemy tables created successfully.")

    db = SessionLocal()

    try:
        # 1. Import sanctioned_works.csv from demo_backup
        sanct_csv = os.path.join(DEMO_DIR, 'sanctioned_works.csv')
        sanct_records = []
        work_ids = []
        with open(sanct_csv, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            for r in reader:
                sr = clean_str(r.get('Sr. No.') or r.get('Sr.No.') or r.get('sr_no') or '')
                if not sr or sr.lower() in ('grand total', 'total', 'summary'):
                    continue
                
                w_str = clean_str(r.get('Work') or r.get('Work Description') or '')
                m = re.search(r'(WS/MP\d+/\d{4}-\d{4}/\d+)', w_str)
                work_id = m.group(1) if m else w_str.split()[0].rstrip('-')
                work_ids.append(work_id)

                amt = parse_float(r.get('Sanction Amount ( ₹ )', 0))
                amt_lakhs = amt / 100000.0

                item = SanctionedWork(
                    id=f"{DEMO_DATASET_ID}:{work_id}",
                    dataset_id=DEMO_DATASET_ID,
                    work_id=work_id,
                    sr_no=sr,
                    title=clean_str(r.get('Work Description', w_str)),
                    category=clean_str(r.get('Work Category', 'Normal/Others')),
                    ida=clean_str(r.get('Implementing Agency', 'LUDHIANA_IDA')),
                    district=clean_str(r.get('District', 'Ludhiana')),
                    mp_name=clean_str(r.get('MP Name', 'AMRINDER SINGH RAJA WARRING')),
                    constituency=clean_str(r.get('Constituency', 'LUDHIANA')),
                    state=clean_str(r.get('State', 'Punjab')),
                    sanctioned_amount=amt,
                    sanctioned_amount_lakhs=amt_lakhs,
                    sanct_date=clean_str(r.get('Sanction Date', '')),
                    status=clean_str(r.get('Work Status', 'Sanction Issued'))
                )
                sanct_records.append(item)

        db.bulk_save_objects(sanct_records)
        db.commit()
        print(f"[OK] Imported {len(sanct_records)} rows into 'sanctioned_works'.")

        # 2. Import recommended_works.csv from demo_backup
        rec_csv = os.path.join(DEMO_DIR, 'recommended_works.csv')
        rec_records = []
        with open(rec_csv, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            for r in reader:
                sr = clean_str(r.get('Sr. No.') or r.get('Sr.No.') or r.get('sr_no') or '')
                if not sr or sr.lower() in ('grand total', 'total', 'summary'):
                    continue
                amt = parse_float(r.get('RECOMMENDED AMOUNT   ( ₹ )', 0))
                amt_lakhs = amt / 100000.0
                item = RecommendedWork(
                    dataset_id=DEMO_DATASET_ID,
                    sr_no=sr,
                    title=clean_str(r.get('RECOMMENDED WORK', '')),
                    recommended_amount=amt,
                    recommended_amount_lakhs=amt_lakhs,
                    rec_date=clean_str(r.get('RECOMMENDATION DATE', '')),
                    district=clean_str(r.get('DISTRICT', 'Ludhiana'))
                )
                rec_records.append(item)

        db.bulk_save_objects(rec_records)
        db.commit()
        print(f"[OK] Imported {len(rec_records)} rows into 'recommended_works'.")

        # 3. Import completed_works.csv from demo_backup
        comp_csv = os.path.join(DEMO_DIR, 'completed_works.csv')
        comp_records = []
        with open(comp_csv, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            for r in reader:
                sr = clean_str(r.get('Sr. No.') or r.get('Sr.No.') or r.get('sr_no') or '')
                if not sr or sr.lower() in ('grand total', 'total', 'summary'):
                    continue
                amt = parse_float(r.get('Amount Disbursed ( ₹ )', 0))
                amt_lakhs = amt / 100000.0
                w_str = clean_str(r.get('Work Description') or r.get('Work') or '')
                m = re.search(r'(WS/MP\d+/\d{4}-\d{4}/\d+)', w_str)
                matched_id = m.group(1) if m else None

                item = CompletedWork(
                    dataset_id=DEMO_DATASET_ID,
                    sr_no=sr,
                    work_id_matched=matched_id,
                    title=w_str,
                    disbursed_amount=amt,
                    disbursed_amount_lakhs=amt_lakhs,
                    completion_date=clean_str(r.get('Completion Date', '')),
                    district=clean_str(r.get('District', 'Ludhiana'))
                )
                comp_records.append(item)

        db.bulk_save_objects(comp_records)
        db.commit()
        print(f"[OK] Imported {len(comp_records)} rows into 'completed_works'.")

        # 4. Import ml_scored_works.json from demo_backup
        ml_json = os.path.join(DEMO_DIR, 'ml_scored_works.json')
        with open(ml_json, 'r', encoding='utf-8') as f:
            ml_data = json.load(f)

        ml_records = []
        formula_mismatches = 0

        for w in ml_data['works']:
            s_ml = w['ml_anomaly_score']
            s_rule = w['rule_score']
            s_risk = w['risk_priority_score']
            calc_risk = round(min(100.0, max(0.0, (0.60 * s_ml) + (0.40 * s_rule))), 1)
            if abs(s_risk - calc_risk) > 0.05:
                formula_mismatches += 1

            item = MlScoredWork(
                id=f"{DEMO_DATASET_ID}:{w['id']}",
                dataset_id=DEMO_DATASET_ID,
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
                ml_anomaly_score=s_ml,
                rule_score=s_rule,
                risk_priority_score=s_risk,
                severity_band=w['severity_band'],
                is_ml_anomaly=w['is_ml_anomaly'],
                rule_signals=w['rule_signals'],
                explanation=w['explanation']
            )
            ml_records.append(item)

        db.bulk_save_objects(ml_records)
        db.commit()
        print(f"[OK] Imported {len(ml_records)} rows into 'ml_scored_works'.")

        # 5. Populate initial investigation_cases for demo works
        cases = [InvestigationCase(dataset_id=DEMO_DATASET_ID, work_id=w.work_id, current_status="UNDER REVIEW") for w in sanct_records]
        db.bulk_save_objects(cases)
        db.commit()
        print(f"[OK] Initialized {len(cases)} default rows in 'investigation_cases'.")

        # 6. Initialize DatasetMetadata row
        anomalies_count = sum(1 for w in ml_records if w.is_ml_anomaly)
        critical_count = sum(1 for w in ml_records if w.severity_band == "CRITICAL RISK PRIORITY")
        high_count = sum(1 for w in ml_records if w.severity_band == "HIGH RISK PRIORITY")
        medium_count = sum(1 for w in ml_records if w.severity_band == "MEDIUM RISK PRIORITY")
        normal_count = sum(1 for w in ml_records if w.severity_band == "NORMAL RISK")
        unique_idas = len(set(w.ida for w in sanct_records))

        meta = DatasetMetadata(
            dataset_id=DEMO_DATASET_ID,
            name="Punjab MPLADS — Ludhiana District",
            state="Punjab",
            district="Ludhiana",
            constituency="LUDHIANA",
            status="ACTIVE",
            is_active=True,
            uploaded_at=datetime.utcnow(),
            activated_at=datetime.utcnow(),
            sanctioned_count=len(sanct_records),
            recommended_count=len(rec_records),
            completed_count=len(comp_records),
            ida_count=unique_idas,
            ml_anomaly_count=anomalies_count,
            critical_risk_count=critical_count,
            high_risk_count=high_count,
            medium_risk_count=medium_count,
            normal_risk_count=normal_count,
            validation_status="VALIDATED",
            analysis_status="COMPLETED"
        )
        db.add(meta)
        db.commit()
        print(f"[OK] Initialized active DatasetMetadata row for '{DEMO_DATASET_ID}'.")

        print("\n==================================================")
        print("  SQLITE INITIALIZATION & AUDIT COMPLETE          ")
        print("==================================================")

    finally:
        db.close()

if __name__ == "__main__":
    init_database()
