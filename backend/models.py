from sqlalchemy import Column, Integer, Float, String, Boolean, Text, DateTime, JSON
from datetime import datetime
from database import Base

class SanctionedWork(Base):
    __tablename__ = "sanctioned_works"

    id = Column(String, primary_key=True, index=True) # Compound key: dataset_id:work_code
    dataset_id = Column(String, nullable=False, index=True, default="dataset_ludhiana_demo")
    work_id = Column(String, nullable=False, index=True) # Canonical Work ID (WS/MP.../...)
    sr_no = Column(String, nullable=True)
    title = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    ida = Column(String, nullable=False)
    district = Column(String, nullable=False)
    mp_name = Column(String, nullable=False)
    constituency = Column(String, nullable=False)
    state = Column(String, nullable=False)
    sanctioned_amount = Column(Float, nullable=False) # INR
    sanctioned_amount_lakhs = Column(Float, nullable=False) # Lakhs
    sanct_date = Column(String, nullable=True)
    status = Column(String, nullable=False)

class RecommendedWork(Base):
    __tablename__ = "recommended_works"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, nullable=False, index=True, default="dataset_ludhiana_demo")
    sr_no = Column(String, nullable=True)
    title = Column(Text, nullable=False)
    recommended_amount = Column(Float, nullable=False) # INR
    recommended_amount_lakhs = Column(Float, nullable=False) # Lakhs
    rec_date = Column(String, nullable=True)
    district = Column(String, nullable=False)

class CompletedWork(Base):
    __tablename__ = "completed_works"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, nullable=False, index=True, default="dataset_ludhiana_demo")
    sr_no = Column(String, nullable=True)
    work_id_matched = Column(String, nullable=True, index=True)
    title = Column(Text, nullable=False)
    disbursed_amount = Column(Float, nullable=False) # INR
    disbursed_amount_lakhs = Column(Float, nullable=False) # Lakhs
    completion_date = Column(String, nullable=True)
    district = Column(String, nullable=False)

class MlScoredWork(Base):
    __tablename__ = "ml_scored_works"

    id = Column(String, primary_key=True, index=True) # Compound key: dataset_id:work_code
    dataset_id = Column(String, nullable=False, index=True, default="dataset_ludhiana_demo")
    work_id = Column(String, nullable=False, index=True) # Canonical Work ID
    sr_no = Column(String, nullable=True)
    title = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    ida = Column(String, nullable=False)
    district = Column(String, nullable=False)
    mp_name = Column(String, nullable=False)
    constituency = Column(String, nullable=False)
    state = Column(String, nullable=False)

    sanctioned_amount_lakhs = Column(Float, nullable=False)
    recommended_amount_lakhs = Column(Float, nullable=False)
    sanction_delay_days = Column(Integer, nullable=False)
    is_recommendation_date_imputed = Column(Boolean, default=False)
    status = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    disbursed_amount_lakhs = Column(Float, default=0.0)

    # 6 Feature Vector stored as JSON
    features = Column(JSON, nullable=False)

    # Scores
    ml_anomaly_score = Column(Float, nullable=False) # S_ml [0, 100]
    rule_score = Column(Float, nullable=False)       # S_rule [0, 100]
    risk_priority_score = Column(Float, nullable=False) # S_risk = 0.60 S_ml + 0.40 S_rule
    severity_band = Column(String, nullable=False)  # HIGH RISK PRIORITY, MEDIUM, NORMAL
    is_ml_anomaly = Column(Boolean, default=False)   # S_ml >= 70.0
    rule_signals = Column(JSON, nullable=False)      # List of triggered rule descriptions
    explanation = Column(JSON, nullable=False)       # Explanation dictionary

class InvestigationCase(Base):
    __tablename__ = "investigation_cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, nullable=False, index=True, default="dataset_ludhiana_demo")
    work_id = Column(String, index=True) # Persistent Work ID identifier
    current_status = Column(String, default="UNDER REVIEW")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InvestigationNote(Base):
    __tablename__ = "investigation_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, nullable=False, index=True, default="dataset_ludhiana_demo")
    work_id = Column(String, index=True) # Persistent Work ID identifier
    officer_name = Column(String, default="State Nodal Officer")
    note_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, nullable=True, index=True)
    work_id = Column(String, nullable=False, index=True)
    action_type = Column(String, nullable=False)
    previous_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False)
    actor = Column(String, default="State Nodal Officer")
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class DatasetMetadata(Base):
    __tablename__ = "dataset_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False, default="Punjab MPLADS — Ludhiana District")
    state = Column(String, nullable=False, default="Punjab")
    district = Column(String, nullable=False, default="Ludhiana")
    constituency = Column(String, nullable=False, default="LUDHIANA")
    status = Column(String, nullable=False, default="ACTIVE")
    is_active = Column(Boolean, default=True, index=True)

    uploaded_at = Column(DateTime, default=datetime.utcnow)
    activated_at = Column(DateTime, default=datetime.utcnow)

    sanctioned_count = Column(Integer, default=0)
    recommended_count = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    ida_count = Column(Integer, default=0)

    ml_anomaly_count = Column(Integer, default=0)
    critical_risk_count = Column(Integer, default=0)
    high_risk_count = Column(Integer, default=0)
    medium_risk_count = Column(Integer, default=0)
    normal_risk_count = Column(Integer, default=0)

    validation_status = Column(String, default="VALIDATED")
    analysis_status = Column(String, default="COMPLETED")
    validation_report = Column(JSON, nullable=True)
