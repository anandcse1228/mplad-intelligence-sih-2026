// 100% Empirical CSV Ingestion Baseline Metadata & Real ML Isolation Forest Scoring Metadata
export const INGESTION_METADATA = {
  // Real Empirical Data Counts
  totalRecommendedWorks: 242,
  totalRecommendedAmountCr: 9.32,      // ₹9,32,19,872.00
  totalSanctionedWorks: 220,
  totalSanctionedAmountCr: 8.52,       // ₹8,51,86,872.00
  totalCompletedWorks: 59,
  totalDisbursedAmountCr: 1.84,        // ₹1,83,72,811.00
  
  // Real Calculated Metrics
  avgSanctionDelayDays: 75.4,          // 75.35 Days empirical mean across 220 sanctioned records
  medianSanctionDelayDays: 54,         // 54 Days empirical median
  minSanctionDelayDays: 2,
  maxSanctionDelayDays: 356,
  
  // IDA Breakdown (Empirical)
  ludhianaIdaCount: 206,               // 93.6%
  ludhianaIdaAmountCr: 7.89,
  otherIdaCount: 14,                   // 6.4% (Sri Muktsar Sahib: 11, Jalandhar: 1, Ferozepur: 1, Fazilka: 1)
  otherIdaAmountCr: 0.62,

  // Real Work Status Distribution (Sanctioned Feed)
  statusBreakdown: [
    { label: "Sanction Issued", count: 104, percentage: 47.3 },
    { label: "Physical Inspection", count: 51, percentage: 23.2 },
    { label: "Vendor Identification", count: 33, percentage: 15.0 },
    { label: "Work Partially Completed", count: 22, percentage: 10.0 },
    { label: "Work Completed", count: 9, percentage: 4.1 },
    { label: "Time Estimation", count: 1, percentage: 0.5 }
  ],

  // ML Isolation Forest Model Engine Output Metadata
  mlStatus: "MODEL_FITTED",
  modelName: "Isolation Forest (Unsupervised Anomaly Model)",
  nEstimators: 100,
  contaminationRate: 0.10,
  totalScoredRecords: 220,
  anomalyCandidatesCount: 7,           // 7 Works (3.2%) with S_ml >= 70.0
  criticalRiskCount: 0,
  highRiskCount: 5,
  mediumRiskCount: 11,
  normalRiskCount: 204,
  lastIngestionDate: "2026-08-26 01:57 IST",

  // Validated Active Data Feeds
  dataSources: [
    { name: "Recommended Works Feed", status: "VALIDATED", count: "242 Records", origin: "recommended_works.csv" },
    { name: "Sanctioned Works Feed", status: "VALIDATED", count: "220 Records", origin: "sanctioned_works.csv" },
    { name: "Completed Works Feed", status: "VALIDATED", count: "59 Records", origin: "completed_works.csv" }
  ]
};

// Real ML Model Scored Works (Top Priority Anomalies & Risk Queue Preview)
// Verified 100% Unique Work IDs from scripts/train_ml_engine.py
export const TOP_REAL_WORKS_PREVIEW = [
  {
    id: "WS/MP18157/2024-2025/163249",
    srNo: "35",
    title: "Public Lift, Lawyers Chamber Complex, Ward no-01, Jagraon, Distt. Ludhiana",
    mpName: "AMRINDER SINGH RAJA WARRING",
    constituency: "LUDHIANA",
    district: "Ludhiana",
    state: "Punjab",
    agency: "LUDHIANA(DEPUTY COMMISSIONER LUDHIANA_IDA)",
    sanctionedAmountLakhs: 25.0,
    recommendedAmountLakhs: 25.0,
    sanctionDelayDays: 28,
    status: "Sanction",
    isCompleted: false,
    features: {
      sanction_delay_days: 28,
      log_sanction_amount: 14.7318,
      category_cost_zscore: 6.75,
      ida_concentration_pct: 93.6,
      disbursed_variance_pct: 0.0
    },
    mlRiskScore: 92.4,
    ruleScore: 35.0,
    riskPriorityScore: 69.4,
    severityLabel: "HIGH RISK PRIORITY",
    isMlAnomaly: true,
    ruleSignals: [
      "Category Cost Outlier: Z-Score +6.75 in 'Normal/Others'",
      "High-Value Project Allocation: ₹25.0 Lakhs"
    ],
    explanation: {
      mlAnomalyEvidence: "Isolation Forest Path Anomaly (S_ml: 92.4/100)",
      deterministicRuleEvidence: "Triggered Cost Outlier Signal (Score: 35.0/100)",
      compositeRiskFormula: "S_risk = 0.60 * S_ml (92.4) + 0.40 * S_rule (35.0) = 69.4"
    }
  },
  {
    id: "WS/MP18157/2024-2025/169462",
    srNo: "215",
    title: "Construction of Street by laying Interlock tiles From House of Jarnail Singh to house of Gurdas Singh in Vill. Gurri Sangar",
    mpName: "AMRINDER SINGH RAJA WARRING",
    constituency: "LUDHIANA",
    district: "Sri muktsar sahib",
    state: "Punjab",
    agency: "SRI MUKTSAR SAHIB(DEPUTY COMMISSIONER SRI MUKTSAR SAHIB_IDA)",
    sanctionedAmountLakhs: 5.75,
    recommendedAmountLakhs: 5.75,
    sanctionDelayDays: 2,
    status: "Work Completed",
    isCompleted: true,
    features: {
      sanction_delay_days: 2,
      log_sanction_amount: 13.2621,
      category_cost_zscore: 0.28,
      ida_concentration_pct: 5.0,
      disbursed_variance_pct: 50.4
    },
    mlRiskScore: 100.0,
    ruleScore: 20.0,
    riskPriorityScore: 68.0,
    severityLabel: "HIGH RISK PRIORITY",
    isMlAnomaly: true,
    ruleSignals: [
      "Disbursed Amount Variance: 50.4% deviation from sanction",
      "Completed Feed Disbursed: ₹2.85 Lakhs vs Sanctioned ₹5.75 Lakhs"
    ],
    explanation: {
      mlAnomalyEvidence: "Isolation Forest Extreme Outlier (S_ml: 100.0/100)",
      deterministicRuleEvidence: "Disbursed Amount Variance Penalty (Score: 20.0/100)",
      compositeRiskFormula: "S_risk = 0.60 * S_ml (100.0) + 0.40 * S_rule (20.0) = 68.0"
    }
  },
  {
    id: "WS/MP18157/2025-2026/198799",
    srNo: "144",
    title: "Construction of Shelter at Shamshanghat, Vill. Walipur Kalan, Block Sidhwan Bet, Distt. Ludhiana.",
    mpName: "AMRINDER SINGH RAJA WARRING",
    constituency: "LUDHIANA",
    district: "Ludhiana",
    state: "Punjab",
    agency: "LUDHIANA(DEPUTY COMMISSIONER LUDHIANA_IDA)",
    sanctionedAmountLakhs: 3.0,
    recommendedAmountLakhs: 3.0,
    sanctionDelayDays: 157,
    status: "Work Completed",
    isCompleted: true,
    features: {
      sanction_delay_days: 157,
      log_sanction_amount: 12.6115,
      category_cost_zscore: -0.27,
      ida_concentration_pct: 93.6,
      disbursed_variance_pct: 22.3
    },
    mlRiskScore: 76.6,
    ruleScore: 45.0,
    riskPriorityScore: 64.0,
    severityLabel: "HIGH RISK PRIORITY",
    isMlAnomaly: true,
    ruleSignals: [
      "Administrative Delay: 157 Days (>120d threshold)",
      "Disbursed Amount Variance: 22.3% deviation from sanction"
    ],
    explanation: {
      mlAnomalyEvidence: "Isolation Forest Timeline & Variance Anomaly (S_ml: 76.6/100)",
      deterministicRuleEvidence: "Triggered 2 Rule Signals (Score: 45.0/100)",
      compositeRiskFormula: "S_risk = 0.60 * S_ml (76.6) + 0.40 * S_rule (45.0) = 64.0"
    }
  },
  {
    id: "WS/MP18157/2024-2025/163242",
    srNo: "127",
    title: "Installation 25 HP Water Borewell Pump, Ward no-94, Distt. Ludhiana",
    mpName: "AMRINDER SINGH RAJA WARRING",
    constituency: "LUDHIANA",
    district: "Ludhiana",
    state: "Punjab",
    agency: "LUDHIANA(DEPUTY COMMISSIONER LUDHIANA_IDA)",
    sanctionedAmountLakhs: 12.49,
    recommendedAmountLakhs: 12.49,
    sanctionDelayDays: 67,
    status: "Physical Inspection",
    isCompleted: true,
    features: {
      sanction_delay_days: 67,
      log_sanction_amount: 14.0379,
      category_cost_zscore: 2.75,
      ida_concentration_pct: 93.6,
      disbursed_variance_pct: 1.2
    },
    mlRiskScore: 78.7,
    ruleScore: 35.0,
    riskPriorityScore: 61.2,
    severityLabel: "HIGH RISK PRIORITY",
    isMlAnomaly: true,
    ruleSignals: [
      "Category Cost Outlier: Z-Score +2.75 in 'Installing tube-wells and borewells'",
      "Significant Allocation: ₹12.49 Lakhs"
    ],
    explanation: {
      mlAnomalyEvidence: "Isolation Forest Cost Feature Outlier (S_ml: 78.7/100)",
      deterministicRuleEvidence: "Cost Outlier Signal (Score: 35.0/100)",
      compositeRiskFormula: "S_risk = 0.60 * S_ml (78.7) + 0.40 * S_rule (35.0) = 61.2"
    }
  },
  {
    id: "WS/MP18157/2026-2027/236495",
    srNo: "208",
    title: "50 tons of annealed wire for strengthening the embankments of the Satluj river for flood prevention in Vill. Ruknewala Kalan, tehsil zira, block makhu, Distt. Ferozepur",
    mpName: "AMRINDER SINGH RAJA WARRING",
    constituency: "LUDHIANA",
    district: "Ferozepur",
    state: "Punjab",
    agency: "FEROZEPUR(DEPUTY COMMISSIONER FIROZEPUR_IDA)",
    sanctionedAmountLakhs: 3.0,
    recommendedAmountLakhs: 3.0,
    sanctionDelayDays: 268,
    status: "Sanction",
    isCompleted: false,
    features: {
      sanction_delay_days: 268,
      log_sanction_amount: 12.6115,
      category_cost_zscore: -0.27,
      ida_concentration_pct: 0.45,
      disbursed_variance_pct: 0.0
    },
    mlRiskScore: 73.7,
    ruleScore: 40.0,
    riskPriorityScore: 60.2,
    severityLabel: "HIGH RISK PRIORITY",
    isMlAnomaly: true,
    ruleSignals: [
      "Administrative Delay: 268 Days (>180d threshold)",
      "Out-of-District Allocation (Ferozepur IDA)"
    ],
    explanation: {
      mlAnomalyEvidence: "Isolation Forest Anomaly (S_ml: 73.7/100)",
      deterministicRuleEvidence: "Administrative Delay Penalty (>180 Days, Score: 40.0/100)",
      compositeRiskFormula: "S_risk = 0.60 * S_ml (73.7) + 0.40 * S_rule (40.0) = 60.2"
    }
  }
];

// Real Agency Distribution from ML Dataset
export const REAL_AGENCY_DISTRIBUTION = [
  { name: "LUDHIANA (DC LUDHIANA IDA)", works: 206, percentage: 93.6, amountCr: 7.89 },
  { name: "SRI MUKTSAR SAHIB IDA", works: 11, percentage: 5.0, amountCr: 0.52 },
  { name: "JALANDHAR IDA", works: 1, percentage: 0.5, amountCr: 0.05 },
  { name: "FEROZEPUR IDA", works: 1, percentage: 0.5, amountCr: 0.03 },
  { name: "FAZILKA IDA", works: 1, percentage: 0.5, amountCr: 0.025 }
];
