# Healthcare Claims & Denial Performance Analytics — Master AI Build Workflow

## 0. Purpose

Build a portfolio-ready **Healthcare Claims & Denial Performance Analytics** project using the uploaded synthetic healthcare claims dataset as the source foundation.

Primary target role: **Data Analyst / BI Analyst / Healthcare Operations Analyst**.

Primary tools:
- Python / Pandas for data audit and cleaning
- SQL (prefer PostgreSQL) for relational modeling and analysis
- Tableau for interactive dashboards
- Excel only where useful for validation or simple stakeholder-style reporting

The finished project must be:
- truthful and explainable in interviews
- business-focused rather than ML-heavy
- SQL + Tableau centered
- reproducible
- well documented
- explicit that the underlying data is synthetic
- free of invented source facts

---

# 1. Source Dataset Contract

## 1.1 Source file

Input file:
`claim_data.csv`

The current source contains one flat claims table with these fields:

- Claim ID
- Provider ID
- Patient ID
- Date of Service
- Billed Amount
- Procedure Code
- Diagnosis Code
- Allowed Amount
- Paid Amount
- Insurance Type
- Claim Status
- Reason Code
- Follow-up Required
- AR Status
- Outcome

Do not assume columns that are not present.

## 1.2 Data interpretation rules

Treat the dataset as **synthetic healthcare claims data** for portfolio/educational use.

Do not claim:
- real patient data
- real provider performance
- real payer performance
- real hospital performance
- real Enigma Healthcare Solutions data
- production healthcare experience

The README must clearly state that the dataset is synthetic.

## 1.3 Important type rules

Load identifiers as strings, not integers:
- Claim ID
- Provider ID
- Patient ID
- Procedure Code
- Diagnosis Code

Reason: identifiers and coding fields may contain leading zeros and should not be mathematically transformed.

Load `Date of Service` as a date.

Load monetary fields as numeric:
- Billed Amount
- Allowed Amount
- Paid Amount

---

# 2. Project Objective

Analyze claim volume, claim outcomes, denial patterns, financial leakage, follow-up workload, and accounts-receivable status to identify operational opportunities in revenue cycle management.

The analysis must answer business questions, not merely display charts.

Core business questions:

1. How many claims are denied, under review, and paid?
2. Which insurance types have the highest claim-denial rates?
3. Which denial/reason codes occur most often?
4. How much billed value is associated with denied claims?
5. How large is the gross unpaid balance?
6. Which claim categories or procedure codes have higher financial gaps?
7. What proportion of claims require follow-up?
8. What does AR status look like across the claim population?
9. How do claim outcomes vary by month?
10. Where are potential data-quality inconsistencies between Claim Status and Outcome?

---

# 3. Required Project Architecture

Use this structure:

```text
Healthcare-Claims-Denial-Analytics/
│
├── data/
│   ├── raw/
│   │   └── claim_data.csv
│   ├── processed/
│   │   └── claims_cleaned.csv
│   └── exports/
│       └── tableau_claims_dataset.csv
│
├── notebooks/
│   └── 01_claims_data_preparation.ipynb
│
├── sql/
│   ├── 01_schema.sql
│   ├── 02_staging_load.sql
│   ├── 03_cleaning.sql
│   ├── 04_derived_metrics.sql
│   ├── 05_business_analysis.sql
│   └── 06_views_for_tableau.sql
│
├── tableau/
│   └── Healthcare_Claims_Denial_Analytics.twbx
│
├── docs/
│   ├── data_dictionary.md
│   ├── business_requirements.md
│   ├── metric_definitions.md
│   └── business_insights.md
│
├── screenshots/
│   ├── executive_overview.png
│   ├── denial_analytics.png
│   ├── financial_analytics.png
│   └── ar_followup.png
│
├── README.md
└── requirements.txt
```

For Google Colab, all Python work can initially be done in one notebook with clearly separated sections.

---

# 4. Stage 1 — Data Audit

## Objective
Understand the source before changing anything.

## Required checks

- row count
- column count
- data types
- unique count per column
- missing values
- duplicate rows
- duplicate Claim IDs
- invalid dates
- negative monetary values
- zero monetary values
- `Allowed Amount > Billed Amount`
- `Paid Amount > Allowed Amount`
- `Paid Amount > Billed Amount`
- `Allowed Amount < 0`
- `Paid Amount < 0`
- unexpected category values
- inconsistent Claim Status vs Outcome combinations
- inconsistent AR Status vs Claim Status combinations
- leading-zero preservation for IDs/codes

## Output
Create a data-quality summary table with:

| Check | Result | Action |
|---|---:|---|
| Rows | computed | retain |
| Columns | computed | retain |
| Duplicate Claims | computed | investigate/remove only if exact duplicate |
| Missing values | computed | document treatment |
| Monetary anomalies | computed | flag, do not silently delete |
| Status inconsistencies | computed | create quality flag |

Do not remove suspicious records simply to make results look cleaner.

---

# 5. Stage 2 — Data Cleaning & Standardization

## Required transformations

1. Standardize column names to snake_case.
2. Convert IDs and coding fields to strings.
3. Convert date field to proper date type.
4. Convert monetary fields to numeric.
5. Trim whitespace from text fields.
6. Standardize capitalization of categorical fields.
7. Standardize Yes/No values to `Yes` and `No`.
8. Create explicit null handling rules.
9. Preserve the original raw file unchanged.

## Output table

`claims_cleaned`

The cleaned dataset must preserve all source columns plus derived quality flags.

---

# 6. Stage 3 — Derived Metrics

Create the following fields.

## Financial metrics

### Unpaid Amount

`Billed Amount - Paid Amount`

Label it **Gross Unpaid Amount** to avoid implying that every difference is collectible AR.

### Allowed Amount Gap

`Allowed Amount - Paid Amount`

### Billed-to-Allowed Ratio

`Allowed Amount / Billed Amount`

Protect against division by zero.

### Paid-to-Billed Ratio

`Paid Amount / Billed Amount`

### Paid-to-Allowed Ratio

`Paid Amount / Allowed Amount`

Protect against division by zero.

## Claim flags

### Claim Status Denied Flag

1 when `Claim Status = Denied`, else 0.

### Outcome Denied Flag

1 when `Outcome = Denied`, else 0.

### Any Denial Flag

1 when either operational status or outcome indicates denial.

Do not replace the original fields.

## Operational flags

### Follow-up Flag

1 for Yes, 0 for No.

### Open AR Flag

Create a flag based on documented AR Status values; do not assume that every non-Closed record is collectible AR without documenting the rule.

## Data quality flag

### Status Consistency Flag

Flag records where `Claim Status` and `Outcome` combinations are logically inconsistent according to the project rulebook.

Important: do not label a combination as incorrect without defining the rule. The purpose is to identify ambiguous or inconsistent reporting logic in the source.

## Time fields

Create:
- service_year
- service_month
- service_month_name
- service_quarter
- service_week
- service_day_of_week

---

# 7. Stage 4 — Metric Definitions

Every dashboard metric must have a documented definition.

Required metrics:

### Total Claims
Count of distinct Claim IDs.

### Denied Claims
Count of distinct Claim IDs where `Claim Status = Denied`.

### Claim Status Denial Rate
`Denied Claims / Total Claims`.

### Outcome Denial Rate
Count of distinct claims with `Outcome = Denied` divided by Total Claims.

Because the source has both Claim Status and Outcome, keep these metrics separate.

### Paid Claims
Count of distinct Claim IDs where `Claim Status = Paid`.

### Under Review Claims
Count where Claim Status = Under Review.

### Follow-up Rate
Claims requiring follow-up divided by total claims.

### Gross Unpaid Amount
Sum of Billed Amount minus Paid Amount.

### Total Billed Amount
Sum of Billed Amount.

### Total Allowed Amount
Sum of Allowed Amount.

### Total Paid Amount
Sum of Paid Amount.

### Payment Rate
Total Paid Amount / Total Billed Amount.

### Allowed Rate
Total Allowed Amount / Total Billed Amount.

### Average Claim Value
Total Billed Amount / Total Claims.

All ratios must have divide-by-zero protection.

---

# 8. Stage 5 — SQL Data Model

Do not leave the final project as one flat CSV only.

Build a small star-style model suitable for analytics.

## Staging

### stg_claims
Contains the cleaned source-level fields.

## Fact table

### fact_claims
One row per Claim ID.

Recommended fields:
- claim_key
- claim_id
- provider_key
- patient_key
- date_key
- insurance_key
- procedure_key
- diagnosis_key
- reason_key
- billed_amount
- allowed_amount
- paid_amount
- claim_status
- follow_up_required
- ar_status
- outcome
- derived financial metrics
- derived flags

## Dimension tables

### dim_date
- date_key
- full_date
- year
- month
- month_name
- quarter
- week
- day_of_week

### dim_provider
- provider_key
- provider_id

### dim_patient
- patient_key
- patient_id

### dim_insurance
- insurance_key
- insurance_type

### dim_procedure
- procedure_key
- procedure_code

### dim_diagnosis
- diagnosis_key
- diagnosis_code

### dim_reason
- reason_key
- reason_code

Do not invent provider names, patient demographics, payer company names, hospital names, or clinical descriptions unless they actually exist in the source or are explicitly documented as synthetic enrichment.

---

# 9. Stage 6 — SQL Analysis

Create at least **30 strong SQL analyses** and group them by difficulty.

## Basic queries

1. Total claim count
2. Total billed amount
3. Total allowed amount
4. Total paid amount
5. Claim status distribution
6. Insurance type distribution
7. AR status distribution
8. Follow-up distribution
9. Reason code frequency
10. Outcome distribution

## Intermediate queries

11. Denial rate by insurance type
12. Denial rate by reason code
13. Billed amount by insurance type
14. Paid amount by insurance type
15. Gross unpaid amount by insurance type
16. Follow-up rate by insurance type
17. Monthly claim volume
18. Monthly denied amount
19. Average claim value by insurance type
20. Payment rate by insurance type

## Advanced queries

21. Rank insurance types by denied amount
22. Rank reason codes by denial frequency
23. Monthly denial-rate trend using window functions
24. Month-over-month claim volume change
25. Month-over-month paid amount change
26. Cumulative billed amount by month
27. Top procedures by gross unpaid amount
28. Top diagnoses by denial volume
29. High-value denied claims using percentile logic or window functions
30. Status vs outcome inconsistency report

Add additional advanced queries such as:
- CTE-based KPI summaries
- `ROW_NUMBER`, `RANK`, `DENSE_RANK`
- `LAG` for MoM changes
- conditional aggregation
- subqueries
- views
- date functions

Do not add complex SQL solely for show. Every advanced query must answer a business question.

---

# 10. Stage 7 — Tableau Data Preparation

Create a clean analytical extract from SQL.

Preferred source:
`06_views_for_tableau.sql`

Tableau should connect to a business-friendly view rather than raw staging data.

Recommended view:
`vw_claims_analytics`

Include:
- claim date fields
- insurance type
- claim status
- reason code
- follow-up flag
- AR status
- outcome
- billed amount
- allowed amount
- paid amount
- gross unpaid amount
- denial flags
- payment rates
- quality flags

---

# 11. Stage 8 — Tableau Dashboard Design

Build **4 dashboards**.

## Dashboard 1 — Executive Claims Overview

### KPI cards
- Total Claims
- Total Billed Amount
- Total Paid Amount
- Claim Status Denial Rate
- Follow-up Rate
- Gross Unpaid Amount

### Visuals
- Monthly claim volume trend
- Claim status mix
- Insurance type comparison
- Outcome distribution

### Filters
- Date
- Insurance Type
- Claim Status
- AR Status

---

## Dashboard 2 — Denial Analytics

### KPI cards
- Denied Claims
- Denial Rate
- Denied Billed Amount
- Any Denial Amount

### Visuals
- Denials by reason code
- Denial rate by insurance type
- Monthly denial trend
- Denied amount by insurance type
- Top procedures by denied amount

### Interactivity
- Filter by month
- Filter by insurance type
- Click a reason to cross-filter the dashboard

---

## Dashboard 3 — Financial Performance

### KPI cards
- Total Billed
- Total Allowed
- Total Paid
- Gross Unpaid
- Payment Rate

### Visuals
- Billed vs Allowed vs Paid by month
- Insurance-type payment rate
- Top procedures by gross unpaid amount
- Paid-to-Billed distribution

Important: clearly label gross unpaid amount and do not call it recoverable AR without evidence.

---

## Dashboard 4 — AR, Follow-up & Data Quality

### KPI cards
- Follow-up Rate
- Open AR Records
- Status Inconsistency Count
- Claims Under Review

### Visuals
- AR status distribution
- Follow-up rate by insurance type
- Follow-up count by reason code
- Claim Status vs Outcome matrix
- Data-quality issue trend/table

This dashboard differentiates the project from generic healthcare dashboards.

---

# 12. Stage 9 — Dashboard UX Rules

Use a clean enterprise layout.

Rules:
- one consistent font family
- meaningful titles
- avoid unnecessary 3D charts
- use bars/lines before pies
- maximum 6–8 major visuals per dashboard
- prioritize KPI + trend + comparison
- use filters consistently
- avoid visual clutter
- show units clearly (₹ / % / claim count)
- use tooltips to explain metrics
- keep color meaning consistent
- use accessible contrast

Every dashboard should tell a story from:
**What happened → Where → Why → What needs attention**.

---

# 13. Stage 10 — Business Insights

Do not generate generic statements such as "Insurance X has many claims."

Each insight must include:

**Observation → Evidence → Business implication → Potential action**

Example structure:

> Observation: One insurance category shows a materially higher claim-status denial rate than the portfolio average.
>
> Evidence: Cite the exact computed KPI and time period.
>
> Implication: A larger portion of billed value may require additional review or follow-up.
>
> Potential action: Investigate the dominant reason codes and review front-end claim validation rules.

Do not claim causation unless the data supports it.

---

# 14. Stage 11 — RCM-Oriented Business Questions

The project should answer realistic revenue-cycle questions such as:

### Claims
- Where is claim volume concentrated?
- Which insurance types contribute the largest billed and paid amounts?

### Denials
- Which reason codes drive the highest denial volume?
- Which insurance categories have the largest denial amounts?

### Financial
- Where is the largest gross unpaid balance?
- Which procedure codes have the largest payment gaps?

### Follow-up
- Which segments generate the most follow-up workload?
- Is follow-up more common among denied or under-review claims?

### AR
- What is the composition of AR status?
- Which categories have the highest open-status exposure?

### Data quality
- How often do Claim Status and Outcome disagree?
- Which fields or categories contribute most to reporting ambiguity?

---

# 15. Stage 12 — Data Quality / Integrity Rules

This is a key differentiator.

Create a section of the analysis specifically for data quality.

Check for:
- duplicate claim IDs
- impossible monetary relationships
- missing values
- invalid categories
- inconsistent claim/outcome status
- invalid code formats
- suspicious identifier formatting

Do not silently "fix" all anomalies.

For each issue, choose one:
- correct when objectively deterministic
- retain + flag
- remove only when it is a true duplicate or unusable record
- document as unresolved

---

# 16. Stage 13 — Python/Colab Notebook Structure

Use these notebook headings exactly:

```text
1. Project Overview
2. Import Libraries
3. Load Raw Data
4. Data Audit
5. Data Quality Checks
6. Data Cleaning
7. Feature / Metric Engineering
8. Exploratory Data Analysis
9. Export Clean Dataset
10. Export Tableau Dataset
11. Validation Summary
```

The notebook should be readable by a recruiter or interviewer.

Use functions where repeated logic exists.

Do not leave dozens of unexplained cells.

---

# 17. Stage 14 — Validation Tests

Before SQL/Tableau, run a final validation.

Required assertions:

- Claim ID is unique in the fact table.
- No unexpected nulls in required fields.
- Monetary fields are numeric.
- Date parsing succeeded.
- All categorical values are within documented sets.
- Derived metrics are mathematically correct.
- Dashboard totals reconcile with SQL totals.
- Tableau KPI totals reconcile with SQL KPI totals.

Create a final validation table:

| Validation | Expected | Actual | Status |
|---|---:|---:|---|
| Distinct Claims | computed | computed | PASS/FAIL |
| Total Billed | computed | computed | PASS/FAIL |
| Total Paid | computed | computed | PASS/FAIL |
| Denied Claims | computed | computed | PASS/FAIL |
| Follow-up Claims | computed | computed | PASS/FAIL |

The project is not finished until all critical reconciliation checks pass.

---

# 18. Stage 15 — Documentation

## README structure

```text
# Healthcare Claims & Denial Performance Analytics

## Business Problem
## Objective
## Dataset
## Tools & Technologies
## Data Preparation
## Data Model
## Key Metrics
## SQL Analysis
## Tableau Dashboards
## Key Findings
## Business Implications
## Data Quality
## How to Run
## Project Limitations
## Future Enhancements
## Disclaimer
```

## Data disclaimer

Use wording similar to:

> The dataset used in this project is synthetic and intended for analytics/portfolio purposes only. No real patient information or confidential healthcare records are used.

---

# 19. Stage 16 — Resume Version

Final resume title:

**Healthcare Claims & Denial Performance Analytics**

Target tools:
`SQL | PostgreSQL | Tableau | Python | Pandas`

Resume description should focus on:
- claims analysis
- denial analysis
- KPI reporting
- financial analysis
- dashboard development
- business insights

Do not claim:
- healthcare employment
- medical coding expertise
- HIPAA compliance experience
- actual payer/provider consulting
- real-world revenue figures

unless separately supported by genuine experience.

---

# 20. Stage 17 — Interview Preparation

Generate interview questions based only on the project actually implemented.

## SQL questions
- Why did you normalize the source data?
- Why use a star schema?
- When would you use CTEs vs subqueries?
- How did you calculate denial rate?
- How did you calculate MoM change?
- Where did you use window functions?
- How did you handle divide-by-zero?
- How did you validate SQL vs Tableau totals?

## Analytics questions
- What was the most important KPI?
- What did you learn from denial reasons?
- How did you distinguish denial from outcome?
- Why did you flag status inconsistencies?
- What limitations does the dataset have?

## Tableau questions
- Why did you choose each chart?
- What filters and dashboard actions did you use?
- How did you keep KPI definitions consistent?
- How did you design the executive view?

---

# 21. Stage 18 — Future Enhancements

Only add these after the core project is complete.

Possible enhancements:
- payer dimension enrichment using clearly labeled synthetic data
- provider specialty as synthetic enrichment
- claim submission date and payment date as synthetic event layers
- denial appeal tracking
- claim aging buckets
- first-pass acceptance / clean-claim metric
- monthly trend forecasting
- Power BI version of the dashboard

Any enriched field must be explicitly labeled as **synthetically generated/enriched** and must never be presented as if it came from the original source.

---

# 22. AI Agent Operating Rules

When implementing this project, follow these rules strictly.

## Rule 1 — Use the actual file
Inspect the source file before writing cleaning logic.

## Rule 2 — Never invent source columns
If a desired metric requires missing information, either:
1. calculate a valid proxy and label it clearly, or
2. create a separate synthetic enrichment layer and document it.

## Rule 3 — Never hide data problems
Data inconsistencies are part of the analytical story when they are genuine.

## Rule 4 — Preserve raw data
Never overwrite `data/raw/claim_data.csv`.

## Rule 5 — Reproducibility
Use a fixed random seed whenever synthetic enrichment is created.

## Rule 6 — Reconciliation
Python, SQL, and Tableau must reconcile on key KPIs.

## Rule 7 — Business first
Every SQL query and dashboard visual must answer a business question.

## Rule 8 — No KPI inflation
Never manufacture inflated row counts or claim unrealistic scale.

## Rule 9 — Interview defensibility
Every resume bullet must be traceable to an actual project artifact.

## Rule 10 — Keep scope controlled
The core deliverable is SQL + Tableau analytics. ML is optional and should not dominate the project.

---

# 23. Ideal Final Deliverables Checklist

## Data
- [ ] Raw dataset preserved
- [ ] Cleaned dataset generated
- [ ] Tableau-ready dataset generated
- [ ] Data dictionary completed

## Python
- [ ] Audit complete
- [ ] Cleaning complete
- [ ] Derived metrics complete
- [ ] Validation checks complete

## SQL
- [ ] Schema script
- [ ] Staging script
- [ ] Cleaning script
- [ ] Derived metrics script
- [ ] 30+ business queries
- [ ] Tableau views
- [ ] KPI reconciliation

## Tableau
- [ ] Executive Overview
- [ ] Denial Analytics
- [ ] Financial Performance
- [ ] AR / Follow-up / Data Quality
- [ ] Filters
- [ ] Dashboard actions
- [ ] Tooltips
- [ ] KPI definitions

## Documentation
- [ ] README
- [ ] Business requirements
- [ ] Data dictionary
- [ ] Metric definitions
- [ ] Business insights
- [ ] Limitations
- [ ] Synthetic data disclaimer

## Resume
- [ ] ATS-friendly project title
- [ ] 3–4 concise bullets
- [ ] SQL + Tableau clearly visible
- [ ] No unsupported claims

## Interview
- [ ] 10 SQL questions
- [ ] 10 analytics questions
- [ ] 5 Tableau questions
- [ ] 2-minute project explanation
- [ ] 30-second resume explanation

---

# 24. Definition of Done

The project is complete only when a recruiter can open the GitHub repository and understand:

1. what business problem was solved,
2. what data was used,
3. how the data was cleaned,
4. how SQL was used,
5. which KPIs were calculated,
6. what the Tableau dashboards show,
7. what insights were discovered,
8. what the limitations are,
9. how the results were validated,
10. and how the project relates to a Data Analyst / healthcare operations analytics role.

The final project should feel like a small **analytics consulting engagement**, not a generic Kaggle dashboard.

---

# 25. Recommended Build Order

Execute in exactly this order:

```text
SOURCE DATA
   ↓
DATA AUDIT
   ↓
DATA CLEANING
   ↓
DERIVED METRICS
   ↓
EXPLORATORY ANALYSIS
   ↓
SQL DATA MODEL
   ↓
SQL BUSINESS QUERIES
   ↓
TABLEAU DATA VIEW
   ↓
4 TABLEAU DASHBOARDS
   ↓
KPI RECONCILIATION
   ↓
BUSINESS INSIGHTS
   ↓
README + DOCUMENTATION
   ↓
RESUME BULLETS
   ↓
INTERVIEW QUESTIONS
```

Do not jump to Tableau before cleaning and defining metrics.
Do not write resume claims before the analysis is actually complete.

---

# 26. Immediate Next Action

Start with **Stage 1 — Data Audit** in Google Colab.

Required output:
- shape
- column list
- dtypes
- missing-value report
- duplicate report
- unique-value report for categorical fields
- financial range report
- status/outcome cross-tab
- monetary consistency checks

After the audit, freeze the data-quality rules and proceed to Stage 2.
