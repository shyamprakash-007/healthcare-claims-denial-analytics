# SQL business question catalog

Source: `sql/05_business_analysis.sql`. Results in `sql/results/` (DuckDB CSV) and `sql/results_postgres/` (PostgreSQL JSON). All 37 queries executed. Rates are proportions unless displayed as percentages.

| Query | Level | Business question | Result stem |
| --- | --- | --- | --- |
| 01 | Basic | How many unique claims are in scope? | total_claims |
| 02 | Basic | What is the billed value? | total_billed |
| 03 | Basic | What is the allowed value? | total_allowed |
| 04 | Basic | What is the paid value? | total_paid |
| 05 | Basic | How are operational statuses distributed? | claim_status_distribution |
| 06 | Basic | Where is insurance-category claim volume concentrated? | insurance_type_distribution |
| 07 | Basic | How are AR labels distributed? | ar_status_distribution |
| 08 | Basic | How many claims require follow-up? | follow_up_required_distribution |
| 09 | Basic | Which source reasons appear across all statuses? | reason_code_distribution |
| 10 | Basic | How are outcomes distributed? | outcome_distribution |
| 11 | Intermediate | Which insurance category has the highest denial rate? | denial_rate_by_insurance |
| 12 | Intermediate | Which reason groups have the highest within-group denial rate? | denial_rate_by_reason |
| 13 | Intermediate | Which insurance categories contribute billed value? | billed_by_insurance |
| 14 | Intermediate | Which insurance categories contribute paid value? | paid_by_insurance |
| 15 | Intermediate | Where is gross unpaid concentrated? | gross_unpaid_by_insurance |
| 16 | Intermediate | Where is follow-up most common? | follow_up_rate_by_insurance |
| 17 | Intermediate | How many claims occur in each service month? | monthly_claim_volume |
| 18 | Intermediate | How much billed value is associated with denied claims each month? | monthly_denied_amount |
| 19 | Intermediate | How does average claim value differ by category? | average_claim_value_by_insurance |
| 20 | Intermediate | What share of billed amount was paid by insurance category? | payment_rate_by_insurance |
| 21 | Advanced | Which insurance categories rank highest by denied billed exposure? | rank_insurance_denied_amount |
| 22 | Advanced | Which reasons rank highest by denied claim frequency? | rank_denial_reasons |
| 23 | Advanced | How does the denial rate change month to month? | monthly_denial_trend |
| 24 | Advanced | How does service-month volume change? | mom_claim_volume |
| 25 | Advanced | How does service-month paid value change? | mom_paid_amount |
| 26 | Advanced | How much billed value accumulates across observed months? | cumulative_monthly_billed |
| 27 | Advanced | Which procedures have the largest gross unpaid amounts? | top_procedures_gross_unpaid |
| 28 | Advanced | Which diagnoses appear most frequently on denied claims? | top_diagnoses_denials |
| 29 | Advanced | Which denied claims are at or above the denied-population 90th percentile? | high_value_denied_claims |
| 30 | Advanced | Which status/outcome combinations trigger review? | status_outcome_inconsistency |
| 31 | Advanced | Do all governed KPIs reconcile? | kpi_summary |
| 32 | Advanced | Is follow-up more common among denied or under-review claims? | follow_up_by_status |
| 33 | Advanced | Where is gross unpaid concentrated among explicitly open statuses? | open_ar_exposure |
| 34 | Advanced | How do quality review flags vary by month? | monthly_quality_issues |
| 35 | Advanced | How do the two denial definitions overlap? | denial_definition_overlap |
| 36 | Advanced | How much has already been paid on denied-status claims? | denied_paid_value |
| 37 | Advanced | Which three reason groups contribute the most denied billed value within each insurance category? | reason_by_insurance_priority |

`RANK` retains ties in denied amount ranking; `DENSE_RANK` ranks reason frequencies without rank gaps; `ROW_NUMBER` provides deterministic claim review order and per-insurance top-three reason selection. `LAG` supports month-to-month comparisons. `PERCENTILE_CONT` supplies a data-relative high-value threshold rather than inventing a currency cutoff. Conditional aggregation keeps denominators visible. September is a partial month. Rates by reason are within all claims carrying that reason; reason frequency among denials is a separate query.
