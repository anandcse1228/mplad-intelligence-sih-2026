# Document 01 — Research & System Architecture
## MPLAD Intelligence (SIH26102)

---

## 1. MPLADS Problem Understanding

The Members of Parliament Local Area Development Scheme (MPLADS) is a Central Sector Scheme fully funded by the Government of India. It enables Members of Parliament (MPs) to recommend developmental works with an emphasis on creating durable community assets based on locally felt needs. Under the scheme, each MP is entitled to recommend works up to ₹5 Crore per annum.

### Core Problem Landscape
Despite its positive socio-economic impact, independent audit reports by the Comptroller and Auditor General (CAG) of India and administrative reviews have persistently highlighted systemic implementation bottlenecks and financial irregularities:
* **Severe Administrative & Execution Delays**: Prolonged time gaps between MP recommendation, administrative sanction by District Authorities (DAs), fund release, and actual work execution.
* **Financial & Progress Mismatches**: Rapid disbursement/release of funds while verified physical progress remains low, resulting in idle fund parking or potential diversion.
* **Contractor Monopoly & Entity Concentration**: A small cluster of contractors or implementing agencies capturing a disproportionate share of local works, sometimes linked to directorship overlaps or sub-contracting syndicates.
* **Inadmissible & Duplicate Works**: Sanctioning works on non-permissible sites (private assets, unverified trusts) or double-recommending similar works under slightly altered titles across financial years.
* **Information Asymmetry & Monitoring Gaps**: Manual reporting structures produce thousands of unstructured monthly progress reports (MPRs), making manual inspection prioritization mathematically impossible for central and state nodal officers.

---

## 2. Official Workflow

The revised MPLADS Guidelines (effective April 1, 2023) and the eSAKSHI digital portal mandate a structured multi-stage administrative lifecycle:

```
[ Hon'ble MP ] Recommends Work via eSAKSHI Portal
      │
      ▼
[ District Authority (DA) ] Checks Eligibility & Technical Feasibility
      │
      ├───────────────────────► [ Rejected ] (Non-permissible / Infeasible)
      ▼
[ Administrative Sanction (AS) ] Issued by DA & Implementing Agency (IA) Assigned
      │
      ▼
[ Single Nodal Account (SNA) ] Annual Drawing Limits Authorized & Funds Drawn Just-in-Time
      │
      ▼
[ Implementing Agency (IA) ] Executes Work & Uploads Stage-wise Geo-Tagged Photos
      │
      ▼
[ Progress & Completion ] Utilization Certificate (UC) & Completion Certificate (CC) Uploaded
      │
      ▼
[ Nodal Monitoring & Audit ] State & Central Nodal Reviews / CAG Audit Verification
```

---

## 3. Stakeholders & Responsibilities

| Stakeholder | Organization / Level | Core Role & Responsibilities | Information Handled | Platform Utility Provided |
| :--- | :--- | :--- | :--- | :--- |
| **Central Nodal Officer** | MoSPI (Ministry of Statistics & Programme Implementation) | Overall policy implementation, budget release, national monitoring. | Macro allocations, state releases, national summary MPRs. | National Command Center dashboard, macro KPI metrics, state risk heatmaps. |
| **State Nodal Authority** | State Planning Department | State-level oversight, inter-district coordination, CAG audit follow-up. | Constituency allocations, district progress reports, SC/ST fund compliance. | State & District Analytics, high-risk queue filtering, anomaly cluster mapping. |
| **District Authority (DA)** | District Collector / District Magistrate (DM) / Deputy Commissioner | Sanctioning authority, IA allocation, fund disbursement, inspection dispatch. | Work recommendations, AS documents, IA estimates, UC/CC certificates. | Deep Project Intelligence view, evidence mismatch viewer, inspection dispatch workspace. |
| **Implementing Agency (IA)** | PWD, Zilla Parishad, Municipal Corp, Rural Dev | Physical execution of works, tender award, geo-tagged photo upload. | Estimates, tender notices, contractor bills, milestone photos. | Standardized data upload validation, milestone verification tracking. |
| **Field Auditor / Vigilance** | CAG / State Vigilance Wing | Formal investigation of flagged irregularities, physical audit. | Financial ledgers, site inspection reports, contractor registers. | Forensic Chronology, Contractor Relationship Network, immutable audit log. |

---

## 4. Important Data Access Principles & Source Classification

To avoid unverified technical assumptions, all data sources are classified according to their actual public accessibility, machine-readability, and suitability for the MVP.

### Category A — Publicly Visible

Information that can be viewed through an official public webpage or dashboard, but for which unrestricted bulk download or API access has not been technically verified.

**Technical Classification Rule:**

If a portal is publicly viewable but free bulk download or REST/API access has not been explicitly confirmed, classify it as:

> "Publicly accessible; bulk/API access requires technical verification."

### Category B — Publicly Downloadable

Official or open-government resources providing direct downloadable files such as CSV, XLSX, or ZIP without requiring a paid subscription.

### Category C — Public API-Enabled

Official datasets for which the source explicitly provides a documented API or other machine-readable programmatic access mechanism.

The API must be evaluated separately from general website accessibility.

### Category D — Public Dashboard / Bulk Access Unverified

Information available through an official dashboard or reporting interface where the underlying information is public, but bulk extraction, API availability, or automated ingestion has not yet been technically validated.

### Category E — Restricted / Authenticated

Government or institutional data requiring official credentials, authentication, or non-public access.

Such data is NOT a dependency for the MVP.

### Category F — Third-Party / Optional

Datasets provided or curated by third-party services such as Dataful.

These may be used for enrichment or validation only after confirming accessibility, licensing/usage conditions, required fields, and paid dependencies.

### Category G — Synthetic / Derived

Data generated or derived by MPLAD Intelligence for controlled anomaly evaluation, feature engineering, ground-truth creation, feature testing, and edge-case simulation.

---

## 4.1 Implementation CSV Ingestion & Validation Results

Initial ingestion and technical validation of the primary CSV data feed for the current implementation revealed the following verified structures:

```
[ Uploaded CSV Feed Ingestion ]
  ├── 2 Duplicate Recommended Works CSV Files (Deduplicated & Merged)
  └── 1 Sanctioned Works CSV File
            │
            ▼
[ Validated Matching Metrics ]
  ├── Total Unique Sanctioned Works: 220
  ├── Recommended ↔ Sanctioned Matches: 206 Works (Matched via Work ID / Title)
  └── Sanctioned-Only Works: 14 Works (Sanctioned without explicit MP recommendation in feed)
```

> [!IMPORTANT]
> **Data Availability & Pending Features Status**:  
> The **Works Completed CSV** feed is currently **UNAVAILABLE** in the uploaded raw dataset.  
> Consequently, all features dependent on completion certificates, actual expenditure reports, unspent balance ratios, and completion timelines are explicitly marked as **PENDING DATA AVAILABILITY** and are **NOT** fabricated or artificially assumed.

---

## 4.2 Open Government Data Platform (`data.gov.in`)

- **Platform:** Open Government Data (OGD) Platform India (`data.gov.in`)
- **Platform maintained by:** National Informatics Centre (NIC), Government of India.
- **Classification:** Official Government Open-Data Platform.
- **MPLADS Role:** Primary open-data baseline candidate for the 3–5 Day MVP.

### Verified MPLADS Dataset Candidates

1. **Utilisation of MPLAD Scheme funds and detail of works – 16th Lok Sabha MPs**
   - Provides MPLADS fund-utilisation and work-related information.
   - The catalogue provides downloadable/API-enabled resources where explicitly listed.

2. **MPLADS Utilisation since Inception**
   - Provides historical fund-utilisation and work-completion indicators.
   - Useful for historical benchmarking and aggregate trend analysis.

---

## 5. Verified Data Source Analysis

### A. Official MPLADS Portal (`mplads.gov.in`)
* **Owner**: Ministry of Statistics and Programme Implementation (MoSPI).
* **Access Classification**: Category D (Public Dashboard / Bulk Access Unverified) | Official Government Source.
* **Available Content**: Work Register, Recommended Works, Completed Works, Non-Progress Works, Status of Works.

### B. eSAKSHI Portal (`mplads.mospi.gov.in`)
* **Owner**: MoSPI / State Bank of India.
* **Access Classification**: Category D (Public Dashboard / Bulk Access Unverified) | Official Government Source.
* **Digital Era Constraint**: eSAKSHI was introduced on **1 April 2023**. Historical Lok Sabha terms (2019–2022) require OGD dataset normalization.

### C. Dataful Repository (`dataful.in`)
* **Owner**: Dataful (Independent Third-Party).
* **Access Classification**: Category F (Third-Party / Optional) | Potential Enrichment Source (*NOT A HARD DEPENDENCY*).

---

## 6. Formal Data Availability Matrix

| Source | Dataset | Category | Validation Status | Validated Rows / Matches | Key Fields Available | Status for MVP |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Uploaded CSV` | Recommended Works | Cat B | **INGESTED & DEDUPLICATED** | Deduplicated from 2 Files | MP, State, District, Rec Date, Rec Amount, Title | **VALIDATED BASELINE** |
| `Uploaded CSV` | Sanctioned Works | Cat B | **INGESTED & MATCHED** | 220 Unique (206 Matched, 14 Sanctioned-Only) | Work ID, Sanct Date, Sanct Amount, Agency, Sector | **VALIDATED BASELINE** |
| `Uploaded CSV` | Completed Works | Cat B | **UNAVAILABLE / PENDING** | 0 Records | None | **PENDING DATA FEED** |
| `data.gov.in` | 16th LS Work Utilisation| Cat B/C | **VERIFIED CANDIDATE** | ~100k+ (Approx) | Funds, Sanctioned, Spent, Works | Work level | **CORE BASELINE** |
| `Dataful` | 18th LS Expenditure | Cat F | **OPTIONAL / UNVERIFIED** | ~96k (Approx) | Vendor, Expenditure Date | **OPTIONAL ENRICHMENT** |

---

## 7. Canonical MPLADS Data Model

Our canonical data model reflects actual validated CSV ingestion outputs:

```sql
-- Core Canonical Projects Entity
CREATE TABLE canonical_projects (
    project_id VARCHAR(64) PRIMARY KEY,       -- Real or Synthetic Unique ID
    source_id VARCHAR(64),                     -- Original source reference ID
    source_name VARCHAR(64) NOT NULL,          -- e.g. UPLOADED_CSV, OGD_16LS, SYNTHETIC
    data_origin VARCHAR(16) NOT NULL,          -- REAL | SYNTHETIC
    
    -- Mandatory Geographic & Context Fields (REAL_REQUIRED)
    mp_name VARCHAR(128) NOT NULL,
    state VARCHAR(64) NOT NULL,
    constituency VARCHAR(128) NOT NULL,
    district VARCHAR(64) NOT NULL,
    block VARCHAR(64),                         -- SOURCE_DEPENDENT
    village VARCHAR(64),                       -- SOURCE_DEPENDENT
    
    -- Work Attributes (REAL_REQUIRED / SOURCE_DEPENDENT)
    work_name TEXT NOT NULL,
    work_description TEXT,                     -- SOURCE_DEPENDENT
    work_category VARCHAR(64),                 -- SOURCE_DEPENDENT
    
    -- Dates & Timelines (VALIDATED / SOURCE_DEPENDENT)
    recommendation_date DATE,                  -- VALIDATED IN CSV
    sanction_date DATE,                        -- VALIDATED IN CSV
    work_start_date DATE,                      -- SOURCE_DEPENDENT
    target_completion_date DATE,               -- DERIVED
    actual_completion_date DATE,               -- PENDING (Works Completed CSV Unavailable)
    
    -- Financial Fields (VALIDATED / PENDING)
    recommended_amount_inr FLOAT,              -- VALIDATED IN CSV
    sanctioned_amount_inr FLOAT,               -- VALIDATED IN CSV (220 Works)
    released_amount_inr FLOAT,                 -- SOURCE_DEPENDENT
    expenditure_amount_inr FLOAT,              -- PENDING (Works Completed CSV Unavailable)
    expenditure_date DATE,                     -- PENDING
    
    -- Operational Status
    work_status VARCHAR(32) NOT NULL,          -- SANCTIONED, RECOMMENDED_ONLY, SANCTIONED_ONLY, PENDING_COMPLETION
    implementing_agency VARCHAR(128),          -- VALIDATED IN CSV
    vendor_name VARCHAR(128),                  -- SOURCE_DEPENDENT (Not a core dependency)
    image_available BOOLEAN DEFAULT FALSE,     -- SOURCE_DEPENDENT
    
    -- Traceability & Lineage Metadata
    retrieval_date DATE NOT NULL,
    transformation_version VARCHAR(16) NOT NULL,
    
    -- Evaluation Ground Truth (SYNTHETIC_ONLY - Never used in ML features)
    ground_truth_anomaly BOOLEAN DEFAULT FALSE
);
```

---

## 8. Real vs. Synthetic Data Strategy

**MPLAD Intelligence** combines validated real public data with synthetic anomaly augmentation:

```
[ Validated Real Data (220 Sanctioned Works) ] ──► Establishes Empirical Baseline
                                                      │ (Real Titles, Rec/Sanct Costs, Rec/Sanct Dates)
                                                      ▼
[ Synthetic Anomaly Augmentation ]              ──► Injects Anomaly Cases into ~10% Augmentation Set
                                                      │ (Sanction Delay, Cost Inflation, Agency Monopoly)
                                                      ▼
[ Canonical MVP Dataset ]                       ──► 10,000 to 25,000 Target Records
```

---

## 9. What We Will NOT Claim

> [!CAUTION]
> **Strict Operational Boundaries**:
> 1. The system does **NOT** claim to prove fraud or corruption.
> 2. The system does **NOT** fabricate completion dates or expenditure records when the Completed Works CSV is missing.
> 3. The system does **NOT** claim that synthetic anomaly cases represent real historical prosecutions.
> 
> **Official Framing**: "The system prioritizes projects for human review based on observable data deviations and explainable signals."

---

## 10. Final Data Strategy Recommendation

### Recommended Strategy: **Option A — Real Public Data + Synthetic Anomaly Augmentation**
* **Primary Baseline**: 220 validated sanctioned works (206 matched recommendations, 14 sanctioned-only).
* **Synthetic Role**: Injects CAG-documented anomaly profiles (~10% augmentation set) with ground-truth flags.
* **Feasibility Rating**: 🟢 **GO — Implementation Ready for 3–5 Day MVP**.
