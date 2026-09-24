# Data dictionary

All identifiers/codes remain strings. All source fields are required for this snapshot build. Derived ratios can be null when a denominator is zero.

| Field | Origin | Type | Definition |
| --- | --- | --- | --- |
| claim_id | source | text | Source claim identifier; fact business key; 1,000 distinct values. |
| provider_id | source | text | Source provider identifier; no name or specialty supplied. All 1,000 distinct. |
| patient_id | source | text | Source synthetic patient identifier; no demographics supplied. All 1,000 distinct. |
| date_of_service | source | date | Service date, originally MM/DD/YYYY; exported YYYY-MM-DD. |
| billed_amount | source | numeric | Source billed amount; source currency units, unspecified currency. |
| procedure_code | source | text | Source procedure code as text; no clinical label or validity inferred. |
| diagnosis_code | source | text | Source diagnosis code as text; no clinical description inferred. |
| allowed_amount | source | numeric | Source allowed amount; same unspecified currency units. |
| paid_amount | source | numeric | Source paid amount associated with the claim; payment date unavailable. |
| insurance_type | source | text | Observed broad insurance category; not a payer company. Observed values: Commercial, Medicaid, Medicare, Self-Pay. |
| claim_status | source | text | Operational source status; basis of primary denial rate. Observed values: Denied, Paid, Under Review. |
| reason_code | source | text | Descriptive source reason, present for all statuses; not an official code mapping. Observed values: Authorization not obtained, Duplicate claim, Incorrect billing information, Lack of medical necessity, Missing documentation, Patient eligibility issues, Pre-existing condition, Service not covered. |
| follow_up_required | source | text | Canonical Yes/No source field. Observed values: No, Yes. |
| ar_status | source | text | Unmodified source AR label after case/whitespace normalization. Observed values: Closed, Denied, On Hold, Open, Partially Paid, Pending. |
| outcome | source | text | Separate source outcome; preserve independently of Claim Status. Observed values: Denied, Paid, Partially Paid. |
| gross_unpaid_amount | derived | numeric | Billed minus paid. Source currency units. Collectibility unknown. |
| allowed_amount_gap | derived | numeric | Allowed minus paid. Source currency units. |
| billed_to_allowed_ratio | derived | numeric | Allowed / billed; null if billed=0. Name retained from workflow; displayed definition removes naming ambiguity. |
| paid_to_billed_ratio | derived | numeric | Paid / billed per claim; null if billed=0. |
| paid_to_allowed_ratio | derived | numeric | Paid / allowed per claim; null if allowed=0. |
| claim_status_denied_flag | derived | numeric | 1 if Claim Status Denied, else 0. |
| outcome_denied_flag | derived | numeric | 1 if Outcome Denied, else 0. |
| any_denial_flag | derived | numeric | 1 if either status or outcome is Denied; union, not sum. |
| follow_up_flag | derived | numeric | Yes=1, No=0. Missing/other values fail preparation. |
| open_ar_flag | derived | numeric | 1 for Open/Pending/On Hold/Partially Paid, else 0. Not proof of collectibility. |
| status_consistency_flag | derived | numeric | 0/1 review flag; exact rule in data_quality_rulebook.md. |
| status_ambiguity_flag | derived | numeric | 0/1 review flag; exact rule in data_quality_rulebook.md. |
| ar_status_review_flag | derived | numeric | 0/1 review flag; exact rule in data_quality_rulebook.md. |
| monetary_anomaly_flag | derived | numeric | 0/1 review flag; exact rule in data_quality_rulebook.md. |
| zero_amount_flag | derived | numeric | 0/1 review flag; exact rule in data_quality_rulebook.md. |
| denied_with_payment_flag | derived | numeric | 0/1 review flag; exact rule in data_quality_rulebook.md. |
| paid_with_allowed_gap_flag | derived | numeric | 0/1 review flag; exact rule in data_quality_rulebook.md. |
| code_format_flag | derived | numeric | 0/1 review flag; exact rule in data_quality_rulebook.md. |
| service_year | derived | numeric | Calendar service year. |
| service_month | derived | numeric | Calendar month number 1–12. |
| service_month_name | derived | text | English calendar month name. Sort with service_month_start. |
| service_quarter | derived | numeric | Calendar quarter 1–4. |
| service_week | derived | numeric | ISO week number; do not group across years using this alone. |
| service_day_of_week | derived | numeric | ISO weekday Monday=1 to Sunday=7. |
| service_month_start | derived | date | First date of the service month; chronological month key. |

The SQL analytical view adds `claim_key`, an ordered integer surrogate key. Dimension keys are technical join keys only. Numeric source amounts are integers in this file; the SQL model uses NUMERIC(18,2). No source currency, coding-system validity or payer identity is inferred.
