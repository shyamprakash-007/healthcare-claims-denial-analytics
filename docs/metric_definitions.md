# Metric definitions

Population: all 1,000 retained claims, service dates May 1–September 20, 2024. Filters restrict both numerator and denominator. One fact row per claim makes flag sums equivalent to distinct conditional counts. All divisions guard zero denominators and return null (not zero). Amounts are source currency units.

| Metric | Definition | Unfiltered value |
| --- | --- | --- |
| Total Claims | Distinct Claim ID | 1,000 |
| Denied Claims | Distinct Claim ID where Claim Status=Denied | 328 |
| Claim Status Denial Rate | Denied Claims / Total Claims | 32.8% |
| Outcome Denial Rate | Distinct Claim ID where Outcome=Denied / Total Claims | 33.1% |
| Paid Claims | Distinct Claim ID where Claim Status=Paid | 334 |
| Under Review Claims | Distinct Claim ID where Claim Status=Under Review | 338 |
| Follow-up Claims | Distinct claims requiring Yes | 522 |
| Follow-up Rate | Follow-up Claims / Total Claims | 52.2% |
| Total Billed | Sum Billed Amount | 297,191 |
| Total Allowed | Sum Allowed Amount | 223,112 |
| Total Paid | Sum Paid Amount | 200,754 |
| Gross Unpaid | Sum (Billed - Paid) | 96,437 |
| Allowed Amount Gap | Sum (Allowed - Paid) | 22,358 |
| Payment Rate | Total Paid / Total Billed | 67.5505% |
| Allowed Rate | Total Allowed / Total Billed | 75.0736% |
| Average Claim Value | Total Billed / Total Claims | 297.191 |
| Denied Billed Amount | Sum Billed where Claim Status=Denied | 98,069 |
| Any Denial Amount | Sum Billed where Claim Status OR Outcome=Denied | 160,801 |
| Any Denial Claims | Distinct claims where either denial flag=1 | 547 |
| Open AR Records | Distinct claims in four documented open statuses | 683 |
| Status Inconsistency Count | Distinct claims with status_consistency_flag=1 | 315 |

Rates shown in this document are rounded only for display. SQL and validation use unrounded values. Do not average claim-level payment ratios to calculate portfolio Payment Rate. The denied billed amount is an exposure associated with denied labels, not lost revenue. Any Denial uses an OR so overlapping claims are counted once. Open AR is a count under a documented grouping, not collectible AR. Denial rates filtered to Claim Status=Denied equal 100% by definition; they are not comparable with the all-status headline.

The workflow calls Allowed/Billed the “Billed-to-Allowed Ratio.” The field is retained for contract compatibility and its actual formula is stated explicitly. Allowed Rate is the aggregate version of Allowed/Billed.

Reference implementation: `scripts/pipeline.py`, `sql/04_derived_metrics.sql`, `sql/06_views_for_tableau.sql`. Native Tableau baseline and filtered KPI displays reconcile to SQL. See data/exports/tableau_native_validation.csv and the validation report. Dashboard rates use one decimal place; the backend retains full precision.
