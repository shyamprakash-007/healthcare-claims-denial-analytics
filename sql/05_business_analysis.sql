-- September is partial (through Sep 20). MoM changes are descriptive, not like-for-like performance.
-- Amounts are source currency units; currency is unspecified.

-- BASIC

-- Q01 | total_claims
SELECT COUNT(DISTINCT claim_id) AS total_claims FROM fact_claims;

-- Q02 | total_billed
SELECT SUM(billed_amount) AS total_billed FROM fact_claims;

-- Q03 | total_allowed
SELECT SUM(allowed_amount) AS total_allowed FROM fact_claims;

-- Q04 | total_paid
SELECT SUM(paid_amount) AS total_paid FROM fact_claims;

-- Q05 | claim_status_distribution
SELECT claim_status, COUNT(DISTINCT claim_id) AS claims FROM vw_claims_analytics GROUP BY claim_status ORDER BY claims DESC, claim_status;

-- Q06 | insurance_type_distribution
SELECT insurance_type, COUNT(DISTINCT claim_id) AS claims FROM vw_claims_analytics GROUP BY insurance_type ORDER BY claims DESC, insurance_type;

-- Q07 | ar_status_distribution
SELECT ar_status, COUNT(DISTINCT claim_id) AS claims FROM vw_claims_analytics GROUP BY ar_status ORDER BY claims DESC, ar_status;

-- Q08 | follow_up_required_distribution
SELECT follow_up_required, COUNT(DISTINCT claim_id) AS claims FROM vw_claims_analytics GROUP BY follow_up_required ORDER BY claims DESC, follow_up_required;

-- Q09 | reason_code_distribution
SELECT reason_code, COUNT(DISTINCT claim_id) AS claims FROM vw_claims_analytics GROUP BY reason_code ORDER BY claims DESC, reason_code;

-- Q10 | outcome_distribution
SELECT outcome, COUNT(DISTINCT claim_id) AS claims FROM vw_claims_analytics GROUP BY outcome ORDER BY claims DESC, outcome;

-- INTERMEDIATE

-- Q11 | denial_rate_by_insurance
SELECT insurance_type, COUNT(DISTINCT claim_id) AS denominator_claims, 1.0*SUM(claim_status_denied_flag)/NULLIF(COUNT(DISTINCT claim_id),0) AS metric FROM vw_claims_analytics GROUP BY insurance_type ORDER BY insurance_type;

-- Q12 | denial_rate_by_reason
SELECT reason_code, COUNT(DISTINCT claim_id) AS denominator_claims, 1.0*SUM(claim_status_denied_flag)/NULLIF(COUNT(DISTINCT claim_id),0) AS metric FROM vw_claims_analytics GROUP BY reason_code ORDER BY reason_code;

-- Q13 | billed_by_insurance
SELECT insurance_type, COUNT(DISTINCT claim_id) AS denominator_claims, SUM(billed_amount) AS metric FROM vw_claims_analytics GROUP BY insurance_type ORDER BY insurance_type;

-- Q14 | paid_by_insurance
SELECT insurance_type, COUNT(DISTINCT claim_id) AS denominator_claims, SUM(paid_amount) AS metric FROM vw_claims_analytics GROUP BY insurance_type ORDER BY insurance_type;

-- Q15 | gross_unpaid_by_insurance
SELECT insurance_type, COUNT(DISTINCT claim_id) AS denominator_claims, SUM(gross_unpaid_amount) AS metric FROM vw_claims_analytics GROUP BY insurance_type ORDER BY insurance_type;

-- Q16 | follow_up_rate_by_insurance
SELECT insurance_type, COUNT(DISTINCT claim_id) AS denominator_claims, 1.0*SUM(follow_up_flag)/NULLIF(COUNT(DISTINCT claim_id),0) AS metric FROM vw_claims_analytics GROUP BY insurance_type ORDER BY insurance_type;

-- Q17 | monthly_claim_volume
SELECT service_month_start, COUNT(DISTINCT claim_id) AS denominator_claims, COUNT(DISTINCT claim_id) AS metric FROM vw_claims_analytics GROUP BY service_month_start ORDER BY service_month_start;

-- Q18 | monthly_denied_amount
SELECT service_month_start, COUNT(DISTINCT claim_id) AS denominator_claims, SUM(CASE WHEN claim_status='Denied' THEN billed_amount ELSE 0 END) AS metric FROM vw_claims_analytics GROUP BY service_month_start ORDER BY service_month_start;

-- Q19 | average_claim_value_by_insurance
SELECT insurance_type, COUNT(DISTINCT claim_id) AS denominator_claims, SUM(billed_amount)/NULLIF(COUNT(DISTINCT claim_id),0) AS metric FROM vw_claims_analytics GROUP BY insurance_type ORDER BY insurance_type;

-- Q20 | payment_rate_by_insurance
SELECT insurance_type, COUNT(DISTINCT claim_id) AS denominator_claims, SUM(paid_amount)/NULLIF(SUM(billed_amount),0) AS metric FROM vw_claims_analytics GROUP BY insurance_type ORDER BY insurance_type;

-- ADVANCED

-- Q21 | rank_insurance_denied_amount
WITH s AS (SELECT insurance_type, SUM(billed_amount) AS denied_amount FROM vw_claims_analytics WHERE claim_status='Denied' GROUP BY insurance_type) SELECT *, RANK() OVER (ORDER BY denied_amount DESC) AS amount_rank FROM s ORDER BY amount_rank,insurance_type;

-- Q22 | rank_denial_reasons
WITH s AS (SELECT reason_code,COUNT(DISTINCT claim_id) AS denied_claims FROM vw_claims_analytics WHERE claim_status='Denied' GROUP BY reason_code) SELECT *,DENSE_RANK() OVER (ORDER BY denied_claims DESC) AS reason_rank FROM s ORDER BY reason_rank,reason_code;

-- Q23 | monthly_denial_trend
WITH m AS (SELECT service_month_start, COUNT(DISTINCT claim_id) AS claims, 1.0*SUM(claim_status_denied_flag)/NULLIF(COUNT(DISTINCT claim_id),0) AS denial_rate FROM vw_claims_analytics GROUP BY service_month_start) SELECT *,denial_rate-LAG(denial_rate) OVER (ORDER BY service_month_start) AS change_proportion FROM m ORDER BY service_month_start;

-- Q24 | mom_claim_volume
WITH m AS (SELECT service_month_start,COUNT(DISTINCT claim_id) AS metric FROM vw_claims_analytics GROUP BY service_month_start), p AS (SELECT *, LAG(metric) OVER (ORDER BY service_month_start) AS previous FROM m) SELECT *,1.0*(metric-previous)/NULLIF(previous,0) AS mom_change FROM p ORDER BY service_month_start;

-- Q25 | mom_paid_amount
WITH m AS (SELECT service_month_start,SUM(paid_amount) AS metric FROM vw_claims_analytics GROUP BY service_month_start), p AS (SELECT *, LAG(metric) OVER (ORDER BY service_month_start) AS previous FROM m) SELECT *,1.0*(metric-previous)/NULLIF(previous,0) AS mom_change FROM p ORDER BY service_month_start;

-- Q26 | cumulative_monthly_billed
WITH m AS (SELECT service_month_start,SUM(billed_amount) AS billed FROM vw_claims_analytics GROUP BY service_month_start) SELECT *,SUM(billed) OVER (ORDER BY service_month_start ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_billed FROM m ORDER BY service_month_start;

-- Q27 | top_procedures_gross_unpaid
SELECT procedure_code,COUNT(*) AS claims,SUM(gross_unpaid_amount) AS gross_unpaid FROM vw_claims_analytics GROUP BY procedure_code ORDER BY gross_unpaid DESC,procedure_code LIMIT 10;

-- Q28 | top_diagnoses_denials
SELECT diagnosis_code,COUNT(DISTINCT claim_id) AS denied_claims FROM vw_claims_analytics WHERE claim_status='Denied' GROUP BY diagnosis_code ORDER BY denied_claims DESC,diagnosis_code LIMIT 10;

-- Q29 | high_value_denied_claims
WITH threshold AS (SELECT PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY billed_amount) AS p90 FROM vw_claims_analytics WHERE claim_status='Denied') SELECT claim_id,insurance_type,billed_amount,reason_code,p90,ROW_NUMBER() OVER (ORDER BY billed_amount DESC,claim_id) AS review_order FROM vw_claims_analytics CROSS JOIN threshold WHERE claim_status='Denied' AND billed_amount>=p90 ORDER BY review_order;

-- Q30 | status_outcome_inconsistency
SELECT claim_status,outcome,COUNT(*) AS claims,SUM(status_consistency_flag) AS inconsistent,SUM(status_ambiguity_flag) AS ambiguous FROM vw_claims_analytics GROUP BY claim_status,outcome ORDER BY claim_status,outcome;

-- Q31 | kpi_summary
SELECT * FROM vw_kpi_summary;

-- Q32 | follow_up_by_status
SELECT claim_status,COUNT(*) AS claims,SUM(follow_up_flag) AS follow_up_claims,1.0*SUM(follow_up_flag)/NULLIF(COUNT(*),0) AS follow_up_rate FROM vw_claims_analytics GROUP BY claim_status ORDER BY follow_up_rate DESC;

-- Q33 | open_ar_exposure
SELECT insurance_type,ar_status,COUNT(*) AS claims,SUM(gross_unpaid_amount) AS gross_unpaid FROM vw_claims_analytics WHERE open_ar_flag=1 GROUP BY insurance_type,ar_status ORDER BY gross_unpaid DESC,insurance_type,ar_status;

-- Q34 | monthly_quality_issues
SELECT service_month_start,SUM(status_consistency_flag) AS status_review,SUM(ar_status_review_flag) AS ar_review,SUM(monetary_anomaly_flag) AS monetary_anomalies,COUNT(*) AS claims FROM vw_claims_analytics GROUP BY service_month_start ORDER BY service_month_start;

-- Q35 | denial_definition_overlap
SELECT claim_status_denied_flag,outcome_denied_flag,COUNT(*) AS claims,SUM(billed_amount) AS billed FROM vw_claims_analytics GROUP BY claim_status_denied_flag,outcome_denied_flag ORDER BY claim_status_denied_flag,outcome_denied_flag;

-- Q36 | denied_paid_value
SELECT COUNT(*) AS denied_with_payment,SUM(paid_amount) AS paid_on_denied,SUM(gross_unpaid_amount) AS gross_unpaid_on_denied FROM vw_claims_analytics WHERE denied_with_payment_flag=1;

-- Q37 | reason_by_insurance_priority
WITH s AS (SELECT insurance_type,reason_code,COUNT(*) AS denied_claims,SUM(billed_amount) AS denied_billed FROM vw_claims_analytics WHERE claim_status='Denied' GROUP BY insurance_type,reason_code),r AS (SELECT *,ROW_NUMBER() OVER (PARTITION BY insurance_type ORDER BY denied_billed DESC,reason_code) AS priority FROM s) SELECT * FROM r WHERE priority<=3 ORDER BY insurance_type,priority;
