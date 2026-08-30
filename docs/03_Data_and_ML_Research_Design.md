# Document 03 — Data & ML Research & Design
## MPLAD Intelligence (SIH26102)

---

## 1. Feature Classification: Validated Computable vs. Pending Data Features

Based on the actual CSV validation results (220 unique sanctioned works, 206 recommendation matches, 14 sanction-only works; Works Completed CSV unavailable), feature vectors are strictly partitioned into **Currently Computable Features** vs. **Pending Data Features**:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ VALIDATED COMPUTABLE FEATURES (Available in Current Ingested CSV Feed)          │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1. Sanction Delay Days (F_DAYS_SANCTION): sanction_date - recommendation_date │
│ 2. Sanction Amount Deviation % (F_SANCT_DEV): (sanctioned - recommended) / rec  │
│ 3. Sector Cost Z-Score (F_COST_OUTLIER): Z-score of sanctioned cost in sector   │
│ 4. Implementing Agency Work Share % (F_AGENCY_CONC): Agency's district share    │
│ 5. Duplicate Title Similarity (F_TITLE_DUP): Jaro-Winkler similarity            │
│ 6. Unmatched Sanction Flag (F_UNMATCHED_SANCT): 1.0 if sanctioned without rec   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ PENDING DATA FEATURES (Unavailable - Works Completed CSV Feed Pending)          │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 7. Actual Expenditure % (F_EXP_PCT) - PENDING Works Completed CSV               │
│ 8. Financial Release % (F_FIN_REL_PCT) - PENDING Expenditure/Release Feed       │
│ 9. Completion Timeline Overrun (F_COMPLETION_VAR) - PENDING Completion Feed     │
│ 10. Continuous Physical Progress % (F_PHY_PRG_PCT) - PENDING Geotag Feed         │
│ 11. Vendor Concentration % (F_VENDOR_CONC) - PENDING Vendor Feed                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Feature Engineering Pipeline (Validated Features Vector)

The feature extraction engine transforms canonical project records into a 6-dimensional normalized feature vector $\vec{X}_{valid}$ using strictly available validated fields:

| Feature Code | Feature Name | Mathematical Definition | Data Source | Core Target |
| :--- | :--- | :--- | :--- | :--- |
| `F_DAYS_SANCTION` | Sanction Delay Days | $\text{sanction\_date} - \text{recommendation\_date}$ | Rec & Sanct CSV | Administrative Lag |
| `F_SANCT_DEV` | Sanction Amount Dev | $\frac{\text{sanctioned\_amount} - \text{recommended\_amount}}{\text{recommended\_amount}}$ | Rec & Sanct CSV | Scope Inflation |
| `F_COST_OUTLIER`| Sector Cost Z-Score | $\frac{\text{sanctioned\_cost} - \mu_{\text{sector}}}{\sigma_{\text{sector}}}$ | Sanct CSV | Cost Anomaly |
| `F_AGENCY_CONC` | Agency Work Share | $\frac{\text{agency\_works\_in\_district}}{\text{total\_district\_works}}$ | Sanct CSV | Agency Monopoly |
| `F_TITLE_DUP` | Title Similarity | Max Jaro-Winkler similarity against district titles | Rec & Sanct CSV | Duplicate Work |
| `F_UNMATCHED` | Unmatched Sanction | $1.0$ if project is sanctioned without MP rec; else $0.0$ | Matching Logic | Procedural Violation |

---

## 3. Anomaly Injection Logic (Validated Set Baseline)

Synthetic anomaly injection targets validated operational patterns across 220 sanctioned works baseline:

| Anomaly ID | Category | Trigger Logic (Validated Features Only) | Ground-Truth Injection Signature |
| :--- | :--- | :--- | :--- |
| **ANM-01** | `SANCTION_DELAY` | `F_DAYS_SANCTION > 180 days` | Sanction delay > 180 days |
| **ANM-02** | `SANCTION_DEV` | `F_SANCT_DEV > 0.30` | Sanctioned cost exceeds recommendation by >30% |
| **ANM-03** | `AGENCY_CONC` | `F_AGENCY_CONC > 0.50` | Agency controls >50% of district works |
| **ANM-04** | `DUPLICATE_WORK` | `F_TITLE_DUP > 0.88` | Work title >88% match with existing work |
| **ANM-05** | `UNMATCHED_SANCTION`| `F_UNMATCHED == 1.0` | Sanctioned work without matching MP recommendation |

---

## 4. Deterministic Rule Engine (Validated Rules)

```python
def evaluate_validated_compliance_rules(features):
    rule_score = 0.0
    signals = []
    
    # Rule 1: Administrative Sanction Delay (> 180 Days)
    if features.get('F_DAYS_SANCTION') and features['F_DAYS_SANCTION'] > 180:
        rule_score += 35.0
        signals.append("ANM-01: Sanction delay exceeds 180 days")
        
    # Rule 2: Scope Inflation (> 30% Deviation)
    if features.get('F_SANCT_DEV') and features['F_SANCT_DEV'] > 0.30:
        rule_score += 30.0
        signals.append("ANM-02: Sanctioned amount exceeds recommendation by >30%")
        
    # Rule 3: Agency Concentration (> 50% Share)
    if features.get('F_AGENCY_CONC') and features['F_AGENCY_CONC'] > 0.50:
        rule_score += 25.0
        signals.append("ANM-03: Implementing agency controls >50% of district works")
        
    # Rule 4: Duplicate Work Title (> 88% Similarity)
    if features.get('F_TITLE_DUP') and features['F_TITLE_DUP'] > 0.88:
        rule_score += 40.0
        signals.append(f"ANM-04: Potential duplicate work title ({int(features['F_TITLE_DUP']*100)}% match)")
        
    # Rule 5: Sanctioned-Only Work (No Recommendation Record)
    if features.get('F_UNMATCHED') == 1.0:
        rule_score += 30.0
        signals.append("ANM-05: Work sanctioned without explicit MP recommendation in feed")
        
    return min(100.0, rule_score), signals
```

---

## 5. Machine Learning Anomaly Engine (Isolation Forest)

* **Algorithm**: `sklearn.ensemble.IsolationForest` (PRIMARY Baseline).
* **Input Feature Vector**: $\vec{X}_{valid} = [\text{F\_DAYS\_SANCTION}, \text{F\_SANCT\_DEV}, \text{F\_COST\_OUTLIER}, \text{F\_AGENCY\_CONC}, \text{F\_TITLE\_DUP}, \text{F\_UNMATCHED}]$
* **Constraint**: Isolation Forest operates **strictly** on the validated 6-dimensional available feature vector.
* **Hyperparameters**: `n_estimators=100`, `contamination=0.10`, `random_state=42`.

---

## 6. Risk Priority Score Formulation

$$S_{risk} = \min\left(100.0, \, 0.50 \cdot S_{rules} + 0.30 \cdot S_{iforest} + 0.20 \cdot S_{dup}\right)$$

### Proposed MVP Severity Bands
* `80.0 - 100.0`: **CRITICAL / PRIORITY REVIEW**
* `60.0 - 79.9`: **HIGH RISK**
* `30.0 - 59.9`: **MODERATE WARNING**
* `0.0 - 29.9`: **LOW / NORMAL**

---

## 7. Implementation Readiness Check

```
[✓] VALIDATED FEATURES: 6 features extracted from 220 sanctioned works baseline.
[✓] UNEXPOSABLE DATA HANDLING: Pending features (expenditure, completion) explicitly marked PENDING DATA.
[✓] ISOLATION FOREST CONSTRAINED: ML engine uses strictly validated computable features.
[✓] 3-5 DAY SCOPING: Aligned with hackathon delivery timeframe.
[✓] GO / NO-GO CHECK: 🟢 GO — Ready for Execution.
```
