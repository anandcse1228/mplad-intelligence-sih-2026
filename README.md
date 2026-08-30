# MPLAD Intelligence — AI-Driven Project Integrity & Anomaly Investigation System

> **Problem Statement ID**: SIH26102  
> **Product Name**: MPLAD Intelligence  
> **Target Scope**: Ludhiana Constituency & Punjab State Datasets (3–5 Day MVP Timeline)

---

## 📌 Executive Summary

**MPLAD Intelligence** is an institutional command center and anomaly audit platform built for monitoring Members of Parliament Local Area Development Scheme (MPLADS) projects. The system ingests public government project feeds, validates financial and timeline data integrity, computes calculated rule signals (such as administrative delays and scope deviations), and prioritizes works for field inspection and risk audit.

---

## 📁 Repository & Project Structure

```
mplads_intelligence/
├── README.md                      # Primary project guide & documentation
├── data/                          # Audited raw CSV data feeds
│   ├── recommended_works.csv      # 242 MP Recommendation Records (₹9.32 Cr)
│   ├── sanctioned_works.csv       # 220 Official Sanctioned Works (₹8.52 Cr)
│   └── completed_works.csv        # 59 Work Completion & Disbursement Records (₹1.84 Cr)
├── docs/                          # Comprehensive system specifications
│   ├── 01_Research_and_System_Architecture.md (.docx)
│   ├── 02_Product_Requirements_Document_PRD.md (.docx)
│   ├── 03_Data_and_ML_Research_Design.md (.docx)
│   ├── 05_Technical_Architecture_and_10_Day_Plan.md (.docx)
│   ├── 07_Decision_Log.md (.docx)
│   └── 08_UI_UX_Design_Specification.md (.docx)
├── frontend/                      # Vite + React 18 + Tailwind CSS Institutional Command Center UI
│   ├── package.json               # Node dependencies & script runners
│   ├── vite.config.js             # Vite configuration (port 3000, @tailwindcss/vite)
│   ├── index.html                 # HTML entrypoint
│   └── src/
│       ├── App.jsx                # Main Command Center Dashboard Page 1 Layout
│       ├── index.css              # Dark institutional theme styles (#0D1117 / #161B22)
│       ├── components/
│       │   ├── Navbar.jsx         # Institutional header with badge status
│       │   ├── Sidebar.jsx        # Drawer navigation with module status
│       │   ├── KpiCards.jsx       # Real-data KPI overview cards
│       │   ├── DataNoticeBanner.jsx# 3/3 CSV validated data notice banner
│       │   ├── RiskQueueTable.jsx # Priority review & calculated rule signal table
│       │   └── AnalyticsWidgets.jsx# Real scheme status & IDA share charts
│       └── data/
│           └── mockData.js        # 100% empirical CSV audited metrics & preview records
└── scripts/                       # Automated data audit and doc tools
    ├── audit_data.py              # Python audit script for CSV parsing & metric calculation
    └── compile_docx.py            # Markdown-to-DOCX compilation utility
```

---

## 🚀 Setup & Local Execution Instructions

### Prerequisites
* **Node.js**: v18.0.0 or higher
* **npm**: v9.0.0 or higher
* **Python**: v3.9+ (for running `scripts/audit_data.py`)

---

### 1. Running the Frontend (Command Center Dashboard)

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start local development server
npm run dev

# 4. Access the Command Center in your browser:
# http://localhost:3000/
```

To build for production verification:
```bash
npm run build
```

---

### 2. Running the Data Audit Verification Script

To parse the raw CSV feeds directly from disk and re-verify all baseline totals, run:

```bash
# Execute from project root
python scripts/audit_data.py
```

---

## 📊 Empirical Data Audit Summary (Page 1 Baseline)

All numbers displayed on the **Page 1 Command Center** are derived 100% empirically from the raw uploaded CSV files:

* **Total Recommended Works**: 242 Records | **₹9.32 Cr** (`recommended_works.csv`)
* **Total Sanctioned Works**: 220 Records | **₹8.52 Cr** (`sanctioned_works.csv`)
* **Total Completed Works**: 59 Records | **₹1.84 Cr** (`completed_works.csv`)
* **Mean Sanction Delay**: **75.4 Days** (Median: 54 Days, Min: 2d, Max: 356d)
* **Implementing Agency Distribution (IDA)**:
  * `Ludhiana DC IDA`: **206 Works (93.6%)** | ₹7.89 Cr
  * `Sri Muktsar Sahib IDA`: **11 Works (5.0%)** | ₹0.52 Cr
  * `Jalandhar / Ferozepur / Fazilka IDAs`: **3 Works (1.4%)** | ₹0.11 Cr
* **Official Scheme Status Breakdown**:
  * Sanction Issued: **104 Works (47.3%)**
  * Physical Inspection: **51 Works (23.2%)**
  * Vendor Identification: **33 Works (15.0%)**
  * Work Partially Completed: **22 Works (10.0%)**
  * Work Completed: **9 Works (4.1%)**
  * Time Estimation: **1 Work (0.5%)**

---

## ⚙️ Implementation Roadmap Status (3–5 Day MVP Timeline)

| Module / Layer | Feature / Screen | Status | Details |
| :--- | :--- | :--- | :--- |
| **Data Layer** | Data Ingestion & Audit | **✅ COMPLETED** | All 3 CSV feeds parsed, audited, and verified via `scripts/audit_data.py`. |
| **Frontend UI** | Page 1 — Institutional Command Center | **✅ COMPLETED** | Navbar, Sidebar, Real KPI Cards, 3/3 Data Notice Banner, Operational Queue Table, Analytics Widgets. |
| **Frontend UI** | Page 2 — Investigation Queue & Filters | **⏳ PENDING (Day 4)** | Advanced tabular filtering, district breakdown, risk band sorters. |
| **Frontend UI** | Page 3 — Project Audit Deep-Dive Modal | **⏳ PENDING (Day 4)** | Timeline breakdown, recommendation vs sanction comparison. |
| **ML Engine** | Isolation Forest Anomaly Detection | **⏳ PENDING (Day 4)** | Unsupervised Isolation Forest model training on available feature vector ($S_{risk}$). |
| **Backend API** | FastAPI REST Endpoints | **⏳ PENDING (Day 4)** | Python FastAPI backend serving calculated scores and GeoJSON boundaries. |

---

## 🛡️ Operational Integrity Principles

1. **Zero Fake Risk Scores**: Risk scores are explicitly marked **`Pending Day 4 Model Run`** until the ML model is trained.
2. **Empirical Precision**: All real-data KPIs match the exact calculated totals from government CSV files.
3. **Institutional UI Design**: Dark theme base (`#0D1117` base, `#161B22` cards, `#0E857C` teal accent) designed for government audit workflows.
