CREATE VIEW vw_claims_analytics AS
SELECT f.claim_key,f.claim_id,provider.provider_id, patient.patient_id, insurance.insurance_type, procedure.procedure_code, diagnosis.diagnosis_code, reason.reason_code, dt.full_date AS date_of_service,
f.billed_amount, f.allowed_amount, f.paid_amount, f.claim_status, f.follow_up_required, f.ar_status, f.outcome, f.gross_unpaid_amount, f.allowed_amount_gap, f.billed_to_allowed_ratio, f.paid_to_billed_ratio, f.paid_to_allowed_ratio, f.claim_status_denied_flag, f.outcome_denied_flag, f.any_denial_flag, f.follow_up_flag, f.open_ar_flag, f.status_consistency_flag, f.status_ambiguity_flag, f.ar_status_review_flag, f.monetary_anomaly_flag, f.zero_amount_flag, f.denied_with_payment_flag, f.paid_with_allowed_gap_flag, f.code_format_flag,
 dt.year AS service_year, dt.month AS service_month, dt.month_name AS service_month_name, dt.quarter AS service_quarter, dt.week AS service_week, dt.day_of_week AS service_day_of_week, dt.service_month_start
FROM fact_claims f
JOIN dim_provider provider ON f.provider_key=provider.provider_key
JOIN dim_patient patient ON f.patient_key=patient.patient_key
JOIN dim_insurance insurance ON f.insurance_key=insurance.insurance_key
JOIN dim_procedure procedure ON f.procedure_key=procedure.procedure_key
JOIN dim_diagnosis diagnosis ON f.diagnosis_key=diagnosis.diagnosis_key
JOIN dim_reason reason ON f.reason_key=reason.reason_key
JOIN dim_date dt ON f.date_key=dt.date_key;
CREATE VIEW vw_kpi_summary AS SELECT
COUNT(DISTINCT claim_id) AS total_claims,
SUM(billed_amount) AS total_billed_amount,
SUM(allowed_amount) AS total_allowed_amount,
SUM(paid_amount) AS total_paid_amount,
COUNT(DISTINCT CASE WHEN claim_status='Denied' THEN claim_id END) AS denied_claims,
COUNT(DISTINCT CASE WHEN outcome='Denied' THEN claim_id END) AS outcome_denied_claims,
COUNT(DISTINCT CASE WHEN claim_status='Paid' THEN claim_id END) AS paid_claims,
COUNT(DISTINCT CASE WHEN claim_status='Under Review' THEN claim_id END) AS under_review_claims,
SUM(follow_up_flag) AS follow_up_claims,
SUM(gross_unpaid_amount) AS gross_unpaid_amount,
SUM(CASE WHEN claim_status='Denied' THEN billed_amount ELSE 0 END) AS denied_billed_amount,
SUM(CASE WHEN any_denial_flag=1 THEN billed_amount ELSE 0 END) AS any_denial_amount,
SUM(open_ar_flag) AS open_ar_records,
SUM(status_consistency_flag) AS status_inconsistency_count,
SUM(paid_amount)/NULLIF(SUM(billed_amount),0) AS payment_rate,
SUM(allowed_amount)/NULLIF(SUM(billed_amount),0) AS allowed_rate,
SUM(billed_amount)/NULLIF(COUNT(DISTINCT claim_id),0) AS average_claim_value,
1.0*SUM(claim_status_denied_flag)/NULLIF(COUNT(DISTINCT claim_id),0) AS claim_status_denial_rate,
1.0*SUM(outcome_denied_flag)/NULLIF(COUNT(DISTINCT claim_id),0) AS outcome_denial_rate,
1.0*SUM(follow_up_flag)/NULLIF(COUNT(DISTINCT claim_id),0) AS follow_up_rate
FROM vw_claims_analytics;
