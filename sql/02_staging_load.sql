-- Run psql from the repository root after running the Python preparation notebook.
-- CSV contains additional derived columns; use the source-only staging file.
-- This client-side command is PostgreSQL psql syntax. The Python runner uses a bound dataframe instead.
\copy stg_claims (claim_id, provider_id, patient_id, date_of_service, billed_amount, procedure_code, diagnosis_code, allowed_amount, paid_amount, insurance_type, claim_status, reason_code, follow_up_required, ar_status, outcome) FROM 'data/processed/claims_staging.csv' WITH (FORMAT csv, HEADER true, NULL '');
