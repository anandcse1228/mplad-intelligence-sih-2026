# Document 05 — Technical Architecture & 3–5 Day Implementation Plan
## MPLAD Intelligence (SIH26102)

---

## 1. Technical Stack & System Topology

```
+-------------------------------------------------------------------------------------------------+
| FRONTEND: React 18 + Tailwind CSS + Lucide Icons + Recharts + Vis.js                            |
| (Dark Institutional Theme: Base #0D1117, Card #161B22, Border #21262D, Accent #0E857C)          |
+-------------------------------------------------------------------------------------------------+
                                               │
                                               │ REST API (JSON / Pydantic)
                                               ▼
+-------------------------------------------------------------------------------------------------+
| BACKEND: FastAPI (Python 3.10+) + Uvicorn ASGI Server                                           |
| - Layer 1: Deterministic Compliance Rule Engine (Validated Feature Computations)                |
| - Layer 2: Scikit-learn Isolation Forest (Primary Baseline on Validated Feature Vector)         |
| - Layer 3: Risk Priority Score Aggregator & SHAP Explainability Engine                          |
+-------------------------------------------------------------------------------------------------+
                                               │
                                               │ SQLAlchemy ORM Engine
                                               ▼
+-------------------------------------------------------------------------------------------------+
| DATABASE: SQLite (File-based relational DB for MVP; PostgreSQL ready for Production)            |
| Tables: canonical_projects, anomaly_signals, risk_scores, data_sources, model_runs,           |
| investigation_cases, investigation_notes                                                       |
+-------------------------------------------------------------------------------------------------+
```

---

## 2. Ingestion & Storage Pipeline Architecture (Completed Data Ingestion Phase)

```
[ Uploaded Raw CSV Feeds ] ──► [ Ingestion Adapter & Deduplicator ] (COMPLETED)
  ├── 2 Duplicate Recommended CSVs
  └── 1 Sanctioned CSV
            │
            ▼
[ Validated Canonical Store ] ──► 220 Unique Sanctioned Works (COMPLETED)
  ├── 206 Rec ↔ Sanct Matches
  └── 14 Sanctioned-Only Works
            │
            ▼
[ Feature Extraction Engine ] ──► Extracts 6 Validated Computable Features
            │
            ▼
[ Rule Engine + Isolation Forest ] ──► Computes anomaly_signals & risk_scores
```

---

## 3. Revised 3–5 Day Execution Plan

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ REVISED 3–5 DAY SPRINT SCHEDULE (DATA INSPECTION & INGESTION COMPLETED)         │
├───────────────────────┬─────────────────────────────────────────────────────────┤
│ DAY 1: Data & Ingestion│ COMPLETED: CSV inspection, deduplication, 220-work DB  │
│ DAY 2: Features & Rules│ COMPLETED/ACTIVE: Compute 6 validated feature vectors   │
│ DAY 3: Dashboard UI   │ IN PROGRESS: Build React National Command Center Page   │
│ DAY 4: ML & Backend   │ Train Isolation Forest & expose FastAPI endpoints       │
│ DAY 5: Integration    │ Connect React UI to FastAPI backend, test & polish demo │
└───────────────────────┴─────────────────────────────────────────────────────────┘
```

### Sprint Detail

#### Day 1: Data Ingestion & Validation (**COMPLETED**)
* **Achieved**: Ingested 2 duplicate Recommended CSVs (deduplicated) and 1 Sanctioned CSV. Created SQLite `canonical_projects` database populated with 220 unique sanctioned works (206 matched, 14 sanctioned-only).
* **Pending Feeds Identified**: Works Completed CSV feed marked PENDING.

#### Day 2: Feature Extraction & Rule Engine (**COMPLETED / ACTIVE**)
* **Deliverables**: 6-dimensional feature extractor (`F_DAYS_SANCTION`, `F_SANCT_DEV`, `F_COST_OUTLIER`, `F_AGENCY_CONC`, `F_TITLE_DUP`, `F_UNMATCHED`) and deterministic compliance rules (`rule_engine.py`).

#### Day 3: Frontend Command Center Dashboard (**IN PROGRESS**)
* **Deliverables**: Build Page 1 — National Command Center / Dashboard landing page in React + Tailwind CSS (`#0D1117` base, `#161B22` cards, `#0E857C` teal accent, key KPIs, review queue preview, and data-status indicators).

#### Day 4: Isolation Forest ML Training & FastAPI REST API
* **Deliverables**: Train `sklearn.ensemble.IsolationForest` on 6-dimensional validated feature vector; expose REST API endpoints (`/overview/kpis`, `/projects/risk-queue`, `/projects/{id}/intelligence`).

#### Day 5: System Integration, Testing & SIH Presentation Rehearsal
* **Deliverables**: Full frontend-backend integration, end-to-end workflow validation, UI visual polish, edge-case auditing, and presentation demo rehearsal.

---

## 4. Implementation Go / No-Go Decision

```
[✓] TIMELINE SCOPED: 3–5 Day MVP Plan aligned with SIH competition window.
[✓] DATA INGESTION: COMPLETED (220 unique sanctioned works, 206 matched recommendations).
[✓] PENDING DATA HANDLING: Completed Works feed marked PENDING (zero fabrication).
[✓] ML CONSTRAINED: Isolation Forest executes strictly on validated 6-dimensional vector.
[✓] FINAL GO / NO-GO CHECK: 🟢 GO — Implementation Ready & Frozen.
```
