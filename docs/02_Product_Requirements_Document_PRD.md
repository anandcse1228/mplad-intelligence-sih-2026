# Document 02 — Product Requirements Document (PRD)
## MPLAD Intelligence (SIH26102)

---

## 1. Product Overview & Vision

**MPLAD Intelligence** is an institutional-grade, AI-assisted monitoring, analytics, and investigation prioritization platform designed specifically for the Member of Parliament Local Area Development Scheme (MPLADS). 

### Product Vision
To transform MPLADS monitoring from reactive, manual paper-report auditing into a proactive, data-driven intelligence workflow. By continuously analyzing multi-source scheme data—including financial releases, milestone completion reports, geo-tagged physical evidence, and contractor relationships—the platform computes a dynamic **Risk Priority Score (0–100)** and generates transparent, evidence-backed anomaly signals. The system does NOT automatically issue fraud verdicts; instead, it empowers authorized government officers to prioritize investigations and execute defensible administrative actions with complete auditability.

---

## 2. Product-Level Problem Statement

Managing over 5,000 active MPLADS projects annually across 543 Lok Sabha and 245 Rajya Sabha constituencies generates immense volume and operational complexity for nodal monitoring officers.

Current monitoring processes suffer from key vulnerabilities:
1. **Manual Audit Bottlenecks**: Central and State Nodal Officers receive thousands of static Monthly Progress Reports (MPRs), making it humanly impossible to identify high-risk projects requiring urgent physical inspection.
2. **Hidden Progress Mismatches**: Substantial funds are disbursed rapidly via district channels while verified physical execution lags behind without automated detection.
3. **Contractor Cartels & Monopoly**: Implementing agencies may repeatedly allocate local works to single contractor syndicates or interconnected entities sharing common promoters without triggering administrative flags.
4. **Lack of Evidence Traceability**: Auditors lack a single-pane workspace that connects fund release logs, geo-tagged photo evidence, timeline milestones, and contractor ownership structures.

---

## 3. Product Goals & Success Metrics

| Goal | Target MVP Metric | Measurement Method |
| :--- | :--- | :--- |
| **High-Risk Case Identification** | 100% of projects with Risk Score $\ge 80.0$ highlighted in Priority Queue | Automated database query assertion on batch run |
| **Signal Explainability** | 100% of flagged projects display $\ge 1$ human-readable Evidence Signal | Evidence signal mapping validation |
| **Inspection Dispatch Speed** | < 2 minutes for an officer to review a case and dispatch an inspection | User interaction workflow logging |
| **System Query Performance** | Sub-250ms API response time for dashboard KPI loading and table filtering | Load testing on 1,000 synthetic project database |
| **Audit Traceability** | 100% of officer actions stored with mandatory justification in append-only log | Database FK constraint & audit log check |

---

## 4. Target Users & User Personas

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CENTRAL / STATE NODAL OFFICER                      │
│ (Macro Monitoring, National Command Center, State Analytics, Risk Heatmap)│
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       DISTRICT AUTHORITY (DA / DM)                      │
│ (Constituency Oversight, Project Intelligence, Evidence Mismatch Review) │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FIELD AUDITOR / VIGILANCE OFFICER                    │
│(Forensic Chronology, Contractor Network Graph, Inspection Dispatch WS)  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Persona 1: Central Nodal Officer (MoSPI)
* **Role**: National Monitoring & Policy Oversight.
* **Goal**: Understand overall national risk posture; identify states and sectors with high anomaly density; ensure optimal fund utilization.
* **Pain Point**: Overwhelmed by macro spreadsheets; inability to spot cross-state contractor concentration.

### Persona 2: District Authority (Collector / DM)
* **Role**: Sanctioning and Local Execution Oversight.
* **Goal**: Verify that physical progress matches fund release requests before disbursing subsequent tranches.
* **Pain Point**: Lack of automated verification tools to catch progress discrepancies or contractor bid-rigging.

### Persona 3: Vigilance & Field Auditor
* **Role**: Deep-dive Investigation and On-ground Verification.
* **Goal**: Gather clear, defensible evidence to substantiate administrative or legal audit findings.
* **Pain Point**: Fragmented paper trails; absence of historical contractor directorship linkage records.

---

## 5. Core User Journey

```
[ Step 1: Login & Command Center ]
Nodal Officer logs in ──► Views National Command Center ──► Observes 127 High-Risk Projects flag
                                                                         │
                                                                         ▼
[ Step 2: Risk Queue Filtering ] ◄────────────────────────────────────────┘
Officer opens Risk Queue ──► Applies filter: State="Maharashtra", District="Pune", MinRisk=80
                                                                         │
                                                                         ▼
[ Step 3: Project Intelligence ] ◄───────────────────────────────────────┘
Selects Project ID `MPL-MH-2023-441` ──► Reviews Risk Priority Score (92/100) & Breakdown Matrix
                                                                         │
                                                                         ▼
[ Step 4: Evidence & Graph Review ]
Examines Evidence Card: "85% Funds Disbursed vs 15% Physical Progress" ──► Checks Contractor Graph
                                                                         │
                                                                         ▼
[ Step 5: Officer Action & Audit Log ]
Opens Operator Workspace ──► Selects "Hold Payment Release" ──► Enters Justification ──► Audit Log Saved
```

---

## 6. Functional Requirements

All functional requirements directly map to backend contracts defined in **Document 01 — Research & System Architecture**.

### Module 1: Application Shell & Global Controls
* **FR-1.1**: The system shall render a persistent left sidebar containing navigation links to all 10 platform modules.
* **FR-1.2**: The top bar shall feature a global search input capable of querying Project IDs, MP names, Contractor names, and District locations.
* **FR-1.3**: The system shall provide context dropdowns for selecting State, District, and Reporting Period to globally filter all screen metrics.

### Module 2: National Command Center (Dashboard)
* **FR-2.1**: The dashboard shall display a 4-card KPI strip showing: Total Monitored Projects, High-Risk Projects Count ($\ge 80.0$), Detected Anomalies Count, and Total Sanctioned Value (₹ Cr).
* **FR-2.2**: The dashboard shall render an interactive System-Detected Anomaly Trend bar chart categorized by severity (Critical, High, Warning, Normal).
* **FR-2.3**: The dashboard shall display a Geographic Risk panel showing high-density anomaly clusters across states.
* **FR-2.4**: The dashboard shall render a Priority Review Queue preview table highlighting top high-risk projects.

### Module 3: Risk & Investigation Queue
* **FR-3.1**: The queue shall display a high-density data table with pagination (15 items/page), column sorting, and multi-select filtering.
* **FR-3.2**: Filtering controls must support: State, District, Project Sector, Risk Score Range (Slider), Anomaly Category, and Project Status.
* **FR-3.3**: Each row shall display Project ID, Work Title, Implementing Agency, Risk Priority Score Badge (Red $\ge 80$, Yellow $50-79$, Green $<50$), Primary Anomaly Signal, Status, and Action menu.

### Module 4: Project Intelligence View
* **FR-4.1**: The header shall present complete project metadata: ID, Work Title, State, District, Constituency, Agency, Sanction Date, and Risk Priority Score (0–100).
* **FR-4.2**: The view shall render a Risk Breakdown Matrix scoring 4 specific sub-dimensions: Financial Velocity, Physical Progress, Timeline Variance, and Contractor Integrity.
* **FR-4.3**: The view shall feature an Evidence & Trigger Signals section detailing factual observations vs AI/ML signals.
* **FR-4.4**: The view shall display a Forensic Chronology timeline rendering all historical administrative, financial, and physical milestones.

### Module 5: Operator Workspace & Investigation Actions
* **FR-5.1**: The workspace shall provide 4 primary administrative action triggers: `Request Field Inspection`, `Hold Payment Release`, `Escalate Case to Vigilance`, and `Mark Verified / Clear`.
* **FR-5.2**: High-impact actions (`Hold Payment`, `Escalate Case`, `Mark Verified`) shall enforce a 2-step confirmation modal requiring a mandatory justification string (minimum 15 characters).
* **FR-5.3**: The workspace shall provide an Investigator Notes text area allowing officers to record append-only observations.

### Module 6: Contractor Network Graph
* **FR-6.1**: The system shall render an interactive node-link graph using NetworkX backend data.
* **FR-6.2**: Graph nodes shall distinguish Implementing Agencies (square), Contractor Entities (circle), and Directors (user icon).
* **FR-6.3**: Edges shall visually represent contract awards, shared registered addresses, or shared directorship links.
* **FR-6.4**: Clicking any node shall filter the sidebar to show associated contract values and linked risk flags.

### Module 7: District Analytics
* **FR-7.1**: The module shall display comparative charts analyzing expenditure velocity and physical completion rates across districts.
* **FR-7.2**: The module shall provide an interactive Scatter Plot (X-axis = Funds Released %, Y-axis = Physical Progress %, Dot size = Sanctioned Cost, Dot color = Risk Level).

### Module 8: Geo Risk Map
* **FR-8.1**: The map shall display a vector map of India with state and district boundaries.
* **FR-8.2**: High-risk project markers shall be rendered at precise latitude/longitude coordinates with color-coded severity pins.

### Module 9: Project Comparison
* **FR-9.1**: The system shall allow officers to select up to 4 projects for side-by-side comparative analysis across cost, disbursement rate, completion velocity, and risk signals.

### Module 10: Audit Log
* **FR-10.1**: The log shall render a read-only table displaying all historical officer actions, timestamps, role titles, justifications, and target project IDs.

### Module 11: Data Sources Monitoring
* **FR-11.1**: The screen shall display integration health, sync freshness, and record counts for eSAKSHI, PFMS/SNA, and Bhuvan Geo-tag feeds.

---

## 7. MVP Scope Prioritization (MoSCoW Matrix)

```
┌───────────────────────────────────────┬───────────────────────────────────────┐
│               MUST HAVE               │              SHOULD HAVE              │
│ - National Command Center Dashboard   │ - Contractor Network Graph (NetworkX) │
│ - Filterable Risk Queue Table         │ - District Analytics Scatter Plot     │
│ - Project Intelligence & Evidence View│ - Project Comparison (Side-by-Side)   │
│ - Operator Action Modal & Audit Log   │ - Geo Risk Map Component              │
│ - Synthetic Data Generator (1,000 Rec)│ - CSV Report Export Capability        │
├───────────────────────────────────────┼───────────────────────────────────────┤
│              NICE TO HAVE             │             OUT OF SCOPE              │
│ - Automated PDF Audit Brief Generator │ - Live eSAKSHI Production API Scraping│
│ - Advanced NLP Work Title Deduplication│ - Automated Facial Recognition on Photos│
│ - Real-time Push Notifications        │ - Direct Bank Payment Gateway Freeze  │
└───────────────────────────────────────┴───────────────────────────────────────┘
```

---

## 8. Non-Functional Requirements

### 1. Performance
* **NFR-1.1 Dashboard Load Time**: Initial load of the National Command Center shall complete in $< 1.5$ seconds over standard broadband.
* **NFR-1.2 API Latency**: API endpoints (`/overview/kpis`, `/projects/risk-queue`) shall respond in $< 250\text{ ms}$ for a 1,000-project dataset.
* **NFR-1.3 Graph Render Speed**: NetworkX graph rendering in Vis.js shall maintain 60 FPS interaction speed for up to 200 nodes.

### 2. Usability & Ergonomics
* **NFR-2.1 Dark Institutional Theme**: The interface shall strictly enforce the approved dark palette (`#0D1117` base, `#161B22` card, `#0E857C` teal accent) to reduce eye fatigue during 8+ hour monitoring sessions.
* **NFR-2.2 Zero Ambiguity Framing**: AI outputs shall be explicitly labeled as `AI/ML Signal` or `Observed Anomaly`, reserving verbs like `Confirmed` or `Sanctioned` strictly for officer actions.

### 3. Security & Compliance
* **NFR-3.1 Input Validation**: All incoming API requests shall be validated using Pydantic schemas to prevent SQL injection and cross-site scripting (XSS).
* **NFR-3.2 Audit Immutability**: Database constraints shall prohibit `UPDATE` or `DELETE` operations on `investigation_actions` records.

### 4. Explainability & Reliability
* **NFR-4.1 Defensible Scoring**: Every Risk Priority Score must be decomposed into its 4 constituent sub-scores (Financial, Physical, Timeline, Contractor) with associated evidence text.

---

## 9. Acceptance Criteria

| Feature ID | Feature Name | Testable Acceptance Criteria |
| :--- | :--- | :--- |
| **AC-01** | National Dashboard KPIs | Given 1,000 synthetic projects, when Command Center loads, then KPI cards display total projects, high-risk count ($\ge 80$), detected anomalies, and sanctioned value matching database sums within $\pm 0.01\%$. |
| **AC-02** | Risk Queue Filtering | Given the Risk Queue table, when an officer selects State="Maharashtra" and MinRisk=80, then the table returns only projects matching Maharashtra with Risk Score $\ge 80.0$ in $< 250\text{ ms}$. |
| **AC-03** | Project Intelligence View | Given a selected project ID, when opened, then the view renders Risk Priority Score, Risk Breakdown Matrix, Evidence Cards, and Forensic Chronology matching database records. |
| **AC-04** | Action Confirmation Modal | Given the Operator Workspace, when an officer clicks "Hold Payment Release", then a modal appears requiring a justification input ($\ge 15$ chars). Clicking confirm creates an entry in `investigation_actions` and updates project status to `HOLD`. |
| **AC-05** | Contractor Network Graph | Given the Contractor Network view, when a district is selected, then the graph renders nodes for agencies and contractors, correctly highlighting shared directorship links. |
| **AC-06** | Audit Log Traceability | Given an executed officer action, when opening the Audit Log screen, then the action is permanently listed with timestamp, officer name, action type, justification, and project ID. |
