-- Stage contains the normalized source columns only; all metrics are recomputed in SQL.
-- Required values, date syntax, vocabularies and conflicting IDs are validated by Python before load.
INSERT INTO dim_provider SELECT ROW_NUMBER() OVER (ORDER BY provider_id), provider_id FROM (SELECT DISTINCT TRIM(provider_id) AS provider_id FROM stg_claims) s;
INSERT INTO dim_patient SELECT ROW_NUMBER() OVER (ORDER BY patient_id), patient_id FROM (SELECT DISTINCT TRIM(patient_id) AS patient_id FROM stg_claims) s;
INSERT INTO dim_insurance SELECT ROW_NUMBER() OVER (ORDER BY insurance_type), insurance_type FROM (SELECT DISTINCT TRIM(insurance_type) AS insurance_type FROM stg_claims) s;
INSERT INTO dim_procedure SELECT ROW_NUMBER() OVER (ORDER BY procedure_code), procedure_code FROM (SELECT DISTINCT TRIM(procedure_code) AS procedure_code FROM stg_claims) s;
INSERT INTO dim_diagnosis SELECT ROW_NUMBER() OVER (ORDER BY diagnosis_code), diagnosis_code FROM (SELECT DISTINCT TRIM(diagnosis_code) AS diagnosis_code FROM stg_claims) s;
INSERT INTO dim_reason SELECT ROW_NUMBER() OVER (ORDER BY reason_code), reason_code FROM (SELECT DISTINCT TRIM(reason_code) AS reason_code FROM stg_claims) s;
INSERT INTO dim_date
SELECT CAST(EXTRACT(YEAR FROM d)*10000 + EXTRACT(MONTH FROM d)*100 + EXTRACT(DAY FROM d) AS INTEGER), d,
 CAST(EXTRACT(YEAR FROM d) AS INTEGER), CAST(EXTRACT(MONTH FROM d) AS INTEGER),
 CASE CAST(EXTRACT(MONTH FROM d) AS INTEGER) WHEN 1 THEN 'January' WHEN 2 THEN 'February' WHEN 3 THEN 'March' WHEN 4 THEN 'April' WHEN 5 THEN 'May' WHEN 6 THEN 'June' WHEN 7 THEN 'July' WHEN 8 THEN 'August' WHEN 9 THEN 'September' WHEN 10 THEN 'October' WHEN 11 THEN 'November' WHEN 12 THEN 'December' END,
 CAST(EXTRACT(QUARTER FROM d) AS INTEGER), CAST(EXTRACT(WEEK FROM d) AS INTEGER), CAST(EXTRACT(ISODOW FROM d) AS INTEGER), CAST(DATE_TRUNC('month',d) AS DATE)
FROM (SELECT DISTINCT CAST(date_of_service AS DATE) AS d FROM stg_claims) s;
INSERT INTO fact_claims (claim_key, claim_id, provider_key, patient_key, insurance_key, procedure_key, diagnosis_key, reason_key, date_key, billed_amount, allowed_amount, paid_amount, claim_status, follow_up_required, ar_status, outcome)
SELECT ROW_NUMBER() OVER (ORDER BY s.claim_id), TRIM(s.claim_id), provider.provider_key, patient.patient_key, insurance.insurance_key, procedure.procedure_key, diagnosis.diagnosis_key, reason.reason_key, dt.date_key, CAST(s.billed_amount AS NUMERIC(18,2)), CAST(s.allowed_amount AS NUMERIC(18,2)), CAST(s.paid_amount AS NUMERIC(18,2)), TRIM(s.claim_status), TRIM(s.follow_up_required), TRIM(s.ar_status), TRIM(s.outcome)
FROM stg_claims s
JOIN dim_provider provider ON provider.provider_id=TRIM(s.provider_id)
JOIN dim_patient patient ON patient.patient_id=TRIM(s.patient_id)
JOIN dim_insurance insurance ON insurance.insurance_type=TRIM(s.insurance_type)
JOIN dim_procedure procedure ON procedure.procedure_code=TRIM(s.procedure_code)
JOIN dim_diagnosis diagnosis ON diagnosis.diagnosis_code=TRIM(s.diagnosis_code)
JOIN dim_reason reason ON reason.reason_code=TRIM(s.reason_code)
JOIN dim_date dt ON dt.full_date=CAST(s.date_of_service AS DATE);
