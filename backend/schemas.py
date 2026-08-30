from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

# Overview KPIs Response Schema
class OverviewKpisResponse(BaseModel):
    total_sanctioned_works: int
    total_sanctioned_amount_cr: float
    total_recommended_works: int
    total_recommended_amount_cr: float
    total_completed_works: int
    total_disbursed_amount_cr: float
    ida_count: int = 1
    ml_anomaly_candidates_count: int
    critical_risk_count: int
    high_risk_count: int
    medium_risk_count: int
    normal_risk_count: int
    active_dataset_id: Optional[str] = "dataset_ludhiana_demo"
    active_dataset_name: Optional[str] = "Punjab MPLADS — Ludhiana District"
    state: Optional[str] = "Punjab"
    district: Optional[str] = "Ludhiana"
    constituency: Optional[str] = "LUDHIANA"

# ML Scored Work Schema
class MlScoredWorkSchema(BaseModel):
    id: str # Work code (e.g. WS/MP...)
    dataset_id: Optional[str] = "dataset_ludhiana_demo"
    sr_no: Optional[str] = None
    title: str
    category: str
    ida: str
    district: str
    mp_name: str
    constituency: str
    state: str
    sanctioned_amount_lakhs: float
    recommended_amount_lakhs: float
    sanction_delay_days: int
    is_recommendation_date_imputed: bool
    status: str
    is_completed: bool
    disbursed_amount_lakhs: float
    features: Dict[str, Any]
    ml_anomaly_score: float
    rule_score: float
    risk_priority_score: float
    severity_band: str
    is_ml_anomaly: bool
    rule_signals: List[str]
    explanation: Dict[str, Any]

    class Config:
        from_attributes = True

# Risk Queue Paginated Response Schema
class RiskQueuePaginatedResponse(BaseModel):
    items: List[MlScoredWorkSchema]
    page: int
    page_size: int
    total: int
    total_pages: int
    dataset_id: Optional[str] = None
    dataset_name: Optional[str] = None

# Investigation Action Request Schema
class InvestigationActionRequest(BaseModel):
    action: str = Field(..., description="MARK_FOR_FIELD_VERIFICATION, REQUEST_NODAL_AGENCY_AUDIT, or CLEAR_AFTER_REVIEW")
    details: Optional[str] = None
    actor: Optional[str] = "State Nodal Officer"

# Investigation Case Response Schema
class InvestigationCaseResponse(BaseModel):
    dataset_id: Optional[str] = None
    work_id: str
    current_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Investigation Note Create Request Schema
class InvestigationNoteRequest(BaseModel):
    note_text: str = Field(..., min_length=1, description="Official investigation note or field observation text")
    officer_name: Optional[str] = "State Nodal Officer"

# Investigation Note Response Schema
class InvestigationNoteResponse(BaseModel):
    id: int
    dataset_id: Optional[str] = None
    work_id: str
    officer_name: str
    note_text: str
    timestamp: datetime

    class Config:
        from_attributes = True

# Audit Log Response Schema
class AuditLogResponse(BaseModel):
    id: int
    dataset_id: Optional[str] = None
    work_id: str
    action_type: str
    previous_status: Optional[str] = None
    new_status: str
    actor: str
    details: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# Audit Log Paginated Response Schema
class AuditLogPaginatedResponse(BaseModel):
    items: List[AuditLogResponse]
    page: int
    page_size: int
    total: int
    total_pages: int

# Health Response Schema
class HealthResponse(BaseModel):
    status: str
    database: str

# ----------------------------------------------------
# DATASET MANAGEMENT SCHEMAS
# ----------------------------------------------------

class DatasetMetadataResponse(BaseModel):
    id: Optional[int] = None
    dataset_id: str
    name: str
    state: str
    district: str
    constituency: str
    status: str
    is_active: bool
    uploaded_at: datetime
    activated_at: datetime
    sanctioned_count: int
    recommended_count: int
    completed_count: int
    ida_count: int = 1
    ml_anomaly_count: int
    critical_risk_count: int
    high_risk_count: int
    medium_risk_count: int
    normal_risk_count: int
    validation_status: str
    analysis_status: str
    validation_report: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ValidationCheckItem(BaseModel):
    name: str
    status: str # PASS, WARN, FAIL
    message: str

class DatasetValidationResponse(BaseModel):
    valid: bool
    sanctioned_count: int
    recommended_count: int
    completed_count: int
    duplicate_ids_count: int
    checks: List[ValidationCheckItem]
    errors: List[str]
    warnings: List[str]

class DatasetAnalyzeRequest(BaseModel):
    dataset_name: Optional[str] = None

class DatasetAnalysisResponse(BaseModel):
    status: str
    dataset_id: str
    dataset_name: str
    total_scored_works: int
    ml_anomaly_candidates: int
    critical_risk_count: int
    high_risk_count: int
    medium_risk_count: int
    normal_risk_count: int
    message: str

class DatasetListResponse(BaseModel):
    items: List[DatasetMetadataResponse]
    total: int
