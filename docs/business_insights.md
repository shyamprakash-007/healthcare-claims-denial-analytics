# Business insights

All observations concern synthetic claims with service dates May 1–September 20, 2024. No real healthcare organization or realized operational impact is represented. All amounts are source currency units.

## Denial definitions overlap only partially

**Observation and evidence:** Claim Status reports 328 denied claims; Outcome reports 331. Only 112 are in both groups. The union is 547 claims, or 54.7%.

**Business implication:** Two similar headline rates hide different claim populations. Combining the counts would double-count the overlap.

**Potential action:** Keep the two rates side by side and confirm the intended status lifecycle before choosing an operational KPI.

Evidence: `sql/results/Q35_denial_definition_overlap.csv`.

## Denied billed value is not lost revenue

**Observation and evidence:** Denied claims carry 98,069 billed, 65,931 paid and 32,138 gross unpaid. All 328 denied claims have positive paid amounts.

**Business implication:** Treating all denied billed value as unrecovered revenue would overstate the available evidence.

**Potential action:** Review denial/payment timing definitions and retain the positive payments. Do not estimate recovery without payment and adjustment events.

Evidence: `sql/results/Q36_denied_paid_value.csv`.

## Medicare has the highest observed denial rate

**Observation and evidence:** Medicare: 84/233 = 36.05%; portfolio: 328/1,000 = 32.80%; Medicaid: 75/259 = 28.96%. Medicare is 3.25 percentage points above the portfolio.

**Business implication:** The sample suggests a review segment, but these descriptive synthetic differences do not establish payer behavior or causation.

**Potential action:** Inspect reason mix within Medicare using Q37 before proposing targeted validation checks.

Evidence: `sql/results/Q11_denial_rate_by_insurance.csv`.

## Commercial has the largest denied billed amount

**Observation and evidence:** Commercial accounts for 27,386 of 98,069 denied billed units (27.93%), ahead of Self-Pay at 24,435.

**Business implication:** The category with the highest denial rate is not the category with the highest denied billed exposure.

**Potential action:** Prioritize amount-based and rate-based review queues separately, and inspect value and volume together.

Evidence: `sql/results/Q21_rank_insurance_denied_amount.csv`.

## Two reasons account for almost three in ten denied claims

**Observation and evidence:** Incorrect billing information appears on 49 denied claims (14.94%); Authorization not obtained on 48 (14.63%). Together: 97/328 = 29.57%.

**Business implication:** These source reason descriptions concentrate a useful share of the denied review queue, without proving the origin of denial.

**Potential action:** Review source billing-information and authorization workflows in a hypothetical operational follow-up; verify reason coding first.

Evidence: `sql/results/Q22_rank_denial_reasons.csv`.

## Gross unpaid exceeds the allowed amount gap

**Observation and evidence:** Total gross unpaid is 96,437, comprising a 74,079 billed-to-allowed difference and a 22,358 allowed-to-paid gap.

**Business implication:** Billed minus paid includes amounts outside the allowed amount. Neither component establishes contract adjustments or recoverability.

**Potential action:** Report both gaps explicitly and request adjustment/contract evidence before treating either as collectible.

Evidence: `sql/results/Q31_kpi_summary.csv`.

## Procedure 99231 has the largest gross unpaid total

**Observation and evidence:** Code 99231 has 114 claims and 11,127 gross unpaid units (11.54% of the total). Code 99221 follows at 10,478.

**Business implication:** The largest total partly reflects claim volume and should not be described as the worst-performing clinical service.

**Potential action:** Compare average gap and reason mix for these codes without inventing procedure descriptions.

Evidence: `sql/results/Q27_top_procedures_gross_unpaid.csv`.

## Follow-up work is not concentrated only in denied claims

**Observation and evidence:** 522 claims require follow-up. Paid-status claims contribute 181 (54.19% within status); Under Review 177 (52.37%); Denied 164 (50.00%).

**Business implication:** A denied-only queue would omit 358 follow-up claims in the supplied data.

**Potential action:** Use the explicit Follow-up Required field for workload and investigate why paid claims still require action.

Evidence: `sql/results/Q32_follow_up_by_status.csv`.

## Open-status records are a documented subset

**Observation and evidence:** Open 160, Pending 162, On Hold 177 and Partially Paid 184 total 683 open-status records. Denied 157 and Closed 160 are shown separately.

**Business implication:** The grouping describes operational labels, not a finance-certified AR balance.

**Potential action:** Keep Denied separate until collection/closure policies can define its treatment.

Evidence: `sql/results/Q07_ar_status_distribution.csv`.

## Status ambiguity is a major reporting limitation

**Observation and evidence:** 315 claims (31.5%) meet the contradiction rule; an additional 218 (21.8%) have Under Review with a paid/partially-paid outcome.

**Business implication:** Summaries may be sensitive to whether status or outcome is considered authoritative. The dataset has no event timestamps to resolve this.

**Potential action:** Publish the rulebook and both measures, and obtain lifecycle definitions before assigning error corrections.

Evidence: `sql/results/Q30_status_outcome_inconsistency.csv`.

## September cannot be compared as a full month

**Observation and evidence:** The file has 198 August claims and 131 September claims through September 20. The raw MoM change is -33.84%, while recorded calendar coverage also shortens.

**Business implication:** The volume decline cannot be interpreted as a full-month operational deterioration.

**Potential action:** Mark September partial. Obtain the remaining month or explicitly compare matched date windows before drawing a trend conclusion.

Evidence: `sql/results/Q24_mom_claim_volume.csv`.

## Provider and patient comparisons lack repeat observations

**Observation and evidence:** Each of the 1,000 provider IDs and each of the 1,000 patient IDs appears once. There are 10 procedure codes and 100 diagnosis codes.

**Business implication:** A provider denial rate would be 0% or 100% from a single claim and would not support a performance ranking.

**Potential action:** Focus on insurance categories, procedures and source reasons; request repeated observations for provider/patient analysis.

Evidence: `data/audit/column_profile.csv`.
