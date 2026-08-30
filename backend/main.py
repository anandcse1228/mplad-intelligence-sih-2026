import csv
import json
import math
import os
import shutil
import urllib.parse
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, Query, Response, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, func, text
from sqlalchemy.orm import Session
from io import BytesIO

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
from schemas import (
    OverviewKpisResponse,
    MlScoredWorkSchema,
    RiskQueuePaginatedResponse,
    InvestigationActionRequest,
    InvestigationCaseResponse,
    InvestigationNoteRequest,
    InvestigationNoteResponse,
    AuditLogPaginatedResponse,
    HealthResponse,
    DatasetMetadataResponse,
    DatasetValidationResponse,
    DatasetAnalyzeRequest,
    DatasetAnalysisResponse,
    DatasetListResponse
)
from pipeline import validate_dataset_files, run_ml_pipeline, activate_dataset_in_db
from report_generator import generate_pdf_report

app = FastAPI(
    title="MPLAD Intelligence REST API",
    description="Statutory Compliance & Risk Prioritization Engine for MPLADS Projects",
    version="2.0.0"
)

# Enable CORS for Frontend Dev Server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://mplad-intelligence-sih-2026-1.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STAGING_DIR = os.path.join(DATA_DIR, 'staging')
DEMO_BACKUP_DIR = os.path.join(DATA_DIR, 'demo_backup')

os.makedirs(STAGING_DIR, exist_ok=True)
os.makedirs(DEMO_BACKUP_DIR, exist_ok=True)

# Helper: Get Active Dataset Metadata
def get_active_meta(db: Session) -> DatasetMetadata:
    meta = db.query(DatasetMetadata).filter(DatasetMetadata.is_active == True).first()
    if not meta:
        meta = db.query(DatasetMetadata).first()
        if meta:
            meta.is_active = True
            db.commit()
            db.refresh(meta)
    return meta

# Helper: Dynamic Enriched Explanation
def build_enriched_explanation(work: MlScoredWork) -> Dict[str, Any]:
    feats = work.features or {}
    
    sanction_delay = feats.get("sanction_delay_days", work.sanction_delay_days or 0)
    delay_eval = "High Delay (>120 Days)" if sanction_delay > 120 else ("Moderate Delay (>75 Days)" if sanction_delay > 75 else "Within Mean Baseline")
    
    cost_zscore = feats.get("category_cost_zscore", 0.0)
    zscore_eval = "Extreme Outlier (Z > +3.0)" if cost_zscore > 3.0 else ("Outlier (Z > +2.0)" if cost_zscore > 2.0 else "Within Expected Category Range")
    
    ida_pct = feats.get("ida_concentration_pct", 50.0)
    ida_eval = "High Agency Concentration (>70%)" if ida_pct > 70.0 else "Normal Agency Allocation"
    
    sanction_amt = work.sanctioned_amount_lakhs
    amt_eval = "High Value Project (≥₹25.0 L)" if sanction_amt >= 25.0 else ("Medium Value Project (>₹10.0 L)" if sanction_amt >= 10.0 else "Standard Outlay")

    comp_flag = feats.get("is_completed_flag", 1 if work.is_completed else 0)
    comp_eval = "Completed Feed Matched" if comp_flag == 1 else "Pending Completion Record"
    
    var_pct = feats.get("disbursed_variance_pct", 0.0)
    var_eval = "Disbursement Variance (>20%)" if abs(var_pct) > 20.0 else "Normal Disbursement Flow"

    feature_evidence_matrix = [
        {
            "feature_name": "Sanction Delay",
            "observed_value": f"{sanction_delay} Days",
            "dataset_benchmark": "Dataset Baseline Delay (Empirical Mean)",
            "evaluation": delay_eval,
            "severity": "HIGH" if sanction_delay > 120 else ("MEDIUM" if sanction_delay > 75 else "NORMAL")
        },
        {
            "feature_name": "Category Cost Z-Score",
            "observed_value": f"+{cost_zscore:.2f} SD",
            "dataset_benchmark": f"Category Benchmark: '{work.category}'",
            "evaluation": zscore_eval,
            "severity": "HIGH" if cost_zscore > 2.0 else "NORMAL"
        },
        {
            "feature_name": "IDA Agency Concentration",
            "observed_value": f"{ida_pct:.1f}%",
            "dataset_benchmark": f"Active Agency Outlay Frequency ({work.ida})",
            "evaluation": ida_eval,
            "severity": "HIGH" if ida_pct > 70.0 else "NORMAL"
        },
        {
            "feature_name": "Sanctioned Amount",
            "observed_value": f"₹{sanction_amt:.2f} Lakhs",
            "dataset_benchmark": f"Category Context: '{work.category}'",
            "evaluation": amt_eval,
            "severity": "HIGH" if sanction_amt >= 25.0 else "NORMAL"
        },
        {
            "feature_name": "Completion Status Match",
            "observed_value": "Completed" if comp_flag == 1 else "In Progress / Pending",
            "dataset_benchmark": "Cross-Feed Completion Reconciliation",
            "evaluation": comp_eval,
            "severity": "NORMAL" if comp_flag == 1 else "MEDIUM"
        },
        {
            "feature_name": "Disbursement Variance",
            "observed_value": f"{var_pct:.1f}%",
            "dataset_benchmark": "Expected Variance: 0.0%",
            "evaluation": var_eval,
            "severity": "HIGH" if abs(var_pct) > 20.0 else "NORMAL"
        }
    ]

    s_risk = work.risk_priority_score
    s_ml = work.ml_anomaly_score
    s_rule = work.rule_score
    band = work.severity_band
    
    narrative = f"Project #{work.work_id} is classified as {band} (S_risk = {s_risk:.1f}/100). "
    if work.is_ml_anomaly:
        narrative += f"The Isolation Forest model identified an anomaly intensity score of S_ml = {s_ml:.1f}/100 due to multivariate feature isolation. "
    else:
        narrative += f"Multivariate anomaly intensity is S_ml = {s_ml:.1f}/100. "
    
    if work.rule_signals:
        narrative += f"The statutory rule engine triggered {len(work.rule_signals)} compliance signal(s) giving S_rule = {s_rule:.1f}/100."
    else:
        narrative += f"No critical statutory rule thresholds were violated (S_rule = {s_rule:.1f}/100)."

    base_exp = work.explanation or {}
    
    return {
        "is_ml_anomaly": work.is_ml_anomaly,
        "ml_anomaly_score": s_ml,
        "rule_score": s_rule,
        "risk_priority_score": s_risk,
        "severity_band": band,
        "weights_applied": {"w_ml": 0.60, "w_rule": 0.40},
        "score_attribution": {
            "ml_contribution": round(0.60 * s_ml, 1),
            "rule_contribution": round(0.40 * s_rule, 1),
            "total_risk_score": s_risk
        },
        "executive_summary": narrative,
        "feature_evidence_matrix": feature_evidence_matrix,
        "rule_signals": work.rule_signals or [],
        "ml_anomaly_evidence": base_exp.get("ml_anomaly_evidence", {
            "is_ml_anomaly": work.is_ml_anomaly,
            "ml_anomaly_score": s_ml,
            "anomaly_threshold_rule": "S_ml >= 70.0"
        })
    }

# ==================================================
# ROOT & SERVICE ENDPOINTS
# ==================================================

@app.get("/")
def read_root():
    return {
        "service": "MPLAD Intelligence REST API",
        "status": "running",
        "database": "connected",
        "version": "2.0.0"
    }

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ==================================================
# 1. HEALTH CHECK ENDPOINT
# ==================================================

@app.get("/api/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1;"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {str(e)}"
        )

# ==================================================
# 2. READ-ONLY DATA ENDPOINTS (SCOPED TO ACTIVE DATASET)
# ==================================================

@app.get("/api/overview/kpis", response_model=OverviewKpisResponse)
def get_overview_kpis(db: Session = Depends(get_db)):
    meta = get_active_meta(db)
    active_dataset_id = meta.dataset_id if meta else "dataset_ludhiana_demo"

    total_sanct_works = db.query(SanctionedWork).filter(SanctionedWork.dataset_id == active_dataset_id).count()
    sanct_sum = db.query(SanctionedWork.sanctioned_amount).filter(SanctionedWork.dataset_id == active_dataset_id).all()
    total_sanct_amt = sum(s[0] for s in sanct_sum) if sanct_sum else 0.0

    total_rec_works = db.query(RecommendedWork).filter(RecommendedWork.dataset_id == active_dataset_id).count()
    rec_sum = db.query(RecommendedWork.recommended_amount).filter(RecommendedWork.dataset_id == active_dataset_id).all()
    total_rec_amt = sum(r[0] for r in rec_sum) if rec_sum else 0.0

    total_comp_works = db.query(CompletedWork).filter(CompletedWork.dataset_id == active_dataset_id).count()
    comp_sum = db.query(CompletedWork.disbursed_amount).filter(CompletedWork.dataset_id == active_dataset_id).all()
    total_comp_amt = sum(c[0] for c in comp_sum) if comp_sum else 0.0

    unique_idas = len(set(w[0] for w in db.query(SanctionedWork.ida).filter(SanctionedWork.dataset_id == active_dataset_id).all())) or 1

    ml_anomalies = db.query(MlScoredWork).filter(MlScoredWork.dataset_id == active_dataset_id, MlScoredWork.is_ml_anomaly == True).count()
    critical_risk = db.query(MlScoredWork).filter(MlScoredWork.dataset_id == active_dataset_id, MlScoredWork.severity_band == "CRITICAL RISK PRIORITY").count()
    high_risk = db.query(MlScoredWork).filter(MlScoredWork.dataset_id == active_dataset_id, MlScoredWork.severity_band == "HIGH RISK PRIORITY").count()
    medium_risk = db.query(MlScoredWork).filter(MlScoredWork.dataset_id == active_dataset_id, MlScoredWork.severity_band == "MEDIUM RISK PRIORITY").count()
    normal_risk = db.query(MlScoredWork).filter(MlScoredWork.dataset_id == active_dataset_id, MlScoredWork.severity_band == "NORMAL RISK").count()

    return {
        "total_sanctioned_works": total_sanct_works,
        "total_sanctioned_amount_cr": round(total_sanct_amt / 1e7, 4),
        "total_recommended_works": total_rec_works,
        "total_recommended_amount_cr": round(total_rec_amt / 1e7, 4),
        "total_completed_works": total_comp_works,
        "total_disbursed_amount_cr": round(total_comp_amt / 1e7, 4),
        "ida_count": unique_idas,
        "ml_anomaly_candidates_count": ml_anomalies,
        "critical_risk_count": critical_risk,
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "normal_risk_count": normal_risk,
        "active_dataset_id": active_dataset_id,
        "active_dataset_name": meta.name if meta else "Active MPLADS Dataset",
        "state": meta.state if meta else "Punjab",
        "district": meta.district if meta else "Ludhiana",
        "constituency": meta.constituency if meta else "LUDHIANA"
    }

@app.get("/api/projects/risk-queue", response_model=RiskQueuePaginatedResponse)
def get_risk_queue(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page (15, 25, 50, 220)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    severity: Optional[str] = Query(None, description="Filter by severity band"),
    search: Optional[str] = Query(None, description="Search query"),
    db: Session = Depends(get_db)
):
    meta = get_active_meta(db)
    active_dataset_id = meta.dataset_id if meta else "dataset_ludhiana_demo"

    query = db.query(MlScoredWork).filter(MlScoredWork.dataset_id == active_dataset_id)

    if category and category != "ALL":
        query = query.filter(MlScoredWork.category == category)
    
    if severity and severity != "ALL":
        if severity == "CRITICAL":
            query = query.filter(MlScoredWork.severity_band == "CRITICAL RISK PRIORITY")
        elif severity == "HIGH":
            query = query.filter(MlScoredWork.severity_band == "HIGH RISK PRIORITY")
        elif severity == "MEDIUM":
            query = query.filter(MlScoredWork.severity_band == "MEDIUM RISK PRIORITY")
        elif severity == "NORMAL":
            query = query.filter(MlScoredWork.severity_band == "NORMAL RISK")
        elif severity == "ML_ANOMALY":
            query = query.filter(MlScoredWork.is_ml_anomaly == True)

    if search and search.strip():
        q = f"%{search.strip()}%"
        query = query.filter(
            (MlScoredWork.work_id.like(q)) | 
            (MlScoredWork.title.like(q)) | 
            (MlScoredWork.ida.like(q)) | 
            (MlScoredWork.district.like(q))
        )

    total_records = query.count()
    total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1

    raw_items = query.order_by(desc(MlScoredWork.risk_priority_score))\
                     .offset((page - 1) * page_size)\
                     .limit(page_size)\
                     .all()

    items = []
    for w in raw_items:
        item_dict = {c.name: getattr(w, c.name) for c in w.__table__.columns}
        item_dict["id"] = w.work_id
        item_dict["explanation"] = build_enriched_explanation(w)
        items.append(item_dict)

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total_records,
        "total_pages": total_pages,
        "dataset_id": active_dataset_id,
        "dataset_name": meta.name if meta else "Active Dataset"
    }

@app.get("/api/projects/{work_id:path}/intelligence", response_model=MlScoredWorkSchema)
def get_project_intelligence(work_id: str, db: Session = Depends(get_db)):
    clean_id = urllib.parse.unquote(work_id).strip()
    meta = get_active_meta(db)
    active_dataset_id = meta.dataset_id if meta else "dataset_ludhiana_demo"

    # Look strictly in active dataset
    work = db.query(MlScoredWork).filter(
        MlScoredWork.dataset_id == active_dataset_id,
        (MlScoredWork.work_id == clean_id) | (MlScoredWork.id == clean_id)
    ).first()

    if not work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work ID '{clean_id}' not found in active dataset '{active_dataset_id}'."
        )

    res_dict = {c.name: getattr(work, c.name) for c in work.__table__.columns}
    res_dict["id"] = work.work_id
    res_dict["explanation"] = build_enriched_explanation(work)
    return res_dict

# ==================================================
# 3. INVESTIGATION & AUDIT ENDPOINTS
# ==================================================

@app.get("/api/projects/{work_id:path}/investigation", response_model=InvestigationCaseResponse)
def get_investigation_case(work_id: str, db: Session = Depends(get_db)):
    clean_id = urllib.parse.unquote(work_id).strip()
    meta = get_active_meta(db)
    active_dataset_id = meta.dataset_id if meta else "dataset_ludhiana_demo"

    case = db.query(InvestigationCase).filter(
        InvestigationCase.dataset_id == active_dataset_id,
        InvestigationCase.work_id == clean_id
    ).first()

    if not case:
        # Create case dynamically scoped strictly to the active dataset
        case = InvestigationCase(dataset_id=active_dataset_id, work_id=clean_id, current_status="UNDER REVIEW")
        db.add(case)
        db.commit()
        db.refresh(case)

    return case

@app.post("/api/projects/{work_id:path}/investigation-action", response_model=InvestigationCaseResponse)
def post_investigation_action(
    work_id: str,
    action_data: InvestigationActionRequest,
    db: Session = Depends(get_db)
):
    clean_id = urllib.parse.unquote(work_id).strip()
    meta = get_active_meta(db)
    active_dataset_id = meta.dataset_id if meta else "dataset_ludhiana_demo"

    case = db.query(InvestigationCase).filter(
        InvestigationCase.dataset_id == active_dataset_id,
        InvestigationCase.work_id == clean_id
    ).first()

    if not case:
        case = InvestigationCase(dataset_id=active_dataset_id, work_id=clean_id, current_status="UNDER REVIEW")
        db.add(case)
        db.commit()
        db.refresh(case)

    status_mapping = {
        "MARK_FOR_FIELD_VERIFICATION": "MARKED FOR FIELD VERIFICATION",
        "REQUEST_NODAL_AGENCY_AUDIT": "AUDIT REQUESTED (IDA)",
        "CLEAR_AFTER_REVIEW": "CLEARED / AUDIT RESOLVED"
    }
    
    if action_data.action not in status_mapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action '{action_data.action}'. Allowed actions: {list(status_mapping.keys())}"
        )

    previous_status = case.current_status
    new_status = status_mapping[action_data.action]
    case.current_status = new_status
    case.updated_at = datetime.utcnow()

    # Log in persistent audit trail
    audit_entry = AuditLog(
        dataset_id=active_dataset_id,
        work_id=clean_id,
        action_type=f"VERIFICATION STATUS: {new_status}",
        previous_status=previous_status,
        new_status=new_status,
        actor=action_data.actor or "State Nodal Officer",
        details=action_data.details or f"Investigation action '{action_data.action}' applied to project #{clean_id}.",
        timestamp=datetime.utcnow()
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(case)

    return case

@app.get("/api/projects/{work_id:path}/notes", response_model=List[InvestigationNoteResponse])
def get_investigation_notes(work_id: str, db: Session = Depends(get_db)):
    clean_id = urllib.parse.unquote(work_id).strip()
    meta = get_active_meta(db)
    active_dataset_id = meta.dataset_id if meta else "dataset_ludhiana_demo"

    notes = db.query(InvestigationNote).filter(
        InvestigationNote.dataset_id == active_dataset_id,
        InvestigationNote.work_id == clean_id
    ).order_by(desc(InvestigationNote.timestamp)).all()
    return notes

@app.post("/api/projects/{work_id:path}/notes", response_model=InvestigationNoteResponse, status_code=status.HTTP_201_CREATED)
def add_investigation_note(
    work_id: str,
    note_data: InvestigationNoteRequest,
    db: Session = Depends(get_db)
):
    clean_id = urllib.parse.unquote(work_id).strip()
    meta = get_active_meta(db)
    active_dataset_id = meta.dataset_id if meta else "dataset_ludhiana_demo"

    new_note = InvestigationNote(
        dataset_id=active_dataset_id,
        work_id=clean_id,
        officer_name=note_data.officer_name or "State Nodal Officer",
        note_text=note_data.note_text.strip(),
        timestamp=datetime.utcnow()
    )
    db.add(new_note)

    audit_entry = AuditLog(
        dataset_id=active_dataset_id,
        work_id=clean_id,
        action_type="INVESTIGATION NOTE ADDED",
        previous_status=None,
        new_status="NOTE LOGGED",
        actor=note_data.officer_name or "State Nodal Officer",
        details=f"Officer added investigation note: '{note_data.note_text.strip()}'",
        timestamp=datetime.utcnow()
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(new_note)

    return new_note

@app.get("/api/audit-logs", response_model=AuditLogPaginatedResponse)
def get_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    total_records = query.count()
    total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1

    items = query.order_by(desc(AuditLog.timestamp))\
                 .offset((page - 1) * page_size)\
                 .limit(page_size)\
                 .all()

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total_records,
        "total_pages": total_pages
    }

@app.delete("/api/audit-logs")
def clear_audit_logs(db: Session = Depends(get_db)):
    deleted_count = db.query(AuditLog).delete()
    db.commit()
    return {"status": "cleared", "deleted_count": deleted_count}

# ==================================================
# 4. DATASET LIBRARY & MANAGEMENT ENDPOINTS
# ==================================================

@app.get("/api/datasets/active", response_model=DatasetMetadataResponse)
def get_active_dataset(db: Session = Depends(get_db)):
    meta = get_active_meta(db)
    if not meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active dataset found in database."
        )
    return meta

@app.get("/api/datasets", response_model=DatasetListResponse)
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.query(DatasetMetadata).order_by(desc(DatasetMetadata.is_active), desc(DatasetMetadata.uploaded_at)).all()
    return {
        "items": datasets,
        "total": len(datasets)
    }

@app.post("/api/datasets/upload")
def upload_dataset_files(
    sanctioned_file: UploadFile = File(...),
    recommended_file: UploadFile = File(...),
    completed_file: UploadFile = File(...)
):
    for f, label in [(sanctioned_file, 'Sanctioned Works'), (recommended_file, 'Recommended Works'), (completed_file, 'Completed Works')]:
        if not f.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file format for {label} ('{f.filename}'). Only CSV files (.csv) are supported."
            )

    sanct_staged = os.path.join(STAGING_DIR, 'sanctioned_works.csv')
    rec_staged = os.path.join(STAGING_DIR, 'recommended_works.csv')
    comp_staged = os.path.join(STAGING_DIR, 'completed_works.csv')

    try:
        with open(sanct_staged, 'wb') as buffer:
            shutil.copyfileobj(sanctioned_file.file, buffer)
        with open(rec_staged, 'wb') as buffer:
            shutil.copyfileobj(recommended_file.file, buffer)
        with open(comp_staged, 'wb') as buffer:
            shutil.copyfileobj(completed_file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store staged files: {str(e)}"
        )

    return {
        "status": "staged",
        "message": "3 CSV files successfully uploaded to staging storage and prepared for validation.",
        "files": {
            "sanctioned_file": sanctioned_file.filename,
            "recommended_file": recommended_file.filename,
            "completed_file": completed_file.filename
        },
        "staging_ready": True
    }

@app.post("/api/datasets/validate", response_model=DatasetValidationResponse)
def validate_dataset():
    sanct_staged = os.path.join(STAGING_DIR, 'sanctioned_works.csv')
    rec_staged = os.path.join(STAGING_DIR, 'recommended_works.csv')
    comp_staged = os.path.join(STAGING_DIR, 'completed_works.csv')

    if not os.path.exists(sanct_staged) or not os.path.exists(rec_staged) or not os.path.exists(comp_staged):
        sanct_staged = os.path.join(DATA_DIR, 'sanctioned_works.csv')
        rec_staged = os.path.join(DATA_DIR, 'recommended_works.csv')
        comp_staged = os.path.join(DATA_DIR, 'completed_works.csv')

    validation_result = validate_dataset_files(sanct_staged, rec_staged, comp_staged)
    return validation_result

@app.post("/api/datasets/analyze", response_model=DatasetAnalysisResponse)
def run_intelligence_analysis(
    payload: Optional[DatasetAnalyzeRequest] = None,
    db: Session = Depends(get_db)
):
    sanct_staged = os.path.join(STAGING_DIR, 'sanctioned_works.csv')
    rec_staged = os.path.join(STAGING_DIR, 'recommended_works.csv')
    comp_staged = os.path.join(STAGING_DIR, 'completed_works.csv')

    if not os.path.exists(sanct_staged) or not os.path.exists(rec_staged) or not os.path.exists(comp_staged):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No staged dataset files found. Please upload 3 CSV files first."
        )

    val = validate_dataset_files(sanct_staged, rec_staged, comp_staged)
    if not val["valid"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Dataset validation failed: {'; '.join(val['errors'])}"
        )

    # Run Real ML Isolation Forest & Rule Pipeline
    try:
        ml_scored_path = os.path.join(DATA_DIR, 'ml_scored_works.json')
        ml_result = run_ml_pipeline(sanct_staged, rec_staged, comp_staged, output_json_path=ml_scored_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ML Pipeline execution failed: {str(e)}"
        )

    first_w = ml_result['works'][0] if (ml_result.get('works') and len(ml_result['works']) > 0) else {}
    st = first_w.get('state', 'State')
    dist = first_w.get('district', 'District')

    if payload and payload.dataset_name and payload.dataset_name.strip():
        dataset_name = payload.dataset_name.strip()
    else:
        dataset_name = f"{st} MPLADS — {dist} District"

    # Multi-Dataset Isolated Activation
    try:
        meta_row = activate_dataset_in_db(
            db, 
            ml_result, 
            dataset_name=dataset_name, 
            source_type="UPLOADED",
            validation_report=val
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database activation transaction failed: {str(e)}"
        )

    return {
        "status": "COMPLETED",
        "dataset_id": meta_row.dataset_id,
        "dataset_name": dataset_name,
        "total_scored_works": meta_row.sanctioned_count,
        "ml_anomaly_candidates": meta_row.ml_anomaly_count,
        "critical_risk_count": meta_row.critical_risk_count,
        "high_risk_count": meta_row.high_risk_count,
        "medium_risk_count": meta_row.medium_risk_count,
        "normal_risk_count": meta_row.normal_risk_count,
        "message": f"Successfully analyzed and activated dataset '{dataset_name}' with {meta_row.sanctioned_count} scored works."
    }

@app.post("/api/datasets/{dataset_id}/activate", response_model=DatasetMetadataResponse)
def switch_active_dataset(dataset_id: str, db: Session = Depends(get_db)):
    target_meta = db.query(DatasetMetadata).filter(DatasetMetadata.dataset_id == dataset_id).first()
    if not target_meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID '{dataset_id}' not found in library."
        )

    # Deactivate all other datasets and activate target
    db.query(DatasetMetadata).filter(DatasetMetadata.dataset_id != dataset_id).update({"is_active": False, "status": "STORED"})
    target_meta.is_active = True
    target_meta.status = "ACTIVE"
    target_meta.activated_at = datetime.utcnow()

    # Log audit event
    audit_entry = AuditLog(
        dataset_id=dataset_id,
        work_id="SYSTEM_DATASET",
        action_type="DATASET_SWITCHED",
        previous_status="STORED",
        new_status=f"ACTIVE ({target_meta.name})",
        actor="State Nodal Officer",
        details=f"Switched active dataset to '{target_meta.name}' [{dataset_id}].",
        timestamp=datetime.utcnow()
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(target_meta)

    return target_meta

@app.delete("/api/datasets/{dataset_id}")
def delete_dataset_from_library(dataset_id: str, db: Session = Depends(get_db)):
    target_meta = db.query(DatasetMetadata).filter(DatasetMetadata.dataset_id == dataset_id).first()
    if not target_meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID '{dataset_id}' not found."
        )

    if target_meta.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the currently active dataset. Please activate another dataset first."
        )

    # Delete records for this dataset
    db.query(MlScoredWork).filter(MlScoredWork.dataset_id == dataset_id).delete()
    db.query(SanctionedWork).filter(SanctionedWork.dataset_id == dataset_id).delete()
    db.query(RecommendedWork).filter(RecommendedWork.dataset_id == dataset_id).delete()
    db.query(CompletedWork).filter(CompletedWork.dataset_id == dataset_id).delete()
    db.query(InvestigationCase).filter(InvestigationCase.dataset_id == dataset_id).delete()
    db.query(DatasetMetadata).filter(DatasetMetadata.dataset_id == dataset_id).delete()

    db.commit()
    return {"status": "deleted", "dataset_id": dataset_id, "message": f"Dataset '{target_meta.name}' removed from library."}

@app.get("/api/datasets/{dataset_id}/report-pdf")
def download_dataset_pdf_report(dataset_id: str, db: Session = Depends(get_db)):
    meta = db.query(DatasetMetadata).filter(DatasetMetadata.dataset_id == dataset_id).first()
    if not meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found."
        )

    # Query top scored works for this dataset
    works = db.query(MlScoredWork).filter(MlScoredWork.dataset_id == dataset_id)\
              .order_by(desc(MlScoredWork.risk_priority_score))\
              .all()

    works_list = []
    for w in works:
        works_list.append({
            "id": w.work_id,
            "title": w.title,
            "category": w.category,
            "ida": w.ida,
            "district": w.district,
            "sanctioned_amount_lakhs": w.sanctioned_amount_lakhs,
            "sanction_delay_days": w.sanction_delay_days,
            "ml_anomaly_score": w.ml_anomaly_score,
            "rule_score": w.rule_score,
            "risk_priority_score": w.risk_priority_score,
            "severity_band": w.severity_band,
            "rule_signals": w.rule_signals or [],
            "features": w.features or {}
        })

    meta_dict = {
        "name": meta.name,
        "state": meta.state,
        "district": meta.district,
        "constituency": meta.constituency,
        "is_active": meta.is_active,
        "uploaded_at": meta.uploaded_at.strftime('%Y-%m-%d %H:%M IST') if meta.uploaded_at else "",
        "sanctioned_count": meta.sanctioned_count,
        "recommended_count": meta.recommended_count,
        "completed_count": meta.completed_count,
        "ml_anomaly_count": meta.ml_anomaly_count,
        "critical_risk_count": meta.critical_risk_count,
        "high_risk_count": meta.high_risk_count,
        "medium_risk_count": meta.medium_risk_count,
        "normal_risk_count": meta.normal_risk_count
    }

    pdf_bytes = generate_pdf_report(meta_dict, works_list, meta.validation_report)

    filename = f"MPLAD_Intelligence_Report_{meta.district}_{dataset_id}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.post("/api/datasets/restore-demo", response_model=DatasetAnalysisResponse)
def restore_demo_dataset(db: Session = Depends(get_db)):
    demo_id = "dataset_ludhiana_demo"
    demo_meta = db.query(DatasetMetadata).filter(DatasetMetadata.dataset_id == demo_id).first()

    if demo_meta:
        # Re-activate existing demo dataset in library
        db.query(DatasetMetadata).filter(DatasetMetadata.dataset_id != demo_id).update({"is_active": False, "status": "STORED"})
        demo_meta.is_active = True
        demo_meta.status = "ACTIVE"
        demo_meta.activated_at = datetime.utcnow()
        db.commit()
        db.refresh(demo_meta)
        meta_row = demo_meta
    else:
        # Re-run pipeline from demo_backup
        sanct_demo = os.path.join(DEMO_BACKUP_DIR, 'sanctioned_works.csv')
        rec_demo = os.path.join(DEMO_BACKUP_DIR, 'recommended_works.csv')
        comp_demo = os.path.join(DEMO_BACKUP_DIR, 'completed_works.csv')
        ml_scored_path = os.path.join(DATA_DIR, 'ml_scored_works.json')

        ml_result = run_ml_pipeline(sanct_demo, rec_demo, comp_demo, output_json_path=ml_scored_path)
        meta_row = activate_dataset_in_db(
            db, 
            ml_result, 
            dataset_name="Punjab MPLADS — Ludhiana District", 
            source_type="DEMO_RESTORE",
            dataset_id=demo_id
        )

    return {
        "status": "RESTORED",
        "dataset_id": demo_id,
        "dataset_name": meta_row.name,
        "total_scored_works": meta_row.sanctioned_count,
        "ml_anomaly_candidates": meta_row.ml_anomaly_count,
        "critical_risk_count": meta_row.critical_risk_count,
        "high_risk_count": meta_row.high_risk_count,
        "medium_risk_count": meta_row.medium_risk_count,
        "normal_risk_count": meta_row.normal_risk_count,
        "message": f"Successfully activated original demo dataset '{meta_row.name}' (220 Sanctioned Works, 7 ML Anomalies)."
    }
