-- Flag=1 means REVIEW, not confirmed error. See docs/data_quality_rulebook.md.
UPDATE fact_claims SET
 gross_unpaid_amount = billed_amount - paid_amount,
 allowed_amount_gap = allowed_amount - paid_amount,
 billed_to_allowed_ratio = 1.0 * allowed_amount / NULLIF(billed_amount,0),
 paid_to_billed_ratio = 1.0 * paid_amount / NULLIF(billed_amount,0),
 paid_to_allowed_ratio = 1.0 * paid_amount / NULLIF(allowed_amount,0),
 claim_status_denied_flag = CASE WHEN claim_status='Denied' THEN 1 ELSE 0 END,
 outcome_denied_flag = CASE WHEN outcome='Denied' THEN 1 ELSE 0 END,
 any_denial_flag = CASE WHEN claim_status='Denied' OR outcome='Denied' THEN 1 ELSE 0 END,
 follow_up_flag = CASE WHEN follow_up_required='Yes' THEN 1 ELSE 0 END,
 open_ar_flag = CASE WHEN ar_status IN ('Open','Pending','On Hold','Partially Paid') THEN 1 ELSE 0 END,
 status_consistency_flag = CASE WHEN (claim_status='Denied' AND outcome IN ('Paid','Partially Paid')) OR (claim_status='Paid' AND outcome='Denied') THEN 1 ELSE 0 END,
 status_ambiguity_flag = CASE WHEN claim_status='Under Review' AND outcome IN ('Paid','Partially Paid') THEN 1 ELSE 0 END,
 ar_status_review_flag = CASE WHEN (claim_status='Paid' AND ar_status='Denied') OR (claim_status='Under Review' AND ar_status='Closed') OR (claim_status='Denied' AND ar_status='Partially Paid') THEN 1 ELSE 0 END,
 monetary_anomaly_flag = CASE WHEN billed_amount<0 OR allowed_amount<0 OR paid_amount<0 OR allowed_amount>billed_amount OR paid_amount>allowed_amount OR paid_amount>billed_amount THEN 1 ELSE 0 END,
 zero_amount_flag = CASE WHEN billed_amount=0 OR allowed_amount=0 OR paid_amount=0 THEN 1 ELSE 0 END,
 denied_with_payment_flag = CASE WHEN claim_status='Denied' AND paid_amount>0 THEN 1 ELSE 0 END,
 paid_with_allowed_gap_flag = CASE WHEN claim_status='Paid' AND allowed_amount>paid_amount THEN 1 ELSE 0 END;
UPDATE fact_claims SET code_format_flag = CASE WHEN claim_id !~ '^[A-Z0-9]{10}$'
 OR provider_key IN (SELECT provider_key FROM dim_provider WHERE provider_id !~ '^[0-9]{10}$')
 OR patient_key IN (SELECT patient_key FROM dim_patient WHERE patient_id !~ '^[0-9]{10}$')
 OR procedure_key IN (SELECT procedure_key FROM dim_procedure WHERE procedure_code !~ '^[0-9]{5}$')
 OR diagnosis_key IN (SELECT diagnosis_key FROM dim_diagnosis WHERE diagnosis_code !~ '^[A-Z][0-9]{2}[.][0-9]$') THEN 1 ELSE 0 END;
